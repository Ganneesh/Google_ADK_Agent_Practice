"""
QA Gate: runs both the structural/trajectory checks (via `adk eval`) and the
semantic business-coverage check (via coverage_evaluator.py) against
a generated .feature file, then combines them into a single pass/fail gate.
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_HISTORY_DIR = BASE_DIR / "qa_agent" / ".adk" / "eval_history"

sys.path.insert(0, str(BASE_DIR))
from evals.coverage_evaluator import evaluate_coverage  # noqa: E402


def run_adk_checks() -> list[dict]:
    """Runs `adk eval` and reads ALL metric results from the freshest
    eval_history file (structure check AND tool trajectory check),
    not just the first one."""
    cmd = [
        "adk", "eval",
        str(BASE_DIR / "qa_agent"),
        str(BASE_DIR / "evals" / "requirement_to_feature.evalset.json"),
        "--config_file_path", str(BASE_DIR / "evals" / "eval_config.json"),
        "--print_detailed_results",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    print(result.stdout)
    if result.returncode != 0 and "PASSED" not in result.stdout:
        print(result.stderr)

    latest = max(EVAL_HISTORY_DIR.glob("*.evalset_result.json"), key=lambda p: p.stat().st_mtime)
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    metric_results = data["eval_case_results"][0]["overall_eval_metric_results"]

    checks = []
    for metric in metric_results:
        passed = metric["score"] is not None and metric["score"] >= metric["threshold"]
        checks.append({
            "check": metric["metric_name"],
            "score": metric["score"],
            "threshold": metric["threshold"],
            "passed": passed,
        })
    return checks


def run_coverage_check(requirement_file: str, feature_file: str) -> dict:
    """Runs the semantic coverage evaluator directly (no subprocess needed)."""
    with open(requirement_file, "r", encoding="utf-8") as f:
        requirement = f.read()
    with open(feature_file, "r", encoding="utf-8") as f:
        feature = f.read()

    result = evaluate_coverage(requirement, feature)

    return {
        "check": "coverage",
        "score": result["coverage_score"],
        "status": result["status"],
        "missing": result["missing_requirements"],
        "extra": result["extra_behavior"],
        "passed": result["status"] == "PASS",
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python qa_gate.py <requirement_file> <feature_file>")
        sys.exit(1)

    requirement_file = sys.argv[1]
    feature_file = sys.argv[2]

    print("=" * 60)
    print("Running ADK EVAL (structure + tool trajectory checks)...")
    print("=" * 60)
    adk_checks = run_adk_checks()

    print("\n" + "=" * 60)
    print("Running Coverage EVAL (business coverage check)...")
    print("=" * 60)
    coverage_result = run_coverage_check(requirement_file, feature_file)

    print("\n" + "=" * 60)
    print("QA GATE SUMMARY")
    print("=" * 60)

    all_passed = True
    for check in adk_checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"{check['check']:30s}: {status} (score: {check['score']}, threshold: {check['threshold']})")
        all_passed = all_passed and check["passed"]

    print(f"{'coverage_check':30s}: {'PASS' if coverage_result['passed'] else 'FAIL'} "
          f"(score: {coverage_result['score']}%)")
    all_passed = all_passed and coverage_result["passed"]

    if coverage_result["missing"]:
        print(f"  Missing: {coverage_result['missing']}")
    if coverage_result["extra"]:
        print(f"  Extra  : {coverage_result['extra']}")

    print("-" * 60)
    print(f"QA GATE = {'PASS' if all_passed else 'FAIL'}")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()