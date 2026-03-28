import sys
import unittest
from pathlib import Path
from unittest.mock import patch


APP_DIR = Path(__file__).resolve().parents[1] / "App"
sys.path.insert(0, str(APP_DIR))

from matching_utils import (
    canonicalize_skills,
    compute_semantic_matches,
    evaluate_resume_score,
    extract_resume_evidence,
    infer_candidate_level,
    infer_role_from_skills,
)


class MatchingUtilsTests(unittest.TestCase):
    def test_resume_score_rewards_detected_sections(self):
        resume_text = """
        Summary
        Education
        Work Experience
        Skills
        Projects
        Certifications
        """
        score, checks = evaluate_resume_score(resume_text)
        self.assertGreaterEqual(score, 70)
        self.assertTrue(any(check["label"] == "Projects" and check["matched"] for check in checks))

    def test_candidate_level_prefers_experience_signal(self):
        self.assertEqual(infer_candidate_level(2, "Work Experience with backend ownership"), "Experienced")
        self.assertEqual(infer_candidate_level(1, "Internship at a startup"), "Intermediate")
        self.assertEqual(infer_candidate_level(1, "Portfolio and education details only"), "Fresher")

    def test_role_inference_from_skills(self):
        result = infer_role_from_skills(["React", "JavaScript", "CSS", "Accessibility"])
        self.assertEqual(result["field"], "Web Development")
        self.assertIn("TypeScript", result["recommended_skills"])

    def test_skill_canonicalization_normalizes_aliases(self):
        normalized = canonicalize_skills(["Postgres", "postgresql", "Node", "React.js", "JS"])
        self.assertIn("SQL", normalized)
        self.assertIn("Node.js", normalized)
        self.assertIn("React", normalized)
        self.assertIn("JavaScript", normalized)

    def test_resume_evidence_recovers_skills_from_resume_text(self):
        resume_text = "Built APIs with FastAPI, Docker, and PostgreSQL. Improved API latency by 40%."
        evidence = extract_resume_evidence(resume_text, ["Python"])
        self.assertIn("FastAPI", evidence)
        self.assertIn("Docker", evidence)
        self.assertIn("SQL", evidence)

    def test_role_inference_uses_resume_text_evidence(self):
        result = infer_role_from_skills(["Python"], "Built REST APIs with Docker, PostgreSQL, caching, and authentication.")
        self.assertEqual(result["title"], "Backend Engineer")

    def test_role_catalog_expansion_supports_devops_signals(self):
        result = infer_role_from_skills(
            ["Docker", "AWS"],
            "Managed CI/CD pipelines, Kubernetes clusters, Terraform modules, and cloud observability.",
        )
        self.assertEqual(result["title"], "DevOps Engineer")

    def test_resume_score_rewards_metrics_and_bullets(self):
        resume_text = """
        Summary
        Education
        Experience
        Projects
        Skills
        - Improved API latency by 42%
        - Reduced build time by 30%
        - Led a migration for 5000 users
        - Built dashboards for analytics reviews
        """
        score, _ = evaluate_resume_score(resume_text)
        self.assertGreaterEqual(score, 75)

    def test_semantic_matching_fallback_uses_normalized_resume_evidence(self):
        with patch("matching_utils.build_vector_indexes", side_effect=RuntimeError("embedding unavailable")):
            results = compute_semantic_matches(
                "Looking for a backend engineer with FastAPI, Docker, PostgreSQL, and authentication experience.",
                "Built APIs using FastAPI, Docker, and Postgres. Implemented auth flows for internal tools.",
                ["Python", "Node"],
            )
        self.assertGreater(len(results["role_matches"]), 0)
        self.assertIn("FastAPI", results["priority_keywords"] + [item["skill"] for item in results["jd_skill_matches"]])
        self.assertIn("SQL", [item["skill"] for item in results["resume_skill_evidence"]])


if __name__ == "__main__":
    unittest.main()
