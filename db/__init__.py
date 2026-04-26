"""
Database Module

Database connections and operations for the Lead Qualification Agent.
Students implement these in Week 4-5.

Components:
- postgres.py: Trace logging and persistent storage
- redis.py: Memory/cache with TTL
"""

from .postgres import (
    get_db_connection,
    log_trace,
    get_traces,
    init_database
)
from .redis import (
    get_redis_connection,
    cache_get,
    cache_set,
    cache_delete
)

__all__ = [
    # Postgres
    "get_db_connection",
    "log_trace",
    "get_traces",
    "init_database",
    # Redis
    "get_redis_connection",
    "cache_get",
    "cache_set",
    "cache_delete",
]
