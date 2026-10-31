"""
Local HTTP Report Receiver
DevOps for Cloud Computing (CSC418) - Lab Mid Project

Listens for incoming test reports posted by CI runner,
saves payload to 'test-report.json', and displays a summary in the terminal.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import datetime


class ReportReceiverHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Health/status endpoint for testing connectivity."""
        if self.path in ("/", "/status", "/report"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status_payload = {
                "receiver": "DevOps Local Report Receiver",
                "status": "online",
                "ready": True,
                "listening_for": "POST /report"
            }
            self.wfile.write(json.dumps(status_payload, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle incoming test report JSON from GitHub Actions CI runner."""
        if self.path not in ("/", "/report", "/api/report"):
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Empty body"}')
            return

        try:
            body = self.rfile.read(content_length)
            report_data = json.loads(body.decode("utf-8"))

            # Save to standard test-report.json in current directory
            output_file = "test-report.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4)

            # Also maintain an archive copy in reports/ folder for record keeping
            archive_dir = "reports"
            os.makedirs(archive_dir, exist_ok=True)
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = os.path.join(archive_dir, f"test-report_{timestamp_str}.json")
            with open(archive_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4)

            # Print receipt in terminal
            print("\n" + "=" * 65)
            print(f"[RECEIVER] New Test Report Received at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 65)
            print(f" Repository : {report_data.get('repository', 'Unknown')}")
            print(f" Branch     : {report_data.get('branch', 'Unknown')}")
            print(f" Commit SHA : {report_data.get('commit_sha', 'Unknown')}")
            print(f" Run ID     : {report_data.get('run_id', 'Unknown')}")
            
            status = report_data.get("overall_status", "UNKNOWN")
            summary = report_data.get("summary", {})
            total = summary.get("total", 0)
            passed = summary.get("passed", 0)
            failed = summary.get("failed", 0)

            print(f" Status     : >>> {status} <<< (Total: {total}, Passed: {passed}, Failed: {failed})")
            print("-" * 65)
            print(" Individual Test Results:")
            for t in report_data.get("tests", []):
                t_name = t.get("name")
                t_res = t.get("result")
                fail_msg = t.get("failure_message")
                status_bullet = "[OK]" if t_res == "PASSED" else "[FAIL]"
                print(f"   {status_bullet} {t_name:<45} : {t_res}")
                if fail_msg:
                    print(f"        -> Reason: {fail_msg}")
            
            print("-" * 65)
            print(f" Saved to file : {os.path.abspath(output_file)}")
            print(f" Archived to   : {os.path.abspath(archive_file)}")
            print("=" * 65 + "\n")

            # Respond with 200 OK
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_body = {
                "status": "success",
                "message": "Report received and saved as test-report.json",
                "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            self.wfile.write(json.dumps(response_body).encode("utf-8"))

        except Exception as exc:
            print(f"[!] Error parsing report: {exc}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default HTTP server logging to keep terminal output clean."""
        return


def run_server(port=5000):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, ReportReceiverHandler)
    print("=" * 65)
    print(f"[*] DevOps Test Report Receiver Started!")
    print(f"[*] Listening on: http://localhost:{port}/report")
    print(f"[*] Ready to accept test reports from GitHub Actions.")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Stopping Report Receiver.")
        httpd.server_close()


if __name__ == "__main__":
    port_num = 5000
    if len(sys.argv) > 1:
        try:
            port_num = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port_num)
