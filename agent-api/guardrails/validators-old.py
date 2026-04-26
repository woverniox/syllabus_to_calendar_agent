"""
Input Validation and Sanitization

Protects against malicious input and ensures data quality.
Students implement this in Week 11.
"""

import re
from typing import Optional, Tuple
from models import LeadInput


class ValidationResult:
    """Result of input validation."""

    def __init__(self, valid: bool, errors: list[str] = None, sanitized: dict = None):
        self.valid = valid
        self.errors = errors or []
        self.sanitized = sanitized or {}


def validate_lead_input(lead: LeadInput) -> ValidationResult:
    """
    Validate lead input for security and data quality.

    Checks:
    - Email format validity
    - Company name length and characters
    - No obvious injection attempts
    - Field length limits

    Args:
        lead: The lead input to validate

    Returns:
        ValidationResult with validity status and any errors
    """
    errors = []

    # Email validation (Pydantic handles basic format)
    if lead.email:
        if len(lead.email) > 254:
            errors.append("Email address too long")
        if _contains_suspicious_patterns(lead.email):
            errors.append("Email contains suspicious patterns")

    # Company name validation
    if lead.company:
        if len(lead.company) < 2:
            errors.append("Company name too short")
        if len(lead.company) > 200:
            errors.append("Company name too long")
        if _contains_suspicious_patterns(lead.company):
            errors.append("Company name contains suspicious patterns")

    # Need validation
    if lead.need:
        if len(lead.need) > 2000:
            errors.append("Need description too long")
        if _contains_prompt_injection(lead.need):
            errors.append("Need field contains potential prompt injection")

    # Timeline validation
    if lead.timeline:
        if len(lead.timeline) > 200:
            errors.append("Timeline too long")

    # Budget validation
    if lead.budget:
        if len(lead.budget) > 100:
            errors.append("Budget field too long")

    # Title validation
    if lead.title:
        if len(lead.title) > 100:
            errors.append("Title too long")

    # Company size validation
    if lead.company_size is not None:
        if lead.company_size < 1:
            errors.append("Company size must be positive")
        if lead.company_size > 10_000_000:
            errors.append("Company size seems unrealistic")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )


def sanitize_input(text: str) -> str:
    """
    Sanitize text input to prevent injection attacks.

    Removes or escapes:
    - HTML tags
    - Script injection attempts
    - SQL-like patterns
    - Prompt injection patterns

    Args:
        text: Raw input text

    Returns:
        Sanitized text safe for processing
    """
    if not text:
        return ""

    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', text)

    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')

    # Limit consecutive whitespace
    sanitized = re.sub(r'\s{3,}', '  ', sanitized)

    # Remove control characters (except newlines and tabs)
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)

    return sanitized.strip()


def _contains_suspicious_patterns(text: str) -> bool:
    """Check for obviously suspicious input patterns."""
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onclick=',
        r'onerror=',
        r'\x00',  # null byte
        r'&#x',   # HTML entity encoding
    ]

    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in suspicious_patterns)


def _contains_prompt_injection(text: str) -> bool:
    """
    Detect potential prompt injection attempts.

    This is a basic check - more sophisticated detection
    should be implemented in Week 11.
    """
    injection_patterns = [
        r'ignore (?:previous|above|all) instructions',
        r'disregard (?:previous|above|all)',
        r'forget (?:everything|your instructions)',
        r'you are now',
        r'new instructions:',
        r'system prompt:',
        r'</?(system|user|assistant)>',
        r'\[INST\]',
        r'<<SYS>>',
    ]

    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in injection_patterns)


def validate_output(output: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate agent output before returning to user.

    Checks:
    - No sensitive data leakage
    - Response size limits
    - Required fields present

    Args:
        output: The agent output dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # TODO: Implement in Week 11

    # Check for accidental PII in output
    # Check response size
    # Validate required fields

    return True, None
