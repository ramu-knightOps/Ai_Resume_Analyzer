import unittest
from pathlib import Path


class ProjectStructureTests(unittest.TestCase):
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    def test_application_uses_separate_backend_and_frontend(self):
        backend_dir = self.PROJECT_ROOT / "backend" / "app"
        frontend_dir = self.PROJECT_ROOT / "frontend"

        self.assertTrue((backend_dir / "main.py").is_file())
        self.assertTrue((backend_dir / "api" / "server.py").is_file())
        self.assertTrue((backend_dir / "core" / "resume_analysis.py").is_file())
        self.assertTrue((backend_dir / "models" / "analysis.py").is_file())
        self.assertTrue((backend_dir / "schemas" / "analysis.py").is_file())
        self.assertTrue((frontend_dir / "app.py").is_file())
        self.assertTrue((frontend_dir / "api_client.py").is_file())
        self.assertTrue((frontend_dir / "pages" / "candidate.py").is_file())
        self.assertTrue((frontend_dir / "pages" / "admin.py").is_file())
        self.assertTrue((frontend_dir / "components" / "report.py").is_file())
        self.assertTrue((frontend_dir / "services" / "storage.py").is_file())
        self.assertTrue((frontend_dir / "services" / "pdf_parser.py").is_file())
        self.assertTrue((self.PROJECT_ROOT / "app.py").is_file())

    def test_application_modules_import_from_project_root(self):
        from backend.app import main
        from backend.app.core import matching, parser, resume_analysis

        self.assertTrue(callable(main.create_server))
        self.assertTrue(callable(matching.compute_semantic_matches))
        self.assertTrue(callable(parser.parse_resume_document))
        self.assertTrue(callable(resume_analysis.build_full_analysis))


if __name__ == "__main__":
    unittest.main()
