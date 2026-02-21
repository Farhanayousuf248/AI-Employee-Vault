"""
Auto Processor v3.0 - AI Employee Vault
========================================
Bonsai/Claude Chat Edition — No API Key Needed

What it does:
  1. Watches Inbox/ for new .md files
  2. Reads content + checks sensitive keywords
  3. Generates Claude prompt + saves to Generated_Prompts/
  4. AUTO-COPIES prompt to clipboard (pyperclip)
  5. After you paste in Claude, asks for feedback → saves to Logs/feedback-log.md

Just: python auto_processor.py
"""

import time
import os
import sys
import io
from datetime import datetime

# Fix Windows terminal encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("watchdog not installed. Run:  pip install watchdog")
    sys.exit(1)

# Clipboard — optional but recommended
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("[WARN] pyperclip not installed. Auto-clipboard disabled.")
    print("       Install with:  pip install pyperclip")


# ============================================================
# PATHS
# ============================================================
VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
INBOX_PATH = os.path.join(VAULT_ROOT, "Inbox")
NEEDS_ACTION_PATH = os.path.join(VAULT_ROOT, "Needs_Action")
LOGS_PATH = os.path.join(VAULT_ROOT, "Logs")
ACTION_LOG = os.path.join(LOGS_PATH, "action-log.md")
FEEDBACK_LOG = os.path.join(LOGS_PATH, "feedback-log.md")
DASHBOARD = os.path.join(VAULT_ROOT, "Dashboard.md")
PROMPTS_PATH = os.path.join(VAULT_ROOT, "Generated_Prompts")

SENSITIVE_KEYWORDS = [
    "money", "payment", "transfer", "send", "post", "publish",
    "delete", "remove", "password", "credential", "secret",
    "bank", "invoice", "pay", "wire", "transaction"
]


# ============================================================
# HELPERS
# ============================================================
def read_file_safe(filepath):
    """Read file content safely."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"  [ERROR] Cannot read {filepath}: {e}")
        return None


def check_sensitive(content):
    """Return list of sensitive keywords found."""
    lower = content.lower()
    return [kw for kw in SENSITIVE_KEYWORDS if kw in lower]


def ask_human_approval(filename, sensitive_words):
    """Ask human to approve sensitive file processing."""
    print()
    print("!" * 55)
    print("  SENSITIVE CONTENT DETECTED")
    print(f"  File: {filename}")
    print(f"  Keywords found: {', '.join(sensitive_words)}")
    print("!" * 55)
    while True:
        answer = input("  Approve processing? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Type 'yes' or 'no'")


def copy_to_clipboard(text):
    """Copy text to clipboard if pyperclip available."""
    if not CLIPBOARD_AVAILABLE:
        return False
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


# ============================================================
# PROMPT BUILDER
# ============================================================
def build_prompt(filename, file_content, dashboard_content, log_content):
    """Build a copy-paste prompt for Claude Chat."""
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")

    prompt = f"""You are my AI Employee working in the AI-Employee-Vault folder.

A new file was detected in Inbox/. Process it using CORE_SKILLS.

## Detected File
- **Filename:** {filename}
- **Detected at:** {today} {now}
- **Content:**
```
{file_content}
```

## Current Dashboard.md
```
{dashboard_content}
```

## Current Logs/action-log.md (latest)
```
{log_content}
```

## Your Processing Steps
1. Read the file content above
2. <thinking> step-by-step: What is this about? Any deadline keywords (tomorrow, urgent, ASAP, today)? What priority?
3. Write a short summary (1-2 lines)
4. Decide priority: LOW / MEDIUM / HIGH
5. Copy file to Needs_Action/{filename} with this format:
   - Header with filename, source, date, priority, deadline
   - Original content
   - AI Summary section
6. Add entries in Logs/action-log.md under date {today} with these rows:
   | {now} | DETECTED | {filename} | New file detected in Inbox |
   | {now} | READ | {filename} | <what the content says> |
   | {now} | ANALYZED | {filename} | <priority reasoning> |
   | {now} | COPIED | {filename} | Inbox -> Needs_Action (original preserved) |
   | {now} | UPDATED | Dashboard.md | Added pending task |
7. Update Dashboard.md:
   - Increment "Needs Action" count by 1
   - Increment "Completed Today" count by 1
   - Add new row in Pending Actions table
   - Add new line at top of Recent Activity
   - Update "Last Updated" date to {today}

## IMPORTANT RULES
- Do NOT delete the original file from Inbox/
- Make ALL changes in the vault files directly
- Keep the existing data in Dashboard and Logs, only ADD to them"""

    return prompt


def save_prompt_to_file(filename, prompt):
    """Save prompt as .txt in Generated_Prompts/."""
    os.makedirs(PROMPTS_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_filename = f"prompt_{filename.replace('.md', '')}_{timestamp}.txt"
    prompt_filepath = os.path.join(PROMPTS_PATH, prompt_filename)

    with open(prompt_filepath, "w", encoding="utf-8") as f:
        f.write(prompt)

    return prompt_filepath


# ============================================================
# FEEDBACK SYSTEM
# ============================================================
def collect_feedback(filename):
    """Ask 3 feedback questions after Claude processes a file.
    Save answers to Logs/feedback-log.md."""

    print()
    print("~" * 55)
    print("  FEEDBACK TIME")
    print(f"  File processed: {filename}")
    print("~" * 55)
    print()

    # Question 1: Rating
    print("  Q1: How did Claude perform on this task?")
    print("      1=Poor  2=Average  3=Good  4=Great  5=Excellent")
    while True:
        rating_input = input("      Your rating (1-5, or 's' to skip feedback): ").strip().lower()
        if rating_input == "s":
            print("  [SKIPPED] Feedback skipped.")
            return
        if rating_input in ("1", "2", "3", "4", "5"):
            rating_map = {"1": "Poor", "2": "Average", "3": "Good", "4": "Great", "5": "Excellent"}
            rating = rating_map[rating_input]
            break
        print("      Enter 1-5 or 's' to skip")

    # Question 2: What was missing
    print()
    print("  Q2: What was missing or could be improved?")
    missing = input("      (or press Enter to skip): ").strip()
    if not missing:
        missing = "Nothing noted"

    # Question 3: Suggestions
    print()
    print("  Q3: Any concrete suggestions for next iteration?")
    suggestions = input("      (or press Enter to skip): ").strip()
    if not suggestions:
        suggestions = "No suggestions"

    # Save to feedback-log.md
    save_feedback(filename, rating, missing, suggestions)

    print()
    print("  Feedback saved to Logs/feedback-log.md")
    print("~" * 55)


def save_feedback(filename, rating, missing, suggestions):
    """Append feedback entry to Logs/feedback-log.md."""
    os.makedirs(LOGS_PATH, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")

    # Create file with header if it doesn't exist
    if not os.path.exists(FEEDBACK_LOG):
        header = "# Feedback Log\n\nAll feedback on AI Employee performance.\n\n---\n\n"
        with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
            f.write(header)

    entry = f"""## {today} {now} — {filename}

| Question | Answer |
|----------|--------|
| Performance Rating | **{rating}** |
| What was missing? | {missing} |
| Suggestions | {suggestions} |

---

"""

    with open(FEEDBACK_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


# ============================================================
# MAIN PROCESSOR
# ============================================================
def process_detected_file(filepath):
    """Full pipeline: detect → read → prompt → clipboard → feedback."""
    filename = os.path.basename(filepath)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 55)
    print(f"  New file detected: {filename}")
    print(f"  Ready to process with Claude")
    print(f"  Time: {now_str}")
    print("=" * 55)

    # Step 1: Read file
    file_content = read_file_safe(filepath)
    if file_content is None or not file_content.strip():
        print(f"  [SKIP] File is empty or unreadable: {filename}")
        return

    preview = file_content.strip()[:80]
    if len(file_content.strip()) > 80:
        preview += "..."
    print(f"  Content: \"{preview}\"")

    # Step 2: Sensitive check
    sensitive_words = check_sensitive(file_content)
    if sensitive_words:
        approved = ask_human_approval(filename, sensitive_words)
        if not approved:
            print(f"  [BLOCKED] You denied processing of {filename}")
            print(f"  File remains in Inbox/ untouched.")
            return
        print(f"  [APPROVED] Continuing...")

    # Step 3: Read vault state
    dashboard_content = read_file_safe(DASHBOARD) or "(could not read)"
    log_content = read_file_safe(ACTION_LOG) or "(could not read)"

    # Step 4: Build prompt
    prompt = build_prompt(filename, file_content, dashboard_content, log_content)

    # Step 5: Save prompt to file
    saved_path = save_prompt_to_file(filename, prompt)

    # Step 6: Auto-copy to clipboard
    copied = copy_to_clipboard(prompt)

    # Step 7: Display status
    print()
    if copied:
        print("  *** PROMPT COPIED TO CLIPBOARD! ***")
        print("  Just Ctrl+V in Claude Chat / Bonsai")
    else:
        print("  [INFO] Clipboard not available — copy manually")
        print()
        print("-" * 55)
        print(prompt)
        print("-" * 55)

    print()
    print(f"  Prompt saved: {os.path.basename(saved_path)}")
    print(f"  Full path:    {saved_path}")
    print()
    print("  NEXT STEPS:")
    if copied:
        print("  1. Ctrl+V in Claude Chat (Bonsai) — already on clipboard!")
    else:
        print("  1. Open the saved prompt file and copy-paste into Claude")
    print("  2. Claude will process and update your vault")
    print("  3. Come back here to give feedback")
    print("  4. Original file stays safe in Inbox/")
    print("=" * 55)

    # Step 8: Ask for feedback (after user pastes in Claude)
    print()
    print("  When Claude finishes processing, give feedback below.")
    print("  (Press 's' at rating prompt to skip)")
    collect_feedback(filename)


# ============================================================
# WATCHER
# ============================================================
class InboxHandler(FileSystemEventHandler):
    """Watch Inbox/ for new .md files."""

    def __init__(self):
        self.processed = set()
        if os.path.exists(INBOX_PATH):
            for f in os.listdir(INBOX_PATH):
                if f.endswith(".md"):
                    self.processed.add(f)

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return

        filename = os.path.basename(event.src_path)
        if filename in self.processed:
            return

        # Wait for file write to complete
        time.sleep(1)

        self.processed.add(filename)
        process_detected_file(event.src_path)


# ============================================================
# MAIN
# ============================================================
def main():
    for folder in [INBOX_PATH, NEEDS_ACTION_PATH, LOGS_PATH]:
        os.makedirs(folder, exist_ok=True)

    handler = InboxHandler()
    observer = Observer()
    observer.schedule(handler, INBOX_PATH, recursive=False)
    observer.start()

    clipboard_status = "ON" if CLIPBOARD_AVAILABLE else "OFF (install pyperclip)"

    print()
    print("=" * 55)
    print("  AI EMPLOYEE - AUTO PROCESSOR v3.0")
    print("  Bonsai Edition + Clipboard + Feedback")
    print("=" * 55)
    print(f"  Vault:       {VAULT_ROOT}")
    print(f"  Monitoring:  Inbox/")
    print(f"  Clipboard:   {clipboard_status}")
    print(f"  Feedback:    ON (after each file)")
    print(f"  Sensitive:   ON ({len(SENSITIVE_KEYWORDS)} keywords)")
    print(f"  Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    print("  Drop any .md file in Inbox/ to auto-process")
    print("  Press Ctrl+C to stop")
    print("=" * 55)

    if handler.processed:
        print(f"\n  Existing files (skipped): {', '.join(sorted(handler.processed))}")

    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopping Auto Processor...")
        observer.stop()

    observer.join()
    print("  Auto Processor stopped.")


if __name__ == "__main__":
    main()
