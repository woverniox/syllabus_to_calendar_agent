"""
PostgreSQL Database Operations

Trace logging and persistent storage.
Students implement this in Week 4.
"""

from typing import Optional, List
from datetime import datetime
import json
from config import settings


# Database connection placeholder
_connection = None


async def get_db_connection():
    """
    Get a database connection.

    TODO: Implement in Week 4 using asyncpg or SQLAlchemy.
    """
    global _connection

    # Placeholder - implement actual connection
    # import asyncpg
    # if _connection is None:
    #     _connection = await asyncpg.connect(settings.DATABASE_URL)
    # return _connection

    print("[PLACEHOLDER] Would connect to PostgreSQL")
    return None


async def init_database():
    """
    Initialize database schema.

    Creates tables if they don't exist.
    See /db/init.sql for the schema.
    """
    # TODO: Implement in Week 4
    # conn = await get_db_connection()
    # await conn.execute(open('db/init.sql').read())

    print("[PLACEHOLDER] Would initialize database schema")


async def log_trace(
    trace_id: str,
    lead_key: str,
    input_data: dict,
    score_result: Optional[dict] = None,
    actions_taken: List[str] = None,
    approval_required: bool = False,
    approval_reason: Optional[str] = None,
    error: Optional[str] = None,
    token_usage: Optional[dict] = None
) -> bool:
    """
    Log an agent execution trace.

    Traces are used for:
    - Debugging agent behavior
    - Running evaluations
    - Cost tracking (Week 10)
    - Audit trail

    Args:
        trace_id: Unique trace identifier
        lead_key: The lead being processed
        input_data: Original input
        score_result: Scoring output
        actions_taken: List of actions performed
        approval_required: Whether approval was needed
        approval_reason: Why approval was needed
        error: Any error that occurred
        token_usage: LLM token usage for cost tracking

    Returns:
        True if logged successfully
    """
    trace = {
        "trace_id": trace_id,
        "lead_key": lead_key,
        "started_at": datetime.utcnow().isoformat(),
        "input_data": input_data,
        "score_result": score_result,
        "actions_taken": actions_taken or [],
        "approval_required": approval_required,
        "approval_reason": approval_reason,
        "error": error,
        "token_usage": token_usage,
    }

    # TODO: Implement in Week 4
    # conn = await get_db_connection()
    # await conn.execute("""
    #     INSERT INTO traces (trace_id, lead_key, data, created_at)
    #     VALUES ($1, $2, $3, NOW())
    # """, trace_id, lead_key, json.dumps(trace))

    print(f"[PLACEHOLDER] Would log trace: {trace_id}")
    return True


async def get_traces(
    lead_key: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    """
    Retrieve agent execution traces.

    Args:
        lead_key: Optional filter by lead
        limit: Maximum number of traces
        offset: Pagination offset

    Returns:
        List of trace dictionaries
    """
    # TODO: Implement in Week 4
    # conn = await get_db_connection()
    # if lead_key:
    #     rows = await conn.fetch("""
    #         SELECT * FROM traces
    #         WHERE lead_key = $1
    #         ORDER BY created_at DESC
    #         LIMIT $2 OFFSET $3
    #     """, lead_key, limit, offset)
    # else:
    #     rows = await conn.fetch("""
    #         SELECT * FROM traces
    #         ORDER BY created_at DESC
    #         LIMIT $1 OFFSET $2
    #     """, limit, offset)
    # return [dict(row) for row in rows]

    print(f"[PLACEHOLDER] Would retrieve traces (limit={limit})")
    return []


async def get_trace_by_id(trace_id: str) -> Optional[dict]:
    """
    Get a specific trace by ID.

    Args:
        trace_id: The trace identifier

    Returns:
        Trace dictionary or None
    """
    # TODO: Implement in Week 4
    print(f"[PLACEHOLDER] Would retrieve trace: {trace_id}")
    return None
