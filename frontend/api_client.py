import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class BackendAPIError(RuntimeError):
    pass


class ResumeAnalyzerClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("BACKEND_API_URL", "http://127.0.0.1:8001")).rstrip("/")

    def _post(self, path: str, payload: dict, *, accept: str = "application/json"):
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": accept},
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                return response.read()
        except (HTTPError, URLError) as error:
            raise BackendAPIError("The backend API is unavailable. Start it with `python -m backend.app.main`.") from error

    def analyze(self, *, candidate_name: str, resume_text: str, resume_skills: list[str], job_description: str) -> dict:
        try:
            body = self._post(
                "/api/v1/analyses",
                {
                    "candidate_name": candidate_name,
                    "resume_text": resume_text,
                    "resume_skills": resume_skills,
                    "job_description": job_description,
                },
            )
            return json.loads(body.decode("utf-8"))["data"]
        except (KeyError, json.JSONDecodeError) as error:
            raise BackendAPIError("The backend API returned an unexpected response.") from error

    def download_report(self, *, candidate_name: str, resume_text: str, resume_skills: list[str], job_description: str) -> bytes:
        return self._post(
            "/api/v1/reports/pdf",
            {
                "candidate_name": candidate_name,
                "resume_text": resume_text,
                "resume_skills": resume_skills,
                "job_description": job_description,
            },
            accept="application/pdf",
        )
