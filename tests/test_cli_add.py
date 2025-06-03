import unittest
import subprocess
import sys

class TestAddCommand(unittest.TestCase):

    def test_cli_add_stub(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "add"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("Add not implemented yet", result.stdout)

    def test_cli_add_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "add", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("usage: gitmini add", result.stdout)
        self.assertIn("Add specified files to GitMini's staging area", result.stdout)
        self.assertIn("-h, --help", result.stdout)
