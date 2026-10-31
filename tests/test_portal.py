"""
Automated Test Suite for Assignment Submission Portal
DevOps for Cloud Computing (CSC418) - Lab Mid Exam

Test Cases Specified in Mid Exam:
1. Complete details and a valid submission URL -> The submission is saved and appears in the submission list.
2. Missing registration number -> The submission is rejected with a validation message.
3. Invalid submission URL -> The submission is rejected and is not saved.
"""

import unittest
import json
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, submissions


class TestAssignmentSubmissionPortal(unittest.TestCase):

    def setUp(self):
        """Set up test client and reset in-memory state before every test."""
        self.client = app.test_client()
        self.client.testing = True
        submissions.clear()

    def tearDown(self):
        """Clean up state after test execution."""
        submissions.clear()

    def test_complete_details_and_valid_submission_url(self):
        """
        Test Case 1 (Required by Spec):
        Complete details and a valid submission URL.
        Expected: The submission is saved and appears in the submission list.
        """
        payload = {
            "student_name": "Mian Ameer Muhammad",
            "reg_no": "FA23-BAI-021",
            "assignment_title": "DevOps Lab Mid - CI/CD Pipeline",
            "submission_url": "https://github.com/mianameer314/devops-lab-mid"
        }

        # Submit assignment
        post_response = self.client.post(
            "/api/submissions",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(post_response.status_code, 201, "Expected status code 201 for valid submission")
        post_data = json.loads(post_response.data.decode("utf-8"))
        self.assertEqual(post_data["status"], "success")
        self.assertIn("The submission is saved and appears in the submission list.", post_data["message"])

        # Verify it appears in submission list
        get_response = self.client.get("/api/submissions")
        self.assertEqual(get_response.status_code, 200)
        get_data = json.loads(get_response.data.decode("utf-8"))
        self.assertEqual(get_data["count"], 1)
        self.assertEqual(len(get_data["submissions"]), 1)

        saved = get_data["submissions"][0]
        self.assertEqual(saved["student_name"], payload["student_name"])
        self.assertEqual(saved["reg_no"], payload["reg_no"])
        self.assertEqual(saved["assignment_title"], payload["assignment_title"])
        self.assertEqual(saved["submission_url"], payload["submission_url"])

    def test_missing_registration_number(self):
        """
        Test Case 2 (Required by Spec):
        Missing registration number.
        Expected: The submission is rejected with a validation message and not saved.
        """
        payload = {
            "student_name": "Mian Ameer Muhammad",
            "reg_no": "",  # Missing registration number
            "assignment_title": "DevOps Lab Mid - CI/CD Pipeline",
            "submission_url": "https://github.com/mianameer314/devops-lab-mid"
        }

        post_response = self.client.post(
            "/api/submissions",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(post_response.status_code, 400, "Expected status code 400 when reg_no is missing")
        post_data = json.loads(post_response.data.decode("utf-8"))
        self.assertEqual(post_data["status"], "error")
        self.assertIn("Missing registration number", post_data["message"])

        # Verify not saved in list
        get_response = self.client.get("/api/submissions")
        get_data = json.loads(get_response.data.decode("utf-8"))
        self.assertEqual(get_data["count"], 0)
        self.assertEqual(len(get_data["submissions"]), 0)

    def test_invalid_submission_url(self):
        """
        Test Case 3 (Required by Spec):
        Invalid submission URL.
        Expected: The submission is rejected and is not saved.
        """
        payload = {
            "student_name": "Mian Ameer Muhammad",
            "reg_no": "FA23-BAI-021",
            "assignment_title": "DevOps Lab Mid - CI/CD Pipeline",
            "submission_url": "invalid_url_without_http"  # Invalid URL
        }

        post_response = self.client.post(
            "/api/submissions",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(post_response.status_code, 400, "Expected status code 400 for invalid submission URL")
        post_data = json.loads(post_response.data.decode("utf-8"))
        self.assertEqual(post_data["status"], "error")
        self.assertIn("Invalid submission URL", post_data["message"])

        # Verify not saved in list
        get_response = self.client.get("/api/submissions")
        get_data = json.loads(get_response.data.decode("utf-8"))
        self.assertEqual(get_data["count"], 0)
        self.assertEqual(len(get_data["submissions"]), 0)

    def test_health_check_endpoint(self):
        """Verify health check endpoint returns 200 OK."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(data["status"], "healthy")


if __name__ == "__main__":
    unittest.main()

