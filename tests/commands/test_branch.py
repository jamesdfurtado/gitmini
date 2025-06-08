import os
import unittest
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR

class TestBranchCommand(GitMiniTestCase):

    def test_create_branch_successfully(self):
        """ Test that 'gitmini branch <name>' creates a new branch. """
        self.run_gitmini(['init'])

        file_path = os.path.join(self.repo_dir, "a.txt")
        with open(file_path, "w") as f:
            f.write("Initial content")
        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "first commit"])

        result = self.run_gitmini(["branch", "dev"])
        self.assertTrue(os.path.exists(os.path.join(GITMINI_DIR, "refs", "heads", "dev")))

    def test_branch_name_collision(self):
        """ Test that creating a branch with an existing name fails. """
        self.run_gitmini(['init'])
        self.run_gitmini(["branch", "dev"])
        result = self.run_gitmini(["branch", "dev"])
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("fatal" in result.stderr.lower() or result.returncode != 0)
