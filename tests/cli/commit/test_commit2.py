import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR

class TestCommitCommand2(GitMiniTestCase):

    def test_commit_includes_timestamp_and_message(self):
        """ Test that commit metadata includes timestamp and message """

        self.run_gitmini(['init'])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("abc123 file1.txt\n")

        result = self.run_gitmini(['commit', '-m', 'Test commit'])
        self.assertIn("date", result.stdout)
        self.assertIn("message Test commit", result.stdout)
        self.assertIn("abc123 file1.txt", result.stdout)


    def test_commit_uses_parent_if_head_exists(self):
        """ Test that commit includes 'parent' field if HEAD exists """

        self.run_gitmini(['init'])

        head_path = os.path.join(GITMINI_DIR, "HEAD")
        with open(head_path, "w") as f:
            f.write("deadbeef1234567890abcdef")

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("abc123 file1.txt\n")

        result = self.run_gitmini(['commit', '-m', 'With parent'])
        self.assertIn("parent deadbeef1234567890abcdef", result.stdout)
        self.assertIn("message With parent", result.stdout)


    def test_commit_omits_parent_if_no_head(self):
        """ Test that commit omits 'parent' field if HEAD is missing """

        self.run_gitmini(['init'])

        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("abc123 file1.txt\n")

        result = self.run_gitmini(['commit', '-m', 'First commit'])
        self.assertNotIn("parent", result.stdout)
        self.assertIn("message First commit", result.stdout)
