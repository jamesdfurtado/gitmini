import unittest
import subprocess
import sys

class TestInitCommand(unittest.TestCase):

    def test_cli_init_stub(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "init"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("Init not implemented yet", result.stdout)

    def test_cli_init_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "init", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("usage: gitmini init", result.stdout)
        self.assertIn("Initialize a new GitMini repository in the current directory.", result.stdout)
        self.assertIn("-h, --help", result.stdout)
