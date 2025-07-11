import unittest
import subprocess
import os
import sys
from unittest import mock
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini.commands.login import handle_login

# Note: All tests use the test server at localhost:8001 via test_helpers.py

class TestLoginCLI(GitMiniTestCase):
    """Unit tests for the gitmini login CLI command."""

    @mock.patch("gitmini.commands.login.httpx.post")
    @mock.patch("gitmini.commands.login.webbrowser.open")
    def test_login_success(self, mock_webbrowser, mock_post):
        # Simulate a successful login init
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"cli_token": "tok", "login_url": "http://login"}
        # Patch polling to immediately return success
        with mock.patch("gitmini.commands.login.httpx.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"username": "testuser", "api_key": "abc123"}
            # Prepare .gitmini/config.json
            self.run_gitmini(["init"])
            handle_login(mock.Mock())
            config_path = os.path.join(GITMINI_DIR, "config.json")
            self.assertTrue(os.path.exists(config_path))
            with open(config_path) as f:
                config = f.read()
            self.assertIn("testuser", config)
            self.assertIn("abc123", config)

    @mock.patch("gitmini.commands.login.httpx.post")
    def test_login_failure(self, mock_post):
        # Simulate a failed login init
        mock_post.side_effect = Exception("Server error")
        self.run_gitmini(["init"])
        with self.assertRaises(SystemExit):
            handle_login(mock.Mock())

    def test_login_no_repo(self):
        # Should fail if not initialized
        if os.path.exists(GITMINI_DIR):
            import shutil
            shutil.rmtree(GITMINI_DIR)
        with self.assertRaises(SystemExit):
            handle_login(mock.Mock())

class TestLoginIntegration(GitMiniTestCase):
    """Integration tests for the gitmini login CLI command against the test server."""

    def test_login_success_integration(self):
        self.run_gitmini(["init"])
        result = self.run_gitmini(["login"])
        self.assertIn("[SUCCESS] Logged in as", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_login_no_init(self):
        # Should fail if repo not initialized
        result = self.run_gitmini(["login"])
        self.assertIn("fatal", result.stderr.lower())
        self.assertNotEqual(result.returncode, 0)

    def test_login_server_unavailable(self):
        # Point to a non-existent server and check for fatal error
        os.environ["GITMINI_API_URL"] = "http://localhost:9999"
        self.run_gitmini(["init"])
        result = self.run_gitmini(["login"])
        self.assertIn("fatal: Failed to initiate authentication", result.stderr)
        self.assertNotEqual(result.returncode, 0)
        # Restore test server URL
        os.environ["GITMINI_API_URL"] = "http://localhost:8001"