import os
import uuid
import json
import redis
import pypdf
from google import genai
from datetime import datetime, date
from typing import List, Optional, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# Import your custom architecture
from models import SyllabusTask, CalendarEvent, ApprovalUpdate, ExtractionStatus, SyllabusComplexity
from utils import pre_filter_syllabus, format_schedule_as_text, extract_text_from_pdf
from agent import call_gemini_extraction  # Assuming this exists in agent.py
# Import the actual logic/data from the specific files
from models import SyllabusComplexity
from guardrails.approvals import CONFIDENCE_THRESHOLDS, sort_and_summarize # Add it here
from integrations.calendar_service import add_event_to_calendar

load_dotenv()

# --- CONFIG ---
MODEL_ID = "gemini-2.5-flash"
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
client = genai.Client()
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

app = FastAPI(title="Syllabus to Calendar Agent")

# task catalog
active_schedules: Dict[str, dict] = {}


# --- SCHEMAS ---
class Assignment(BaseModel):
    title: str
    due_date: date
    category: str
    description: Optional[str] = None

class ApprovalRequest(BaseModel):
    trace_id: str
    approved: bool

# --- UTILS ---
async def extract_text_from_pdf(file) -> str:
    """Uses pypdf to extract raw text."""
    if file.content_type == "application/pdf":
        reader = pypdf.PdfReader(file.file)
        return "\n".join([p.extract_text() for p in reader.pages])
    return (await file.read()).decode("utf-8")

def format_schedule_as_text(events: List[CalendarEvent]) -> str:
    """Uses the models to create a summary for the user."""
    lines = ["\n--- EXTRACTED SCHEDULE ---"]
    for i, e in enumerate(events, 1):
        badge = "🟢" if e.confidence == "high" else "🟡" if e.confidence == "medium" else "🔴"
        lines.append(f"{i}. {badge} {e.event_date} | {e.title}")
    return "\n".join(lines)

# --- ENDPOINTS ---

# syllabus intake and parsing
# Ensure this dictionary is defined at the top of main.py
# active_schedules = {}

@app.post("/syllabus", response_model=dict)
async def process_syllabus(
    file: UploadFile = File(...),
    course_code: str = Form(...)
):
    """
    Endpoint 1: Extract text, filter noise, run AI extraction, and store result.
    """ 
    # 1. Text Extraction
    try:
        raw_text = await extract_text_from_pdf(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF Extraction Failed: {e}")

    # 2. Complexity Assessment & Filtering
    STANDARD_MAX_CHARS = 10000 
    # --- FIX: Use lowercase strings to match the Enum expectations ---
    complexity = (
        "dense" if len(raw_text) > STANDARD_MAX_CHARS else "standard"
    )
    
    # 3. Create the Task Object
    filtered_text = pre_filter_syllabus(raw_text)

    # Ensure we are dealing with a string before calling len()
    text_to_measure = filtered_text if isinstance(filtered_text, str) else ""
    
    print(f"DEBUG [Step 1]: Raw text extracted length: {len(raw_text)}")
    print(f"DEBUG [Step 3]: Filtered text length: {len(text_to_measure)}")

    # If the filter returned False or an empty string, fallback to raw_text
    if not filtered_text or len(text_to_measure) == 0:
        print("WARNING: Filtered text invalid or empty. Falling back to raw_text.")
        filtered_text = raw_text

    # ----------------------

    task = SyllabusTask(
        filename=file.filename,
        complexity=complexity,
        raw_text_length=len(raw_text)
    )

    # 4. AI Extraction

    try:
        # Use the course_code to provide context to Gemini
        events = await call_gemini_extraction(filtered_text, course_code)
        
        print(f"DEBUG [Step 4]: AI found {len(events)} events.")
        task.events = events
        task.is_processed = True
        formatted_summary = sort_and_summarize(events)
        
        # Check if human review is needed
        task.requires_human_review = any(
            getattr(e, 'confidence', 'high') == "low" for e in events
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Extraction Error: {e}")

    # 5. Storage Logic 
    # We use .upper() and strip spaces to ensure consistent keys
    storage_key = course_code.strip().upper()
    
    active_schedules[storage_key] = {
        "course": storage_key,
        "events": events,
        "processed_at": datetime.now().isoformat(),
        "task_id": task.task_id
    }

    # 6. Final Return (ONLY ONE RETURN ALLOWED)
    return {
        "message": f"Syllabus for {storage_key} processed.",
        "view_url": f"/calendar/{storage_key}",
        "task_id": task.task_id,
        "requires_review": task.requires_human_review,
        "review_summary": formatted_summary,
        "data": events 
    }

# calendar view
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/calendar/{course_id}")
async def get_course_calendar(course_id: str):
    """
    Retrieves the pre-processed JSON schedule from memory.
    """
    # Normalize the key to match how /syllabus stores it (Upper, stripped)
    storage_key = course_id.strip().upper()
    
    # Look up the JSON in your global dictionary
    data = active_schedules.get(storage_key)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"Calendar for {course_id} not found. Please upload the syllabus first."
        )

    # Return the JSON schedule
    return {
        "course": data.get("course"),
        "last_updated": data.get("processed_at"),
        "events": data.get("events")  # This is the JSON list Gemini created
    }

# calendar commit
@app.patch("/calendar/commit/{course_code}")
async def commit_to_calendar(course_code: str, approved: bool = Body(..., embed=True)):
    """
    Final User-in-the-loop approval. 
    If approved, it syncs the stored JSON from active_schedules to Google Calendar.
    """
    storage_key = course_code.strip().upper()
    
    # 1. Retrieve the processed data from your memory store
    data = active_schedules.get(storage_key)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No processed syllabus found for {course_code}. Run /syllabus first."
        )

    if not approved:
        # Cleanup if rejected
        del active_schedules[storage_key]
        return {"status": "REJECTED", "message": "Data cleared. Please re-upload with fixes."}

    # 2. Extract events
    events = data.get("events", [])
    if not events:
        return {"status": "SKIPPED", "message": "No events found to sync."}

    # 3. Trigger Google Calendar Sync
    synced_links = []
    try:
        for event in events:
            # We use the helper function from your utils
            link = add_event_to_calendar(
                summary=f"[{storage_key}] {event.get('title')}",
                date_str=event.get('date'),  # Expects YYYY-MM-DD
                description=f"Type: {event.get('type')}"
            )
            synced_links.append(link)
    except Exception as e:
        print(f"Google Calendar Sync Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calendar sync failed. Is Google API configured? Error: {str(e)}"
        )

    # 4. Success - Clear memory or mark as synced
    data["synced"] = True
    
    return {
        "status": "SUCCESS",
        "course": storage_key,
        "synced_count": len(synced_links),
        "links": synced_links
    }

