import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from frontend.api_client import ResumeAnalyzerClient


class ResumeAnalyzerClientTestCase(unittest.TestCase):
    @patch("frontend.api_client.urlopen")
    def test_healthcheck_reports_connected_api(self, mocked_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps({"data": {"status": "ok"}}).encode("utf-8")
        mocked_urlopen.return_value.__enter__.return_value = response

        self.assertTrue(ResumeAnalyzerClient("http://example.test").is_available())
        mocked_urlopen.assert_called_once_with("http://example.test/api/v1/health", timeout=2)

    @patch("frontend.api_client.urlopen", side_effect=URLError("offline"))
    def test_healthcheck_reports_unavailable_api(self, _mocked_urlopen):
        self.assertFalse(ResumeAnalyzerClient("http://example.test").is_available())


if __name__ == "__main__":
    unittest.main()
