from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from enum import Enum
from uuid import uuid4

class MessageType(str, Enum):
    EXTRACTION_REQ = "extraction_request"   # Client -> Agent
    VALIDATION_ACK = "validation_ack"       # Agent -> Client (Checkpoint 1)
    DENSITY_ALERT = "density_alert"         # Agent -> Client (Checkpoint 2)
    CALENDAR_SYNC = "calendar_sync"         # Client -> Agent (Checkpoint 3)

class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    msg_type: MessageType
    payload: Dict[str, Any]
    metadata: Dict[str, str] = {"version": "1.0.0", "model": "gemini-2-flash"}
