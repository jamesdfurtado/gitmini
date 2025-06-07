import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestInit(GitMiniTestCase):

    def test_help(self):
        """ 'gitmini init --help' prints help msg. """
        result = self.run_gitmini(['init', '--help'])
        self.assertIn('usage: gitmini init', result.stdout)
        self.assertIn('Initialize a new GitMini repository', result.stdout)

    def test_success_creates_repo(self):
        """ Init creates a new GitMini repository. """
        result = self.run_gitmini(['init'])
        self.assertTrue(os.path.isdir(GITMINI_DIR))
        self.assertIn('Initialized empty GitMini repository', result.stdout)

    def test_reinit_errors(self):
        """ Trying to init when .gitmini/ exists should raise an error. """
        self.run_gitmini(['init'])
        result = self.run_gitmini(['init'])
        self.assertIn('fatal: reinitialized existing GitMini repository', result.stdout)
        self.assertNotEqual(result.returncode, 0)
