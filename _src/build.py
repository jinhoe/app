#!/usr/bin/env python3
"""Build app.jinhoe.com.

    python3 _src/build.py

Reads _src/apps.json, _src/layout.html and the page fragments in _src/,
and writes index.html files into the repo root, where GitHub Pages serves
them as-is. Standard library only. Jekyll ignores _src/ (leading underscore).

Add an app: append it to apps.json, add _src/<slug>/{overview,support,privacy}.html,
put icon.png, favicon.png and screenshots/N.jpg in /<slug>/, then rebuild.
"""
import hashlib
import json
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import quote

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
DATA = json.loads((SRC / "apps.json").read_text(encoding="utf-8"))
SITE, APPS = DATA["site"], DATA["apps"]
LAYOUT = Template((SRC / "layout.html").read_text(encoding="utf-8"))
CSS_VERSION = hashlib.sha256((ROOT / "assets/site.css").read_bytes()).hexdigest()[:8]

# (path segment, nav label, fragment name)
PAGES = (("", "Overview", "overview"), ("support", "Support", "support"), ("privacy", "Privacy", "privacy"))

ICON = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
ARROW_OUT = ICON.format(s=14, w=2, d='<path d="M7 17 17 7"/><path d="M8 7h9v9"/>')
ARROW_BACK = ICON.format(s=14, w=2, d='<path d="M19 12H5"/><path d="m11 18-6-6 6-6"/>')
ARROW_NEXT = ICON.format(s=22, w=1.75, d='<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>')


def fragment(path, **values):
    return Template((SRC / path).read_text(encoding="utf-8")).safe_substitute(values)


def write(rel, **values):
    out = ROOT / rel / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(LAYOUT.substitute(version=CSS_VERSION, **values), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


def url(path):
    return SITE["url"] + path


# ---------- hub ----------

def hub_header():
    return f"""<header class="wrap site-header">
<a class="wordmark" href="/">jinhoe<span>/apps</span></a>
<a class="mono ext" href="{SITE['home']}">jinhoe.com{ARROW_OUT}</a>
</header>"""


def hub_footer():
    return f"""<footer class="site-footer"><div class="wrap">
<span>© {escape(SITE['author'])}</span>
<a href="{SITE['home']}">jinhoe.com</a>
</div></footer>"""


def card(app):
    s = app["slug"]
    return f"""<a class="card" href="/{s}/" style="--accent:{app['accent']}">
<div class="card-head">
<img src="/{s}/icon.png" alt="" width="64" height="64">
<div><h3>{escape(app['name'])}</h3><span class="mono muted">{escape(app['platforms'])}</span></div>
{ARROW_NEXT}
</div>
<p>{escape(app['summary'])}</p>
<div class="card-shot"><img src="/{s}/screenshots/1.jpg" alt="" width="236" loading="lazy"></div>
</a>"""


def build_home():
    write(
        "",
        html_attrs="",
        title=escape(SITE["title"]),
        description=escape(SITE["description"]),
        canonical=url("/"),
        head_extra="",
        header=hub_header(),
        content=fragment("home.html", cards="\n".join(card(a) for a in APPS), count=f"{len(APPS):02d}"),
        footer=hub_footer(),
    )


# ---------- app mini-sites ----------

def app_header(app, current):
    s, name = app["slug"], escape(app["name"])
    current_attr = ' aria-current="page"'
    links = "".join(
        f'<a href="/{s}/{seg + "/" if seg else ""}"{current_attr if seg == current else ""}>{label}</a>'
        for seg, label, _ in PAGES
    )
    return f"""<header class="app-header"><div class="wrap">
<a class="brand" href="/{s}/"><img src="/{s}/icon.png" alt="" width="34" height="34">{name}</a>
<nav class="app-nav" aria-label="{name}">{links}<span class="sep" aria-hidden="true"></span><a class="back" href="/">{ARROW_BACK}All apps</a></nav>
</div></header>"""


def app_footer(app):
    s, name = app["slug"], escape(app["name"])
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-app">
<a class="brand" href="/{s}/"><img src="/{s}/icon.png" alt="" width="24" height="24">{name}</a>
<a href="/{s}/support/">Support</a>
<a href="/{s}/privacy/">Privacy</a>
</div>
<div class="footer-links mono">
<a href="/">app.jinhoe.com</a>
<a href="{SITE['home']}">jinhoe.com</a>
</div>
</div></footer>"""


def badge(app):
    if not app.get("app_store"):
        return ""
    return (f'<a class="badge" href="{app["app_store"]}">'
            f'<img src="/assets/app-store-badge.svg" alt="Download {escape(app["name"])} on the App Store" width="144" height="48"></a>')


def shots(app):
    s, n, name = app["slug"], app["screenshots"], escape(app["name"])
    lazy = ' loading="lazy"'
    imgs = "\n".join(
        f'<img src="/{s}/screenshots/{i}.jpg" alt="{name} screenshot {i} of {n}" width="264" height="574"{lazy if i > 3 else ""}>'
        for i in range(1, n + 1)
    )
    return f'<section class="shots" aria-label="Screenshots"><div class="wrap shots-track" tabindex="0">\n{imgs}\n</div></section>'


def build_app(app):
    s, name = app["slug"], app["name"]
    titles = {
        "": (app["title"], app["description"]),
        "support": (f"Support – {name}", f"Help and contact for {name}."),
        "privacy": (f"Privacy Policy – {name}", f"How {name} handles your data."),
    }
    values = {
        "name": escape(name),
        "slug": s,
        "badge": badge(app),
        "shots": shots(app),
        "support_form": escape(SITE["support_form"] + quote(name)),
    }
    head = (f'<meta property="og:image" content="{url(f"/{s}/icon.png")}">\n'
            f'<link rel="icon" href="/{s}/favicon.png">\n'
            f'<link rel="apple-touch-icon" href="/{s}/icon.png">')
    for seg, _, frag in PAGES:
        title, desc = titles[seg]
        path = f"/{s}/" + (f"{seg}/" if seg else "")
        write(
            f"{s}/{seg}".rstrip("/"),
            html_attrs=f' style="--accent:{app["accent"]}"',
            title=escape(title),
            description=escape(desc),
            canonical=url(path),
            head_extra=head,
            header=app_header(app, seg),
            content=fragment(f"{s}/{frag}.html", **values),
            footer=app_footer(app),
        )


if __name__ == "__main__":
    build_home()
    for a in APPS:
        build_app(a)
