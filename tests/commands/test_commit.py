import os
import unittest
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini_core.classes.HEAD import HEAD
from gitmini_core.classes.Repo import Repo

class TestCommit(GitMiniTestCase):
    """ Ensure committing updates HEAD correctly. """
    def test_commit_creates_object_and_updates_HEAD(self):
        self.run_gitmini(["init"])
        file_path = os.path.join(self.repo_dir, "file.txt")
        with open(file_path, "w") as f:
            f.write("test")

        self.run_gitmini(["add", "."])
        self.run_gitmini(["commit", "-m", "store it"])

        self.repo = Repo(self.repo_dir)
        head = HEAD(self.repo)
        head_val = head.get_commit()
        self.assertIsNotNone(head_val)
        self.assertEqual(len(head_val), 40)
