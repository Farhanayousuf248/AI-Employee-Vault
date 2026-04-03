"""
LinkedIn Auto Post Generator v1.0 - Silver Tier
=================================================
AI Employee Vault — Watches Needs_Action/ for .md files,
generates professional LinkedIn posts, and displays them
in terminal for copy-paste.

Just: python linkedin_poster.py
"""

import time
import os
import sys
import io
import shutil
from datetime import datetime

# Fix Windows terminal encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("[ERROR] watchdog not installed. Run:  pip install watchdog")
    sys.exit(1)

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("[WARN] pyperclip not installed. Auto-clipboard disabled.")

# ============================================================
# PATHS
# ============================================================
VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
NEEDS_ACTION_PATH = os.path.join(VAULT_ROOT, "Needs_Action")
LOGS_PATH = os.path.join(VAULT_ROOT, "Logs")
ACTION_LOG = os.path.join(LOGS_PATH, "action-log.md")
GENERATED_POSTS_PATH = os.path.join(VAULT_ROOT, "Generated_Posts")

SENSITIVE_KEYWORDS = [
    "money", "payment", "transfer", "send", "salary", "bank",
    "password", "credential", "secret", "confidential", "private",
    "invoice", "revenue", "profit", "loss", "fired", "terminated",
    "legal", "lawsuit", "nda", "contract"
]

# Hashtag mapping by topic
HASHTAG_MAP = {
    "meeting": ["#Meetings", "#Teamwork", "#Collaboration"],
    "presentation": ["#PublicSpeaking", "#Presentations", "#Leadership"],
    "client": ["#ClientSuccess", "#CustomerFirst", "#BusinessGrowth"],
    "project": ["#ProjectManagement", "#Productivity", "#Goals"],
    "deadline": ["#TimeManagement", "#Hustle", "#Productivity"],
    "report": ["#DataDriven", "#Analytics", "#BusinessIntelligence"],
    "email": ["#Communication", "#Networking", "#ProfessionalGrowth"],
    "team": ["#Teamwork", "#Leadership", "#Culture"],
    "budget": ["#Finance", "#BusinessStrategy", "#Planning"],
    "ai": ["#AI", "#ArtificialIntelligence", "#FutureOfWork"],
    "hackathon": ["#Hackathon", "#Innovation", "#BuildInPublic"],
    "task": ["#Productivity", "#TaskManagement", "#GettingThingsDone"],
}

DEFAULT_HASHTAGS = ["#Productivity", "#ProfessionalGrowth", "#LinkedIn", "#CareerGrowth"]


# ============================================================
# HELPERS
# ============================================================
def read_file_safe(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"  [ERROR] Cannot read {filepath}: {e}")
        return None


def check_sensitive(content):
    lower = content.lower()
    return [kw for kw in SENSITIVE_KEYWORDS if kw in lower]


def ask_approval(filename, reason):
    print()
    print("!" * 55)
    print(f"  APPROVAL REQUIRED — {reason}")
    print(f"  File: {filename}")
    print("!" * 55)
    while True:
        answer = input("  Farhana, approve this post? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Type 'yes' or 'no'")


def pick_hashtags(content):
    lower = content.lower()
    tags = set()
    for keyword, hashtags in HASHTAG_MAP.items():
        if keyword in lower:
            tags.update(hashtags)
    if len(tags) < 3:
        tags.update(DEFAULT_HASHTAGS)
    return sorted(tags)[:6]


def log_action(action, filename, details):
    os.makedirs(LOGS_PATH, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")
    entry = f"| {now} | {action} | {filename} | {details} |\n"

    content = read_file_safe(ACTION_LOG) or ""
    if f"## {today}" not in content:
        entry = f"\n## {today}\n\n| Time | Action | File | Details |\n|------|--------|------|---------|{chr(10)}{entry}"

    with open(ACTION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


# ============================================================
# LINKEDIN POST GENERATOR
# ============================================================
def generate_linkedin_post(filename, content):
    """Generate a professional LinkedIn post from .md file content."""

    # Extract useful info from the content
    lines = [l.strip() for l in content.strip().splitlines() if l.strip()]
    title = lines[0].replace("#", "").strip() if lines else filename.replace(".md", "")

    # Find summary/action if present
    summary = ""
    priority = ""
    for line in lines:
        if "summary" in line.lower() or "type:" in line.lower():
            summary = line.split(":", 1)[-1].strip().strip("*")
        if "priority:" in line.lower():
            priority = line.split(":", 1)[-1].strip().strip("*")

    # Build the core message from content (strip markdown formatting)
    core_text = []
    skip_keys = ["priority", "status", "type:", "action required", "processed by",
                 "original:", "source:", "detected:", "deadline:", "original content",
                 "ai summary"]
    for line in lines:
        clean = line.lstrip("#-*> ").strip().replace("**", "")
        lower_clean = clean.lower()
        if not clean:
            continue
        if clean.startswith("|") or clean.startswith("---"):
            continue
        if any(k in lower_clean for k in skip_keys):
            continue
        if lower_clean == title.lower():
            continue
        core_text.append(clean)
    core_message = " ".join(core_text[:4]) if core_text else title

    # Pick relevant hashtags
    hashtags = pick_hashtags(content)
    hashtag_line = " ".join(hashtags)

    # Build the post
    post = f"""{title}

{core_message}

As professionals, staying on top of our tasks and priorities is what separates good from great. Whether it's a client follow-up, a team presentation, or a critical deadline — showing up prepared makes all the difference.

Here's what I'm focused on today:
- Prioritizing what matters most
- Taking action instead of just planning
- Keeping my team and stakeholders informed

What's your top priority this week? Drop it in the comments!

{hashtag_line}"""

    return post


# ============================================================
# MAIN PROCESSOR
# ============================================================
def process_file(filepath):
    filename = os.path.basename(filepath)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 55)
    print(f"  LinkedIn Post Generator")
    print(f"  File: {filename}")
    print(f"  Time: {now_str}")
    print("=" * 55)

    # Read file
    content = read_file_safe(filepath)
    if not content or not content.strip():
        print(f"  [SKIP] Empty file: {filename}")
        return

    log_action("READ", filename, "Read file for LinkedIn post generation")

    # Sensitive check — always ask approval for posting
    sensitive_words = check_sensitive(content)
    if sensitive_words:
        print(f"  [WARN] Sensitive keywords: {', '.join(sensitive_words)}")
        approved = ask_approval(filename, f"Sensitive content ({', '.join(sensitive_words)})")
        if not approved:
            print(f"  [BLOCKED] Post generation denied by Farhana.")
            log_action("BLOCKED", filename, f"LinkedIn post denied — sensitive: {', '.join(sensitive_words)}")
            return
        log_action("APPROVED", filename, "Farhana approved sensitive LinkedIn post")

    # Generate the post
    post = generate_linkedin_post(filename, content)
    log_action("GENERATED", filename, "LinkedIn post generated")

    # Save to Generated_Posts/
    os.makedirs(GENERATED_POSTS_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    post_filename = f"linkedin_{filename.replace('.md', '')}_{timestamp}.txt"
    post_filepath = os.path.join(GENERATED_POSTS_PATH, post_filename)
    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(post)

    # Display the post
    print()
    print("-" * 55)
    print("  LINKEDIN POST (copy-paste ready)")
    print("-" * 55)
    print()
    print(post)
    print()
    print("-" * 55)

    # Copy to clipboard
    if CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(post)
            print("  [COPIED] Post copied to clipboard!")
        except Exception:
            print("  [INFO] Clipboard copy failed. Copy manually from above.")
    else:
        print("  [INFO] Copy the post above manually.")

    print(f"  [SAVED] {post_filepath}")
    log_action("SAVED", filename, f"LinkedIn post saved to Generated_Posts/{post_filename}")

    # Ask final approval before "posting"
    print()
    approved = ask_approval(filename, "Ready to post on LinkedIn?")
    if approved:
        print()
        print("  *** POST APPROVED ***")
        print("  Paste it on LinkedIn now!")
        print("  (Auto-posting requires LinkedIn API — coming in Gold Tier)")
        log_action("POST_APPROVED", filename, "Farhana approved LinkedIn post for publishing")
    else:
        print("  [HELD] Post saved but not approved for publishing.")
        log_action("POST_HELD", filename, "LinkedIn post held — not approved for publishing")

    print("=" * 55)


# ============================================================
# WATCHER — monitors Needs_Action/ for new .md files
# ============================================================
class NeedsActionHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed = set()
        if os.path.exists(NEEDS_ACTION_PATH):
            for f in os.listdir(NEEDS_ACTION_PATH):
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
        time.sleep(1)
        self.processed.add(filename)
        process_file(event.src_path)


# ============================================================
# CLI — run with a specific file OR watch mode
# ============================================================
def main():
    os.makedirs(NEEDS_ACTION_PATH, exist_ok=True)
    os.makedirs(LOGS_PATH, exist_ok=True)
    os.makedirs(GENERATED_POSTS_PATH, exist_ok=True)

    # Mode 1: Process a specific file
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if not os.path.isabs(target):
            # Check if it exists as-is (e.g. "Needs_Action/file.md")
            if os.path.exists(os.path.join(VAULT_ROOT, target)):
                target = os.path.join(VAULT_ROOT, target)
            else:
                target = os.path.join(NEEDS_ACTION_PATH, target)
        if not os.path.exists(target):
            print(f"[ERROR] File not found: {target}")
            sys.exit(1)
        process_file(target)
        return

    # Mode 2: Watch Needs_Action/ for new files
    handler = NeedsActionHandler()
    observer = Observer()
    observer.schedule(handler, NEEDS_ACTION_PATH, recursive=False)
    observer.start()

    clipboard_status = "ON" if CLIPBOARD_AVAILABLE else "OFF (pip install pyperclip)"

    print()
    print("=" * 55)
    print("  AI EMPLOYEE — LINKEDIN POST GENERATOR v1.0")
    print("  Silver Tier")
    print("=" * 55)
    print(f"  Vault:       {VAULT_ROOT}")
    print(f"  Monitoring:  Needs_Action/")
    print(f"  Clipboard:   {clipboard_status}")
    print(f"  Sensitive:   ON ({len(SENSITIVE_KEYWORDS)} keywords)")
    print(f"  Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    print("  Drop a .md file in Needs_Action/ to generate a post")
    print("  Or run:  python linkedin_poster.py <filename.md>")
    print("  Press Ctrl+C to stop")
    print("=" * 55)

    if handler.processed:
        print(f"\n  Existing files (skipped): {', '.join(sorted(handler.processed))}")

    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopping LinkedIn Post Generator...")
        observer.stop()

    observer.join()
    print("  LinkedIn Post Generator stopped.")


if __name__ == "__main__":
    main()
