#!/usr/bin/env python3
"""
Evaluation Runner

Runs the lead qualification agent against test cases and reports accuracy.
Students build this in Week 6.

Usage:
    python eval/run_eval.py
    python eval/run_eval.py --verbose
    python eval/run_eval.py --case 5  # Run specific case
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import requests
import io

@dataclass
class EvalResult:
    """Result of a single test case evaluation."""
    case_id: int
    passed: bool
    expected_tier: str
    actual_tier: Optional[str]
    expected_approval: bool
    actual_approval: Optional[bool]
    score_in_range: Optional[bool]
    error: Optional[str] = None

def load_test_cases():
    # Change this line to point to your new 20-case JSON
    with open("cases/eval-suite-v1.json", "r") as f: 
        return json.load(f)
    
def load_expected_outputs(path: str = "expected-outputs.json") -> list[dict]:
    with open(path) as f:
        return json.load(f)

def run_agent(test_input: dict) -> dict:
    """
    Calls the Syllabus Agent /syllabus endpoint using multipart form data.
    """
    url = "http://localhost:8000/syllabus"
    content = test_input.get("content", "Empty Syllabus")
    course_code = test_input.get("course_code", "UNKNOWN")

    file_io = io.BytesIO(content.encode('utf-8'))
    files = {'file': ('test.txt', file_io, 'text/plain')}
    data = {'course_code': course_code}

    try:
        response = requests.post(url, files=files, data=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def evaluate_case(test_case: dict, expected: dict = None) -> EvalResult:
    """
    Updated to handle the 'expected' argument being passed by the loop.
    We pull the actual expectations directly from the test_case.
    """
    case_id = test_case["id"]
    
    # 1. Run the agent
    actual_response = run_agent(test_case["input"])
    
    # 2. Get the actual extraction count
    actual_events = actual_response.get("data", [])
    actual_count = len(actual_events)
    
    # 3. Pull expectations from the nested 'expected' block
    expectations = test_case.get("expected", {})
    expected_count = expectations.get("assignment_count", 0)
    expected_course = expectations.get("course_name", "UNKNOWN")
    
    # 4. Validation Logic
    actual_msg = actual_response.get("message", "")
    course_match = expected_course.upper() in actual_msg.upper()
    passed = (actual_count == expected_count) and course_match

    return EvalResult(
        case_id=case_id,
        passed=passed,
        expected_tier=f"Count: {expected_count}",
        actual_tier=f"Count: {actual_count}",
        expected_approval=True,
        actual_approval=course_match,
        score_in_range=True
    )

def run_eval(verbose: bool = False, case_id: Optional[int] = None) -> tuple[int, int, list[EvalResult]]:
    """
    Run the full evaluation suite.

    Args:
        verbose: Print detailed output for each case
        case_id: Run only a specific case (optional)

    Returns:
        Tuple of (passed_count, total_count, results)
    """
    test_cases = load_test_cases()
    expected_outputs = load_expected_outputs()

    # Build lookup for expected outputs
    expected_by_id = {e["id"]: e for e in expected_outputs}

    results = []

    for test_case in test_cases:
        cid = test_case["id"]

        # Skip if filtering to specific case
        if case_id is not None and cid != case_id:
            continue

        expected = expected_by_id.get(cid, {})
        result = evaluate_case(test_case, expected)
        results.append(result)

        if verbose:
            status = "✓" if result.passed else "✗"
            print(f"{status} Case {cid}: {test_case['category']}")
            if not result.passed:
                print(f"    Expected tier: {result.expected_tier}, Got: {result.actual_tier}")
                print(f"    Expected approval: {result.expected_approval}, Got: {result.actual_approval}")
                if result.error:
                    print(f"    Error: {result.error}")

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    return passed, total, results


def print_summary(passed: int, total: int, results: list[EvalResult]):
    """Print evaluation summary."""
    print(f"\n{'='*50}")
    print(f"Evaluation Results: {passed}/{total} passed ({100*passed/total:.1f}%)")
    print(f"{'='*50}\n")

    if passed < total:
        print("Failures:")
        for r in results:
            if not r.passed:
                print(f"  - Case {r.case_id}: Expected {r.expected_tier}, got {r.actual_tier}")
                if r.error:
                    print(f"    Error: {r.error}")


def main():
    parser = argparse.ArgumentParser(description="Run agent evaluation suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--case", "-c", type=int, help="Run specific case ID")
    args = parser.parse_args()

    print("Running evaluation suite...")
    print(f"Loading test cases from eval/sample-leads.json")
    print()

    passed, total, results = run_eval(verbose=args.verbose, case_id=args.case)
    print_summary(passed, total, results)

    # Exit with error code if not all passed
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
