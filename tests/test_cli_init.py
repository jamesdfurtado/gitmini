import os
import shutil
import subprocess
import unittest

GITMINI_DIR = '.gitmini'

class TestInitCommand(unittest.TestCase):
    # Clean up .gitmini before each test
    def setUp(self):
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

    # Remove .gitmini after each test
    def tearDown(self):
        if os.path.exists(GITMINI_DIR):
            shutil.rmtree(GITMINI_DIR)

    # Test that 'gitmini init' initializes the correct folder structure and prints confirmation
    def test_cli_init_stub(self):
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'init'],
            capture_output=True,
            text=True
        )
        self.assertIn("Initialized empty GitMini repository in .gitmini/", result.stdout)
        self.assertTrue(os.path.isdir(GITMINI_DIR))
        self.assertTrue(os.path.isdir(os.path.join(GITMINI_DIR, 'objects')))
        self.assertTrue(os.path.isdir(os.path.join(GITMINI_DIR, 'logs')))
        self.assertTrue(os.path.isfile(os.path.join(GITMINI_DIR, 'index')))

    # Test that running 'gitmini init' twice prints an "already initialized" message
    def test_cli_init_already_initialized(self):
        subprocess.run(['python', '-m', 'gitmini', 'init'], capture_output=True, text=True)
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'init'],
            capture_output=True,
            text=True
        )
        self.assertIn("GitMini repository already initialized.", result.stdout)

    # Test that 'gitmini init --help' displays the help message
    def test_cli_init_help(self):
        result = subprocess.run(
            ['python', '-m', 'gitmini', 'init', '--help'],
            capture_output=True,
            text=True
        )
        self.assertIn("usage: gitmini init", result.stdout)
        self.assertIn("Initialize a new GitMini repository in the current directory.", result.stdout)
