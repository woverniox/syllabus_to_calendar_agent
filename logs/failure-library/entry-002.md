Failure Library Entry #002

Date: 2026-03-01
Run ID: RUN-007
Severity: Medium
Status: Fixed
Summary

Calendar sync failed because the agent could not detect an open Google Calendar tab and has no direct authorization to access the user’s account.
Reproduction
Input

{
  "message": "Sync my Spring 2026 schedule into the Google Calendar tab I have open.",
  "context": {
    "courses": ["BIO101", "CS201"],
    "requested_action": "create_calendar_events_from_schedule"
  }
}

Expected Behavior

    Agent should detect that Google Calendar appears to be open in the user’s browser

    Generate event data from the parsed syllabi

    Guide the user through inserting these events into the visible calendar interface

Actual Behavior

    Agent attempted to initiate a calendar sync flow assuming API-style access

    Failed to detect any usable in-tab calendar context

    Returned a generic failure message without clear instructions for manual completion

Root Cause Analysis

    Immediate cause: No reliable signal that a Google Calendar tab was available or focused in the user’s environment.

    Contributing factor: Interaction design assumed background API access instead of an in-tab, user-driven workflow.

    Design gap: No graceful fallback path for “calendar not directly accessible,” such as exporting events or providing copy‑paste instructions.

Fix Applied
Before (assumes direct calendar access)

def sync_to_google_calendar(events):
    # Assumes direct programmatic access to the user's calendar
    for event in events:
        calendar_api.create_event(event)
    return {"status": "success"}

After (tab-aware, user-in-the-loop)

def prepare_calendar_sync(events, calendar_tab_detected: bool):
    if not calendar_tab_detected:
        # Fallback: provide user-friendly export instead of failing silently
        return {
            "status": "needs_user_action",
            "export_format": "ics",
            "instructions": (
                "Download the .ics file and import it into the open Google "
                "Calendar tab, or copy the provided event details manually."
            ),
            "events": events,
        }

    # When user confirms they have Google Calendar open and ready
    return {
        "status": "guided_manual_entry",
        "instructions": (
            "I will show you each event with title, date, and time. "
            "Please paste these into your open Google Calendar tab."
        ),
        "events": events,
    }

Verification

    Simulated a run with no detectable calendar tab and verified that the agent offered an export plus clear manual instructions instead of a generic error.

    Simulated a run where the user confirmed an open Google Calendar tab and verified that events were presented in a copy‑paste friendly format.

    Confirmed that no attempt is made to access the user’s calendar account directly.

    Verified that failure messages now include explicit next steps for the user.

Prevention

    Added explicit branch for “no calendar context available” with a non‑destructive fallback.

    Updated UX copy to clarify that the agent cannot directly access Google Calendar and requires user interaction.

    Added tests for both “calendar tab present” and “calendar tab missing” scenarios.

    Documented environment constraints so future features do not assume direct authorization.

