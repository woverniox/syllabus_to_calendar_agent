"""
Approval Gate Logic

Human-in-the-loop approval for high-risk agent actions.
Students implement this in Week 7.
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from config import APPROVAL_REQUIRED_ACTIONS


@dataclass
class ApprovalCheck:
    """Result of an approval check."""
    required: bool
    reason: Optional[str] = None
    action_type: Optional[str] = None
    context: Optional[dict] = None


@dataclass
class ApprovalRequest:
    """A pending approval request."""
    action_id: str
    action_type: str
    lead_key: str
    reason: str
    context: dict
    requested_at: datetime
    status: str = "pending"  # pending, approved, rejected


# In-memory store for demo purposes
# TODO: Replace with database in Week 7
_pending_approvals: dict[str, ApprovalRequest] = {}


def check_approval(action: str, context: dict) -> ApprovalCheck:
    """
    Check if an action requires human approval.

    Actions requiring approval (configurable in config.py):
    - reject_decision: Rejecting a lead
    - enterprise_scheduling: Scheduling with enterprise leads
    - send_email: Actually sending (not drafting) emails
    - mark_spam: Marking a lead as spam

    Args:
        action: The action being attempted
        context: Additional context (lead data, score, etc.)

    Returns:
        ApprovalCheck indicating if approval is needed and why
    """
    if action in APPROVAL_REQUIRED_ACTIONS and APPROVAL_REQUIRED_ACTIONS[action]:
        return ApprovalCheck(
            required=True,
            reason=f"{action} requires human approval",
            action_type=action,
            context=context
        )

    # Check for enterprise leads
    if context.get("segment") == "enterprise":
        if action in ["schedule_meeting", "send_proposal"]:
            return ApprovalCheck(
                required=True,
                reason="Enterprise actions require approval",
                action_type=f"enterprise_{action}",
                context=context
            )

    return ApprovalCheck(required=False)


def request_approval(
    action_type: str,
    lead_key: str,
    reason: str,
    context: dict
) -> str:
    """
    Create an approval request for human review.

    Args:
        action_type: Type of action needing approval
        lead_key: The lead this action relates to
        reason: Why approval is needed
        context: Additional context for the approver

    Returns:
        action_id for tracking the approval request
    """
    action_id = f"approval_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{lead_key[:8]}"

    request = ApprovalRequest(
        action_id=action_id,
        action_type=action_type,
        lead_key=lead_key,
        reason=reason,
        context=context,
        requested_at=datetime.utcnow()
    )

    # TODO: Store in database in Week 7
    _pending_approvals[action_id] = request

    print(f"[APPROVAL REQUIRED] {action_type}")
    print(f"  Action ID: {action_id}")
    print(f"  Lead: {lead_key}")
    print(f"  Reason: {reason}")

    return action_id


def process_approval(action_id: str, approved: bool, notes: Optional[str] = None) -> bool:
    """
    Process an approval decision.

    Args:
        action_id: The approval request ID
        approved: Whether the action was approved
        notes: Optional notes from the approver

    Returns:
        True if processed successfully
    """
    if action_id not in _pending_approvals:
        print(f"[ERROR] Approval request not found: {action_id}")
        return False

    request = _pending_approvals[action_id]
    request.status = "approved" if approved else "rejected"

    print(f"[APPROVAL {'GRANTED' if approved else 'DENIED'}] {action_id}")
    if notes:
        print(f"  Notes: {notes}")

    # TODO: Trigger the approved action in Week 7
    # if approved:
    #     execute_approved_action(request)

    return True


def list_pending_approvals(lead_key: Optional[str] = None) -> list[ApprovalRequest]:
    """
    List pending approval requests.

    Args:
        lead_key: Optional filter by lead

    Returns:
        List of pending approval requests
    """
    pending = [
        req for req in _pending_approvals.values()
        if req.status == "pending"
    ]

    if lead_key:
        pending = [req for req in pending if req.lead_key == lead_key]

    return pending


def get_approval_status(action_id: str) -> Optional[str]:
    """
    Get the status of an approval request.

    Args:
        action_id: The approval request ID

    Returns:
        Status string or None if not found
    """
    if action_id in _pending_approvals:
        return _pending_approvals[action_id].status
    return None
