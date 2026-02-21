"""
Clipboard Auto Copy - AI Employee Vault
========================================
Picks the latest prompt from Generated_Prompts/ and copies it to clipboard.
Can be run standalone OR called from auto_processor.py.

Usage:
  Standalone:   python clipboard_auto_copy.py
  From code:    from clipboard_auto_copy import copy_latest_prompt
"""

import os
import sys
import glob

try:
    import pyperclip
except ImportError:
    print("pyperclip not installed. Run:  pip install pyperclip")
    sys.exit(1)


VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROMPTS_PATH = os.path.join(VAULT_ROOT, "Generated_Prompts")


def get_latest_prompt_file():
    """Find the most recently created .txt file in Generated_Prompts/."""
    pattern = os.path.join(PROMPTS_PATH, "prompt_*.txt")
    files = glob.glob(pattern)
    if not files:
        return None
    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def copy_latest_prompt():
    """Read latest prompt file and copy its content to clipboard.
    Returns (success: bool, message: str)."""
    latest = get_latest_prompt_file()

    if latest is None:
        return False, "No prompt files found in Generated_Prompts/"

    try:
        with open(latest, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"Cannot read {latest}: {e}"

    if not content.strip():
        return False, f"Prompt file is empty: {latest}"

    try:
        pyperclip.copy(content)
    except Exception as e:
        return False, f"Clipboard copy failed: {e}"

    filename = os.path.basename(latest)
    char_count = len(content)
    return True, f"Copied to clipboard! ({char_count} chars) File: {filename}"


def copy_text_to_clipboard(text):
    """Directly copy any text to clipboard.
    Returns (success: bool, message: str)."""
    try:
        pyperclip.copy(text)
        return True, f"Copied to clipboard! ({len(text)} chars)"
    except Exception as e:
        return False, f"Clipboard copy failed: {e}"


def main():
    """Standalone mode — find latest prompt and copy to clipboard."""
    print()
    print("=" * 50)
    print("  Clipboard Auto Copy")
    print("=" * 50)

    latest = get_latest_prompt_file()
    if latest is None:
        print("  No prompt files found in Generated_Prompts/")
        print("  Run auto_processor.py first and drop a .md file in Inbox/")
        return

    print(f"  Latest: {os.path.basename(latest)}")
    print(f"  Size:   {os.path.getsize(latest)} bytes")

    success, message = copy_latest_prompt()
    if success:
        print(f"  {message}")
        print()
        print("  Now just Ctrl+V in Claude Chat / Bonsai!")
    else:
        print(f"  ERROR: {message}")

    print("=" * 50)


if __name__ == "__main__":
    main()
