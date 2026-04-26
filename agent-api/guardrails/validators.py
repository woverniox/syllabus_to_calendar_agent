"""
Syllabus Validation and Sanitization
Protects against malicious syllabus uploads and ensures extraction quality.
"""

import re
import yaml
from typing import Optional, Tuple, List

class ValidationResult:
    """Result of input validation."""
    def __init__(self, action: str = "ALLOW", response_override: str = None):
        self.action = action # ALLOW or BLOCK
        self.response_override = response_override

class GuardrailPipeline:
    """
    The main interface used by agent.py.
    Reads config from the .yaml file we created.
    """
    def __init__(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception:
            self.config = {}

    def check_input(self, text: str) -> ValidationResult:
        # Check for Prompt Injection
        if _contains_prompt_injection(text):
            return ValidationResult(
                action="BLOCK", 
                response_override="Security Alert: Potential prompt injection detected in document."
            )
        
        # Check for length (too short isn't a syllabus)
        if len(text) < 100:
            return ValidationResult(
                action="BLOCK",
                response_override="Error: The uploaded document is too short to be a valid syllabus."
            )

        return ValidationResult(action="ALLOW")

    def check_output(self, user_input: str, agent_output: any) -> ValidationResult:
        """Strategy 2: Validate the AI didn't hallucinate 'party' dates."""
        if "party" in str(agent_output).lower():
            return ValidationResult(action="BLOCK", response_override="Sanitization: AI attempted to include non-academic events.")
        return ValidationResult(action="ALLOW")


def _contains_prompt_injection(text: str) -> bool:
    """Strategy 2: Detect attempts to hijack the Agent."""
    injection_patterns = [
        r'ignore (?:previous|above|all) instructions',
        r'disregard (?:previous|above|all)',
        r'system prompt:',
        r'you are now an administrator',
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in injection_patterns)

def sanitize_syllabus_text(text: str) -> str:
    """Clean up PDF artifacts."""
    if not text: return ""
    # Remove null bytes and control chars
    sanitized = sanitized = text.replace('\x00', '')
    sanitized = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
    return sanitized.strip()
