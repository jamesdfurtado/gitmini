import unittest
import subprocess
import sys

class TestCommitCommand(unittest.TestCase):

    def test_cli_commit_stub(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "commit"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("Commit not implemented yet", result.stdout)

    def test_cli_commit_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "commit", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("usage: gitmini commit", result.stdout)
        self.assertIn("Record a new commit with the current staged files.", result.stdout)
        self.assertIn("-h, --help", result.stdout)
