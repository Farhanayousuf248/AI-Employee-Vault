# Core Skills

## 1. Inbox Processing
- Read new items in Inbox/
- Summarize content
- Categorize: Action Required / FYI / Archive
- Move to appropriate folder

## 2. Task Management
- Identify actionable items
- Create follow-up reminders
- Track completion status

## 3. Communication Drafting
- Draft emails/responses
- Always seek approval before sending

## 4. Logging
- Log every action with timestamp
- Maintain audit trail in Logs/action-log.md

## 5. Dashboard Updates
- Keep Dashboard.md current
- Reflect real-time status

## 6. Gmail Watcher (Silver Tier)
- Monitor Gmail inbox for new unread emails
- Auto-create .md files in Inbox/ with email metadata + body summary
- Sensitive email detection (money, payment, invoice, urgent, etc.)
- Human-in-the-loop approval for sensitive emails
- READ-ONLY scope — never deletes or modifies emails in Gmail
- Works alongside auto_processor.py for full pipeline

## 7. LinkedIn Auto Post Generator (Silver Tier)
- Watches Needs_Action/ for new .md files
- Generates professional LinkedIn posts (150-250 words)
- Smart hashtag selection based on content topics
- Sensitive content detection (salary, NDA, confidential, etc.)
- Human-in-the-loop: approval required before publishing
- Copy-paste ready output in terminal + clipboard auto-copy
- Saves posts to Generated_Posts/ with timestamps
- Two modes: watch mode (auto) or single file mode (CLI arg)

## 8. Weekly CEO Report Generator (Gold Tier)
- Parses action-log.md and Dashboard.md automatically
- Generates professional weekly summary with Executive Summary, Pending Tasks, Completed Tasks, Insights, Next Week Focus
- Visual daily activity breakdown with bar charts
- Supports any target week via CLI date argument
- Saves timestamped reports to Weekly_Reports/
- Logs report generation in action-log.md
