import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from resume_analysis_core import (
    analyze_bullet_quality,
    as_json,
    build_api_payload,
    build_full_analysis,
    build_gap_explainer,
    build_pdf_report_bytes,
    generate_interview_prep,
)


def success_response(handler: BaseHTTPRequestHandler, data, status=HTTPStatus.OK, content_type="application/json"):
    payload = data if content_type != "application/json" else {"data": data}
    body = data if isinstance(data, bytes) else as_json(payload)
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def error_response(handler: BaseHTTPRequestHandler, status: HTTPStatus, code: str, message: str, details=None):
    body = as_json(
        {
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            }
        }
    )
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def parse_json_body(handler: BaseHTTPRequestHandler):
    content_length = int(handler.headers.get("Content-Length", "0"))
    raw_body = handler.rfile.read(content_length) if content_length else b"{}"
    try:
        return json.loads(raw_body.decode("utf-8") or "{}"), None
    except json.JSONDecodeError:
        return None, {
            "status": HTTPStatus.BAD_REQUEST,
            "code": "invalid_json",
            "message": "Request body must be valid JSON.",
        }


def require_fields(body, fields):
    missing = [field for field in fields if not body.get(field)]
    if missing:
        return {
            "status": HTTPStatus.UNPROCESSABLE_ENTITY,
            "code": "validation_error",
            "message": "Request validation failed.",
            "details": [{"field": field, "message": "This field is required.", "code": "required"} for field in missing],
        }
    return None


class ResumeAnalysisAPIHandler(BaseHTTPRequestHandler):
    server_version = "ResumeAnalysisAPI/1.0"

    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/v1/health":
            return success_response(
                self,
                {
                    "status": "ok",
                    "service": "resume-analysis-api",
                    "version": "v1",
                },
            )
        return error_response(self, HTTPStatus.NOT_FOUND, "not_found", "Endpoint not found.")

    def do_POST(self):
        parsed = urlparse(self.path)
        body, parse_error = parse_json_body(self)
        if parse_error:
            return error_response(self, parse_error["status"], parse_error["code"], parse_error["message"])

        if parsed.path == "/api/v1/analyses":
            validation_error = require_fields(body, ["resume_text"])
            if validation_error:
                return error_response(
                    self,
                    validation_error["status"],
                    validation_error["code"],
                    validation_error["message"],
                    validation_error["details"],
                )
            analysis = build_api_payload(
                resume_text=body.get("resume_text", ""),
                resume_skills=body.get("resume_skills", []),
                job_description=body.get("job_description", ""),
                candidate_name=body.get("candidate_name", "Candidate"),
            )
            return success_response(self, analysis)

        if parsed.path == "/api/v1/analyses/bullet-quality":
            validation_error = require_fields(body, ["resume_text"])
            if validation_error:
                return error_response(
                    self,
                    validation_error["status"],
                    validation_error["code"],
                    validation_error["message"],
                    validation_error["details"],
                )
            return success_response(self, analyze_bullet_quality(body["resume_text"]))

        if parsed.path == "/api/v1/analyses/jd-gap":
            validation_error = require_fields(body, ["resume_text", "job_description"])
            if validation_error:
                return error_response(
                    self,
                    validation_error["status"],
                    validation_error["code"],
                    validation_error["message"],
                    validation_error["details"],
                )
            return success_response(
                self,
                build_gap_explainer(body["job_description"], body["resume_text"], body.get("resume_skills", [])),
            )

        if parsed.path == "/api/v1/analyses/interview-prep":
            validation_error = require_fields(body, ["job_description"])
            if validation_error:
                return error_response(
                    self,
                    validation_error["status"],
                    validation_error["code"],
                    validation_error["message"],
                    validation_error["details"],
                )
            role_title = body.get("role_title", "target role")
            return success_response(
                self,
                generate_interview_prep(body["job_description"], body.get("resume_skills", []), role_title),
            )

        if parsed.path == "/api/v1/reports/pdf":
            validation_error = require_fields(body, ["resume_text"])
            if validation_error:
                return error_response(
                    self,
                    validation_error["status"],
                    validation_error["code"],
                    validation_error["message"],
                    validation_error["details"],
                )
            analysis = build_api_payload(
                resume_text=body.get("resume_text", ""),
                resume_skills=body.get("resume_skills", []),
                job_description=body.get("job_description", ""),
                candidate_name=body.get("candidate_name", "Candidate"),
            )
            report_bytes = build_pdf_report_bytes("Resume Analysis Report", analysis)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", 'attachment; filename="resume-analysis-report.pdf"')
            self.send_header("Content-Length", str(len(report_bytes)))
            self.end_headers()
            self.wfile.write(report_bytes)
            return

        return error_response(self, HTTPStatus.NOT_FOUND, "not_found", "Endpoint not found.")


def create_server(host="127.0.0.1", port=8001):
    return ThreadingHTTPServer((host, port), ResumeAnalysisAPIHandler)


def run(host="127.0.0.1", port=8001):
    server = create_server(host=host, port=port)
    print(f"Resume Analysis API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
