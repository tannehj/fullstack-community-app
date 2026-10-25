"""Bounded retrieval of public HTML from explicitly supported official hosts."""
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit, urljoin
from urllib.request import Request, HTTPRedirectHandler, build_opener
import socket

from flask import Blueprint, jsonify, request

ALLOWED_HOSTS = {"www.uscis.gov", "uscis.gov", "www.usa.gov", "usa.gov", "www.irs.gov", "irs.gov"}
MAX_BYTES = 2_000_000
resources = Blueprint("resources", __name__)


class SourceError(ValueError):
    pass


def validate_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        raise SourceError("Enter a supported official HTTPS link.")
    try:
        url = urlsplit(value.strip())
        valid = (url.scheme == "https" and url.hostname in ALLOWED_HOSTS
                 and not url.username and not url.password and url.port in (None, 443))
    except ValueError:
        valid = False
    if not valid:
        raise SourceError("Use an HTTPS page from USCIS, USA.gov, or IRS.gov.")
    return urlunsplit((url.scheme, url.netloc, url.path or "/", url.query, ""))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ArticleParser(HTMLParser):
    """Return plain text, preferring the page's main/article content."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = []
        self.body = []
        self.main = []

    def handle_starttag(self, tag, attrs):
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            reverse_index = self.stack[::-1].index(tag)
            del self.stack[len(self.stack) - reverse_index - 1:]

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if "title" in self.stack:
            self.title.append(text)
        if any(tag in self.stack for tag in ("script", "style", "nav", "header", "footer", "noscript", "template", "head")):
            return
        if "body" in self.stack:
            self.body.append(text)
            if "main" in self.stack or "article" in self.stack:
                self.main.append(text)


def retrieve_source(value):
    url = validate_url(value)
    opener = build_opener(NoRedirect())
    for attempt in range(4):
        try:
            response = opener.open(Request(url, headers={"User-Agent": "ImmigrantsHub/0.1", "Accept": "text/html"}), timeout=12)
        except HTTPError as error:
            if error.code in {301, 302, 303, 307, 308} and error.headers.get("Location") and attempt < 3:
                url = validate_url(urljoin(url, error.headers["Location"]))
                error.close()
                continue
            error.close()
            raise SourceError("The source could not be retrieved. Try another official page.") from error
        except (URLError, TimeoutError, socket.timeout) as error:
            raise SourceError("The source did not respond. Please try again later.") from error
        with response:
            if response.headers.get_content_type() != "text/html":
                raise SourceError("Only HTML articles are supported right now. PDF support comes later.")
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise SourceError("This page is too large. Try a shorter article.")
            encoding = response.headers.get_content_charset() or "utf-8"
            try:
                html = raw.decode(encoding, errors="replace")
            except LookupError:
                html = raw.decode("utf-8", errors="replace")
        parser = ArticleParser()
        parser.feed(html)
        text = "\n\n".join(parser.main or parser.body)
        if len(text) < 100:
            raise SourceError("This page did not provide enough readable text. Try another article.")
        return {"title": " ".join(parser.title) or "Official source", "url": url,
                "text": text, "retrieved_at": datetime.now(timezone.utc).isoformat()}
    raise SourceError("Too many source redirects.")


@resources.route("/resources/source", methods=["POST"])
def source():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object containing a source URL."), 400
    try:
        return jsonify(retrieve_source(data.get("url")))
    except SourceError as error:
        return jsonify(error=str(error)), 400
    except (OSError, TimeoutError):
        return jsonify(error="The connection to the source was interrupted. Please try again."), 502
