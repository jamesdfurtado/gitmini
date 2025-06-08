import unittest
import os
from tests.test_helpers import GitMiniTestCase

class TestSmoke(GitMiniTestCase):

    def test_init_add_commit_help(self):
        """ Test that the CLI responds correctly """
        for cmd in [["init"], ["add", "--help"], ["commit", "--help"], ["log", "--help"], ["checkout", "--help"]]:
            result = self.run_gitmini(cmd)
            self.assertEqual(result.returncode, 0)

    def test_full_flow(self):
        """ Basic run-thru of full project """
        self.run_gitmini(["init"])

        with open(os.path.join(self.repo_dir, "test.txt"), "w") as f:
            f.write("Line 1")
        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "Initial commit"])

        self.run_gitmini(["branch", "feature"])
        self.run_gitmini(["checkout", "feature"])

        with open(os.path.join(self.repo_dir, "test.txt"), "a") as f:
            f.write("\\nLine 2")
        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "Feature commit"])

        log = self.run_gitmini(["log"]).stdout
        self.assertIn("Feature commit", log)
        self.assertIn("Initial commit", log)
