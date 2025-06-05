import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestCommitCommand1(GitMiniTestCase):

    def test_help(self):
        """ Test that 'gitmini commit --help' shows help msg """

        result = self.run_gitmini(['commit', '--help'])
        self.assertIn("usage: gitmini commit", result.stdout)
        self.assertIn("Record a new commit with the current staged files.", result.stdout)


    def test_without_repo(self):
        """ Test that 'gitmini commit' fails when .gitmini is missing """

        result = self.run_gitmini(['commit'])
        self.assertIn("fatal: not a gitmini repository", result.stderr)


    def test_with_repo_but_no_index(self):
        """ Test that 'gitmini commit' reports no staged changes if index is missing """

        self.run_gitmini(['init'])

        index_path = os.path.join(GITMINI_DIR, "index")
        if os.path.exists(index_path):
            os.remove(index_path)

        result = self.run_gitmini(['commit'])
        self.assertIn("Nothing to commit: staging area is missing.", result.stdout)



    def test_with_empty_index(self):
        """ Test that 'gitmini commit' reports no staged changes if index is empty """

        self.run_gitmini(['init'])

        # Manually create empty index file
        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            pass

        result = self.run_gitmini(['commit'])
        self.assertIn("Nothing to commit: staging area is empty.", result.stdout)


    def test_with_nonempty_index(self):
        """ Test that 'gitmini commit' detects staged files in index """

        self.run_gitmini(['init'])

        # Create a fake staged file entry
        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("deadbeef1234567890abcdef file.txt\n")

        result = self.run_gitmini(['commit'])
        self.assertIn("Staged files found. Proceeding with commit...", result.stdout)

    def test_commit_reads_index_entries(self):
        """ Test that 'gitmini commit' correctly parses index entries """

        self.run_gitmini(['init'])

        # Write example entries into the index
        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("abc123 file1.txt\n")
            f.write("def456 dir/file2.txt\n")

        result = self.run_gitmini(['commit'])
        self.assertIn("Staged files found. Proceeding with commit...", result.stdout)



