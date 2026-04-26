#!/usr/bin/env python
# coding: utf-8

# In[5]:


import json
from datetime import datetime
from typing import Any

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
    # In your agent's main loop:
    from syllabus_guardrails import GuardrailPipeline, GuardrailAction

    # Initialize guardrail system
    pipeline = GuardrailPipeline('config/syllabus-guardrails-v1.yaml')

    def process_message(user_input: str, context: dict) -> str:
      """
      Main loop for the Syllabus Scheduling Agent.
      Handles syllabus uploads, schedule creation, approval, and calendar sync
      while enforcing all guardrails.
      """

      # Step 1: Validate the user's input
      input_result = pipeline.check_input(user_input)
      if input_result.action in [GuardrailAction.BLOCK, GuardrailAction.PROMPT_RESUBMISSION]:
          return input_result.response_override

      # Step 2: Run the agent’s primary logic (e.g., syllabus parsing or schedule generation)
      agent_output = agent.run(user_input, context)

      # Step 3: Determine if the current action requires user approval
      if context.get('pending_action'):
          action_result = pipeline.check_action(context['pending_action'], context)
          if action_result.action == GuardrailAction.REQUIRE_APPROVAL:
              return (
                  f"Before I continue, this step requires your approval: "
                  f"{action_result.reason}. Do you approve?"
              )

    # Step 4: Verify that output does not trigger any hard blocks (e.g. unauthorized file or calendar change)
    output_result = pipeline.check_output(user_input, agent_output)
    if output_result.action == GuardrailAction.BLOCK:
        return output_result.response_override

    # Step 5: Deliver the approved schedule or sync confirmation to the user
    return agent_output


if __name__ == "__main__":
    agent = SimpleAgent("Find information about AI agents")
    result = agent.run()
    print(json.dumps(result, indent=2, default=str))



# In[6]:




# In[ ]:




