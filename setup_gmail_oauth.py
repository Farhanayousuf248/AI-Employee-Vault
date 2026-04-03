"""
Gmail OAuth Setup Helper - AI Employee Vault
==============================================
This script guides you through getting credentials.json from Google Cloud Console.

Steps:
1. Run this script
2. Open the link in your browser
3. Follow the prompts
4. credentials.json will be auto-saved
5. Then run: python gmail_watcher.py
"""

import webbrowser
import os

SETUP_URL = "https://console.cloud.google.com/"

STEPS = """
SETUP GMAIL API CREDENTIALS
============================

Step 1: Create Google Cloud Project
   • Go to: https://console.cloud.google.com/
   • Click "Select a Project" → "NEW PROJECT"
   • Name it: "AI-Employee-Vault"
   • Click "CREATE"

Step 2: Enable Gmail API
   • Search for "Gmail API" in the search bar
   • Click "Gmail API"
   • Click "ENABLE"

Step 3: Create OAuth 2.0 Credentials
   • Go to "Credentials" (left sidebar)
   • Click "Create Credentials" → "OAuth client ID"
   • If asked, create OAuth consent screen first:
     - User Type: External
     - Fill required fields (app name, email, etc.)
     - Add scope: https://www.googleapis.com/auth/gmail.readonly
   • Application type: Desktop application
   • Click "CREATE"

Step 4: Download Credentials
   • Click the download icon (⬇) on your credential
   • Save as: credentials.json
   • Move it to: C:\\Users\\DELL\\OneDrive\\Desktop\\Heacathon_0\\AI-Employee-Vault\\

Step 5: Test Gmail Watcher
   • Back in terminal: python gmail_watcher.py
   • First run opens browser for Gmail login
   • Approve access when prompted
   • Done! Watcher will monitor your inbox

Questions?
   • Docs: https://developers.google.com/gmail/api/quickstart/python
   • Console: https://console.cloud.google.com/
"""

if __name__ == "__main__":
    print(STEPS)
    input("\nPress ENTER to open Google Cloud Console in browser...")
    webbrowser.open(SETUP_URL)
    print("\n✓ Browser opened. Follow the steps above to get credentials.json")
