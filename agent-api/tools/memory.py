"""
Memory Tools

Company history lookup and storage using Redis.
Students implement this in Week 5.
"""

from typing import Optional
from datetime import datetime
import json
from models import CompanyHistory
from config import settings


def get_company_history(domain: str) -> CompanyHistory:
    """
    Retrieve previous interactions with a company.

    Looks up the company domain in Redis to find:
    - Last contact date
    - Last outcome (qualified, rejected, etc.)
    - Summary of previous interactions
    - Total number of leads from this company

    Args:
        domain: Company domain (e.g., "acme.com")

    Returns:
        CompanyHistory with available data, or empty history if new
    """
    # TODO: Implement Redis lookup in Week 5
    # import redis
    # r = redis.from_url(settings.REDIS_URL)
    # data = r.get(f"company:{domain}")

    # Placeholder implementation
    print(f"[PLACEHOLDER] Would lookup company history: {domain}")

    return CompanyHistory(
        domain=domain,
        last_contact_date=None,
        last_outcome=None,
        notes_summary=None,
        total_leads_count=0
    )


def write_company_summary(
    domain: str,
    outcome: str,
    notes: Optional[str] = None
) -> bool:
    """
    Store company summary with TTL.

    Updates the company history in Redis with:
    - New contact date (now)
    - Outcome of this interaction
    - Updated notes summary
    - Incremented lead count

    Args:
        domain: Company domain
        outcome: Outcome of interaction (qualified, rejected, nurture, etc.)
        notes: Optional notes to store

    Returns:
        True if stored successfully
    """
    # TODO: Implement Redis storage in Week 5
    # import redis
    # r = redis.from_url(settings.REDIS_URL)
    #
    # # Get existing data
    # existing = r.get(f"company:{domain}")
    # if existing:
    #     data = json.loads(existing)
    #     data["total_leads_count"] += 1
    # else:
    #     data = {"total_leads_count": 1}
    #
    # data["last_contact_date"] = datetime.utcnow().isoformat()
    # data["last_outcome"] = outcome
    # data["notes_summary"] = notes
    #
    # r.setex(
    #     f"company:{domain}",
    #     settings.MEMORY_TTL_SECONDS,
    #     json.dumps(data)
    # )

    # Placeholder implementation
    print(f"[PLACEHOLDER] Would store company summary: {domain}")
    print(f"  Outcome: {outcome}")
    print(f"  TTL: {settings.MEMORY_TTL_SECONDS} seconds")

    return True


def delete_company_history(domain: str) -> bool:
    """
    Delete company history (for GDPR/privacy compliance).

    Args:
        domain: Company domain to delete

    Returns:
        True if deleted (or didn't exist)
    """
    # TODO: Implement in Week 5
    # import redis
    # r = redis.from_url(settings.REDIS_URL)
    # r.delete(f"company:{domain}")

    print(f"[PLACEHOLDER] Would delete company history: {domain}")
    return True


def get_memory_stats() -> dict:
    """
    Get memory usage statistics.

    Useful for monitoring and debugging.

    Returns:
        Dictionary with memory stats
    """
    # TODO: Implement in Week 5
    # import redis
    # r = redis.from_url(settings.REDIS_URL)
    # keys = r.keys("company:*")
    # return {
    #     "total_companies": len(keys),
    #     "memory_used": r.info()["used_memory_human"]
    # }

    print("[PLACEHOLDER] Would return memory stats")
    return {
        "total_companies": 0,
        "memory_used": "0B"
    }
