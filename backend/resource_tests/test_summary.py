import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import summary
from flask import Flask
from resources import resources

SOURCE = {'title': 'Example', 'url': 'https://www.usa.gov/example', 'text': 'Source facts. ' * 20, 'retrieved_at': '2026-10-25'}


class SummaryTests(unittest.TestCase):
    def setUp(self):
        summary._cache.clear()
        summary._attempts.clear()

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self):
        with self.assertRaisesRegex(summary.SummaryError, 'OPENAI_API_KEY'):
            summary.summarize_source(SOURCE)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('summary.build_opener')
    def test_summary_and_cache(self, build):
        build.return_value.open.return_value = io.BytesIO(json.dumps({'status': 'completed', 'output': [
            {'type': 'reasoning'}, {'type': 'message', 'content': [{'type': 'output_text', 'text': 'An easy summary.'}]}]}).encode())
        self.assertEqual(summary.summarize_source(SOURCE), 'An easy summary.')
        self.assertEqual(summary.summarize_source(dict(SOURCE, retrieved_at='later')), 'An easy summary.')
        self.assertEqual(build.return_value.open.call_count, 1)
        req = build.return_value.open.call_args.args[0]
        payload = json.loads(req.data)
        self.assertFalse(payload['store'])
        self.assertEqual(json.loads(payload['input'])['source_text'], SOURCE['text'])
        self.assertNotIn('test-key', json.dumps(payload))

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('summary.build_opener')
    def test_incomplete_not_shown(self, build):
        build.return_value.open.return_value = io.BytesIO(b'{"status":"incomplete","output":[]}')
        with self.assertRaisesRegex(summary.SummaryError, 'not completed'):
            summary.summarize_source(SOURCE)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('summary.build_opener')
    def test_long_source_not_silently_truncated(self, build):
        with self.assertRaisesRegex(summary.SummaryError, 'too long'):
            summary.summarize_source(dict(SOURCE, text='a' * 60_001))
        build.assert_not_called()

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('summary.build_opener')
    def test_provider_error_hides_sensitive_details(self, build):
        build.return_value.open.side_effect = HTTPError('https://api.openai.com/v1/responses', 401, 'secret details', {}, None)
        with self.assertRaisesRegex(summary.SummaryError, 'authenticate') as caught:
            summary.summarize_source(SOURCE)
        self.assertNotIn('secret details', str(caught.exception))

    @patch('resources.retrieve_source', return_value=SOURCE.copy())
    @patch('resources.summarize_source', side_effect=summary.SummaryError('AI unavailable'))
    def test_source_survives_summary_failure(self, summarize, retrieve):
        app = Flask(__name__)
        app.register_blueprint(resources)
        result = app.test_client().post('/resources/source', json={'url': SOURCE['url']})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['text'], SOURCE['text'])
        self.assertEqual(result.json['summary_error'], 'AI unavailable')

    @patch('resources.retrieve_source', return_value=SOURCE.copy())
    @patch('resources.summarize_source', return_value='Simple summary.')
    def test_route_returns_summary_with_source(self, summarize, retrieve):
        app = Flask(__name__)
        app.register_blueprint(resources)
        data = app.test_client().post('/resources/source', json={'url': SOURCE['url']}).json
        self.assertEqual(data['summary'], 'Simple summary.')
        self.assertEqual(data['url'], SOURCE['url'])

if __name__ == '__main__':
    unittest.main()
