import io
import sys
import unittest
from pathlib import Path
from email.message import Message
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from resources import ArticleParser, SourceError, retrieve_source, validate_url, resources
from flask import Flask


class SourceTests(unittest.TestCase):
    def test_reject_untrusted_and_confusing_urls(self):
        for url in [None, '', 'http://www.uscis.gov/a', 'https://localhost/',
                    'https://www.uscis.gov.evil.com/', 'https://www.uscis.gov@evil.com/',
                    'https://user:pass@www.uscis.gov/', 'https://www.uscis.gov:8080/',
                    'https://127.0.0.1/', 'file:///etc/passwd']:
            with self.subTest(url=url), self.assertRaises(SourceError):
                validate_url(url)

    def test_main_content_excludes_scripts_and_navigation(self):
        parser = ArticleParser()
        parser.feed('<html><head><title>Official &amp; useful</title></head><body><nav>Menu</nav><main><p>Article text.</p><script>bad()</script></main><footer>Footer</footer></body></html>')
        self.assertEqual(parser.main, ['Article text.'])
        self.assertEqual(parser.title, ['Official & useful'])

    @patch('resources.build_opener')
    def test_redirect_to_private_host_is_rejected(self, build):
        build.return_value.open.side_effect = HTTPError('https://www.usa.gov/a', 302, 'Moved', {'Location': 'http://127.0.0.1/'}, None)
        with self.assertRaises(SourceError):
            retrieve_source('https://www.usa.gov/a')
        self.assertEqual(build.return_value.open.call_count, 1)

    @patch('resources.build_opener')
    def test_pdf_is_rejected(self, build):
        response = io.BytesIO(b'%PDF')
        response.headers = Message()
        response.headers['Content-Type'] = 'application/pdf'
        build.return_value.open.return_value = response
        with self.assertRaisesRegex(SourceError, 'PDF'):
            retrieve_source('https://www.uscis.gov/form.pdf')

    @patch('resources.build_opener')
    def test_large_response_is_rejected(self, build):
        response = io.BytesIO(b'a' * 2_000_001)
        response.headers = Message()
        response.headers['Content-Type'] = 'text/html'
        build.return_value.open.return_value = response
        with self.assertRaisesRegex(SourceError, 'too large'):
            retrieve_source('https://www.usa.gov/a')

    @patch('resources.build_opener')
    def test_reader_returns_plain_text_and_source(self, build):
        response = io.BytesIO(('<html><head><title>Source title</title></head><body><main><p>' + 'Readable source content. ' * 10 + '</p></main></body></html>').encode())
        response.headers = Message()
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        build.return_value.open.return_value = response
        app = Flask(__name__)
        app.register_blueprint(resources)
        result = app.test_client().post('/resources/source', json={'url': 'https://www.usa.gov/a'})
        self.assertEqual(result.status_code, 200)
        data = result.get_json()
        self.assertEqual(data['title'], 'Source title')
        self.assertNotIn('<p>', data['text'])
        self.assertEqual(data['url'], 'https://www.usa.gov/a')

    def test_invalid_payload(self):
        app = Flask(__name__)
        app.register_blueprint(resources)
        self.assertEqual(app.test_client().post('/resources/source', json=[]).status_code, 400)


if __name__ == '__main__':
    unittest.main()
