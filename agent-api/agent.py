#!/usr/bin/env python
# coding: utf-8

# In[5]:


import json
from datetime import datetime
from typing import Any
# agent.py
import os
from google import genai

# Grab from the environment variable we set in Docker
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment!")

client = genai.Client(api_key=api_key)

class SimpleAgent:
    def __init__(self, task: str, max_steps: int = 10):
        self.task = task
        self.max_steps = max_steps
        self.memory = {
            "task": task,
            "history": [],
            "context": {},
            "status": "running"
        }
        self.tools = self._register_tools()

    def _register_tools(self) -> dict:
        """Register available tools."""
        return {
            "search": self._tool_search,
            "calculate": self._tool_calculate,
            "respond": self._tool_respond
        }

    def _tool_search(self, query: str) -> dict:
        """Simulated search tool."""
        return {"results": [f"Result for: {query}"], "count": 1}

    def _tool_calculate(self, expression: str) -> dict:
        """Simple calculator tool."""
        try:
            result = eval(expression)  # In production: use safe_eval
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e)}

    def _tool_respond(self, message: str) -> dict:
        """Final response tool - signals completion."""
        self.memory["status"] = "complete"
        return {"response": message, "final": True}

    def observe(self) -> dict:
        """Phase 1: Gather context from memory and environment."""
        observation = {
            "task": self.task,
            "steps_taken": len(self.memory["history"]),
            "steps_remaining": self.max_steps - len(self.memory["history"]),
            "last_action": self.memory["history"][-1] if self.memory["history"] else None
        }
        return observation

    def decide(self, observation: dict) -> dict:
        """Phase 2: Choose next action based on observation."""
        # Simple decision logic (replace with LLM in production)
        if observation["steps_taken"] == 0:
            return {"tool": "search", "args": {"query": self.task}}
        elif observation["steps_taken"] < 3:
            return {"tool": "calculate", "args": {"expression": "1+1"}}
        else:
            return {"tool": "respond", "args": {"message": f"Completed: {self.task}"}}

    def act(self, decision: dict) -> dict:
        """Phase 3: Execute the decided action."""
        tool_name = decision["tool"]
        tool_args = decision["args"]

        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        result = self.tools[tool_name](**tool_args)
        return result

    def run(self) -> dict:
        """Main agent loop: observe → decide → act → check."""
        for step in range(self.max_steps):
            # Phase 1: Observe
            observation = self.observe()

            # Phase 2: Decide
            decision = self.decide(observation)

            # Phase 3: Act
            result = self.act(decision)

            # Log to history
            self.memory["history"].append({
                "step": step + 1,
                "timestamp": datetime.now().isoformat(),
                "observation": observation,
                "decision": decision,
                "result": result
            })

            # Phase 4: Check stop condition
            if self.memory["status"] == "complete":
                break

        return self.memory

import json
from guardrails.validators import GuardrailPipeline  # <--- MUST BE HERE
from guardrails.approvals import check_syllabus_approval, request_approval

# Initialize guardrail system
pipeline = GuardrailPipeline('guardrails/syllabus-guardrails-v1.yaml')

# --- Mock Guardrails (Ensures the app boots without missing files) ---
class GuardrailAction:
    BLOCK = "block"
    PROMPT_RESUBMISSION = "resubmit"
    REQUIRE_APPROVAL = "require_approval"
    ALLOW = "allow"

class GuardrailResult:
    def __init__(self, action=GuardrailAction.ALLOW, response_override=None, reason=None):
        self.action = action
        self.response_override = response_override
        self.reason = reason

def process_message(user_input: str, context: dict) -> str:
    # 1. Initialize Pipeline (Strategy 2)
    # This now works because GuardrailPipeline is defined in validators.py
    pipeline = GuardrailPipeline('config/syllabus-guardrails-v1.yaml')

    # 2. Safety Gate
    input_result = pipeline.check_input(user_input)
    if input_result.action == "BLOCK":
        return input_result.response_override

    # 3. Execution
    # We pass the user_input (syllabus text) to our Agent
    agent_instance = SimpleAgent(user_input)
    agent_output = agent_instance.run()

    # 4. Approval Gate (Checkpoint 1)
    # We simulate a confidence score here - in real use, this comes from the LLM
    gate_check = check_syllabus_approval("verify_extraction", {"confidence_score": 0.5})
    
    if gate_check.required:
        # Create a tracking ID for the manual review
        request_id = request_approval("LOW_CONFIDENCE", "task_99", gate_check.reason, agent_output)
        return f"STATUS: REVIEW_REQUIRED\nReason: {gate_check.reason}\nID: {request_id}"

    return json.dumps(agent_output)

# --- API Bridge ---

# agent.py

async def call_gemini_extraction(raw_text: str, course_code: str = None):
    try:
        # 1. Call Gemini 
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"Extract all assignments, exams, and deadlines for {course_code}. "
                f"Return as a JSON list of objects with 'title', 'date' (YYYY-MM-DD), 'type', and 'confidence'.\n\n"
                f"Syllabus Text: {raw_text}"
            ),
            config={'response_mime_type': 'application/json'}
        )
        
        if not response or not hasattr(response, 'text'):
            print("DEBUG: No response text found from Gemini")
            return []
        
        # 2. Clean up and Parse
        # Using a unique variable name 'extracted_data' to avoid shadowing the 'json' module
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        
        try:
            extracted_data = json.loads(clean_text)
            
            # Ensure we return a list, even if Gemini returns a single object or dict
            if isinstance(extracted_data, dict):
                # If Gemini wrapped it in a key like {"events": [...]}, extract the list
                if "events" in extracted_data:
                    return extracted_data["events"]
                if "assignments" in extracted_data:
                    return extracted_data["assignments"]
                return [extracted_data] # Wrap single object in list
            
            return extracted_data if isinstance(extracted_data, list) else []

        except json.JSONDecodeError as e:
            print(f"CRITICAL JSON ERROR: Failed to decode AI output: {e}")
            return []

    except Exception as e:
        print(f"CRITICAL AI ERROR: {str(e)}")
        return []

def sort_and_summarize(events: list):
    if not events:
        return "No events found."

    # Sort events by date
    # Assumes 'date' is in 'YYYY-MM-DD' or a parseable format
    try:
        events.sort(key=lambda x: x.get('date', '9999-12-31'))
    except Exception as e:
        print(f"Sorting failed: {e}")

    summary = "\n--- EXTRACTED SCHEDULE ---\n"
    for i, event in enumerate(events, 1):
        summary += f"{i}. [{event.get('date')}] {event.get('title')} ({event.get('type')})\n"
    
    summary += "\nDoes this schedule look correct? (Acceptable: Yes/No)"
    return summary
