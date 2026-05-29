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

## 🛠️ NotebookLM MCP Server 安装与配置指南

本自定义 Skill 依赖于本地安装并配置好的 `notebooklm-mcp-server`。以下是完整的安装与配置步骤：

### 前提条件
- **Python 3.x + pip**
- **Google Chrome 浏览器**
- **Node.js**（可选，如果使用 `npx` 方式）

---

### Step 1：安装 `notebooklm-mcp-server`

请在终端中运行以下命令：
```powershell
pip install notebooklm-mcp-server
```

安装完成后，系统将自动生成两个核心命令行工具：
- **`notebooklm-mcp.exe`**：MCP 服务器主程序
- **`notebooklm-mcp-auth.exe`**：身份认证与 Token 提取工具

您可以使用 `where.exe` 确认安装的路径：
```powershell
where.exe notebooklm-mcp
# 例如输出：C:\Users\Administrator\AppData\Local\Programs\Python\Python314\Scripts\notebooklm-mcp.exe
```

---

### Step 2：认证（获取 Google 登录凭证）

> [!WARNING]
> **在运行认证工具前，建议先关闭所有的 Chrome 窗口**，因为 auth 工具需要以调试模式启动一个干净的 Chrome 进程。

在命令行运行：
```powershell
notebooklm-mcp-auth
```

**执行机制**：
1. 自动以 `--remote-debugging-port=9222` 参数启动 Chrome。
2. 自动打开 NotebookLM 官网主页。若您尚未登录，请在弹出的 Chrome 窗口中完成 Google 账户登录。
3. 登录成功后，工具将自动从浏览器中提取您的 `Cookies` 与 `CSRF Token`。
4. 将所有凭证自动加密并保存到您的本地路径：`~\.notebooklm-mcp\auth.json`。

**成功输出示例**：
```text
========================================
SUCCESS!
========================================
Cookies: 22 extracted
CSRF Token: Yes
Tokens cached to: C:\Users\Administrator\.notebooklm-mcp\auth.json
```

> [!NOTE]
> Token 有效期通常为数小时或数天。若后期遇到过期提示，只需重新运行一次 `notebooklm-mcp-auth` 即可。

---

### Step 3：配置 MCP 服务器

编辑（若不存在则创建）您 AI 助手的 MCP 配置文件 `~\.gemini\config\mcp_config.json`：

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "C:\\Users\\Administrator\\AppData\\Local\\Programs\Python\\Python314\\Scripts\\notebooklm-mcp.exe",
      "args": []
    }
  }
}
```

> [!IMPORTANT]
> **关键**：`command` 字段中请务必使用**绝对路径**（使用 `where.exe notebooklm-mcp` 获取的路径），以防止 AI 助手运行时找不到可执行文件。

---

### Step 4：验证连接

**方法 1：由 AI 助手在对话中验证**
开启一个**新对话**（注：旧对话不会动态重载新配置），向 AI 发出以下指令：
> *“列出我的 NotebookLM notebooks”*

**方法 2：手动测试服务器能否正常启动**
您可以在终端运行：
```powershell
notebooklm-mcp --help          # 查看帮助信息
notebooklm-mcp                 # 以 stdio 模式启动（默认）
notebooklm-mcp --transport http # 以 HTTP 模式启动（默认绑定端口 8000）
```

---

## 🛠️ 可用的 MCP 工具一览

一旦成功绑定，AI 助手将可以直接调用以下工具完成知识问答与多媒体创作：

| 工具名称 | 功能描述 |
| :--- | :--- |
| `notebook_list` | 列出您账户下的所有笔记本 |
| `notebook_create` | 创建一个新的空白笔记本 |
| `notebook_get` | 获取指定笔记本的详细结构与元数据 |
| `notebook_query` | 对绑定的笔记本中的数据源内容进行智能提问 |
| `notebook_add_url` | 向笔记本添加网页 URL 来源 |
| `notebook_add_text` | 向笔记本添加纯文本来源 |
| `notebook_add_drive` | 向笔记本导入 Google Drive 来源 |
| `notebook_rename` / `notebook_delete` | 重命名或永久删除笔记本 |
| `audio_overview_create` | 生成 NotebookLM 特色的双人播客音频概述 |
| `video_overview_create` | 生成视频大纲或概述 |
| `infographic_create` | 自动化生成结构化的信息图设计大纲 |
| `slide_deck_create` | 自动化生成幻灯片结构规划 |
| `report_create` | 自动化生成精美专业的研报或总结报告 |
| `quiz_create` / `flashcards_create` | 一键生成课程测验或知识记忆闪卡 |
| `research_start` / `research_status` / `research_import` | 开启针对学术文献或网路大数据的深度研究 |
| `refresh_auth` | 手动在后台重载或刷新 Google 登录状态 |

---

## 🚀 绑定与激活使用快速开始

在配置好上述 MCP 服务器后，即可使用本 Custom Skill 包含的自动化脚本来智能绑定特定的笔记本了！

### 1. 自动绑定特定笔记本
例如，自动匹配并绑定名为“数据库”的笔记本：
```powershell
python scripts/activate_notebook.py "数据库"
```

### 2. 列出并选择笔记本
若不带任何参数运行，将列出您账户下的所有可用笔记本：
```powershell
python scripts/activate_notebook.py
```

---

## ❓ 常见问题及解决方案 (FAQ)

- **问题 1：`Authentication expired`（登录过期）**
  - **解决方案**：关闭所有的 Chrome 窗口，并在终端重新运行 `notebooklm-mcp-auth` 重新登录并提取 Cookie。
- **问题 2：其他新对话中看不到 NotebookLM 的 MCP 工具**
  - **解决方案**：必须开启一个**新的对话**或重启您的 AI 编辑器。在旧会话中，新修改的 `mcp_config.json` 不会被动态载入。
- **问题 3：`command not found`**
  - **解决方案**：请检查 `mcp_config.json` 中配置的路径，务必将 `command` 修改为您本地 `notebooklm-mcp.exe` 的绝对路径。
- **问题 4：终端中文乱码**
  - **解决方案**：在 PowerShell 终端运行 `chcp 65001`，并设置环境变量 `$env:PYTHONIOENCODING='utf-8'`。

---

## 📄 开源许可证

本项目基于 **MIT License** 开放源代码。欢迎提 Issue 与 PR！
