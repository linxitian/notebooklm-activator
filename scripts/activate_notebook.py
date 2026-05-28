import os
import sys
import json
import time
import shutil
import ctypes
import sqlite3
import argparse
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Ensure stdout uses UTF-8 to avoid encoding errors on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_char))]

def decrypt_key_with_dpapi(encrypted_key):
    p_data_in = DATA_BLOB(len(encrypted_key), ctypes.cast(ctypes.create_string_buffer(encrypted_key), ctypes.POINTER(ctypes.c_char)))
    p_data_out = DATA_BLOB()
    
    if ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(p_data_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(p_data_out)
    ):
        data = ctypes.string_at(p_data_out.pbData, p_data_out.cbData)
        ctypes.windll.kernel32.LocalFree(p_data_out.pbData)
        return data
    else:
        raise OSError("CryptUnprotectData failed")

def get_encryption_key():
    local_state_path = Path(os.environ['USERPROFILE']) / 'AppData/Local/Google/Chrome/User Data/Local State'
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.loads(f.read())
    
    encrypted_key = base64_decode = ctypes.create_string_buffer(
        ctypes.string_at(
            ctypes.windll.crypt32.CryptUnprotectData(
                # dummy
            )
        ) if False else b''
    )
    # Just standard base64 decoding
    import base64
    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
    encrypted_key = encrypted_key[5:] # Strip DPAPI prefix (5 bytes)
    return decrypt_key_with_dpapi(encrypted_key)

def decrypt_cookie(value, key):
    try:
        signature = value[:3]
        if signature in (b'v10', b'v11'):
            nonce = value[3:15]
            ciphertext = value[15:]
            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode('utf-8', errors='ignore')
        else:
            return decrypt_key_with_dpapi(value).decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Decryption Error: {e}]"

def try_dpapi_cookie_extraction():
    """Attempt to silently extract cookies from the default Chrome profile using DPAPI."""
    print("[1/3] Attempting silent Chrome cookie extraction via DPAPI...")
    try:
        key = get_encryption_key()
    except Exception as e:
        print(f"  -> Failed to decrypt Chrome master key: {e}")
        return False

    db_path = Path(os.environ['USERPROFILE']) / 'AppData/Local/Google/Chrome/User Data/Default/Network/Cookies'
    if not db_path.exists():
        print(f"  -> Cookies database not found at {db_path}")
        return False

    # Since Chrome might lock the database exclusively while running,
    # copy it to a temp file. If copy fails due to lock, we'll catch it.
    temp_db = Path("temp_cookies.db")
    try:
        shutil.copyfile(db_path, temp_db)
    except Exception as e:
        print(f"  -> Chrome has exclusive lock on the active cookies database. {e}")
        return False

    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%google.com%'")
        rows = cursor.fetchall()
        
        cookies_dict = {}
        for host, name, encrypted_value in rows:
            decrypted = decrypt_cookie(encrypted_value, key)
            if not decrypted.startswith("[Decryption Error"):
                cookies_dict[name] = decrypted
                
        required = ["SID", "HSID", "SSID", "APISID", "SAPISID"]
        missing = [r for r in required if r not in cookies_dict]
        
        if not missing:
            print("  -> Successfully decrypted all required Google cookies!")
            from notebooklm_mcp.auth import AuthTokens, save_tokens_to_cache
            essential_cookies = [
                "SID", "HSID", "SSID", "APISID", "SAPISID",
                "__Secure-1PSID", "__Secure-3PSID",
                "__Secure-1PAPISID", "__Secure-3PAPISID",
                "__Secure-1PSIDTS", "__Secure-3PSIDTS",
                "__Secure-1PSIDCC", "__Secure-3PSIDCC"
            ]
            filtered_cookies = {k: v for k, v in cookies_dict.items() if k in essential_cookies}
            
            tokens = AuthTokens(
                cookies=filtered_cookies,
                csrf_token="",
                session_id="",
                extracted_at=time.time()
            )
            save_tokens_to_cache(tokens)
            print("  -> Updated NotebookLM MCP credentials cache.")
            return True
        else:
            print(f"  -> Missing required Google cookies in Default profile: {missing}")
            return False
            
    except Exception as e:
        print(f"  -> Error reading decrypted cookies: {e}")
        return False
    finally:
        if temp_db.exists():
            try:
                os.remove(temp_db)
            except Exception:
                pass

def run_interactive_auth_fallback():
    """Launch the interactive notebooklm-mcp-auth tool as fallback."""
    print("[2/3] DPAPI silent extraction unavailable or incomplete.")
    print("      Launching interactive browser login window...")
    print("      Please complete the Google Login inside the Chrome window when it appears.")
    
    import subprocess
    auth_cache = Path.home() / ".notebooklm-mcp/auth.json"
    initial_mtime = auth_cache.stat().st_mtime if auth_cache.exists() else 0
    
    # Run the interactive authenticator in a separate process
    process = subprocess.Popen(
        ["notebooklm-mcp-auth"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for login success or user cancel (up to 3 minutes)
    start_time = time.time()
    success = False
    print("      Waiting for authentication tokens to be cached...")
    while time.time() - start_time < 180:
        time.sleep(3)
        # Check if auth.json has been updated
        if auth_cache.exists():
            current_mtime = auth_cache.stat().st_mtime
            if current_mtime > initial_mtime:
                success = True
                print("  -> Success! Detected fresh authentication tokens.")
                break
                
        # Check if subprocess exited unexpectedly
        if process.poll() is not None:
            print("  -> Interactive authenticator process exited.")
            break
            
    # Terminate process if still running
    if process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
                
    return success

def get_authenticated_client():
    """Get the authenticated API client, attempting refresh/auth flows if needed."""
    from notebooklm_mcp.server import get_client
    
    # Try using existing credentials
    try:
        client = get_client()
        # Verify if they work by listing notebooks
        client.list_notebooks()
        print("  -> Cached credentials are valid. No re-authentication needed.")
        return client
    except Exception as e:
        print(f"  -> Cached credentials expired or invalid: {e}")

    # Reset client singleton to force refresh
    import notebooklm_mcp.server
    notebooklm_mcp.server._client = None

    # Step 1: Try DPAPI silent extraction
    if try_dpapi_cookie_extraction():
        try:
            client = get_client()
            client.list_notebooks()
            return client
        except Exception as e:
            print(f"  -> Silent extraction succeeded but API listing failed: {e}")
            notebooklm_mcp.server._client = None

    # Step 2: Try interactive fallback
    if run_interactive_auth_fallback():
        try:
            client = get_client()
            client.list_notebooks()
            return client
        except Exception as e:
            print(f"  -> Interactive authentication succeeded but API listing failed: {e}")
            notebooklm_mcp.server._client = None
            
    raise RuntimeError("Authentication failed. Unable to authenticate with NotebookLM.")

def main():
    parser = argparse.ArgumentParser(description="NotebookLM Auto-Activator & Binder")
    parser.add_argument("query", nargs="?", default=None, help="Name or part of the name of the notebook to activate")
    args = parser.parse_args()

    print("======================================================================")
    print("       NotebookLM Auto-Activator & Knowledge Binder")
    print("======================================================================")
    
    try:
        client = get_authenticated_client()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    print("\n[3/3] Retrieving your NotebookLM notebooks...")
    try:
        notebooks = client.list_notebooks()
    except Exception as e:
        print(f"  -> Failed to list notebooks: {e}")
        sys.exit(1)

    if not notebooks:
        print("\n[WARNING] No notebooks found in your NotebookLM account.")
        sys.exit(0)

    # If no search query is specified, print all notebooks
    if not args.query:
        print(f"\nFound {len(notebooks)} notebooks in your account:")
        print("-" * 70)
        for idx, nb in enumerate(notebooks, 1):
            print(f"{idx:2d}. 【{nb.title}】")
            print(f"    UUID: {nb.id}")
            print(f"    Sources: {nb.source_count} documents | URL: {nb.url}")
        print("-" * 70)
        print("\nTIP: Provide the notebook name as an argument to activate it.")
        sys.exit(0)

    # Search for matching notebook
    target = args.query.strip().lower()
    matching_notebooks = [nb for nb in notebooks if target in nb.title.lower()]

    if not matching_notebooks:
        print(f"\n[ERROR] No notebook found matching search term: '{args.query}'")
        print("\nAvailable notebooks:")
        for idx, nb in enumerate(notebooks, 1):
            print(f"  - 【{nb.title}】 (UUID: {nb.id})")
        sys.exit(1)

    # If multiple found, pick the best or first one and warn
    selected = matching_notebooks[0]
    if len(matching_notebooks) > 1:
        print(f"\n[INFO] Multiple matches found for '{args.query}'. Selecting the first match: 【{selected.title}】")
    else:
        print(f"\n[SUCCESS] Found matching notebook: 【{selected.title}】")

    print(f"          UUID: {selected.id}")
    print("          Fetching detailed notebook metadata and AI summaries...")

    # Fetch sources and AI generated summary
    try:
        nb_details = client.get_notebook(selected.id)
        nb_summary = client.get_notebook_summary(selected.id)
    except Exception as e:
        print(f"  -> Failed to fetch notebook metadata: {e}")
        nb_details = None
        nb_summary = None

    # Parse sources list
    sources_list = []
    if nb_details and isinstance(nb_details, list) and len(nb_details) > 0:
        # Structure is usually: [title, sources_array, id, ...]
        raw_sources = nb_details[0][1] if len(nb_details[0]) > 1 else []
        for src in raw_sources:
            if isinstance(src, list) and len(src) > 1:
                # src format: [uuid_array, title, metadata...]
                src_uuid = src[0][0] if isinstance(src[0], list) and len(src[0]) > 0 else ""
                src_title = src[1]
                sources_list.append({
                    "title": src_title,
                    "id": src_uuid
                })

    ai_summary = nb_summary.get("summary", ["No summary available."]) if nb_summary else ["No summary available."]
    if isinstance(ai_summary, list):
        ai_summary = " ".join(ai_summary)

    # Save to a persistent bind file for local environment consumption
    bind_data = {
        "notebook_id": selected.id,
        "title": selected.title,
        "source_count": selected.source_count,
        "url": selected.url,
        "sources": sources_list,
        "summary": ai_summary,
        "bound_at": time.time()
    }
    
    last_bound_file = Path.home() / ".notebooklm-mcp/last_bound_notebook.json"
    last_bound_file.parent.mkdir(parents=True, exist_ok=True)
    with open(last_bound_file, "w", encoding="utf-8") as f:
        json.dump(bind_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"🎉 BIND SUCCESS: 【{selected.title}】 is now active!")
    print("=" * 70)
    print(f"ID      : {selected.id}")
    print(f"Sources : {selected.source_count} documents bound")
    print(f"Summary : {ai_summary[:200]}...")
    print(f"Config  : Saved to {last_bound_file}")
    print("=" * 70)

    # Output pure JSON block at the end so parent agents can parse it directly
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(bind_data, ensure_ascii=False, indent=2))
    print("--- END JSON ---")

if __name__ == "__main__":
    main()
