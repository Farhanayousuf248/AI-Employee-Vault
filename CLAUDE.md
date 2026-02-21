# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Employee-Vault is a hackathon project that implements a file-based "AI Employee" task processing system. It uses an Obsidian-style Markdown vault where a human drops `.md` files into an `Inbox/` folder, and Python automation detects them, generates structured Claude prompts, and facilitates a human-in-the-loop workflow. This is the "Bonsai/Claude Chat Edition" — no API key needed; prompts are copy-pasted manually.

## Running the Application

```bash
# Main processor — watches Inbox/ for new .md files, generates prompts, copies to clipboard
python auto_processor.py

# Standalone clipboard utility — copies the latest generated prompt to clipboard
python clipboard_auto_copy.py

# Simple inbox watcher (v1 prototype) — only logs file events, no prompt generation
python inbox_watcher.py
```

## Dependencies

No `requirements.txt` exists. Install manually:

```bash
pip install watchdog      # Required — filesystem monitoring
pip install pyperclip     # Optional but recommended — auto-clipboard
```

Python 3.13 is the current runtime. Dependencies are guarded by `try/except ImportError` blocks at import time.

## Architecture

### Processing Pipeline (`auto_processor.py`)

The core flow when a `.md` file is dropped into `Inbox/`:

1. **Watch** — `watchdog` Observer monitors `Inbox/` for new `.md` files (skips files already present at startup)
2. **Read** — Reads file content; skips empty/unreadable files
3. **Sensitive check** — Scans against 16 keywords (money, payment, password, bank, etc.). If found, blocks and requires interactive human approval via terminal input
4. **Build prompt** — Constructs a Claude prompt embedding: the file content, current `Dashboard.md` state, and current `action-log.md` state, with step-by-step processing instructions
5. **Save + clipboard** — Saves prompt as timestamped `.txt` in `Generated_Prompts/`, auto-copies to clipboard via `pyperclip`
6. **Feedback** — After user pastes prompt into Claude Chat, collects 3-question feedback (rating 1-5, improvements, suggestions) and appends to `Logs/feedback-log.md`

### Vault Folder Structure (Kanban-style workflow)

- **`Inbox/`** — Drop zone for new task `.md` files
- **`Needs_Action/`** — Processed tasks awaiting human action (Claude writes here)
- **`Done/`** — Completed tasks
- **`Generated_Prompts/`** — Auto-generated `.txt` prompt files (timestamped)
- **`Logs/`** — `action-log.md` (audit trail) and `feedback-log.md` (performance ratings)
- **`Handbook/`** — AI behavior rules: `Company_Handbook.md` (communication/approval policies) and `My_Personal_Rules.md` (6 operating principles)
- **`Skills/`** — `CORE_SKILLS.md` defines 5 capabilities: Inbox Processing, Task Management, Communication Drafting, Logging, Dashboard Updates
- **`Dashboard.md`** — Live status board with stats, pending actions table, and recent activity

### Key Design Decisions

- **No API integration** — Prompts are generated for manual copy-paste into Claude Chat/Bonsai
- **File-based state** — All state lives in Markdown files; no database
- **Human-in-the-loop** — Sensitive content requires terminal approval; user manually pastes prompts; user provides feedback
- **Windows-first** — Includes UTF-8 stdout/stderr encoding fix for Windows terminal emoji support
- **`Inbox/` originals preserved** — Files are never deleted from Inbox; they are copied to `Needs_Action/`

### Path Constants

All paths in `auto_processor.py` are derived from `VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))`. The key constants are `INBOX_PATH`, `NEEDS_ACTION_PATH`, `LOGS_PATH`, `ACTION_LOG`, `FEEDBACK_LOG`, `DASHBOARD`, and `PROMPTS_PATH`.
