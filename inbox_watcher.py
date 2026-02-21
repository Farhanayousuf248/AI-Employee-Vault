"""
Inbox Watcher - AI Employee Vault
Monitors the Inbox folder for new .md files
"""

import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Path to Inbox folder (relative to this script)
INBOX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Inbox")


class InboxHandler(FileSystemEventHandler):
    """Handles file system events for Inbox folder"""

    def on_created(self, event):
        """Triggered when a new file is created"""
        if not event.is_directory and event.src_path.endswith('.md'):
            filename = os.path.basename(event.src_path)
            print(f"New file detected: {filename}")

    def on_modified(self, event):
        """Triggered when a file is modified"""
        if not event.is_directory and event.src_path.endswith('.md'):
            filename = os.path.basename(event.src_path)
            print(f"File modified: {filename}")


def main():
    """Main function to start the watcher"""
    # Create Inbox folder if it doesn't exist
    if not os.path.exists(INBOX_PATH):
        os.makedirs(INBOX_PATH)
        print(f"Created Inbox folder: {INBOX_PATH}")

    print("=" * 50)
    print("AI Employee - Inbox Watcher Started")
    print(f"Monitoring: {INBOX_PATH}")
    print("Waiting for new .md files...")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    # Set up the observer
    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, INBOX_PATH, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Inbox Watcher...")
        observer.stop()

    observer.join()
    print("Inbox Watcher stopped.")


if __name__ == "__main__":
    main()
