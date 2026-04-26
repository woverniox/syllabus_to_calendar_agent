"""
Syllabus Approval Gate Logic
Human-in-the-loop for Checkpoints 1, 2, and 3.
"""

from typing import Optional
from datetime import datetime
# Add this line:
from dataclasses import dataclass 
# Keep your other imports
from models import ConfidenceLevel

CONFIDENCE_THRESHOLDS = {
    "unsure": (0, 0.39),      # Red 🔴
    "review": (0.40, 0.69),   # Yellow 🟡
    "confident": (0.70, 1.0), # Green 🟢
}

@dataclass
class ApprovalCheck:
    required: bool
    reason: Optional[str] = None
    action_type: Optional[str] = None
    context: Optional[dict] = None

@dataclass
class ApprovalRequest:
    action_id: str
    action_type: str
    task_id: str
    reason: str
    context: dict
    requested_at: datetime
    status: str = "pending"

_pending_approvals: dict[str, ApprovalRequest] = {}

def check_syllabus_approval(action: str, context: dict) -> ApprovalCheck:
    """
    Logic for Checkpoint 1:
    Uses the ConfidenceLevel from models.py to decide if a human needs to look.
    """
    # If the agent flagged it as LOW confidence in models.py
    confidence = context.get("confidence")
    
    if confidence == ConfidenceLevel.LOW or action == "sync_to_calendar":
        return ApprovalCheck(
            required=True,
            reason=f"Action '{action}' requires review due to {confidence} confidence.",
            action_type=action,
            context=context
        )

    return ApprovalCheck(required=False)

def request_approval(action_type: str, task_id: str, reason: str, context: dict) -> str:
    action_id = f"approv_{datetime.utcnow().strftime('%y%m%d%H%M')}_{task_id[:6]}"
    request = ApprovalRequest(
        action_id=action_id,
        action_type=action_type,
        task_id=task_id,
        reason=reason,
        context=context,
        requested_at=datetime.utcnow()
    )
    _pending_approvals[action_id] = request
    print(f"[GATEKEEPER] Approval required for {action_type} on task {task_id}")
    return action_id

# guardrails/approvals.py

def sort_and_summarize(events: list) -> str:
    """
    Sorts events by date and formats them into a human-readable 
    summary for the approval prompt.
    """
    if not events:
        return "No events were found in the syllabus."

    # Sort by date string (YYYY-MM-DD ensures correct chronological order)
    try:
        # We use .get() to avoid crashing if a dictionary is missing the 'date' key
        events.sort(key=lambda x: x.get('date', '9999-12-31'))
    except Exception as e:
        print(f"Warning: Sorting failed due to {e}")

    summary = "\n--- EXTRACTED SCHEDULE ---\n"
    for i, event in enumerate(events, 1):
        date = event.get('date', 'No Date')
        title = event.get('title', 'Untitled')
        etype = event.get('type', 'Assignment')
        summary += f"{i}. [{date}] {title} ({etype})\n"
    
    summary += "\nDoes this schedule look acceptable for your calendar? (Yes/No)"
    return summary
