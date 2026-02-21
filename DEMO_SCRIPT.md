# Demo Video Script — AI-Employee-Vault

**Duration:** 1:30 - 2:00 minutes
**File name:** `AI-Employee-Vault-Demo-Farhana.mp4`
**Screen recorder:** OBS Studio (free) ya Windows Game Bar (Win+G) ya Zoom screen share + record
**Background music:** YouTube Audio Library se "Clouds" by Joakim Karud (free, no copyright)

---

## Scene 1: Intro (10 sec)

**Screen:** VS Code open, README.md visible
**Voiceover:**
> "Hi, I'm Farhana Yousuf. This is AI-Employee-Vault — a hackathon project where an AI employee processes tasks from a simple Inbox folder using Claude, with no API key needed."

---

## Scene 2: Folder Structure (10 sec)

**Screen:** VS Code Explorer sidebar — expand all folders
**Voiceover:**
> "The vault has a simple structure — Inbox for new tasks, Needs_Action for processed items, Logs for audit trail, Handbook for AI rules, and a live Dashboard."

**Action:** Slowly click through Inbox, Needs_Action, Logs, Handbook, Skills, Dashboard.md

---

## Scene 3: Start the Watcher (10 sec)

**Screen:** VS Code terminal
**Action:** Type and run:
```
python auto_processor.py
```
**Voiceover:**
> "I start the auto processor — it monitors the Inbox folder in real-time and shows clipboard status, sensitive keyword detection, everything is ON."

**Show:** The startup banner with "Monitoring: Inbox/", "Clipboard: ON", "Sensitive: ON"

---

## Scene 4: Drop a Task File (15 sec)

**Screen:** Split — VS Code Explorer + Terminal
**Action:** Create a new file `Inbox/urgent-meeting.md` with this content:
```
Schedule urgent team meeting for Monday 9 AM with marketing team. Discuss Q1 campaign results. ASAP.
```
**Voiceover:**
> "Now I drop a markdown file into Inbox — a simple task about scheduling an urgent meeting."

**Show:** Terminal auto-detects: "New file detected: urgent-meeting.md"

---

## Scene 5: Prompt Generated + Clipboard (15 sec)

**Screen:** Terminal output + Generated_Prompts folder
**Voiceover:**
> "The processor reads the file, checks for sensitive keywords, builds a full Claude prompt with vault context, and auto-copies it to clipboard. The prompt is also saved in Generated_Prompts."

**Action:**
1. Show terminal output: "PROMPT COPIED TO CLIPBOARD!"
2. Click on Generated_Prompts folder — show new .txt file
3. Open the .txt file briefly — show the structured prompt

---

## Scene 6: Paste in Claude Chat (20 sec)

**Screen:** Browser — Claude Chat (claude.ai) ya Bonsai
**Action:**
1. Open Claude Chat
2. Ctrl+V — paste the prompt
3. Show Claude's response (task summary, priority HIGH, vault updates)

**Voiceover:**
> "I paste the prompt into Claude Chat — no API key, just copy-paste. Claude analyzes the task, assigns HIGH priority, and gives me exact vault updates — Dashboard, Logs, Needs_Action, everything."

---

## Scene 7: Feedback Loop (10 sec)

**Screen:** VS Code terminal
**Action:** Terminal shows feedback prompts:
- Rating: type `4`
- What was missing: press Enter (skip)
- Suggestions: press Enter (skip)

**Voiceover:**
> "After Claude processes the task, the system asks for feedback — I rate the performance, and it's saved to the feedback log for continuous improvement."

**Show:** "Feedback saved to Logs/feedback-log.md"

---

## Scene 8: Ending (10 sec)

**Screen:** Browser — GitHub repo page
**Action:** Open https://github.com/Farhanayousuf248/AI-Employee-Vault

**Voiceover:**
> "The full project is open source on GitHub. AI-Employee-Vault by Farhana Yousuf. Thank you!"

**Show:** GitHub repo with README visible

---

## Pre-Recording Checklist

- [ ] VS Code open with AI-Employee-Vault folder
- [ ] Terminal clean (no old output)
- [ ] Inbox folder empty (delete old test files or keep 1-2)
- [ ] `urgent-meeting.md` content ready to paste
- [ ] Claude Chat open in browser tab (logged in)
- [ ] Screen recorder ready (OBS / Win+G / Zoom)
- [ ] Microphone working (test recording 5 sec)
- [ ] Close unnecessary tabs/apps (clean desktop)

## Recording Tips

- Font size bada karo VS Code mein (Ctrl+ + 3 times) taaki screen pe readable ho
- Terminal font bhi bada karo
- Slowly navigate karo — judges ko padhne ka time do
- Agar voiceover uncomfortable hai, toh text annotations use karo (OBS mein ya edit mein)
- 1 baar practice run karo bina recording ke
