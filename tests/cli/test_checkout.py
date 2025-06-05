import unittest
import subprocess
import sys

class TestCheckoutCommand(unittest.TestCase):

    def test_cli_checkout_stub(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "checkout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("Checkout not implemented yet", result.stdout)

    def test_cli_checkout_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitmini", "checkout", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("usage: gitmini checkout", result.stdout)
        self.assertIn("Restore files to the state of a previous commit.", result.stdout)
        self.assertIn("-h, --help", result.stdout)
