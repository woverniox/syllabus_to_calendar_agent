import json
import time
import sys
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Callable
from datetime import datetime
from enum import Enum

# --- 1. CONFIGURATION & IMPORTS ---
# Add the agent-api directory to the path so Python can find main.py
sys.path.append(os.path.abspath("../agent-api"))

# Try to import real logic; fallback to mock if main.py isn't ready
try:
    from main import extract_and_parse_logic
except ImportError:
    def extract_and_parse_logic(input_data):
        return {"events": [{"title": "Midterm", "date": "2025-10-15"}]}

# --- 2. MODELS ---
class TestCategory(Enum):
    HAPPY_PATH = "happy_path"
    YEAR_ROLLOVER = "year_rollover"
    TIMEZONE_SHIFT = "timezone_shift"
    EXTRACTION_ACCURACY = "extraction_accuracy"
    ERROR_HANDLING = "error_handling"
    ADVERSARIAL = "adversarial"

class TestStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"

@dataclass
class TestCase:
    id: str
    name: str
    category: TestCategory
    input: dict
    expected_output: dict
    severity: str

@dataclass
class TestResult:
    test_id: str
    status: TestStatus
    actual_output: dict
    error_message: str = None
    duration_ms: int = 0

@dataclass
class TestReport:
    run_id: str
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    results_by_category: Dict[str, dict]
    failure_analysis: List[dict]

# --- 3. THE RUNNER ---
class TestRunner:
    def __init__(self, agent_func: Callable):
        self.agent_func = agent_func
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []

    def load_test_cases(self, filepath: str):
        with open(filepath) as f:
            data = json.load(f)
        for tc in data["test_cases"]:
            self.test_cases.append(TestCase(
                id=tc["id"],
                name=tc["name"],
                category=TestCategory(tc["category"]),
                input=tc["input"],
                expected_output=tc["expected_output"],
                severity=tc.get("severity", "medium")
            ))

    def run_all(self) -> TestReport:
        for tc in self.test_cases:
            start = time.time()
            try:
                actual = self.agent_func(tc.input)
                duration = int((time.time() - start) * 1000)
                is_valid, msg = self._compare_calendar_outputs(actual, tc.expected_output)
                
                self.results.append(TestResult(
                    test_id=tc.id,
                    status=TestStatus.PASS if is_valid else TestStatus.FAIL,
                    actual_output=actual,
                    error_message=msg if not is_valid else None,
                    duration_ms=duration
                ))
            except Exception as e:
                self.results.append(TestResult(
                    test_id=tc.id,
                    status=TestStatus.FAIL,
                    actual_output={},
                    error_message=f"Agent Crash: {str(e)}",
                    duration_ms=int((time.time() - start) * 1000)
                ))
        return self._generate_report()

    def _compare_calendar_outputs(self, actual: dict, expected: dict) -> (bool, str):
        actual_events = actual.get("events", [])
        if len(actual_events) < expected.get("min_events", 0):
            return False, f"Got {len(actual_events)} events, expected {expected['min_events']}"
        
        for req in expected.get("must_contain", []):
            found = any(req["title"].lower() in a["title"].lower() and req["date"] == a["date"] for a in actual_events)
            if not found:
                return False, f"Missing: {req['title']} on {req['date']}"
        return True, ""

    def _generate_report(self) -> TestReport:
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        return TestReport(
            run_id=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            total_tests=len(self.test_cases),
            passed=passed,
            failed=len(self.test_cases) - passed,
            results_by_category={}, # Summary logic can go here
            failure_analysis=[]     # Detailed fail logic can go here
        )

def print_report(report: TestReport):
    print("=" * 40)
    print(f"REPORT: {report.run_id}")
    print(f"Status: {report.passed}/{report.total_tests} Passed")
    print("=" * 40)

# --- 4. EXECUTION ---
if __name__ == "__main__":
    print("--- Starting Test Runner ---")
    runner = TestRunner(extract_and_parse_logic)
    
    try:
        runner.load_test_cases("test_cases.json")
        print(f"Loaded {len(runner.test_cases)} test cases.")
        report = runner.run_all()
        print_report(report)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
