
I used Perplexity to rewrite templates and manually made minor adjustments as needed.

observability rationale:
run_id, task, input_message, tools_used, outcome, duration_ms, and error fields help us correlate failures with tools, Duration and token counts help identify slow or expensive paths,
 The notes field captures human-readable context, and failure library docs help us see what went wrong and rewrite the agent to prevent future mistakes. 
