"""
Automated Test Runner & Comprehensive Report Generator
DevOps for Cloud Computing (CSC418) - Lab Mid Project

Executes test suite, collects exact test results and metadata,
saves 'test-report.json', and dispatches the payload via HTTP POST to the local receiver.
"""

import os
import sys
import json
import time
import datetime
import unittest
import urllib.request
import urllib.error


class StructuredTestResult(unittest.TestResult):
    """Custom TestResult collector to record exact status and failure messages."""

    def __init__(self):
        super().__init__()
        self.recorded_tests = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.recorded_tests.append({
            "name": test._testMethodName,
            "class": test.__class__.__name__,
            "result": "PASSED",
            "failure_message": None
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        exc_type, exc_val, exc_tb = err
        msg = f"{exc_type.__name__}: {str(exc_val)}"
        self.recorded_tests.append({
            "name": test._testMethodName,
            "class": test.__class__.__name__,
            "result": "FAILED",
            "failure_message": msg.strip()
        })

    def addError(self, test, err):
        super().addError(test, err)
        exc_type, exc_val, exc_tb = err
        msg = f"{exc_type.__name__}: {str(exc_val)}"
        self.recorded_tests.append({
            "name": test._testMethodName,
            "class": test.__class__.__name__,
            "result": "ERROR",
            "failure_message": msg.strip()
        })


def run_and_report():
    print("=" * 60)
    print("Executing Automated Test Suite & Generating Report...")
    print("=" * 60)

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")

    collector = StructuredTestResult()
    start_time = time.time()
    suite.run(collector)
    elapsed_time = round(time.time() - start_time, 3)

    total_tests = collector.testsRun
    failed_count = len(collector.failures) + len(collector.errors)
    passed_count = total_tests - failed_count
    overall_status = "PASSED" if failed_count == 0 else "FAILED"

    # Gather environment metadata (from GitHub Actions env or fallback to local defaults)
    repo_name = os.getenv("GITHUB_REPOSITORY", "mianameer314/devops-lab-mid")
    branch_name = os.getenv("GITHUB_REF_NAME", "main")
    commit_sha = os.getenv("GITHUB_SHA", "local-dev-commit")
    run_id = os.getenv("GITHUB_RUN_ID", "local-manual-run")
    execution_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    report_data = {
        "repository": repo_name,
        "branch": branch_name,
        "commit_sha": commit_sha,
        "run_id": str(run_id),
        "execution_timestamp": execution_time,
        "elapsed_seconds": elapsed_time,
        "overall_status": overall_status,
        "summary": {
            "total": total_tests,
            "passed": passed_count,
            "failed": failed_count
        },
        "tests": collector.recorded_tests
    }

    report_path = "test-report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)

    print(f"\n[+] Test Report generated and saved to: {report_path}")
    print(f"    Status: {overall_status} | Total: {total_tests} | Passed: {passed_count} | Failed: {failed_count}")

    # Optional HTTP dispatch to receiver endpoint (if RECEIVER_URL environment variable is provided)
    receiver_url = os.getenv("RECEIVER_URL", "").strip()
    if receiver_url:
        print(f"\n[*] Dispatching test report to receiver: {receiver_url}")
        try:
            payload_bytes = json.dumps(report_data).encode("utf-8")
            req = urllib.request.Request(
                receiver_url,
                data=payload_bytes,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "GitHub-Actions-CI-Runner"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f"[+] Successfully delivered report! Receiver response HTTP {resp.status}")
        except Exception as exc:
            print(f"[!] Warning: Could not deliver report to receiver: {exc}")
    else:
        print("\n[-] Note: RECEIVER_URL environment variable not set. Report written to local test-report.json only.")

    print("=" * 60)

    # Return exit code based on test outcome
    # Non-zero return code ensures GitHub Actions marks the test step as failed on defect!
    sys.exit(0 if overall_status == "PASSED" else 1)


if __name__ == "__main__":
    run_and_report()
