"""
Email Drafting Tool

Drafts emails based on lead qualification results.
Students implement this in Week 4.

IMPORTANT: This tool creates DRAFTS only - it does NOT send emails.
Sending emails requires human approval (Week 7 guardrails).
"""

from typing import Optional
from datetime import datetime
from models import LeadInput, ScoreResult


class EmailDraft:
    """Represents an email draft."""

    def __init__(
        self,
        draft_id: str,
        to: str,
        subject: str,
        body: str,
        template_type: str
    ):
        self.draft_id = draft_id
        self.to = to
        self.subject = subject
        self.body = body
        self.template_type = template_type
        self.created_at = datetime.utcnow()


def draft_email(
    lead: LeadInput,
    score_result: ScoreResult,
    template_type: Optional[str] = None
) -> EmailDraft:
    """
    Create an email draft based on lead tier.

    Template types:
    - nurture: Educational content, soft touch
    - qualified: Meeting request
    - needs_info: Request for missing information

    Args:
        lead: The original lead input
        score_result: The scoring result
        template_type: Optional override for template type

    Returns:
        EmailDraft ready for review/sending
    """
    # Determine template type from tier if not specified
    if not template_type:
        template_type = _tier_to_template(score_result.tier)

    # Generate draft content
    subject, body = _generate_email_content(lead, score_result, template_type)

    draft_id = f"draft_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # TODO: Implement in Week 4
    # Options:
    # 1. Gmail API - create draft
    # 2. Store in database for later sending
    # 3. Return for human review

    # Placeholder implementation
    print(f"[PLACEHOLDER] Would create email draft: {template_type}")
    print(f"  To: {lead.email}")
    print(f"  Subject: {subject}")

    return EmailDraft(
        draft_id=draft_id,
        to=lead.email,
        subject=subject,
        body=body,
        template_type=template_type
    )


def _tier_to_template(tier: str) -> str:
    """Map tier to email template type."""
    mapping = {
        "reject": "nurture",  # Soft rejection, keep door open
        "nurture": "nurture",
        "qualified": "qualified",
        "needs_info": "needs_info",
    }
    return mapping.get(tier, "nurture")


def _generate_email_content(
    lead: LeadInput,
    score_result: ScoreResult,
    template_type: str
) -> tuple[str, str]:
    """
    Generate email subject and body.

    TODO: Replace with LLM-generated content in Week 4.
    """
    templates = {
        "nurture": {
            "subject": f"Helpful resources for {lead.company}",
            "body": f"""Hi,

Thanks for your interest! Based on what you shared about {lead.need or 'your needs'}, I thought you might find our guide helpful.

[RESOURCE_LINK]

No pressure to chat now - just wanted to share something useful. Feel free to reach out when the timing is right.

Best,
[SENDER_NAME]"""
        },
        "qualified": {
            "subject": f"Quick chat about {lead.company}'s needs?",
            "body": f"""Hi,

Thanks for reaching out about {lead.need or 'your project'}. Based on your timeline of {lead.timeline or 'the near future'}, I'd love to learn more about your goals.

Would any of these times work for a quick 15-minute call?
- [TIME_SLOT_1]
- [TIME_SLOT_2]
- [TIME_SLOT_3]

Or feel free to grab a time here: [CALENDAR_LINK]

Looking forward to connecting!

Best,
[SENDER_NAME]"""
        },
        "needs_info": {
            "subject": f"Quick question for {lead.company}",
            "body": f"""Hi,

Thanks for reaching out! To make sure I can point you in the right direction, could you share a bit more about:

{_format_missing_questions(score_result.missing_fields)}

This will help me understand how we can best help.

Thanks!
[SENDER_NAME]"""
        },
    }

    template = templates.get(template_type, templates["nurture"])
    return template["subject"], template["body"]


def _format_missing_questions(missing_fields: list[str]) -> str:
    """Convert missing fields to natural questions."""
    questions = {
        "need": "- What challenge are you hoping to solve?",
        "timeline": "- When are you hoping to have this up and running?",
        "budget": "- Do you have a budget range in mind?",
        "company": "- What company are you with?",
    }

    return "\n".join(
        questions.get(field, f"- Could you tell me more about {field}?")
        for field in missing_fields
    )
