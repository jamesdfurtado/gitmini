"""
Test the 'gitmini checkout' command for switching branches and commits, including force and uncommitted changes.
"""

import os
import unittest
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR

class TestCheckoutCommand(GitMiniTestCase):

    def test_checkout_branch(self):
        """ Test that 'gitmini checkout <branch>' switches to the specified branch. """
        self.run_gitmini(["init"])
        file_path = os.path.join(self.repo_dir, "file.txt")
        with open(file_path, "w") as f:
            f.write("original")

        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "init commit"])
        self.run_gitmini(["branch", "dev"])
        self.run_gitmini(["checkout", "dev"])

        # Make sure HEAD is updated to dev
        head_file = os.path.join(GITMINI_DIR, "HEAD")
        with open(head_file, "r") as f:
            head_contents = f.read().strip()
        self.assertIn("refs/heads/dev", head_contents)

    def test_checkout_old_commit_detached_head(self):
        """ Test that 'gitmini checkout <commit>' switches to a specific commit in detached HEAD state. """
        self.run_gitmini(["init"])
        f = os.path.join(self.repo_dir, "log.txt")
        with open(f, "w") as out:
            out.write("A")
        self.run_gitmini(["add", "."])
        result = self.run_gitmini(["commit", "-m", "first"])
        commit_hash = self.extract_commit_hash(result.stdout)

        with open(f, "a") as out:
            out.write("B")
        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "second"])

        # Checkout first commit
        result = self.run_gitmini(["checkout", commit_hash])
        self.assertIn("detached HEAD", result.stdout)

    def extract_commit_hash(self, stdout):
        for line in stdout.splitlines():
            if "Commit object written to:" in line:
                return os.path.basename(line.split(":")[-1].strip())
