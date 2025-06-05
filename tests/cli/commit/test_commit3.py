import os
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR

class TestCommitCommand2(GitMiniTestCase):
    def test_commit_object_is_stored_correctly(self):
        """ Test that a new commit object is created in .gitmini/objects/ """

        self.run_gitmini(['init'])

        # Simulate a staged file
        index_path = os.path.join(GITMINI_DIR, "index")
        with open(index_path, "w") as f:
            f.write("abc123 file1.txt\n")

        result = self.run_gitmini(['commit', '-m', 'Store test'])

        # Extract commit hash from stdout
        self.assertIn("Commit object written to:", result.stdout)
        commit_line = [line for line in result.stdout.splitlines() if "Commit object written to:" in line][0]
        commit_hash = os.path.basename(commit_line.strip().split(":")[-1])

        # Confirm object file exists
        object_path = os.path.join(GITMINI_DIR, "objects", commit_hash)
        self.assertTrue(os.path.exists(object_path))

        # Confirm contents include metadata and file
        with open(object_path, "rb") as f:
            contents = f.read().decode()
        self.assertIn("message Store test", contents)
        self.assertIn("abc123 file1.txt", contents)


def test_duplicate_commit_does_not_overwrite(self):
    """ Test that identical commits produce same hash and do not overwrite object """

    self.run_gitmini(['init'])

    # Set up a consistent parent commit in HEAD so both commits have the same parent
    head_path = os.path.join(GITMINI_DIR, "HEAD")
    with open(head_path, "w") as f:
        f.write("parentcommit123456789abcdef")

    # Stage a file
    index_path = os.path.join(GITMINI_DIR, "index")
    with open(index_path, "w") as f:
        f.write("abc123 file1.txt\n")

    # Fix the 'wrong timestamp' bug
    import gitmini.commands.commit as commit_module
    original_datetime = commit_module.datetime
    
    # Simulate metadata
    class MockDateTime:
        @staticmethod
        def now():
            class FixedDateTime:
                @staticmethod
                def isoformat():
                    return "2025-06-05T12:00:00"
            return FixedDateTime()
    commit_module.datetime = type('MockModule', (), {'datetime': MockDateTime})()
    
    try:
        result1 = self.run_gitmini(['commit', '-m', 'Repeatable commit'])
        path_line = [line for line in result1.stdout.splitlines() if "Commit object written to:" in line][0]
        commit_hash = os.path.basename(path_line.strip().split(":")[-1])
        object_path = os.path.join(GITMINI_DIR, "objects", commit_hash)

        with open(object_path, "rb") as f:
            contents1 = f.read()

        # Reset HEAD to the same parent and re-stage files
        with open(head_path, "w") as f:
            f.write("parentcommit123456789abcdef")
        
        with open(index_path, "w") as f:
            f.write("abc123 file1.txt\n")

        result2 = self.run_gitmini(['commit', '-m', 'Repeatable commit'])

        with open(object_path, "rb") as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)
        self.assertIn("Commit already exists in object store.", result2.stdout)
        
    finally:
        # Restore original datetime
        commit_module.datetime = original_datetime