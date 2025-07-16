import os
import json
import unittest
from unittest import mock
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini.commands.remote.add import handle_remote_add

class TestRemoteAddCommand(GitMiniTestCase):
    def setUp(self):
        super().setUp()
        self.config_path = os.path.join(GITMINI_DIR, 'config.json')
        self.refs_dir = os.path.join(GITMINI_DIR, 'refs')
        self.remote_branches_path = os.path.join(self.refs_dir, 'remote_branches.json')

    @mock.patch('gitmini.commands.remote.add.httpx.post')
    def test_successful_remote_add(self, mock_post):
        """ Successful remote add updates config.json and remote_branches.json. """

        # Prepare config.json
        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser', 'api_key': 'rawkey'}, f)
        # Mock API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'ok',
            'message': 'Connected to remote',
            'branches': {'main': 'abc123', 'dev': 'def456'}
        }
        class Args: repository = 'my-repo'
        handle_remote_add(Args())
        # Check config.json updated
        with open(self.config_path) as f:
            config = json.load(f)
        self.assertEqual(config['repo'], 'my-repo')
        # Check remote_branches.json written
        with open(self.remote_branches_path) as f:
            branches = json.load(f)
        self.assertEqual(branches, {'main': 'abc123', 'dev': 'def456'})

    @mock.patch('gitmini.commands.remote.add.httpx.post')
    def test_error_response_does_not_update_files(self, mock_post):
        """ Error response does not update config.json or remote_branches.json. """

        # Prepare config.json
        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser', 'api_key': 'rawkey'}, f)
        # Mock API error response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'error',
            'message': 'Authentication failed'
        }
        class Args: repository = 'my-repo'
        with self.assertRaises(SystemExit):
            handle_remote_add(Args())
        # config.json should not have 'repo'
        with open(self.config_path) as f:
            config = json.load(f)
        self.assertNotIn('repo', config)
        # remote_branches.json should not exist
        self.assertFalse(os.path.exists(self.remote_branches_path))

    @mock.patch('gitmini.commands.remote.add.httpx.post')
    def test_missing_config_json(self, mock_post):
        """ Missing config.json causes fatal error. """

        # Ensure config.json does not exist
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        class Args: repository = 'my-repo'
        with self.assertRaises(SystemExit):
            handle_remote_add(Args())

    @mock.patch('gitmini.commands.remote.add.httpx.post')
    def test_missing_username_or_api_key(self, mock_post):
        """ Missing username or api_key in config.json causes fatal error. """

        # Prepare incomplete config.json
        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({'username': 'testuser'}, f)
        class Args: repository = 'my-repo'
        with self.assertRaises(SystemExit):
            handle_remote_add(Args())
        with open(self.config_path, 'w') as f:
            json.dump({'api_key': 'rawkey'}, f)
        with self.assertRaises(SystemExit):
            handle_remote_add(Args()) 