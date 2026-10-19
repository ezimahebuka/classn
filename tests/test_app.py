import re
import unittest
from unittest.mock import patch

import requests

from app import app, send_demo_notification


class LoginDemoTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=True)
        self.client = app.test_client()

    def csrf_token(self):
        response = self.client.get("/")
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    @patch("app.requests.post")
    def test_valid_demo_login_notifies_with_metadata_only(self, post):
        with patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "test-token", "TELEGRAM_CHAT_ID": "123"},
        ):
            response = self.client.post(
                "/login",
                data={
                    "csrf_token": self.csrf_token(),
                    "username": "demo-user",
                    "password": "demo-pass-123",
                },
            )

        self.assertEqual(response.status_code, 302)
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["chat_id"], "123")
        message = payload["text"]
        self.assertIn("Event type: Demo login attempt", message)
        self.assertIn("Demo validation succeeded: true", message)
        self.assertRegex(message, r"Event ID: [0-9a-f-]{36}")
        self.assertNotIn("demo-user", message)
        self.assertNotIn("demo-pass-123", message)

        result = self.client.get("/")
        self.assertIn(b"Demo login successful.", result.data)
        self.assertNotIn(b"demo-pass-123", result.data)

    @patch("app.requests.post")
    def test_invalid_credentials_show_failure_and_notify_false(self, post):
        with patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "test-token", "TELEGRAM_CHAT_ID": "123"},
        ):
            response = self.client.post(
                "/login",
                data={
                    "csrf_token": self.csrf_token(),
                    "username": "demo-user",
                    "password": "wrong-password",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("Demo validation succeeded: false", post.call_args.kwargs["json"]["text"])
        result = self.client.get("/")
        self.assertIn(b"Demo login failed.", result.data)
        self.assertNotIn(b"wrong-password", result.data)

    def test_missing_csrf_token_is_rejected(self):
        response = self.client.post(
            "/login", data={"username": "demo-user", "password": "demo-pass-123"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.requests.post")
    def test_telegram_error_log_does_not_expose_secrets(self, post):
        response = requests.Response()
        response.status_code = 401
        post.side_effect = requests.HTTPError(response=response)

        with patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "test-token", "TELEGRAM_CHAT_ID": "123"},
        ):
            with self.assertLogs("app", level="WARNING") as captured:
                send_demo_notification("event-id", "timestamp", False)

        log_output = " ".join(captured.output)
        self.assertIn("HTTP status: 401", log_output)
        self.assertNotIn("test-token", log_output)
        self.assertNotIn("demo-pass-123", log_output)


if __name__ == "__main__":
    unittest.main()