import unittest
import subprocess
import sys

class TestRootCLI(unittest.TestCase):

    def test_gitmini_without_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("GitMini – A lightweight version control system", result.stdout)
        self.assertIn("usage: gitmini", result.stdout)
        self.assertIn("init", result.stdout)  # subcommand listing

    def test_gitmini_help_flag(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("GitMini – A lightweight version control system", result.stdout)
        self.assertIn("usage: gitmini", result.stdout)
        self.assertIn("checkout", result.stdout)  # ensure full subcommand list appears
