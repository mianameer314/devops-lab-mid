# Assignment Submission Portal & Automated CI/CD Pipeline

**Course:** DevOps for Cloud Computing (CSC418) - Lab Mid Exam  
**Institution:** COMSATS University Islamabad, Attock Campus  
**Instructor:** Mr. Babar Shazad  
**Student:** Mian Ameer Muhammad  
**Registration Number:** FA23-BAI-021  

---

## 1. Project Overview

This repository implements a complete, production-grade **Assignment Submission Portal** built with Python Flask and vanilla JavaScript, integrated with an automated **GitHub Actions Continuous Integration (CI)** pipeline. 

### Key Features
1. **Assignment Submission Portal (8 Marks):**
   - Web interface allowing students to input their Name, Registration Number, Assignment Title, and Submission URL.
   - Comprehensive input validation (presence check and HTTP/HTTPS URL verification).
   - In-memory/persistent submission storage and dynamic real-time display table.
2. **Automated Continuous Integration (10 Marks):**
   - GitHub Actions workflow triggered on every `git push`.
   - Executes automated test cases covering valid submissions, missing registration numbers, and invalid URLs.
   - A failed test causes the CI test stage to fail.
3. **Localhost Test Report Receiver (14 Marks):**
   - Local HTTP server (`receiver.py`) that receives test reports via HTTP POST and saves them locally as `test-report.json`.
   - Records repository name, branch, commit SHA, run ID, execution timestamp, individual test results, failure messages, and summary counts.
   - Delivered automatically for **both passing and failing** test runs.
4. **Conditional Deployment (Bonus - 5 Marks):**
   - Automatically publishes the portal's static demo to **GitHub Pages** on push to `main` **only if** all tests pass.
5. **Automated Email Reports (Bonus - 5 Marks):**
   - Automatically dispatches test results and attaches `test-report.json` to a configured email on both passing and failing runs.

---

## 2. Directory Structure

```text
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD pipeline
├── docs/                          # Static demo site for GitHub Pages deployment
│   ├── app.js
│   ├── index.html
│   └── style.css
├── static/                        # Frontend assets
│   ├── app.js                     # Dynamic form handling & client-side API calls
│   └── style.css                  # Modern responsive design
├── templates/
│   └── index.html                 # Main portal HTML template
├── tests/
│   ├── __init__.py
│   └── test_portal.py             # Automated unit and integration test suite
├── app.py                         # Flask application & REST API
├── receiver.py                    # Local HTTP server receiving test-report.json
├── run_tests_with_report.py       # Custom test runner collecting metadata & generating JSON
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Complete setup and execution documentation
```

---

## 3. Setup & Installation

### Prerequisites
- Python 3.10+
- Git
- (Optional for remote runner connectivity) [ngrok](https://ngrok.com/)

### Step 1: Clone Repository
```bash
git clone https://github.com/mianameer314/devops-lab-mid.git
cd devops-lab-mid
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. How to Run the Application

Start the Flask web portal locally:
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```
- Fill in your Name, Registration Number (e.g. `FA23-BAI-021`), Assignment Title, and GitHub Submission URL.
- Click **Submit Assignment** to see validation in action and observe the submission appear in the live table.

---

## 5. How to Execute the Automated Tests

### Option A: Standard Pytest
Run the test suite with verbose output:
```bash
pytest tests/ -v
```

### Option B: Test Runner with Full JSON Report
Run the custom reporter script that executes the tests, calculates pass/fail statistics, captures git metadata, and saves `test-report.json`:
```bash
python run_tests_with_report.py
```
The test report is saved to `test-report.json` with the following structure:
```json
{
    "repository": "mianameer314/devops-lab-mid",
    "branch": "main",
    "commit_sha": "...",
    "run_id": "...",
    "execution_timestamp": "2026-10-31T17:09:02+00:00",
    "overall_status": "PASSED",
    "summary": {
        "total": 4,
        "passed": 4,
        "failed": 0
    },
    "tests": [
        {
            "name": "test_complete_details_and_valid_submission_url",
            "result": "PASSED",
            "failure_message": null
        },
        {
            "name": "test_missing_registration_number",
            "result": "PASSED",
            "failure_message": null
        },
        {
            "name": "test_invalid_submission_url",
            "result": "PASSED",
            "failure_message": null
        }
    ]
}
```

---

## 6. How to Start the Local Report Receiver

In a separate terminal on your local computer, run:
```bash
python receiver.py 5000
```
Output:
```text
[*] DevOps Test Report Receiver Started!
[*] Listening on: http://localhost:5000/report
[*] Ready to accept test reports from GitHub Actions.
```
Whenever a test run completes in CI, it delivers the payload to this receiver. The receiver automatically:
1. Writes the current report to `test-report.json`.
2. Archives a timestamped copy to `reports/test-report_<timestamp>.json`.
3. Displays a formatted summary on your terminal screen.

---

## 7. Connecting GitHub Actions to Localhost Receiver

GitHub-hosted runners execute in the cloud, so `localhost` inside GitHub Actions points to the cloud VM. To deliver the test report to your physical machine:

### Using ngrok (Recommended)
1. Open a new terminal and run:
   ```bash
   ngrok http 5000
   ```
2. Copy the forwarding HTTPS URL, for example:
   `https://a1b2-c3d4.ngrok-free.app`
3. Append `/report` to make the full webhook URL:
   `https://a1b2-c3d4.ngrok-free.app/report`
4. In your GitHub repository, navigate to:
   **Settings** > **Secrets and variables** > **Actions** > **New repository secret**
   - **Name:** `RECEIVER_URL`
   - **Value:** `https://a1b2-c3d4.ngrok-free.app/report`

---

## 8. Configuring Email Reports (Bonus Task)

To receive email notifications for both passing and failing runs:
In GitHub Repository **Settings** > **Secrets and variables** > **Actions**:
- `MAIL_USERNAME`: Your Gmail address (e.g. `yourname@gmail.com`)
- `MAIL_PASSWORD`: Your 16-character [Google App Password](https://myaccount.google.com/apppasswords)
- `MAIL_TO`: Destination email address to receive reports

---

## 9. Demonstrating the Complete Workflow (Section 5)

### Step 1: Passing Run
1. Push clean code to `main`:
   ```bash
   git add .
   git commit -m "feat: complete assignment portal and CI pipeline"
   git push origin main
   ```
2. **Observe:**
   - GitHub Actions CI workflow turns **Green (Passed)**.
   - Local `receiver.py` prints the incoming report with `Status: PASSED`.
   - Local `test-report.json` updates with 4 passed tests.
   - GitHub Pages deploys the live demo.

### Step 2: Introduce Defect (Failing Run)
1. Introduce an intentional defect in `tests/test_portal.py` (e.g. change expected status code from `201` to `200` in line 44).
2. Commit and push:
   ```bash
   git add tests/test_portal.py
   git commit -m "test: introduce intentional defect to verify CI failure"
   git push origin main
   ```
3. **Observe:**
   - GitHub Actions CI workflow turns **Red (Failed)** at the test stage.
   - Local `receiver.py` receives the failing report with `Status: FAILED` and the failure message.
   - Local `test-report.json` reflects the failure.
   - GitHub Pages deployment was **skipped**, leaving the previously deployed version unchanged.

### Step 3: Correct Defect (Passing Run)
1. Fix the defect in `tests/test_portal.py` back to `201`.
2. Commit and push:
   ```bash
   git add tests/test_portal.py
   git commit -m "fix: correct defect and restore passing test suite"
   git push origin main
   ```
3. **Observe:**
   - GitHub Actions CI workflow returns to **Green (Passed)**.
   - Local `receiver.py` receives the passing report.
   - Local `test-report.json` updates to `PASSED`.

