import os
import unittest
from gitmini_core.classes.HEAD import HEAD
from gitmini_core.classes.Repo import Repo
from tests.test_helpers import GitMiniTestCase

class TestHEAD(GitMiniTestCase):

    def test_initial_head_points_to_main(self):
        """ Verifies that HEAD defaults to pointing to main branch after init """
        self.run_gitmini(["init"])
        self.repo = Repo(self.repo_dir)
        head = HEAD(self.repo)
        val = head.value
        self.assertEqual(val, "ref: refs/heads/main")

    def test_set_and_read_head_commit(self):
        """ Sets HEAD to a raw commit hash and checks that it's in detached state """
        self.run_gitmini(["init"])
        self.repo = Repo(self.repo_dir)
        head = HEAD(self.repo)
        test_commit_hash = "abc123def456abc123def456abc123def456abcd"
        head.set_commit(test_commit_hash)
        self.assertEqual(head.get_commit(), test_commit_hash)

    def test_set_and_read_head_branch(self):
        """ Sets HEAD to point to a branch """
        self.run_gitmini(["init"])
        self.repo = Repo(self.repo_dir)
        head = HEAD(self.repo)
        head.set_ref("dev")
        self.assertIn("refs/heads/dev", head.value)
