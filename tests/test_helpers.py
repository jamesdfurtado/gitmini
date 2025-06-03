import os
import shutil
import unittest

GITMINI_DIR = '.gitmini'

class GitMiniTestCase(unittest.TestCase):
    """Base test case for GitMini CLI commands. Ensures a clean .gitmini/ repo state before and after each test."""

    # Clean up .gitmini before each test
    def setUp(self):
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

    # Clean up .gitmini after each test
    def tearDown(self):
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)
