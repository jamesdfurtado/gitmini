import os
import shutil
import unittest
import subprocess
import sys

# Allows running CLI commands as if we were in the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

GITMINI_DIR = '.gitmini'
TEST_ENV_DIR = os.path.join('tests', 'test_env')


class GitMiniTestCase(unittest.TestCase):
    # Clean up .gitmini before tests
    def setUp(self):
        self._original_cwd = os.getcwd()
        self.repo_dir = os.path.abspath(TEST_ENV_DIR)  # Absolute path to test_env
        os.chdir(self.repo_dir)

        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

    # Clean up .gitmini after tests
    def tearDown(self):
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

        os.chdir(self._original_cwd)

    def run_gitmini(self, args):
        """Run 'gitmini' inside test environment folder"""
        env = os.environ.copy()
        env['PYTHONPATH'] = self._original_cwd

        # This does 'python -m gitmini' for us to avoid repitition
        return subprocess.run(
            ['python', '-m', 'gitmini'] + args,
            cwd=self.repo_dir,              # run the command inside test environment
            env=env,                        # ensure .gitmini is findable
            capture_output=True,
            text=True
        )
