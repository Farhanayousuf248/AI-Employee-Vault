"""
Weekly CEO Report Generator v1.0 - Gold Tier
=============================================
AI Employee Vault — Reads action-log.md & Dashboard.md,
generates a professional weekly summary report in Markdown,
and saves it to Weekly_Reports/.

Usage:
  python weekly_report.py              # report for current week
  python weekly_report.py 2026-03-26   # report for week containing that date
"""

import os
import sys
import io
import re
from datetime import datetime, timedelta

# Fix Windows terminal encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# PATHS
# ============================================================
VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOGS_PATH = os.path.join(VAULT_ROOT, "Logs")
ACTION_LOG = os.path.join(LOGS_PATH, "action-log.md")
DASHBOARD = os.path.join(VAULT_ROOT, "Dashboard.md")
NEEDS_ACTION_PATH = os.path.join(VAULT_ROOT, "Needs_Action")
DONE_PATH = os.path.join(VAULT_ROOT, "Done")
REPORTS_PATH = os.path.join(VAULT_ROOT, "Weekly_Reports")


# ============================================================
# FILE READERS
# ============================================================
def read_file(filepath):
    """Read a file safely, return empty string on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"  [WARN] Cannot read {filepath}: {e}")
        return ""


# ============================================================
# PARSE ACTION LOG
# ============================================================
def parse_action_log(content):
    """
    Parse action-log.md into structured data.
    Returns dict: { "2026-03-28": [ {time, action, file, details}, ... ], ... }
    """
    entries_by_date = {}
    current_date = None

    for line in content.splitlines():
        line = line.strip()

        # Match date headers like "## 2026-03-28"
        date_match = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            entries_by_date[current_date] = []
            continue

        # Match table rows like "| 12:00 | PROCESSED | test.md | Details |"
        if current_date and line.startswith("|") and "Action" not in line and "---" not in line:
            cols = [c.strip() for c in line.split("|")]
            cols = [c for c in cols if c]  # remove empty from leading/trailing |
            if len(cols) >= 4:
                entries_by_date[current_date].append({
                    "time": cols[0],
                    "action": cols[1],
                    "file": cols[2],
                    "details": cols[3],
                })

    return entries_by_date


def get_week_range(target_date):
    """
    Return (week_start_monday, week_end_sunday) for the week containing target_date.
    """
    start = target_date - timedelta(days=target_date.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    return start, end


def filter_entries_for_week(entries_by_date, week_start, week_end):
    """Return only entries within the given week range."""
    filtered = {}
    for date_str, entries in entries_by_date.items():
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if week_start <= d <= week_end:
            filtered[date_str] = entries
    return filtered


# ============================================================
# PARSE DASHBOARD — extract pending tasks
# ============================================================
def parse_dashboard_pending(content):
    """
    Extract pending action rows from Dashboard.md.
    Returns list of dicts: [{file, summary, priority, deadline}, ...]
    """
    tasks = []
    in_table = False

    for line in content.splitlines():
        line = line.strip()

        # Detect pending actions table header
        if "File" in line and "Summary" in line and "Priority" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")]
            cols = [c for c in cols if c]
            if len(cols) >= 4:
                tasks.append({
                    "file": cols[0],
                    "summary": cols[1],
                    "priority": cols[2].replace("**", ""),
                    "deadline": cols[3],
                })
        elif in_table and not line.startswith("|"):
            in_table = False

    return tasks


# ============================================================
# PARSE NEEDS_ACTION FILES — for richer task details
# ============================================================
def scan_needs_action():
    """Scan Needs_Action/ folder and return list of pending file names."""
    if not os.path.exists(NEEDS_ACTION_PATH):
        return []
    return [f for f in os.listdir(NEEDS_ACTION_PATH) if f.endswith(".md")]


def scan_done():
    """Scan Done/ folder for completed task file names."""
    if not os.path.exists(DONE_PATH):
        return []
    return [f for f in os.listdir(DONE_PATH) if f.endswith(".md")]


# ============================================================
# ANALYSIS — derive insights from log entries
# ============================================================
def analyze_week(week_entries):
    """
    Analyze a week's log entries and return stats + categorized actions.
    """
    stats = {
        "total_actions": 0,
        "files_processed": set(),
        "actions_count": {},       # action_type -> count
        "completed_tasks": [],     # files that were MOVED/COPIED to Done or Needs_Action
        "created_tools": [],       # files that were CREATED (scripts)
        "posts_generated": 0,
        "posts_approved": 0,
        "sensitive_blocked": 0,
        "daily_breakdown": {},     # date -> action count
    }

    for date_str in sorted(week_entries.keys()):
        entries = week_entries[date_str]
        stats["daily_breakdown"][date_str] = len(entries)

        for e in entries:
            stats["total_actions"] += 1
            action = e["action"].upper()
            stats["actions_count"][action] = stats["actions_count"].get(action, 0) + 1
            stats["files_processed"].add(e["file"])

            if action in ("MOVED", "COPIED"):
                stats["completed_tasks"].append({"file": e["file"], "details": e["details"], "date": date_str})
            if action == "CREATED":
                stats["created_tools"].append({"file": e["file"], "details": e["details"], "date": date_str})
            if action == "GENERATED":
                stats["posts_generated"] += 1
            if action == "POST_APPROVED":
                stats["posts_approved"] += 1
            if action == "BLOCKED":
                stats["sensitive_blocked"] += 1

    return stats


# ============================================================
# REPORT BUILDER
# ============================================================
def build_report(target_date):
    """Build the full weekly CEO report as a Markdown string."""

    week_start, week_end = get_week_range(target_date)
    week_label = f"{week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- Parse data sources ----
    log_content = read_file(ACTION_LOG)
    dashboard_content = read_file(DASHBOARD)

    all_entries = parse_action_log(log_content)
    week_entries = filter_entries_for_week(all_entries, week_start, week_end)
    pending_tasks = parse_dashboard_pending(dashboard_content)
    needs_action_files = scan_needs_action()
    done_files = scan_done()

    stats = analyze_week(week_entries)

    # ---- Separate high priority pending tasks ----
    high_priority = [t for t in pending_tasks if "HIGH" in t["priority"].upper()]
    other_pending = [t for t in pending_tasks if "HIGH" not in t["priority"].upper()]

    # ---- Build report ----
    report = []
    report.append(f"# Weekly CEO Report")
    report.append(f"### {week_label}")
    report.append(f"")
    report.append(f"> Generated by AI Employee on {today_str}")
    report.append(f"> Vault: AI-Employee-Vault | Owner: Farhana")
    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ---- Executive Summary ----
    report.append(f"## Executive Summary")
    report.append(f"")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Actions Logged | {stats['total_actions']} |")
    report.append(f"| Unique Files Touched | {len(stats['files_processed'])} |")
    report.append(f"| Tasks Completed/Moved | {len(stats['completed_tasks'])} |")
    report.append(f"| Tools/Scripts Created | {len(stats['created_tools'])} |")
    report.append(f"| LinkedIn Posts Generated | {stats['posts_generated']} |")
    report.append(f"| LinkedIn Posts Approved | {stats['posts_approved']} |")
    report.append(f"| Sensitive Actions Blocked | {stats['sensitive_blocked']} |")
    report.append(f"| Pending in Needs_Action/ | {len(needs_action_files)} |")
    report.append(f"| Completed in Done/ | {len(done_files)} |")
    report.append(f"")

    # ---- High Priority Pending ----
    report.append(f"---")
    report.append(f"")
    report.append(f"## High Priority Pending Tasks")
    report.append(f"")
    if high_priority:
        report.append(f"| # | File | Summary | Deadline |")
        report.append(f"|---|------|---------|----------|")
        for i, t in enumerate(high_priority, 1):
            report.append(f"| {i} | {t['file']} | {t['summary']} | {t['deadline']} |")
    else:
        report.append(f"No high-priority tasks pending. All clear!")
    report.append(f"")

    if other_pending:
        report.append(f"### Other Pending Tasks")
        report.append(f"")
        report.append(f"| # | File | Summary | Priority |")
        report.append(f"|---|------|---------|----------|")
        for i, t in enumerate(other_pending, 1):
            report.append(f"| {i} | {t['file']} | {t['summary']} | {t['priority']} |")
        report.append(f"")

    # ---- Tasks Completed This Week ----
    report.append(f"---")
    report.append(f"")
    report.append(f"## Tasks Completed This Week")
    report.append(f"")
    if stats["completed_tasks"]:
        report.append(f"| # | Date | File | Details |")
        report.append(f"|---|------|------|---------|")
        for i, t in enumerate(stats["completed_tasks"], 1):
            report.append(f"| {i} | {t['date']} | {t['file']} | {t['details']} |")
    else:
        report.append(f"No task movements recorded this week.")
    report.append(f"")

    if stats["created_tools"]:
        report.append(f"### New Tools & Scripts Built")
        report.append(f"")
        report.append(f"| # | Date | File | Description |")
        report.append(f"|---|------|------|-------------|")
        for i, t in enumerate(stats["created_tools"], 1):
            report.append(f"| {i} | {t['date']} | {t['file']} | {t['details']} |")
        report.append(f"")

    # ---- Key Insights / Achievements ----
    report.append(f"---")
    report.append(f"")
    report.append(f"## Key Insights & Achievements")
    report.append(f"")

    insights = []
    if stats["total_actions"] > 0:
        busiest = max(stats["daily_breakdown"], key=stats["daily_breakdown"].get) if stats["daily_breakdown"] else None
        if busiest:
            insights.append(f"Busiest day: **{busiest}** with {stats['daily_breakdown'][busiest]} actions logged")

    if stats["created_tools"]:
        tool_names = [t["file"] for t in stats["created_tools"]]
        insights.append(f"New automation built: **{', '.join(tool_names)}** — expanding AI Employee capabilities")

    if stats["posts_generated"] > 0:
        insights.append(f"LinkedIn content pipeline active: {stats['posts_generated']} posts generated, {stats['posts_approved']} approved for publishing")

    if stats["sensitive_blocked"] > 0:
        insights.append(f"Security gate working: {stats['sensitive_blocked']} sensitive action(s) correctly flagged and blocked")

    top_actions = sorted(stats["actions_count"].items(), key=lambda x: x[1], reverse=True)[:3]
    if top_actions:
        breakdown = ", ".join([f"{a} ({c})" for a, c in top_actions])
        insights.append(f"Top action types: {breakdown}")

    if len(needs_action_files) > 3:
        insights.append(f"Needs_Action/ has **{len(needs_action_files)} files** — consider reviewing and archiving completed items to Done/")

    if not insights:
        insights.append("Quiet week — no major actions logged. Good time to plan ahead!")

    for insight in insights:
        report.append(f"- {insight}")
    report.append(f"")

    # ---- Daily Activity Breakdown ----
    report.append(f"---")
    report.append(f"")
    report.append(f"## Daily Activity Breakdown")
    report.append(f"")
    if stats["daily_breakdown"]:
        report.append(f"| Day | Actions |")
        report.append(f"|-----|---------|")
        for date_str in sorted(stats["daily_breakdown"].keys()):
            count = stats["daily_breakdown"][date_str]
            bar = "█" * min(count, 20)  # visual bar, max 20 blocks
            report.append(f"| {date_str} | {count} {bar} |")
    else:
        report.append(f"No activity recorded this week.")
    report.append(f"")

    # ---- Next Week Focus ----
    report.append(f"---")
    report.append(f"")
    report.append(f"## Next Week Focus")
    report.append(f"")

    focus_items = []
    if high_priority:
        for t in high_priority:
            focus_items.append(f"**[URGENT]** {t['summary']} ({t['file']})")
    if other_pending:
        for t in other_pending[:3]:
            focus_items.append(f"Review and complete: {t['summary']} ({t['file']})")
    if len(needs_action_files) > 3:
        focus_items.append("Clean up Needs_Action/ — archive completed items to Done/")
    focus_items.append("Continue Silver/Gold Tier feature development")
    focus_items.append("Review and refine AI Employee automation pipeline")

    for i, item in enumerate(focus_items, 1):
        report.append(f"{i}. {item}")
    report.append(f"")

    # ---- Footer ----
    report.append(f"---")
    report.append(f"")
    report.append(f"*This report was auto-generated by AI Employee (Gold Tier) — weekly_report.py*")
    report.append(f"*For questions or corrections, contact Farhana.*")

    return "\n".join(report)


# ============================================================
# SAVE & DISPLAY
# ============================================================
def save_report(report_text, target_date):
    """Save report to Weekly_Reports/ folder."""
    os.makedirs(REPORTS_PATH, exist_ok=True)
    filename = f"Weekly_Report_{target_date.strftime('%Y-%m-%d')}.md"
    filepath = os.path.join(REPORTS_PATH, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return filepath


def log_action(details):
    """Append a log entry to action-log.md."""
    os.makedirs(LOGS_PATH, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")

    content = read_file(ACTION_LOG)
    if f"## {today}" not in content:
        entry = f"\n## {today}\n\n| Time | Action | File | Details |\n|------|--------|------|---------|"
        entry += f"\n| {now} | REPORT | Weekly_Report | {details} |\n"
    else:
        entry = f"| {now} | REPORT | Weekly_Report | {details} |\n"

    with open(ACTION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


# ============================================================
# MAIN
# ============================================================
def main():
    # Determine target date
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            print(f"[ERROR] Invalid date format: {sys.argv[1]}")
            print(f"        Use: python weekly_report.py YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = datetime.now().date()

    week_start, week_end = get_week_range(target_date)

    print()
    print("=" * 55)
    print("  AI EMPLOYEE — WEEKLY CEO REPORT GENERATOR v1.0")
    print("  Gold Tier")
    print("=" * 55)
    print(f"  Target date:  {target_date}")
    print(f"  Week range:   {week_start} to {week_end}")
    print(f"  Vault:        {VAULT_ROOT}")
    print("=" * 55)
    print()

    # Generate report
    print("  [1/3] Parsing action-log.md & Dashboard.md...")
    report_text = build_report(target_date)

    print("  [2/3] Saving report...")
    filepath = save_report(report_text, target_date)

    print("  [3/3] Logging action...")
    log_action(f"Weekly CEO Report generated for {week_start} to {week_end}")

    # Display in terminal
    print()
    print("-" * 55)
    print(report_text)
    print("-" * 55)
    print()
    print(f"  Report saved: {filepath}")
    print()
    print("=" * 55)


if __name__ == "__main__":
    main()
