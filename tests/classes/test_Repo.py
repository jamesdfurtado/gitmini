import os
import io
import contextlib

from gitmini_core.classes.Repo import Repo
from tests.test_helpers import GitMiniTestCase


class TestRepo(GitMiniTestCase):

    def test_init_creates_structure(self):
        """ Repo.init should create .gitmini with all required files/folders. """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)

        gitmini_dir = os.path.join(self.repo_dir, ".gitmini")
        self.assertTrue(os.path.isdir(gitmini_dir))
        self.assertTrue(os.path.isdir(os.path.join(gitmini_dir, "objects")))
        self.assertTrue(os.path.isfile(os.path.join(gitmini_dir, "index")))
        self.assertTrue(os.path.isfile(os.path.join(gitmini_dir, "HEAD")))

    def test_init_fails_if_exists(self):
        """ Calling 'gitmini init' within a .gitmini should fail."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)

        # Second call should raise SystemExit with code 1
        with self.assertRaises(SystemExit) as cm, \
             contextlib.redirect_stdout(buf):
            Repo.init(self.repo_dir)
        self.assertEqual(cm.exception.code, 1)
