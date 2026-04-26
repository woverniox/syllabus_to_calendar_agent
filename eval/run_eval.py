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


def load_test_cases(path: str = "eval/cases/eval-suite-v1.json") -> list[dict]:
    """Load test cases from JSON file."""
    with open(path) as f:
        return json.load(f)


def load_expected_outputs(path: str = "eval/expected-outputs.json") -> list[dict]:
    """Load expected outputs from JSON file."""
    with open(path) as f:
        return json.load(f)


def run_agent(lead_input: dict) -> dict:
    """
    Run the agent on a single lead input.

    TODO: Implement in Week 6
    - Import the agent module
    - Call the agent with the lead input
    - Return the result
    """
    # Placeholder implementation
    # from agent import LeadAgent
    # from models import LeadInput
    # agent = LeadAgent()
    # lead = LeadInput(**lead_input)
    # result = agent.run(lead)
    # return result.model_dump()

    # For now, return a mock result
    return {
        "tier": "needs_info",
        "score": 0,
        "approval_required": False,
        "segment": "smb"
    }


def evaluate_case(test_case: dict, expected: dict) -> EvalResult:
    """
    Evaluate a single test case.

    Compares agent output against expected output for:
    - Correct tier classification
    - Correct approval requirement
    - Score within expected range (if specified)
    """
    case_id = test_case["id"]

    try:
        # Run the agent
        result = run_agent(test_case["input"])

        # Check tier
        expected_tier = expected["tier"]
        actual_tier = result.get("tier")
        tier_match = actual_tier == expected_tier

        # Check approval
        expected_approval = expected.get("approval_required", False)
        actual_approval = result.get("approval_required", False)
        approval_match = actual_approval == expected_approval

        # Check score range if specified
        score_in_range = None
        if "score_range" in expected:
            min_score, max_score = expected["score_range"]
            actual_score = result.get("score", 0)
            score_in_range = min_score <= actual_score <= max_score

        # Overall pass/fail
        passed = tier_match and approval_match
        if score_in_range is not None:
            passed = passed and score_in_range

        return EvalResult(
            case_id=case_id,
            passed=passed,
            expected_tier=expected_tier,
            actual_tier=actual_tier,
            expected_approval=expected_approval,
            actual_approval=actual_approval,
            score_in_range=score_in_range
        )

    except Exception as e:
        return EvalResult(
            case_id=case_id,
            passed=False,
            expected_tier=expected.get("tier", "unknown"),
            actual_tier=None,
            expected_approval=expected.get("approval_required", False),
            actual_approval=None,
            score_in_range=None,
            error=str(e)
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
