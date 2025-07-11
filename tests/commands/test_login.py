import unittest
import subprocess
import os
import sys
import time
import re
from unittest import mock
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini.commands.login import handle_login

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

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
        env = os.environ.copy()
        env["GITMINI_TEST_LOGIN"] = "1"
        # Add PYTHONPATH for subprocess
        core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gitmini_core'))
        env['PYTHONPATH'] = core_path + os.pathsep + env.get('PYTHONPATH', '')
        result = self.run_gitmini(["login"], env=env)
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

@unittest.skipUnless(SELENIUM_AVAILABLE, "Selenium and webdriver-manager required for browser automation integration test.")
class TestLoginIntegrationSelenium(GitMiniTestCase):
    """True integration test for gitmini login using Selenium to automate browser login."""
    def test_login_real_flow(self):
        self.run_gitmini(["init"])
        # Start the CLI login command
        proc = subprocess.Popen(
            [sys.executable, "-m", "gitmini", "login"],
            cwd=self.repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Parse CLI output to get the login URL
        login_url = None
        for _ in range(30):  # Wait up to ~15 seconds
            line = proc.stdout.readline()
            if "visit:" in line:
                match = re.search(r'(http://\S+)', line)
                if match:
                    login_url = match.group(1)
                    break
            time.sleep(0.5)
        assert login_url, "Login URL not found in CLI output"
        # Set up Selenium (headless Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # Go to the login URL
        driver.get(login_url)
        # Fill in the login form (adjust selectors as needed)
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("testpass")
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        # Wait for CLI to finish
        stdout, stderr = proc.communicate(timeout=30)
        driver.quit()
        self.assertIn("[SUCCESS] Logged in as", stdout)
        self.assertEqual(proc.returncode, 0)