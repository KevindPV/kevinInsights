import json
import os
from io import BytesIO
from unittest.mock import mock_open, patch
from urllib.error import HTTPError, URLError

from django.test import Client, TestCase
from django.urls import reverse


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def post_gemini(self, prompt):
        return self.client.post(
            reverse("gemini_request"),
            data=json.dumps({"prompt": prompt}),
            content_type="application/json",
        )

    def run_gemini_with_urlopen(self, urlopen_value):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch(
                "kevinInsights.views.urlrequest.urlopen",
                **urlopen_value,
            ):
                return self.post_gemini("hello")

    def run_missing_key_with_env(self, env_exists, env_content=""):
        with patch.dict(os.environ, {}, clear=True):
            with patch("kevinInsights.views.os.path.exists", return_value=env_exists):
                if env_exists:
                    with patch("builtins.open", mock_open(read_data=env_content)):
                        return self.post_gemini("hello")
                return self.post_gemini("hello")

    def test_home_get_ok(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("steps", response.context)
        self.assertEqual(len(response.context["steps"]), 5)

    def test_about_me_get_ok(self):
        response = self.client.get("/about-me/")
        self.assertEqual(response.status_code, 200)

    def test_gemini_invalid_json(self):
        response = self.client.post(
            reverse("gemini_request"),
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Invalid JSON")

    def test_gemini_missing_prompt(self):
        response = self.post_gemini("   ")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Prompt is required")

    def test_gemini_missing_api_key_no_env_file(self):
        response = self.run_missing_key_with_env(False)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json().get("error"), "Missing API key")
        self.assertFalse(response.json().get("env_file_has_key"))

    def test_gemini_missing_api_key_env_file_has_key(self):
        response = self.run_missing_key_with_env(True, "GEMINI_API_KEY=fromfile\n")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json().get("error"), "Missing API key")
        self.assertTrue(response.json().get("env_file_has_key"))

    def test_gemini_success(self):
        fake_response = {
            "candidates": [{"content": {"parts": [{"text": "<h3>OK</h3>"}]}}]
        }

        class FakeHTTPResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(fake_response).encode("utf-8")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch(
                "kevinInsights.views.urlrequest.urlopen",
                return_value=FakeHTTPResponse(),
            ):
                response = self.post_gemini("hello")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get("text"), "<h3>OK</h3>")
        self.assertTrue(payload.get("env_var_set"))

    def test_gemini_http_error(self):
        error_body = b'{"error":"bad request"}'
        http_error = HTTPError(
            url="https://example.com",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=BytesIO(error_body),
        )
        response = self.run_gemini_with_urlopen({"side_effect": http_error})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_gemini_url_error(self):
        response = self.run_gemini_with_urlopen(
            {"side_effect": URLError("network down")}
        )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json().get("error"), "network down")

    def test_gemini_malformed_response(self):
        fake_response = {"unexpected": True}

        class FakeHTTPResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(fake_response).encode("utf-8")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch(
                "kevinInsights.views.urlrequest.urlopen",
                return_value=FakeHTTPResponse(),
            ):
                response = self.post_gemini("hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("text"), "")
