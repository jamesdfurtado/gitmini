import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR

class TestInitCommand(GitMiniTestCase):


    def test_init_stub(self):
        """ Test that 'gitmini init' initializes .gitmini repo correctly """
        result = self.run_gitmini(['init'])

        self.assertIn("Initialized empty GitMini repository in .gitmini/", result.stdout)
        self.assertTrue(os.path.isdir(GITMINI_DIR))
        self.assertTrue(os.path.isdir(os.path.join(GITMINI_DIR, 'objects')))
        self.assertTrue(os.path.isdir(os.path.join(GITMINI_DIR, 'logs')))
        self.assertTrue(os.path.isfile(os.path.join(GITMINI_DIR, 'index')))


    def test_already_initialized(self):
        """ Test that 'gitmini init' does not re-init an existing repository """

        self.run_gitmini(['init'])
        result = self.run_gitmini(['init'])
        self.assertIn("GitMini repository already initialized.", result.stdout)


    def test_help(self):
        """ Test that 'gitmini init --help' shows help msg """

        result = self.run_gitmini(['init', '--help'])
        self.assertIn("usage: gitmini init", result.stdout)
        self.assertIn("Initialize a new GitMini repository in the current directory.", result.stdout)
