"""
Test the 'gitmini log' command for printing commit history.
"""

import os
import unittest
from tests.test_helpers import GitMiniTestCase

class TestLogCommand(GitMiniTestCase):

    def test_log_displays_commit_history(self):
        """ Test that 'gitmini log' displays the commit history correctly. """
        self.run_gitmini(["init"])
        f = os.path.join(self.repo_dir, "logme.txt")
        with open(f, "w") as out:
            out.write("Initial")

        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "first"])

        with open(f, "a") as out:
            out.write(" again")

        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "second"])

        result = self.run_gitmini(["log"])
        self.assertIn("first", result.stdout)
        self.assertIn("second", result.stdout)
