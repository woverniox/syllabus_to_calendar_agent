"""
Task Creation Tool

Creates follow-up tasks based on lead qualification results.
Students implement this in Week 4.
"""

from typing import Optional
from datetime import datetime, timedelta
from models import LeadInput, ScoreResult


class TaskResult:
    """Result of a task creation operation."""

    def __init__(self, success: bool, task_id: str, task_type: str, due_date: datetime):
        self.success = success
        self.task_id = task_id
        self.task_type = task_type
        self.due_date = due_date


def create_followup_task(
    lead: LeadInput,
    score_result: ScoreResult,
    assigned_to: Optional[str] = None
) -> TaskResult:
    """
    Create a follow-up task based on lead tier.

    Task types by tier:
    - reject: "Review rejected lead" (requires approval first)
    - nurture: "Send nurture email" (due in 3 days)
    - qualified/smb: "Schedule discovery call" (due in 1 day)
    - qualified/enterprise: "Prepare enterprise proposal" (due in 1 day, after approval)
    - needs_info: "Request missing information" (due today)

    Args:
        lead: The original lead input
        score_result: The scoring result
        assigned_to: Optional assignee email

    Returns:
        TaskResult with task details
    """
    # Determine task type and due date based on tier
    task_config = _get_task_config(score_result.tier, score_result.segment)

    task_id = f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{lead.email.split('@')[0]}"

    # TODO: Implement in Week 4
    # Options:
    # 1. Google Tasks API
    # 2. Google Sheets (task tracking sheet)
    # 3. Internal task queue

    # Placeholder implementation
    print(f"[PLACEHOLDER] Would create task: {task_config['title']}")
    print(f"  Lead: {lead.email}")
    print(f"  Due: {task_config['due_date']}")
    print(f"  Priority: {task_config['priority']}")

    return TaskResult(
        success=True,
        task_id=task_id,
        task_type=task_config["type"],
        due_date=task_config["due_date"]
    )


def _get_task_config(tier: str, segment: str) -> dict:
    """Get task configuration based on tier and segment."""
    now = datetime.utcnow()

    configs = {
        "needs_info": {
            "type": "request_info",
            "title": "Request missing information from lead",
            "due_date": now + timedelta(hours=4),
            "priority": "high",
        },
        "reject": {
            "type": "review_reject",
            "title": "Review rejected lead decision",
            "due_date": now + timedelta(days=1),
            "priority": "low",
        },
        "nurture": {
            "type": "nurture_outreach",
            "title": "Send nurture email sequence",
            "due_date": now + timedelta(days=3),
            "priority": "medium",
        },
        "qualified_smb": {
            "type": "schedule_call",
            "title": "Schedule discovery call with qualified lead",
            "due_date": now + timedelta(days=1),
            "priority": "high",
        },
        "qualified_enterprise": {
            "type": "prepare_proposal",
            "title": "Prepare enterprise proposal and schedule call",
            "due_date": now + timedelta(days=1),
            "priority": "urgent",
        },
    }

    if tier == "qualified":
        key = f"qualified_{segment}"
    else:
        key = tier

    return configs.get(key, configs["nurture"])


def list_pending_tasks(lead_key: Optional[str] = None) -> list:
    """
    List pending tasks, optionally filtered by lead.

    Args:
        lead_key: Optional lead key to filter by

    Returns:
        List of pending task dictionaries
    """
    # TODO: Implement in Week 4
    print(f"[PLACEHOLDER] Would list pending tasks")
    return []


def complete_task(task_id: str, notes: Optional[str] = None) -> bool:
    """
    Mark a task as completed.

    Args:
        task_id: The task identifier
        notes: Optional completion notes

    Returns:
        True if marked successfully
    """
    # TODO: Implement in Week 4
    print(f"[PLACEHOLDER] Would complete task: {task_id}")
    return True
