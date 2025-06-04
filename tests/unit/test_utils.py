import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
import io
import sys
from gitmini.utils import find_gitmini_root


class TestFindGitminiRoot(GitMiniTestCase):

    def test_find_gitmini_root_success(self):
        """ Test that find_gitmini_root correctly finds .gitmini """
        os.makedirs(GITMINI_DIR)
        root = find_gitmini_root()
        self.assertEqual(root, os.getcwd())

    def test_find_gitmini_root_failure(self):
        """ Test that find_gitmini_root exits when .gitmini is missing """
        stderr_backup = sys.stderr
        sys.stderr = io.StringIO()  # Suppress error output
        try:
            with self.assertRaises(SystemExit) as cm:
                find_gitmini_root()
            self.assertEqual(cm.exception.code, 1)
        finally:
            sys.stderr = stderr_backup

