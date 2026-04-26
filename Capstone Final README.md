This is the list of steps to ensure the Syllabus Calendar Scheduling Agent works as intended.
#### Step 1:
ensure your private **Age key** is present at `~/.config/sops/age/keys.txt`.
#### Step 2:
open a terminal in engineer-track (the root folder of the project) and run `nix develop`.
#### Step 3:
Populate the `.env.example` with the appropriate keys. This includes the regular google API for gemini-2.5-flash as well as a Google Calendar Integration. 
#### Step 4:
Copy the keys over to the `agent-api/secrets.yaml` file.
#### Step 5:
Run `docker compose up --build`.
#### Step 6:
verify health using `curl http://localhost:8000/health`. Go to `http://127.0.0.1:8000/docs#/` in your browser.
#### Step 7:
Add the course ID and a syllabus to the `/syllabus` endpoint.
#### Step 8(Optional):
Use the `/calendar/{course_id}` endpoint to view the created schedule.
#### Step 9:
Approve the schedule to have it automatically added to your Google Calendar.
## Scenario 1: The "Happy Path" (Standard Syllabus)

**Scenario:** A student uploads a standard CS101 syllabus with clear dates.
**Input:**
```
curl -X POST http://localhost:8000/syllabus \
  -F "file=@eval/cases/CS101_syllabus.txt" \
  -F "course_code=CS101"
```
**Expected Output:**
```
{
  "status": "success",
  "message": "Syllabus for CS101 processed successfully.",
  "data": [
    {"event": "Quiz 1", "date": "2026-02-05", "type": "assignment"},
    {"event": "Midterm Exam", "date": "2026-03-12", "type": "exam"}
  ],
  "requires_human_review": false
}
```
**What to Highlight:**
- Agent correctly maps text strings to ISO dates.
- Automatic categorization of "quiz" vs "exam".
- `requires_human_review` is false, indicating high confidence.
## Scenario 2: Edge Case (Missing/Ambiguous Data)
**Scenario:** A syllabus lists a midterm but says the date is "TBD after Spring Break."
**Input:**
```
curl -X POST http://localhost:8000/syllabus \
  -F "file=@eval/cases/PHIL201_ambiguous.txt" \
  -F "course_code=PHIL201"
```
**Expected Output:**
```
{
  "status": "partial_success",
  "message": "Extracted 0 items. Some dates were ambiguous.",
  "data": [],
  "requires_human_review": true,
  "warnings": ["Midterm date 'TBD' could not be parsed."]
}
```
**What to Highlight:**
- **Human-in-the-Loop:** The `requires_human_review` flag triggers a UI warning (if applicable).
## Scenario 3: Guardrail Activation (Prompt Injection)
**Scenario:** A user tries to trick the AI into revealing internal system prompts or bypassing extraction.
**Input:**
```
curl -X POST http://localhost:8000/syllabus \
  -F "file=@eval/cases/injection_attempt.txt" \
  -F "course_code=HACK101"
```
**Expected Output:**
```
{
  "status": "error",
  "reason": "Security Policy Violation",
  "message": "Potential prompt injection detected in input text.",
  "blocked": true
}
```
**What to Highlight:**
- The system recognizes adversarial text that doesn't look like a syllabus.
- The LLM-based filter prevents the "Ignore all previous instructions" attack.
## Scenario 4: Complex Formatting (The "92/100" Stress Test)
**Scenario:** A very long syllabus with highly repetitive or dense data.
**Input:**
```
curl -X POST http://localhost:8000/syllabus \
  -F "file=@eval/cases/dense_syllabus.txt" \
  -F "course_code=ADV3"
```
**What to Highlight:**
- **Performance:** Observe the latency of the Gemini API call.
- **Accuracy:** Show the `Extracted X items` count to demonstrate how the agent handles token-heavy inputs.
## Scenario 5: Error Case (Invalid File/Empty Input)
**Scenario:** User uploads a corrupted file or an empty text document.
**Input:**
```
curl -X POST http://localhost:8000/syllabus \
  -F "file=@eval/cases/empty.txt" \
  -F "course_code=VOID"
```
**Expected Output:**
```
{
  "status": "error",
  "message": "No readable text found in syllabus file."
}
```
**What to Highlight:**
- Validation at the FastAPI layer before even calling the AI.
- Prevents unnecessary API costs by filtering junk input.
## Cleanup
````
docker compose down
````