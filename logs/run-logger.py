import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
import csv
 
@dataclass
class RunLog:
    run_id: str
    timestamp: str
    task: str
    input_message: str
    tools_used: List[str]
    outcome: str  # success, failure, partial
    duration_ms: int
    tokens_used: int
    error: Optional[str]
    notes: str
 
class RunLogger:
    def __init__(self, log_path: str = "logs/run_log_v1.json"):
        self.log_path = log_path
        self.runs: List[RunLog] = []
 
    def log_run(self, run: RunLog):
        self.runs.append(run)
        self._save()
 
    def _save(self):
        with open(self.log_path, 'w') as f:
            json.dump([asdict(r) for r in self.runs], f, indent=2)
 
    def export_csv(self, csv_path: str = "logs/run_log_v1.csv"):
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'run_id', 'timestamp', 'task', 'tools_used',
                'outcome', 'duration_ms', 'tokens_used', 'error', 'notes'
            ])
            writer.writeheader()
            for run in self.runs:
                row = asdict(run)
                row['tools_used'] = ', '.join(run.tools_used)
                writer.writerow(row)
 
    def get_summary(self) -> dict:
        total = len(self.runs)
        successes = sum(1 for r in self.runs if r.outcome == 'success')
        failures = sum(1 for r in self.runs if r.outcome == 'failure')
 
        return {
            'total_runs': total,
            'success_rate': round(successes / total * 100, 1) if total > 0 else 0,
            'failures': failures,
            'avg_duration_ms': sum(r.duration_ms for r in self.runs) // total if total > 0 else 0,
            'total_tokens': sum(r.tokens_used for r in self.runs)
        }
