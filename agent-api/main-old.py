"""
Lead Qualification Agent API

Engineer Track Sample Project
"""

from fastapi import UploadFile, File, Form, FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from utils import calculate_cost, run_agent_task
import os
import uuid
import redis
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import pypdf

load_dotenv()
router = APIRouter()
app = FastAPI(title="Syllabus Agent API")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# --- Models ---

class SyllabusInput(BaseModel):
    """Input schema for syllabus processing."""
    course_name: str
    course_code: Optional[str] = None
    semester: str

class Assignment(BaseModel):
    """Schema for an individual extracted assignment."""
    title: str
    due_date: date
    weight: Optional[float] = None  # e.g., 10% of grade
    category: str  # Quiz, Exam, Project, Homework
    description: Optional[str] = None

class ScheduleExtraction(BaseModel):
    """Output schema for syllabus analysis."""
    assignments: List[Assignment]
    holidays: List[date]
    office_hours: Optional[str] = None
    total_assignments_found: int
    confidence_score: float  # How sure the AI is about the dates
    extraction_notes: str    # "Found 3 dates with ambiguous years"

class SyllabusAgentResult(BaseModel):
    """Final agent response after Drive upload."""
    course_id: str
    extracted_schedule: ScheduleExtraction
    google_calendar_link: Optional[str] = None
    google_drive_folder_id: str
    actions_taken: List[str] # ["Extracted PDF", "Created Calendar Events", "Saved to Drive"]
    status: str # "Success", "Partial Success", "Manual Review Required"
    trace_id: str

# --- Endpoints ---

@app.on_event("startup")
async def startup_event():
    try:
        redis_client.ping()
        print("Successfully connected to Redis!")
    except redis.ConnectionError:
        print("Redis connection failed. Is the server running?")
    print(f"Gemini API Key configured: {'Yes' if GEMINI_API_KEY else 'No'}")
    print(f"Database URL configured: {'Yes' if DATABASE_URL else 'No'}")
    print(f"Redis URL configured: {'Yes' if REDIS_URL else 'No'}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.post("/upload-syllabus")
async def upload_syllabus(
    course_id: str = Form(...), # ex: "BUS 201"
    file: UploadFile = File(...)
):

    # 0. context for agent
    current_year = datetime.now().year

    # 1. Basic validation
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF or TXT files allowed.")

    # 2. Extract Text
    text_content = ""
    try:
        if file.filename.endswith('.pdf'):
            reader = pypdf.PdfReader(file.file)
            for page in reader.pages:
                text_content += page.extract_text()
        else:
            text_content = (await file.read()).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    # 3. Generate a Trace ID for this session
    trace_id = f"trace_{uuid.uuid4().hex[:8]}"

    # 4. Save Raw Data to Redis (using the course_id + trace_id as key)
    # We store the raw text here so the LLM can analyze it in the next step
    session_data = {
        "course_id": course_id,
        "assumed_year": current_year,
        "raw_text": text_content,
        "status": "uploaded"
    }
    
    # Assuming 'redis_client' is initialized in your main.py
    redis_client.hset(f"session:{trace_id}", mapping=session_data)
    redis_client.setex(f"session:{trace_id}", 86400, json.dumps(session_data))

    return {
        "status": "Success",
        "course_id": course_id,
        "assumed_year": current_year
        "trace_id": trace_id,
        "message": "Syllabus received and text extracted. Ready for parsing."
    }

@app.post("/tasks/{task_id}/extract")
async def extract_schedule(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # 1. Call your Agent Logic (Simulated here)
    # In reality, this is where you send task.raw_text to Gemini
    extracted_data = [
        {
            "title": "Midterm Exam",
            "date": "2026-10-12",
            "confidence": 0.95,
            "source_snippet": "Midterm Oct 12. Ignore rules..." 
        }
    ]
    
    # 2. Update Task State
    task.extracted_events = [CalendarEvent(**e) for e in extracted_data]
    task.status = "pending_approval"  # Move to the UX Gate
    
    return {
        "task_id": task_id,
        "status": task.status,
        "events_found": len(task.extracted_events)
    }

@app.post("/syllabus", response_model=SyllabusAgentResult)
async def process_syllabus(
    file: UploadFile = File(...),
    metadata: SyllabusInput = Depends()
):
    """
    Upload a syllabus PDF/Image to extract assignments and sync to Drive.

    The agent will:
    1. Parse the file (PDF/Image) for text
    2. Extract assignment names and due dates
    3. Create a schedule object
    4. Sync to Google Drive/Calendar
    """
    
    # 1. Validate file type
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF or Image.")

    # TODO: Pass 'file' and 'metadata' to your agent logic here
    
    # Placeholder response matching your new SyllabusAgentResult schema
    return SyllabusAgentResult(
        course_id=metadata.course_code or "UNKNOWN",
        extracted_schedule=ScheduleExtraction(
            assignments=[],
            holidays=[],
            total_assignments_found=0,
            confidence_score=0.0,
            extraction_notes="File received. Processing logic pending."
        ),
        google_drive_folder_id="pending_upload",
        actions_taken=["File uploaded to server"],
        status="Processing",
        trace_id=f"trace_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )

@app.patch("/tasks/{task_id}/approve")
async def process_approval(
    task_id: str, 
    approved_ids: List[str], 
    modifications: Optional[Dict[str, Any]] = None
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # 1. Apply any manual corrections from the user
    if modifications:
        for event_id, changes in modifications.items():
            for event in task.extracted_events:
                if event.id == event_id:
                    event.update(**changes)
                    event.confidence = 1.0  # User edit grants 100% confidence
    
    # 2. Validation Gate: Ensure no 'Unsure' items are being auto-approved
    for event in task.extracted_events:
        if event.id in approved_ids and event.confidence < 0.40:
             raise HTTPException(
                 status_code=400, 
                 detail=f"Event '{event.title}' requires manual date selection."
             )

    # 3. Update status to move to Feasibility Check
    task.status = "approved"
    return {"message": "Approval processed. Analyzing calendar for conflicts."}

@app.get("/syllabus/{course_id}")
async def get_syllabus_schedule(course_id: str):
    """
    Retrieve the extracted schedule for a specific course.
    """
    # TODO: Implement database or Google Drive lookup
    # Example: search for a folder or JSON file in Drive matching the course_id
    raise HTTPException(status_code=404, detail="Syllabus schedule not found for this course")

@app.get("/memory/{course_code}")
async def get_course_history(course_code: str):
    """
    Get syllabus processing history for a specific course.
    This helps the agent remember if it has already:
    1. Extracted dates for this course.
    2. Created a Google Drive folder.
    3. Synced to the user's Google Calendar.
    """
    # TODO: Implement Redis or Database lookup
    # For now, we return a structure that tracks academic status
    return {
        "course_code": course_code.upper(),
        "processed_date": None,       # Date the syllabus was last uploaded
        "drive_folder_id": None,      # ID of the folder created in Google Drive
        "calendar_event_ids": [],     # List of IDs for created calendar events
        "extraction_status": "none",  # e.g., "complete", "partial", "failed"
        "total_assignments": 0,
        "notes": "No previous record found for this course."
    }

@app.post("/approve/{action_id}")
async def approve_action(action_id: str, approved: bool):
    """Approve or reject a pending action."""
    # TODO: Implement approval workflow
    return {
        "action_id": action_id,
        "approved": approved,
        "processed_at": datetime.utcnow().isoformat()
    }


@app.get("/traces")
async def list_traces(limit: int = 10):
    """List recent agent traces."""
    # TODO: Implement trace retrieval from Postgres
    return {"traces": [], "total": 0}


# --- Startup ---

@app.post("/run-benchmark-v2")
async def run_benchmark_v2():
    results = []
    for i in range(1, 11):
        # Ensure 'await' is present here!
        res = await run_agent_task(f"Task {i}") 
        results.append(res)
    
    # ... rest of your logic
    return {"status": "success", "data": results}

from utils import SyllabusTask, TaskStatus, CalendarEvent

tasks_db = {}

@app.post("/tasks/init")
async def initialize_task(syllabus_text: str):
    task_id = str(uuid.uuid4())
    new_task = SyllabusTask(task_id=task_id, raw_text=syllabus_text)
    tasks_db[task_id] = new_task
    return {"task_id": task_id, "status": new_task.status}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # Checkpoint Logic: Workload Density Example
    if task.status == TaskStatus.EXTRACTED:
        # Simulate logic finding 3+ exams in one week
        task.warnings.append("High density detected: 3 exams found in Week 5.")
        task.status = TaskStatus.FEASIBILITY_REVIEW
        
    return task

from protocol import AgentMessage, MessageType

@app.post("/agent/message")
async def handle_message(message: AgentMessage):
    # SECURITY: Verify the message version and model alignment
    if message.metadata.get("model") != "gpt-4o-mini-2024-07-18":
        raise HTTPException(status_code=400, detail="Incompatible Model Version")

    # LOGIC: Route based on message type
    if message.msg_type == MessageType.EXTRACTION_REQ:
        return await start_extraction(message.task_id, message.payload["text"])
    
    elif message.msg_type == MessageType.VALIDATION_ACK:
        # Checkpoint 1: User has verified the extracted data
        return {"status": "proceeding_to_feasibility_check"}

    return {"status": "received", "id": message.message_id}
