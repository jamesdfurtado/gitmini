import os
import json
import unittest
from unittest import mock
from tests.test_helpers import GitMiniTestCase, GITMINI_DIR
from gitmini.commands.push import handle_push

class TestPushCommand(GitMiniTestCase):
    def setUp(self):
        super().setUp()
        self.config_path = os.path.join(GITMINI_DIR, 'config.json')
        self.head_path = os.path.join(GITMINI_DIR, 'HEAD')
        self.heads_dir = os.path.join(GITMINI_DIR, 'refs', 'heads')
        os.makedirs(self.heads_dir, exist_ok=True)

    def _write_config(self, config):
        os.makedirs(GITMINI_DIR, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def _write_head(self, ref):
        with open(self.head_path, 'w') as f:
            f.write(ref)

    def _write_branch(self, branch):
        with open(os.path.join(self.heads_dir, branch), 'w') as f:
            f.write('dummy commit hash')

    def _write_remote_branches(self, branches):
        refs_dir = os.path.join(GITMINI_DIR, 'refs')
        os.makedirs(refs_dir, exist_ok=True)
        with open(os.path.join(refs_dir, 'remote_branches.json'), 'w') as f:
            json.dump(branches, f)

    def _write_commit_object(self, commit_hash, tree_hash=None, parent_hash=None, message="test commit"):
        objects_dir = os.path.join(GITMINI_DIR, 'objects')
        os.makedirs(objects_dir, exist_ok=True)
        lines = []
        if tree_hash:
            lines.append(f"tree {tree_hash}")
        if parent_hash:
            lines.append(f"parent {parent_hash}")
        lines.append("timestamp 2025-07-17 14:28:50 (unix: 1752776930)")
        lines.append("")
        lines.append(message)
        with open(os.path.join(objects_dir, commit_hash), 'w') as f:
            f.write("\n".join(lines))

    def _write_tree_object(self, tree_hash, entries=None):
        objects_dir = os.path.join(GITMINI_DIR, 'objects')
        os.makedirs(objects_dir, exist_ok=True)
        lines = []
        if entries:
            for sha, path in entries:
                lines.append(f"{sha} {path}")
        with open(os.path.join(objects_dir, tree_hash), 'w') as f:
            f.write("\n".join(lines))


    @mock.patch('gitmini.commands.push.httpx.post')
    def test_successful_push_with_explicit_branch(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_branch('main')
        self._write_remote_branches({'main': 'remotecommit123'})
        # Write minimal commit object for localcommit456
        self._write_commit_object('localcommit456', tree_hash='treehash456')
        self._write_tree_object('treehash456')
        with open(os.path.join(self.heads_dir, 'main'), 'w') as f:
            f.write('localcommit456')

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful', 'most_recent_remote_branch_commit': 'localcommit456'}
        class Args: branch = 'main:main'
        handle_push(Args())

        # Check remote_branches.json updated
        with open(os.path.join(GITMINI_DIR, 'refs', 'remote_branches.json')) as f:
            branches = json.load(f)
        self.assertEqual(branches['main'], 'localcommit456')


    @mock.patch('gitmini.commands.push.httpx.post')
    def test_successful_push_with_default_branch(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/dev')
        self._write_branch('dev')
        self._write_remote_branches({'dev': 'remotecommit789'})
        self._write_commit_object('localcommit999', tree_hash='treehash999')
        self._write_tree_object('treehash999')
        with open(os.path.join(self.heads_dir, 'dev'), 'w') as f:
            f.write('localcommit999')

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful', 'most_recent_remote_branch_commit': 'localcommit999'}
        class Args: branch = None
        handle_push(Args())

        with open(os.path.join(GITMINI_DIR, 'refs', 'remote_branches.json')) as f:
            branches = json.load(f)
        self.assertEqual(branches['dev'], 'localcommit999')


    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_config_json(self, mock_post):
        """ Missing config.json causes fatal error. """
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        class Args: branch = 'main:main'
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_required_fields_in_config(self, mock_post):
        """ Missing username, api_key, or repo in config.json causes fatal error. """
        # Missing username
        self._write_config({'api_key': 'rawkey', 'repo': 'my-repo'})
        class Args: branch = 'main:main'
        with self.assertRaises(SystemExit):
            handle_push(Args())
        # Missing api_key
        self._write_config({'username': 'testuser', 'repo': 'my-repo'})
        with self.assertRaises(SystemExit):
            handle_push(Args())
        # Missing repo
        self._write_config({'username': 'testuser', 'api_key': 'rawkey'})
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_head_file(self, mock_post):
        """ Missing HEAD file causes fatal error when no branch argument is given. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        if os.path.exists(self.head_path):
            os.remove(self.head_path)
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_detached_head(self, mock_post):
        """ Detached HEAD triggers fatal error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('123456789abcdef')  # Not a ref
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_missing_local_branch(self, mock_post):
        """ Local branch file missing triggers fatal error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        # Do NOT create refs/heads/main
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_auth_error(self, mock_post):
        """ Server returns authentication error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Authentication failed'}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_repo_not_found(self, mock_post):
        """ Server returns repo not found or access denied. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 404
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Repository not found or access denied'}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_branch_not_found(self, mock_post):
        """ Server returns branch not found. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 404
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Remote branch not found.'}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_server_malformed_payload(self, mock_post):
        """ Server returns malformed payload error. """
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        mock_post.return_value.status_code = 422
        mock_post.return_value.json.return_value = {'detail': [{'msg': 'field required', 'loc': ['body', 'branch']}]}
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_colon_remote_only(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        self._write_remote_branches({'main': 'remotecommitcol'})
        # Write minimal commit object for localcommitcol
        self._write_commit_object('localcommitcol', tree_hash='treehashcol')
        self._write_tree_object('treehashcol')
        with open(os.path.join(self.heads_dir, 'main'), 'w') as f:
            f.write('localcommitcol')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful', 'most_recent_remote_branch_commit': 'localcommitcol'}
        class Args: branch = ':remote'
        handle_push(Args())
        with open(os.path.join(GITMINI_DIR, 'refs', 'remote_branches.json')) as f:
            branches = json.load(f)
        self.assertEqual(branches['main'], 'localcommitcol')

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_non_current_local_branch(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('feature')
        self._write_remote_branches({'main': 'remotecommitmain', 'feature': 'remotefeature'})
        # Write minimal commit object for localcommitfeature
        self._write_commit_object('localcommitfeature', tree_hash='treehashfeature')
        self._write_tree_object('treehashfeature')
        with open(os.path.join(self.heads_dir, 'feature'), 'w') as f:
            f.write('localcommitfeature')
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful', 'most_recent_remote_branch_commit': 'localcommitfeature'}
        class Args: branch = 'feature:main'
        handle_push(Args())
        with open(os.path.join(GITMINI_DIR, 'refs', 'remote_branches.json')) as f:
            branches = json.load(f)
        self.assertEqual(branches['main'], 'localcommitfeature')

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_payload_includes_commits_explicit_branch(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_branch('main')
        self._write_remote_branches({'main': 'remotecommit123'})
        self._write_commit_object('localcommit456', tree_hash='treehash456')
        self._write_tree_object('treehash456')
        with open(os.path.join(self.heads_dir, 'main'), 'w') as f:
            f.write('localcommit456')

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful', 'most_recent_remote_branch_commit': 'localcommit456'}
        class Args: branch = 'main:main'
        handle_push(Args())

        sent_payload = mock_post.call_args[1]['files']
        self.assertEqual(sent_payload['last_known_remote_commit'][1], 'remotecommit123')
        self.assertEqual(sent_payload['new_commit'][1], 'localcommit456')


    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_payload_includes_commits_default_branch(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/dev')
        self._write_branch('dev')
        self._write_remote_branches({'dev': 'remotecommit789'})
        self._write_commit_object('localcommit999', tree_hash='treehash999')
        self._write_tree_object('treehash999')
        with open(os.path.join(self.heads_dir, 'dev'), 'w') as f:
            f.write('localcommit999')

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok', 'message': 'Push successful', 'most_recent_remote_branch_commit': 'localcommit999'}
        class Args: branch = None
        handle_push(Args())

        sent_payload = mock_post.call_args[1]['files']
        self.assertEqual(sent_payload['last_known_remote_commit'][1], 'remotecommit789')
        self.assertEqual(sent_payload['new_commit'][1], 'localcommit999')


    @mock.patch('gitmini.commands.push.httpx.post')
    def test_push_fails_if_remote_branch_missing(self, mock_post):
        """Push fails if remote branch is missing in remote_branches.json."""
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_head('ref: refs/heads/main')
        self._write_branch('main')
        self._write_remote_branches({'otherbranch': 'remotecommit'})
        class Args: branch = None
        with self.assertRaises(SystemExit):
            handle_push(Args())

    @mock.patch('gitmini.commands.push.httpx.post')
    def test_remote_branches_not_updated_on_error(self, mock_post):
        self._write_config({'username': 'testuser', 'api_key': 'rawkey', 'repo': 'my-repo'})
        self._write_branch('main')
        self._write_remote_branches({'main': 'remotecommit123'})
        self._write_commit_object('localcommit456', tree_hash='treehash456')
        self._write_tree_object('treehash456')
        with open(os.path.join(self.heads_dir, 'main'), 'w') as f:
            f.write('localcommit456')

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'error', 'message': 'Non-fast-forward push rejected.', 'most_recent_remote_branch_commit': 'remotecommit123'}
        class Args: branch = 'main:main'
        with self.assertRaises(SystemExit):
            handle_push(Args())

        # Should not update remote_branches.json
        with open(os.path.join(GITMINI_DIR, 'refs', 'remote_branches.json')) as f:
            branches = json.load(f)
        self.assertEqual(branches['main'], 'remotecommit123')
