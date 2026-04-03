# AI Employee Vault — Final Submission
### Personal AI Employee Hackathon 0
**By Farhana Yousuf** | [GitHub Repo](https://github.com/Farhanayousuf248/AI-Employee-Vault)

---

## What I Built

A **local-first, autonomous AI Employee** that runs entirely through an Obsidian-style Markdown vault. No cloud dependency, no API keys — just Python scripts, `.md` files, and Claude Chat working together as a personal digital workforce.

Drop a file. AI processes it. Human stays in control.

---

## Tier Completion

| Tier | Status | Features |
|------|--------|----------|
| **Bronze** | COMPLETE | Inbox watcher, auto-processor, prompt generation, clipboard copy, sensitive content detection, human-in-the-loop approval, feedback system, full audit logging |
| **Silver** | COMPLETE | LinkedIn Auto Post Generator — watches `Needs_Action/`, generates professional posts with smart hashtags, copy-paste ready output, approval before publishing |
| **Gold** | COMPLETE | Weekly CEO Report Generator — parses action logs + dashboard, produces executive summary with pending tasks, insights, daily breakdown charts, and next week focus |

---

## Core Architecture

```
Inbox/  -->  auto_processor.py  -->  Claude Chat  -->  Needs_Action/
                                                            |
                                              linkedin_poster.py (Silver)
                                              weekly_report.py   (Gold)
                                                            |
                                                    Weekly_Reports/
                                                    Generated_Posts/
```

**Pipeline:** File drops in Inbox --> detected automatically --> sensitive check --> prompt generated & copied to clipboard --> Claude processes --> human reviews --> AI Employee logs everything.

---

## Key Features

### Bronze Tier — Foundation
- **`auto_processor.py`** — Watches `Inbox/`, generates Claude-ready prompts, auto-copies to clipboard
- **Sensitive Content Gate** — Detects keywords (money, password, payment, etc.) and blocks without human approval
- **Feedback Loop** — Collects performance ratings after each task
- **Full Audit Trail** — Every action timestamped in `Logs/action-log.md`
- **Dashboard** — Live status board with pending tasks and recent activity

### Silver Tier — LinkedIn Auto Poster
- **`linkedin_poster.py`** — Reads processed tasks, generates 150-250 word professional LinkedIn posts
- **Smart Hashtags** — Topic-aware hashtag selection (client, AI, meeting, project, etc.)
- **Two Modes** — Watch mode (auto-detect new files) or single file mode (CLI)
- **Double Approval** — Flags sensitive content + requires final approval before publishing
- **Clipboard + Save** — Post auto-copied and saved to `Generated_Posts/`

### Gold Tier — Weekly CEO Report
- **`weekly_report.py`** — Auto-generates professional weekly reports from vault data
- **Sections:** Executive Summary, High Priority Tasks, Completed Work, Key Insights, Daily Breakdown (with visual bars), Next Week Focus
- **Date Flexible** — Run for any week: `python weekly_report.py 2026-03-26`
- **Auto-Logged** — Report generation logged in action trail

---

## How to Run

```bash
# Setup
pip install watchdog pyperclip

# Bronze — Main processor
python auto_processor.py

# Silver — LinkedIn poster
python linkedin_poster.py                  # watch mode
python linkedin_poster.py test-note.md     # single file

# Gold — Weekly report
python weekly_report.py                    # current week
python weekly_report.py 2026-03-26         # specific week
```

---

## Vault Structure

```
AI-Employee-Vault/
├── Inbox/                  # Drop zone — new tasks land here
├── Needs_Action/           # Processed tasks awaiting human action
├── Done/                   # Completed tasks
├── Generated_Posts/        # LinkedIn posts (auto-generated)
├── Generated_Prompts/      # Claude prompts (auto-generated)
├── Weekly_Reports/         # CEO reports (auto-generated)
├── Logs/                   # action-log.md + feedback-log.md
├── Handbook/               # Company rules + personal preferences
├── Skills/                 # CORE_SKILLS.md (8 skills defined)
├── Dashboard.md            # Live status board
├── auto_processor.py       # Bronze — inbox watcher + prompt builder
├── linkedin_poster.py      # Silver — LinkedIn post generator
├── weekly_report.py        # Gold — weekly CEO report generator
├── gmail_watcher.py        # Silver — Gmail inbox monitor
└── setup_gmail_oauth.py    # Gmail OAuth setup helper
```

---

## What Makes This Different
1. **Zero API keys needed** — runs with Claude Chat / Bonsai, no paid APIs
2. **Human always in control** — sensitive actions blocked until approved
3. **Everything is a file** — fully transparent, auditable, Obsidian-compatible
4. **Real automation pipeline** — not just a chatbot, an actual employee workflow
5. **Built to scale** — add new skills by adding new `.py` scripts

---

*Built with Python + Claude Code + determination.*
*AI Employee Vault — Farhana Yousuf*
