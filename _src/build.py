#!/usr/bin/env python3
"""Build app.jinhoe.com.

    python3 _src/build.py

Reads _src/apps.json, _src/layout.html and the page fragments in _src/,
and writes index.html files into the repo root, where GitHub Pages serves
them as-is. Standard library only. Jekyll ignores _src/ (leading underscore).

Add an app: append it to apps.json, add _src/<slug>/{overview,support,privacy}.html,
put icon.png, favicon.png and screenshots/N.jpg in /<slug>/, then rebuild.
iPad screenshots (optional): screenshots/ipad/N.jpg, 900×1200 (shown at 430 wide), with ipad_screenshots in apps.json.
Mac screenshots (optional): screenshots/mac/N.jpg, 1200×750 (shown at 560 wide), with mac_screenshots in apps.json.
"""
import hashlib
import json
import re
from datetime import date
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
JS_VERSION = hashlib.sha256((ROOT / "assets/site.js").read_bytes()).hexdigest()[:8]

# (path segment, nav label, fragment name)
PAGES = (("", "Overview", "overview"), ("support", "Support", "support"), ("privacy", "Privacy", "privacy"))

ICON = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
ARROW_OUT = ICON.format(s=14, w=2, d='<path d="M7 17 17 7"/><path d="M8 7h9v9"/>')
ARROW_BACK = ICON.format(s=14, w=2, d='<path d="M19 12H5"/><path d="m11 18-6-6 6-6"/>')
ARROW_NEXT = ICON.format(s=22, w=1.75, d='<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>')
CHEVRON_L = ICON.format(s=18, w=2, d='<path d="m15 18-6-6 6-6"/>')
# Appearance toggle, same icons and behaviour as jinhoe.com (light → dark → auto).
THEME_TOGGLE = """<button type="button" class="theme-toggle" aria-label="Appearance">
<svg class="theme-icon theme-icon-light" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg>
<svg class="theme-icon theme-icon-dark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>
<svg class="theme-icon theme-icon-auto" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor"/></svg>
</button>"""
CHEVRON_R = ICON.format(s=18, w=2, d='<path d="m9 18 6-6-6-6"/>')


def fragment(path, **values):
    return Template((SRC / path).read_text(encoding="utf-8")).safe_substitute(values)


def external_in_new_tab(page):
    """Links that leave app.jinhoe.com open in a new tab."""
    return re.sub(
        r'<a ([^>]*?)href="(https?://[^"]+)"',
        lambda m: m.group(0) if m.group(2).startswith(SITE["url"]) or "target=" in m.group(1)
        else f'<a {m.group(1)}href="{m.group(2)}" target="_blank" rel="noopener"',
        page,
    )


def write(rel, **values):
    out = ROOT / rel / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    page = LAYOUT.substitute(version=CSS_VERSION, js_version=JS_VERSION, **values)
    out.write_text(external_in_new_tab(page), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


def url(path):
    return SITE["url"] + path


# ---------- hub ----------

def hub_header():
    return f"""<header class="wrap site-header">
<a class="wordmark" href="/">jinhoe<span>/apps</span></a>
{THEME_TOGGLE}
</header>"""


def hub_footer():
    return f"""<footer class="site-footer"><div class="wrap">
<span>© {date.today().year} {escape(SITE['author'])}</span>
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
        content=fragment("home.html", cards="\n".join(card(a) for a in APPS)),
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
<nav class="app-nav" aria-label="{name}">{links}<span class="sep" aria-hidden="true"></span><a class="back" href="/">{ARROW_BACK}All apps</a>{THEME_TOGGLE}</nav>
</div></header>"""


def app_footer(app):
    s, name = app["slug"], escape(app["name"])
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-app">
<a class="brand" href="/{s}/"><img src="/{s}/icon.png" alt="" width="24" height="24">{name}</a>
<a href="/{s}/support/">Support</a>
<a href="/{s}/privacy/">Privacy</a>
</div>
<a class="mono" href="/">All apps by {escape(SITE['author'])}</a>
</div></footer>"""


def badge(app):
    stores = (("app_store", "app-store-badge.svg", "the App Store", 144),
              ("mac_app_store", "mac-app-store-badge.svg", "the Mac App Store", 187))
    return "".join(
        f'<a class="badge" href="{app[key]}">'
        f'<img src="/assets/{svg}" alt="Download {escape(app["name"])} on {store}" width="{w}" height="48"></a>'
        for key, svg, store, w in stores if app.get(key)
    )


def carousel(app, n, folder, platform, size, cls=""):
    s, name = app["slug"], escape(app["name"])
    w, h = size
    lazy = ' loading="lazy"'
    label = platform or "Screenshots"
    what = f"{platform} screenshots" if platform else "Screenshots"
    alt = f"{name} {platform} screenshot" if platform else f"{name} screenshot"
    imgs = "\n".join(
        f'<img{cls} src="/{s}/screenshots/{folder}{i}.jpg" alt="{alt} {i} of {n}" width="{w}" height="{h}"{lazy if folder or i > 3 else ""}>'
        for i in range(1, n + 1)
    )
    hid = f"shots-{folder.rstrip('/') or 'label'}"
    return f"""<section class="shots" aria-labelledby="{hid}" data-carousel>
<div class="wrap shots-bar">
<h2 class="mono" id="{hid}">{label}</h2>
<div class="shots-nav" hidden>
<button type="button" data-dir="-1" aria-label="Previous screenshots">{CHEVRON_L}</button>
<button type="button" data-dir="1" aria-label="Next screenshots">{CHEVRON_R}</button>
</div>
</div>
<div class="shots-track" tabindex="0" aria-label="{what}, scroll sideways for more">
{imgs}
</div>
</section>"""


# Optional extra carousels: (apps.json key prefix and folder, label, display size, img class)
EXTRA_SHOTS = (("ipad", "iPad", (430, 574), "ipad"), ("mac", "Mac", (560, 350), "wide"))


def shots(app):
    """iPhone screenshots/N.jpg, plus iPad (screenshots/ipad/, 3:4) and Mac (screenshots/mac/, 16:10)
    carousels when ipad_screenshots / mac_screenshots are set."""
    extra = [e for e in EXTRA_SHOTS if app.get(f"{e[0]}_screenshots")]
    out = carousel(app, app["screenshots"], "", "iPhone" if extra else "", (264, 574))
    for key, platform, size, cls in extra:
        out += "\n" + carousel(app, app[f"{key}_screenshots"], f"{key}/", platform, size, f' class="{cls}"')
    return out


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
