# scripts/make_baseline_analysis.py
import json
from pathlib import Path
from datetime import date

REPORT_PATH = Path("eval/reports/baseline-report.json")
OUT_PATH = Path("eval/reports/baseline-analysis.md")

def main():
    with REPORT_PATH.open("r", encoding="utf-8") as f:
        report = json.load(f)

    total_cases = report["total_cases"]
    passed = report["passed"]
    failed = report["failed"]
    accuracy = report["accuracy"]
    by_category = report["by_category"]

    # You can hardcode these or compute dynamically
    agent_version = "v0.1.0"
    eval_suite = "v1.0 (20 cases)"
    # Or use today instead of fixed date:
    report_date = "2026-02-15"  # or: date.today().isoformat()

    # Build markdown content (matching your example exactly)
    lines = [
        "# Baseline Evaluation Report",
        "",
        f"**Date:** {report_date}",
        f"**Agent Version:** {agent_version}",
        f"**Eval Suite:** {eval_suite}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Cases | {total_cases} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| **Accuracy** | **{accuracy}%** |",
        "",
        "## Accuracy by Category",
        "",
        "| Category | Passed | Total | Accuracy |",
        "|----------|--------|-------|----------|",
    ]

    # If you want to force the exact numbers you gave, you can keep them
    # hardcoded; otherwise, build the table from the report:
    #
    # for cat, stats in by_category.items():
    #     lines.append(
    #         f"| {cat} | {stats['passed']} | {stats['total']} | {stats['accuracy']}% |"
    #     )

    # Hardcoded section matching your example:
    lines.extend([
        "| happy_path | 5 | 5 | 100% |",
        "| edge_case | 3 | 5 | 60% |",
        "| error_case | 3 | 5 | 60% |",
        "| adversarial | 2 | 3 | 67% |",
        "| complex | 1 | 2 | 50% |",
        "",
        "## Top 3 Failure Modes",
        "",
        "### 1. Incomplete Clarification (3 failures)",
        "**Pattern:** Agent doesn't ask for missing information",
        "**Cases:** EC001, EC002, ER005",
        "**Root Cause:** Prompt doesn't explicitly require qualification",
        "**Fix:** Add clarification step to routine",
        "",
        "### 2. Adversarial Input Handling (1 failure)",
        "**Pattern:** Agent partially complies with prompt injection",
        "**Cases:** AD001",
        "**Root Cause:** No explicit injection detection",
        "**Fix:** Add input guardrail for known patterns",
        "",
        "### 3. Complex Negotiation (2 failures)",
        "**Pattern:** Agent tries to handle when should escalate",
        "**Cases:** CX001, CX002",
        "**Root Cause:** Escalation triggers not comprehensive",
        "**Fix:** Expand escalation conditions",
        "",
        "## Sample Failure Analysis",
        "",
        "### Case EC001: Empty company size",
        "**Input:** \"I want to learn about your product\"",
        "**Expected:** Ask for company size",
        "**Actual:** Provided generic product overview",
        "**Analysis:** Agent assumed instead of asking",
        "**Action:** Update prompt to require qualification questions",
        "",
    ])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
