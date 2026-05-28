# NotebookLM Activator & Binder Custom Skill

A powerful, robust, and zero-config custom skill designed for AI assistants and local environments to automatically authenticate, query, search, and bind any NotebookLM notebook from your Google account.

This custom skill lets you instantly bring all your courseware, lecture slides, research materials, and personal notes stored in NotebookLM directly into your AI coding session.

---

## ✨ Features

- **Silent & Quiet Authentication**: Automatically decrypts and extracts required Google session cookies from your default Windows Chrome profile using AES-256-GCM and DPAPI encryption. No manual typing or configuration needed!
- **Interactive Fallback**: If silent extraction fails, it safely falls back to standard interactive authentication using `notebooklm-mcp-auth`, allowing you to log in in a browser window.
- **Fuzzy Matching**: Resolves partial, case-insensitive notebook titles to easily activate the notebook you want.
- **Structured Retrieval**: Retrieves the notebook title, document sources, AI-generated overview, and writes local configurations for seamless reference.

---

## 🛠️ Requirements & Installation

- **OS**: Windows (needed for Chrome DPAPI decryption and Windows-native fallback)
- **Python**: Python 3.8+ with `cryptography` library installed
- **NotebookLM MCP**: The `notebooklm-mcp` package installed locally

### Setup Cryptography & SQLite (if not already installed)
```bash
pip install cryptography httpx
```

---

## 🚀 Quick Start & Usage

### 1. Execute the Automation Script
To match and activate a notebook named "软件工程" (Software Engineering), run:
```powershell
python scripts/activate_notebook.py "软件工程"
```

To list all available notebooks in your Google account:
```powershell
python scripts/activate_notebook.py
```

### 2. Output & Binding Location
When successfully bound, the script outputs the complete notebook metadata as a JSON block and saves the configuration locally to:
`~/.notebooklm-mcp/last_bound_notebook.json`

---

## 🛡️ Security & Credential Handling

- **Zero Hardcoded Secrets**: This project does not store or hardcode any personal Google credentials, passwords, or session tokens.
- **Local Decryption**: All credentials are extracted directly on your local machine using standard Windows Data Protection API (DPAPI).
- **Secure Storage**: Cookies are saved in your local home directory under `~/.notebooklm-mcp/auth.json` in accordance with the `notebooklm-mcp` standard.

---

## 📄 License

This project is open-sourced under the **MIT License**. See the `LICENSE` file for details.
