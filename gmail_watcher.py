"""
Gmail Watcher - AI Employee Vault (Silver Tier)
================================================
Monitors Gmail inbox for new unread emails.
Creates .md files in Inbox/ for auto_processor.py to pick up.

Setup:
  1. Enable Gmail API in Google Cloud Console
  2. Download credentials.json to this folder
  3. pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  4. python gmail_watcher.py

First run opens browser for Google OAuth login.
"""

import os
import sys
import io
import time
import base64
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

# Fix Windows terminal encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("=" * 55)
    print("  Gmail API libraries not installed. Run:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    print("=" * 55)
    sys.exit(1)

# ============================================================
# CONFIG
# ============================================================
VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
INBOX_PATH = os.path.join(VAULT_ROOT, "Inbox")
LOGS_PATH = os.path.join(VAULT_ROOT, "Logs")
ACTION_LOG = os.path.join(LOGS_PATH, "action-log.md")

# Gmail API scope — read-only (no delete, no send)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_FILE = os.path.join(VAULT_ROOT, "credentials.json")
TOKEN_FILE = os.path.join(VAULT_ROOT, "token.json")

# Poll interval in seconds
POLL_INTERVAL = 30

# Sensitive keywords — same as auto_processor.py
SENSITIVE_KEYWORDS = [
    "money", "payment", "transfer", "send", "invoice",
    "pay", "wire", "transaction", "bank", "urgent",
    "password", "credential", "secret", "delete"
]


# ============================================================
# AUTH
# ============================================================
def gmail_authenticate():
    """Authenticate with Gmail API using OAuth2.
    First run opens browser. After that, uses saved token.json."""
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  Refreshing Gmail token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("=" * 55)
                print("  ERROR: credentials.json not found!")
                print(f"  Expected at: {CREDENTIALS_FILE}")
                print()
                print("  Setup steps:")
                print("  1. Go to https://console.cloud.google.com/")
                print("  2. Create project > Enable Gmail API")
                print("  3. Create OAuth 2.0 credentials (Desktop App)")
                print("  4. Download JSON > rename to credentials.json")
                print("  5. Place in this folder")
                print("=" * 55)
                sys.exit(1)

            print("  Opening browser for Gmail login...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print("  Token saved to token.json")

    return build("gmail", "v1", credentials=creds)


# ============================================================
# EMAIL FETCHING
# ============================================================
def get_unread_emails(service, max_results=10):
    """Fetch unread emails from Gmail inbox."""
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    return messages


def get_email_detail(service, msg_id):
    """Get full email details by message ID."""
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg.get("payload", {}).get("headers", [])

    subject = ""
    sender = ""
    date = ""
    for header in headers:
        name = header.get("name", "").lower()
        if name == "subject":
            subject = header.get("value", "(No Subject)")
        elif name == "from":
            sender = header.get("value", "(Unknown)")
        elif name == "date":
            date = header.get("value", "")

    # Extract body
    body = extract_body(msg.get("payload", {}))

    # Clean and truncate body for summary
    body_summary = clean_body(body)

    return {
        "id": msg_id,
        "subject": subject,
        "from": sender,
        "date": date,
        "body_summary": body_summary,
        "snippet": msg.get("snippet", "")
    }


def extract_body(payload):
    """Extract plain text body from email payload."""
    # Direct body
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    # Multipart — find text/plain part
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        # Nested multipart
        if part.get("parts"):
            result = extract_body(part)
            if result:
                return result

    return ""


def clean_body(body, max_chars=500):
    """Clean email body and truncate for summary."""
    if not body:
        return "(No body content)"

    # Remove excessive whitespace
    body = re.sub(r'\n{3,}', '\n\n', body)
    body = re.sub(r' {2,}', ' ', body)
    body = body.strip()

    if len(body) > max_chars:
        body = body[:max_chars] + "...(truncated)"

    return body


# ============================================================
# SENSITIVE CHECK + APPROVAL
# ============================================================
def check_sensitive(text):
    """Return list of sensitive keywords found in text."""
    lower = text.lower()
    return [kw for kw in SENSITIVE_KEYWORDS if kw in lower]


def ask_approval(email_info, sensitive_words):
    """Ask human to approve processing of sensitive email."""
    print()
    print("!" * 55)
    print("  SENSITIVE EMAIL DETECTED")
    print(f"  Subject: {email_info['subject']}")
    print(f"  From:    {email_info['from']}")
    print(f"  Keywords: {', '.join(sensitive_words)}")
    print("!" * 55)
    while True:
        answer = input("  Process this email? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Type 'yes' or 'no'")


# ============================================================
# FILE CREATION
# ============================================================
def sanitize_filename(text):
    """Remove invalid filename characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', text)[:50]


def create_inbox_md(email_info):
    """Create .md file in Inbox/ from email data."""
    os.makedirs(INBOX_PATH, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_subject = sanitize_filename(email_info["subject"])
    filename = f"email_{timestamp}_{safe_subject}.md"
    filepath = os.path.join(INBOX_PATH, filename)

    content = f"""# Email: {email_info['subject']}

## Metadata
- **From:** {email_info['from']}
- **Date:** {email_info['date']}
- **Gmail ID:** {email_info['id']}
- **Fetched at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
{email_info['snippet']}

## Body
{email_info['body_summary']}

---
*Auto-imported by Gmail Watcher (Silver Tier)*
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filename, filepath


# ============================================================
# ACTION LOG
# ============================================================
def log_action(action, target, detail):
    """Append entry to action-log.md."""
    os.makedirs(LOGS_PATH, exist_ok=True)
    now = datetime.now().strftime("%H:%M")
    today = datetime.now().strftime("%Y-%m-%d")

    entry = f"| {now} | {action} | {target} | {detail} |\n"

    # Create file if missing
    if not os.path.exists(ACTION_LOG):
        with open(ACTION_LOG, "w", encoding="utf-8") as f:
            f.write("# Action Log\n\n")

    with open(ACTION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


# ============================================================
# MAIN LOOP
# ============================================================
def main():
    print()
    print("=" * 55)
    print("  AI EMPLOYEE - GMAIL WATCHER (Silver Tier)")
    print("=" * 55)

    # Authenticate
    print("  Connecting to Gmail...")
    service = gmail_authenticate()
    print("  Gmail connected!")
    print()
    print(f"  Vault:       {VAULT_ROOT}")
    print(f"  Inbox:       {INBOX_PATH}")
    print(f"  Poll every:  {POLL_INTERVAL}s")
    print(f"  Sensitive:   ON ({len(SENSITIVE_KEYWORDS)} keywords)")
    print(f"  Scope:       READ-ONLY (emails stay in Gmail)")
    print(f"  Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    print("  Monitoring Gmail inbox for new unread emails...")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    print()

    # Track processed email IDs
    seen_ids = set()

    # First run — mark existing unread as seen (don't flood Inbox/)
    print("  Loading existing unread emails (marking as seen)...")
    existing = get_unread_emails(service, max_results=50)
    for msg in existing:
        seen_ids.add(msg["id"])
    print(f"  {len(seen_ids)} existing unread emails marked as seen")
    print(f"  Only NEW emails from now will be processed")
    print()

    log_action("STARTED", "gmail_watcher.py", f"Monitoring Gmail inbox ({len(seen_ids)} existing skipped)")

    try:
        while True:
            time.sleep(POLL_INTERVAL)

            try:
                messages = get_unread_emails(service)
            except Exception as e:
                print(f"  [ERROR] Gmail fetch failed: {e}")
                continue

            new_count = 0
            for msg in messages:
                msg_id = msg["id"]
                if msg_id in seen_ids:
                    continue

                # New email found
                seen_ids.add(msg_id)
                new_count += 1

                try:
                    email_info = get_email_detail(service, msg_id)
                except Exception as e:
                    print(f"  [ERROR] Cannot read email {msg_id}: {e}")
                    continue

                print()
                print("-" * 55)
                print(f"  NEW EMAIL DETECTED")
                print(f"  Subject: {email_info['subject']}")
                print(f"  From:    {email_info['from']}")
                print(f"  Date:    {email_info['date']}")
                print("-" * 55)

                # Sensitive check
                full_text = f"{email_info['subject']} {email_info['body_summary']}"
                sensitive_words = check_sensitive(full_text)

                if sensitive_words:
                    approved = ask_approval(email_info, sensitive_words)
                    if not approved:
                        print(f"  [BLOCKED] Email skipped by Farhana")
                        log_action("BLOCKED", email_info["subject"], f"Sensitive email denied ({', '.join(sensitive_words)})")
                        continue
                    print(f"  [APPROVED] Processing...")

                # Create .md file in Inbox/
                filename, filepath = create_inbox_md(email_info)
                print(f"  Created: Inbox/{filename}")
                log_action("GMAIL_IMPORT", filename, f"Email from {email_info['from']}: {email_info['subject']}")

                print(f"  auto_processor.py will pick this up automatically")
                print()

            if new_count == 0:
                # Silent poll — no output to keep terminal clean
                pass

    except KeyboardInterrupt:
        print()
        print("  Stopping Gmail Watcher...")
        log_action("STOPPED", "gmail_watcher.py", "Manual stop (Ctrl+C)")
        print("  Gmail Watcher stopped.")


if __name__ == "__main__":
    main()
