from dataclasses import dataclass, field


@dataclass(slots=True)
class AnalysisRequest:
    resume_text: str
    candidate_name: str = "Candidate"
    resume_skills: list[str] = field(default_factory=list)
    job_description: str = ""


@dataclass(slots=True)
class AnalysisResponse:
    data: dict
