---
name: notebooklm-activator
description: Automatically authenticate, list, search, and bind any NotebookLM notebook from the user's Google account to the local development environment. Trigger this skill whenever the user mentions 'NotebookLM', 'activate notebook', 'bind notebook', 'access notebook', 'read notebook', or wants to query, import, or retrieve knowledge from their NotebookLM notebooks, even if they don't explicitly name a specific notebook.
---

# NotebookLM Activator & Binder Skill

This skill enables any AI assistant to automatically authenticate, query, and bind any NotebookLM notebook from the user's Google account, making its knowledge instantly accessible for future queries in the local environment.

## 🚀 When to Use This Skill

Make sure to trigger this skill whenever the user:
- Mentions **NotebookLM** in their request.
- Asks to "activate", "bind", "connect", "import", or "read" a notebook.
- Wants to retrieve specialized courseware, lecture notes, or domain knowledge that resides in their NotebookLM notebooks.
- Expresses a desire to set up a knowledge base or reference their personal notes.

---

## 🛠️ Step-by-Step Execution Workflow

To execute this skill, always follow this exact procedural flow:

### Step 1: Execute the Bundled Automation Script

Run the bundled Python automation script to handle all the heavy-lifting (authentication, DPAPI cookie decryption, interactive fallback, matching, and detail retrieval).

Propose running the command:
```powershell
python -C "C:\Users\Administrator\.gemini\antigravity\skills\notebooklm-activator\scripts\activate_notebook.py" "[notebook_name_or_query]"
```
*(Replace `[notebook_name_or_query]` with the target notebook keyword the user wants to bind, or leave it empty to list all available notebooks.)*

### Step 2: Understand the Script Output & Statuses

The script will handle three key scenarios:
1. **Valid Cached Credentials**: It will silently and instantly run using the valid cache.
2. **Expired Credentials (DPAPI Silent Decryption)**: It will attempt to decrypt Chrome's default cookie profile under Windows DPAPI and AES-GCM, automatically caching them. This requires zero user interaction.
3. **Interactive Fallback**: If DPAPI fails, it will launch a separate Chrome window using `notebooklm-mcp-auth`. Instruct the user to complete Google Login in that window, and wait for the script to detect and cache the new credentials.

### Step 3: Present the Results & Bind Status

Once the script completes, it will print a pure JSON block containing the bound notebook details. Extract this information and present it beautifully to the user:

- **Notebook Name & UUID**: Highlight the title and the UUID.
- **Bound Sources**: Display a clean table of all the chapters/documents bound within that notebook.
- **AI Summary**: Render the AI-generated notebook summary so the user knows exactly what knowledge is active.
- **Knowledge Base File**: Remind the user that the notebook configuration is saved to `~/.notebooklm-mcp/last_bound_notebook.json`.

---

## ⚡ Examples

### Example 1: User wants to activate the 'Database' notebook
**Model Proposal:**
```powershell
python "C:\Users\Administrator\.gemini\antigravity\skills\notebooklm-activator\scripts\activate_notebook.py" "数据库"
```

### Example 2: User wants to see all available notebooks
**Model Proposal:**
```powershell
python "C:\Users\Administrator\.gemini\antigravity\skills\notebooklm-activator\scripts\activate_notebook.py"
```
