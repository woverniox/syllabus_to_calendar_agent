"""
Pydantic Models

Data models for the Lead Qualification Agent.
These define the schema for inputs, outputs, and internal data structures.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from uuid import uuid4

# --- Enums ---

class ExtractionStatus(str, Enum):
    """
    Replaces 'Tier'.
    Defines the lifecycle of an extracted event.
    """
    REJECTED = "rejected"      # User explicitly deleted the event
    UNCERTAIN = "uncertain"    # Missing critical data (needs manual input)
    PENDING = "pending"        # Extracted but awaiting user approval
    VERIFIED = "verified"      # Approved and ready for calendar sync


class SyllabusComplexity(str, Enum):
    """
    Replaces 'Segment'.
    Categorizes the document based on length and structure.
    """
    STANDARD = "standard"      # Simple table or list structure
    DENSE = "dense"            # Heavy prose/nested schedules (requires pre-filtering)


class ConfidenceLevel(str, Enum):
    """
    The agent's self-assessment of the extraction accuracy.
    Directly tied to the UI badges (Red, Yellow, Green).
    """
    LOW = "low"                # Score < 40: High hallucination risk
    MEDIUM = "medium"          # Score 40-69: Missing time or slight ambiguity
    HIGH = "high"              # Score 70+: Clear date/title match

# --- Input Models ---

class CalendarEvent(BaseModel):
    """Individual assignment or exam extracted from the text."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    event_date: date
    event_time: Optional[str] = None
    confidence: ConfidenceLevel
    status: ExtractionStatus = ExtractionStatus.PENDING
    source_snippet: str = Field(..., description="The original text used for extraction")
    raw_score: float = Field(..., ge=0, le=100)

class ApprovalUpdate(BaseModel):
    """
    Schema for the user's feedback via the PATCH endpoint.
    Allows for bulk approval, rejection, and granular field edits.
    """
    approved_event_ids: List[str] = []
    rejected_event_ids: List[str] = []
    # Modifications map: { "event_id": { "title": "New Title", "event_date": "2026-10-15" } }
    modifications: Optional[Dict[str, Dict[str, Any]]] = None

# --- Output Models ---

class SyllabusTask(BaseModel):
    """The main container for a syllabus processing job."""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    upload_time: datetime = Field(default_factory=datetime.now)
    
    # Metadata for filtering & quota management
    complexity: SyllabusComplexity = SyllabusComplexity.STANDARD
    raw_text_length: int
    
    # The actual data
    events: List[CalendarEvent] = []
    
    # Workflow state
    is_processed: bool = False
    requires_human_review: bool = False  # True if any event is ConfidenceLevel.LOW
    
    class Config:
        use_enum_values = True

# --- Memory Models ---

class CourseHistory(BaseModel):
    """
    Academic context from long-term memory.
    Helps the agent resolve ambiguous dates by looking at past patterns.
    """
    course_code: str  # e.g., "CS-101"
    professor_name: Optional[str] = None
    semester: str     # e.g., "Fall 2026"
    
    last_processed_date: Optional[datetime] = Field(default_factory=datetime.now)
    total_events_extracted: int = 0
    
    # Metadata for better parsing
    common_deadlines: List[str] = Field(
        default=[], 
        description="Common recurring days, e.g., 'Every Sunday at Midnight'"
    )
    
    parsing_notes: Optional[str] = Field(
        None, 
        description="Internal notes like 'Prof uses relative dates for labs'"
    )
    
    average_confidence_score: float = 0.0

# --- Database Models ---

class EventRow(BaseModel):
    """
    Finalized event record for database or CSV storage.
    Replaces 'LeadRow'.
    """
    event_id: str = Field(..., description="Unique ID for the extracted assignment")
    course_code: str
    title: str
    event_date: datetime
    event_time: Optional[str] = None
    
    # Classification (Replacing Score/Tier/Segment)
    confidence_score: float
    confidence_level: str  # high, medium, low
    category: str          # exam, quiz, assignment, lab
    
    # Metadata
    source_syllabus: str   # filename or task_id reference
    is_synced: bool = False
    google_calendar_id: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    status: str = "new"    # new, pending_approval, synced, archived
    notes: Optional[str] = None


class TraceRecord(BaseModel):
    """
    Agent execution trace for debugging and evaluation.
    Vital for tracking 429 errors and extraction accuracy.
    """
    trace_id: str
    task_id: str           # Links back to the SyllabusTask
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    input_text_snippet: str # The chunk of syllabus sent to the LLM
    extraction_results: Optional[List[dict]] = None
    
    # Performance Metrics
    actions_taken: List[str] = [] # e.g., ["pre_filter", "gemini_call", "human_approval_trigger"]
    approval_required: bool = False
    approval_reason: Optional[str] = None # e.g., "Confidence below threshold"
    
    # Quota & Error Tracking
    error_log: Optional[str] = None      # Captures 429 Resource Exhausted errors
    token_usage: Optional[Dict[str, int]] = None # Tracks prompt vs completion tokens

# --- Approval Models ---

class ApprovalUpdate(BaseModel):
    """
    Schema for the user feedback via PATCH /tasks/{task_id}/approve.
    Used to commit the 'Human-in-the-Loop' decisions to the final calendar.
    """
    approved_event_ids: List[str] = Field(
        default_factory=list, 
        description="List of UUIDs the user has verified as correct."
    )
    rejected_event_ids: List[str] = Field(
        default_factory=list, 
        description="List of UUIDs the user wants to discard."
    )
    # modifications example: { "uuid-123": { "event_date": "2026-12-01", "event_time": "11:59 PM" } }
    modifications: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None, 
        description="Granular overrides for specific event fields."
    )
