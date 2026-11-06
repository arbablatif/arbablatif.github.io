"""Build the static portfolio site into docs/, which GitHub Pages serves.

Usage: python build.py [--repos PATH]

--repos is the folder holding the project repos. Figures are copied from there
when it exists; otherwise the figures already in docs/assets are kept.
Standard library only.
"""
import argparse
import json
import math
import random
import shutil
from html import escape
from pathlib import Path

from content import (ABOUT, EARLIER, GITHUB, GROUPS, HOME, KNOWS_ABOUT, LAST_UPDATED,
                     LINKEDIN, PROJECTS, SITE_URL)

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
AUTHOR = {"@type": "Person", "name": "Arbab Latif", "url": f"{SITE_URL}/"}


def png_size(path):
    """Read width and height from a PNG header, so images reserve their space."""
    head = path.read_bytes()[16:24]
    return int.from_bytes(head[:4], "big"), int.from_bytes(head[4:], "big")


def trace_svg():
    """Decorative hero trace: noise on the left resolving into a clean signal."""
    rng = random.Random(7)  # fixed seed, so rebuilds give identical output
    width, mid, points_noise, points_clean = 880, 36, [], []
    for x in range(0, width + 1, 4):
        clarity = min(1.0, x / (width * 0.62))
        clean = 24 * math.sin(x / 19) * clarity
        noisy = clean + rng.uniform(-26, 26) * (1 - clarity)
        points_noise.append(f"{x},{mid - noisy:.1f}")
        points_clean.append(f"{x},{mid - clean:.1f}")
    split = len(points_clean) // 3
    return (f'<svg class="trace" viewBox="0 0 {width} 72" preserveAspectRatio="none" aria-hidden="true">'
            f'<polyline class="n" fill="none" stroke-width="1.2" points="{" ".join(points_noise[:split * 2])}"/>'
            f'<polyline class="s" fill="none" stroke-width="2" points="{" ".join(points_clean[split:])}"/></svg>')


def page(*, path, title, description, body, schema=None, image="assets/og.png", noindex=False):
    """Wrap page content with the shared head, header and footer."""
    url = f"{SITE_URL}/{path}"
    image_url = f"{SITE_URL}/{image}"
    t, d = escape(title), escape(description)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    canonical = "" if noindex else f'<link rel="canonical" href="{url}">\n'
    ld = ""
    if schema:
        # "<" is escaped so the JSON can never close its script tag.
        ld = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + "</script>\n"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="author" content="Arbab Latif">
<meta name="color-scheme" content="light dark">
{robots}{canonical}<meta property="og:type" content="website">
<meta property="og:site_name" content="Arbab Latif">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{image_url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
{ld}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="/">Arbab Latif</a>
<nav aria-label="Main"><a href="/#work">Work</a><a href="/#about">About</a><a href="/#contact">Contact</a><a href="{GITHUB}">GitHub</a></nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">Arbab Latif. Project code is MIT licensed on <a href="{GITHUB}">GitHub</a>.</div></footer>
</body>
</html>
"""


def project_row(slug):
    """One line in the home page list, led by the project's headline figure."""
    p = PROJECTS[slug]
    value, label = p["metrics"][0]
    return (f'<li><a href="/projects/{slug}/"><div><h3>{escape(p["name"])}</h3><p>{escape(p["summary"])}</p></div>'
            f'<div class="m"><strong>{escape(value)}</strong><span>{escape(label)}</span></div></a></li>')


def home_page():
    groups = "\n".join(
        f'<section class="group"><h2>{escape(name)}</h2><ul class="work">'
        + "".join(project_row(s) for s in slugs) + "</ul></section>"
        for name, slugs in GROUPS)
    earlier = "".join(f'<li><a href="{GITHUB}/{n}">{escape(n)}</a>: {escape(d)}</li>' for n, d in EARLIER)
    about = "".join(f"<p>{escape(x)}</p>" for x in ABOUT)
    body = f"""<section class="hero">
<h1>Dr. Arbab Latif</h1>
<p class="role">{escape(HOME["role"])}</p>
<p class="lede">{escape(HOME["lede"])}</p>
{trace_svg()}
</section>
<div id="work">
{groups}
<section class="group"><h2>Earlier MATLAB work</h2><ul class="plain">{earlier}</ul></section>
</div>
<section class="prose" id="about"><h2>About</h2>{about}</section>
<section class="prose" id="contact"><h2>Contact</h2>
<p>The best way to reach me is <a href="{LINKEDIN}">LinkedIn</a>. All project code is on <a href="{GITHUB}">GitHub</a>.</p></section>"""
    schema = {"@context": "https://schema.org", "@type": "Person", "name": "Arbab Latif",
              "honorificPrefix": "Dr.", "jobTitle": "Applied AI Engineer", "url": f"{SITE_URL}/",
              "sameAs": [GITHUB, LINKEDIN], "knowsAbout": KNOWS_ABOUT}
    return page(path="", title=HOME["title"], description=HOME["description"], body=body, schema=schema)


def items(values, tag="ul"):
    return f"<{tag}>" + "".join(f"<li>{escape(v)}</li>" for v in values) + f"</{tag}>"


def project_page(slug):
    p = PROJECTS[slug]
    repo = f"{GITHUB}/{slug}"
    metrics = "".join(f"<div><dt>{escape(l)}</dt><dd>{escape(v)}</dd></div>" for v, l in p["metrics"])
    figure, image = "", "assets/og.png"
    if "image" in p:
        image = f"assets/projects/{slug}.png"
        w, h = png_size(ROOT / "docs" / image)
        figure = (f'<figure><img src="/{image}" alt="{escape(p["image"]["alt"], quote=True)}" width="{w}" height="{h}" loading="lazy">'
                  f'<figcaption>{escape(p["image"]["caption"])}</figcaption></figure>')
    stack = "".join(f"<li>{escape(s)}</li>" for s in p["stack"])
    related = "".join(project_row(s) for s in p["related"])
    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/#work">Work</a></li><li>{escape(p["name"])}</li></ol></nav>
<article class="project">
<h1>{escape(p["title"])}</h1>
<p class="lede">{escape(p["lede"])}</p>
<p class="actions"><a class="btn primary" href="{repo}">View the code on GitHub</a><a class="btn" href="{repo}#results">Full results</a></p>
<dl class="metrics">{metrics}</dl>
{figure}
<section class="prose"><h2>Problem</h2><p>{escape(p["problem"])}</p></section>
<section class="prose"><h2>Approach</h2>{items(p["approach"])}</section>
<section class="prose"><h2>Results</h2>{items(p["findings"])}</section>
<section class="prose"><h2>Limitations</h2>{items(p["limitations"])}</section>
<section class="prose"><h2>Built with</h2><ul class="stack">{stack}</ul></section>
</article>
<section class="group"><h2>Related projects</h2><ul class="work">{related}</ul></section>"""
    url = f"{SITE_URL}/projects/{slug}/"
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "SoftwareSourceCode", "name": p["name"], "description": p["description"], "url": url,
         "codeRepository": repo, "programmingLanguage": "Python", "author": AUTHOR,
         "license": "https://opensource.org/licenses/MIT"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": p["name"], "item": url}]}]}
    return page(path=f"projects/{slug}/", title=f'{p["title"]} | Arbab Latif', description=p["description"],
                body=body, schema=schema, image=image)


def not_found_page():
    body = '<section class="hero"><h1>Page not found</h1><p class="lede">That page does not exist. <a href="/">Go to the home page</a>.</p></section>'
    return page(path="404.html", title="Page not found | Arbab Latif",
                description="This page does not exist.", body=body, noindex=True)


def sitemap():
    urls = [""] + [f"projects/{s}/" for s in PROJECTS]
    entries = "".join(f"<url><loc>{SITE_URL}/{u}</loc><lastmod>{LAST_UPDATED}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>\n'


def write(relative, text):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def copy_assets(repos):
    """Copy static files, plus one figure per project when the repos are available."""
    for name in ("style.css", "favicon.svg"):
        shutil.copyfile(ROOT / "static" / name, OUT / name)
    (OUT / "assets" / "projects").mkdir(parents=True, exist_ok=True)
    if (ROOT / "static" / "og.png").exists():
        shutil.copyfile(ROOT / "static" / "og.png", OUT / "assets" / "og.png")
    for slug, p in PROJECTS.items():
        source = repos / p["image"]["src"] if "image" in p else None
        if source and source.exists():
            shutil.copyfile(source, OUT / "assets" / "projects" / f"{slug}.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", type=Path, default=ROOT.parent)
    args = parser.parse_args()

    OUT.mkdir(exist_ok=True)
    copy_assets(args.repos)
    write(".nojekyll", "")  # serve the files exactly as built
    write("index.html", home_page())
    write("404.html", not_found_page())
    for slug in PROJECTS:
        write(f"projects/{slug}/index.html", project_page(slug))
    write("sitemap.xml", sitemap())
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Built {len(PROJECTS) + 2} pages in {OUT}")


if __name__ == "__main__":
    main()
