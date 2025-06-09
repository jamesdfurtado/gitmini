import os
from gitmini.utils import compute_sha1
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR


class TestAdd(GitMiniTestCase):

    def setUp(self):
        super().setUp()
        self.run_gitmini(['init'])

    def test_help(self):
        """ Test that 'gitmini add --help'  print usage info. """
        result = self.run_gitmini(['add', '--help'])
        self.assertIn('usage: gitmini add', result.stdout)

    def test_add_single_file_creates_blob_and_index(self):
        """ Ensure that blob is created and index is updated appropriately. """
        filename = 'file.txt'
        content = b'hello world'
        with open(filename, 'wb') as f:
            f.write(content)

        self.run_gitmini(['add', filename])

        expected_hash = compute_sha1(content)
        blob_path = os.path.join(GITMINI_DIR, 'objects', expected_hash)
        self.assertTrue(os.path.exists(blob_path))

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            index_content = f.read()
        self.assertIn(f'{expected_hash} {filename}', index_content)

    def test_add_dot_stages_all_files(self):
        """ Adding '.' stages all files in CWD """
        with open('a.txt', 'w') as f:
            f.write('A')
        with open('b.txt', 'w') as f:
            f.write('B')
        os.makedirs('sub', exist_ok=True)
        with open('sub/c.txt', 'w') as f:
            f.write('C')

        self.run_gitmini(['add', '.'])

        with open(os.path.join(GITMINI_DIR, 'index'), 'r') as f:
            lines = f.read().splitlines()

        indexed_paths = [line.split(" ", 1)[1] for line in lines]

        self.assertIn('a.txt', indexed_paths)
        self.assertIn('b.txt', indexed_paths)
        self.assertIn(os.path.normpath('sub/c.txt'), map(os.path.normpath, indexed_paths))
        self.assertTrue(all('.gitmini' not in path for path in indexed_paths if path != '.gitmini-ignore'))

# Could add tests to ensure that .gitmini is not staged 