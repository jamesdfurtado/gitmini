import unittest
import subprocess
import sys

class TestLogCommand(unittest.TestCase):

    def test_cli_log_stub(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "log"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("Log not implemented yet", result.stdout)

    def test_cli_log_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "log", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("usage: gitmini log", result.stdout)
        self.assertIn("Display the commit history", result.stdout)
        self.assertIn("-h, --help", result.stdout)
