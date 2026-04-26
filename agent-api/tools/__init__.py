"""
Tools Module

Agent tools for the Lead Qualification Agent.
Each tool is a function that the agent can call to perform actions.

Students implement these tools week by week:
- Week 3: score_lead
- Week 4: upsert_lead, create_task, draft_email
- Week 5: memory (get/write company history)
"""

from .score_lead import score_lead
from .upsert_lead import upsert_lead_row
from .create_task import create_followup_task
from .draft_email import draft_email
from .memory import get_company_history, write_company_summary

__all__ = [
    "score_lead",
    "upsert_lead_row",
    "create_followup_task",
    "draft_email",
    "get_company_history",
    "write_company_summary",
]
