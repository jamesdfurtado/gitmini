import os
import io
import contextlib

from gitmini.classes.Repo import Repo
from gitmini.classes.HEAD import HEAD
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestHEAD(GitMiniTestCase):

    def test_initial_head_is_none(self):
        """New repo should have an empty HEAD."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)

        head = HEAD(repo)
        self.assertIsNone(head.value)

    def test_set_and_read_head(self):
        """ Set HEAD's contents and ensure it contains correct info ."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        repo = Repo(self.repo_dir)

        head = HEAD(repo)
        head.set("abcde")

        self.assertEqual(head.value, "abcde")

        head_file = os.path.join(repo.gitmini_dir, "HEAD")
        with open(head_file, "r") as f:
            self.assertEqual(f.read().strip(), "abcde")
