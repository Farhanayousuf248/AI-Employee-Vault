# AI-Employee-Vault

**Hackathon Project by Farhana Yousuf**
**GitHub:** https://github.com/Farhanayousuf248/AI-Employee-Vault

AI Employee Vault — File watcher + Claude/Bonsai prompts | No API key needed

A file-based "AI Employee" task processing system built for hackathon. Drop `.md` files into an Inbox folder, and Python automation detects them, generates structured Claude prompts, and copies them to your clipboard — no API key needed. Designed to work as an Obsidian-style Markdown vault with a human-in-the-loop workflow.

## Setup

```bash
pip install watchdog pyperclip
```

- `watchdog` — required (filesystem monitoring)
- `pyperclip` — optional but recommended (auto-clipboard)

## Usage

```bash
python auto_processor.py
```

1. Drop any `.md` file into `Inbox/`
2. The processor detects it, checks for sensitive content, and generates a Claude prompt
3. Prompt is auto-copied to clipboard (or saved to `Generated_Prompts/`)
4. Paste into Claude Chat / Bonsai — Claude processes the task and updates your vault
5. Come back to the terminal to give feedback

## Folder Structure

```
AI-Employee-Vault/
├── Inbox/                 # Drop new task .md files here
├── Needs_Action/          # Processed tasks awaiting human action
├── Done/                  # Completed tasks
├── Generated_Prompts/     # Auto-generated prompt .txt files
├── Logs/                  # action-log.md + feedback-log.md
├── Handbook/              # AI behavior rules and company policies
├── Skills/                # AI capability definitions (CORE_SKILLS.md)
├── Dashboard.md           # Live status board
├── auto_processor.py      # Main application — inbox watcher + prompt builder
├── clipboard_auto_copy.py # Standalone clipboard utility
└── inbox_watcher.py       # Simple inbox watcher (v1 prototype)
```
