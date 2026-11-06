"""Checks on the built site in docs/. Run `python build.py` first, then `pytest`."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT))
from content import PROJECTS, SITE_URL  # noqa: E402

PAGES = sorted(DOCS.rglob("*.html"))
INDEXED = [p for p in PAGES if p.name != "404.html"]


class Page(HTMLParser):
    """Collect the tags the SEO checks care about."""

    def __init__(self, path):
        super().__init__()
        self.meta, self.links, self.images, self.h1, self.ld = {}, [], [], 0, []
        self.title, self.canonical, self.lang = "", None, None
        self._in = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "meta" and ("name" in a or "property" in a):
            self.meta[a.get("name") or a.get("property")] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a["href"]
        elif tag == "link" and "href" in a:
            self.links.append(a["href"])
        elif tag == "a":
            self.links.append(a.get("href", ""))
        elif tag == "img":
            self.images.append(a)
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self._in = "title"
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in = "ld"

    def handle_endtag(self, tag):
        if tag in ("title", "script"):
            self._in = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "ld":
            self.ld.append(data)


def local_target(href):
    """Map an internal link to its file in docs/, or None for external links."""
    if not href.startswith("/"):
        return None
    path = href.split("#")[0].lstrip("/")
    target = DOCS / path
    return target / "index.html" if target.is_dir() or not path else target


@pytest.mark.parametrize("path", INDEXED, ids=lambda p: str(p.relative_to(DOCS)))
def test_page_metadata(path):
    page = Page(path)
    assert page.lang == "en"
    assert 20 <= len(page.title) <= 60, page.title
    assert 70 <= len(page.meta["description"]) <= 160, len(page.meta["description"])
    assert page.h1 == 1
    relative = path.relative_to(DOCS).parent.as_posix()
    expected = f"{SITE_URL}/" if relative == "." else f"{SITE_URL}/{relative}/"
    assert page.canonical == expected
    for key in ("og:title", "og:description", "og:image", "twitter:card"):
        assert page.meta.get(key)
    image = page.meta["og:image"].removeprefix(f"{SITE_URL}/")
    assert (DOCS / image).exists(), image
    assert json.loads("".join(page.ld))  # structured data parses


@pytest.mark.parametrize("path", PAGES, ids=lambda p: str(p.relative_to(DOCS)))
def test_links_and_images(path):
    page = Page(path)
    for href in page.links:
        target = local_target(href)
        assert target is None or target.exists(), href
    for image in page.images:
        assert image.get("alt"), image
        assert image.get("width") and image.get("height")
        assert (DOCS / image["src"].lstrip("/")).exists()


def test_sitemap_and_robots():
    urls = re.findall(r"<loc>(.+?)</loc>", (DOCS / "sitemap.xml").read_text(encoding="utf-8"))
    assert len(urls) == len(INDEXED) == len(PROJECTS) + 1
    assert f"Sitemap: {SITE_URL}/sitemap.xml" in (DOCS / "robots.txt").read_text(encoding="utf-8")


def test_404_is_not_indexed():
    assert Page(DOCS / "404.html").meta.get("robots") == "noindex"


@pytest.mark.parametrize("slug", PROJECTS)
def test_metrics_appear_in_project_readme(slug):
    """No figure on the site may differ from what the project itself reports."""
    readme = ROOT.parent / slug / "README.md"
    if not readme.exists():
        pytest.skip("project repo is not checked out alongside this one")
    text = readme.read_text(encoding="utf-8")
    for value, _label in PROJECTS[slug]["metrics"]:
        assert value in text, f"{slug}: {value}"
