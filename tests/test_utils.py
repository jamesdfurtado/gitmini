import os
import shutil
import unittest
import io
import sys
from gitmini.utils import find_gitmini_root

GITMINI_DIR = '.gitmini'

class TestFindGitminiRoot(unittest.TestCase):

    # Clean up .gitmini before each test
    def setUp(self):
        self.start_dir = os.getcwd()
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

    # Clean up .gitmini after each test
    def tearDown(self):
        os.chdir(self.start_dir)
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

    def test_find_gitmini_root_success(self):
        """ Test that find_gitmini_root correctly finds .gitmini """
        os.makedirs(GITMINI_DIR)
        root = find_gitmini_root()
        self.assertEqual(root, os.getcwd())

    def test_find_gitmini_root_failure(self):
        """ Test that find_gitmini_root exits when .gitmini is missing without printing to console """
        stderr_backup = sys.stderr
        sys.stderr = io.StringIO()  # Suppress error output
        try:
            with self.assertRaises(SystemExit) as cm:
                find_gitmini_root()
            self.assertEqual(cm.exception.code, 1)
        finally:
            sys.stderr = stderr_backup
