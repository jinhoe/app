# app.jinhoe.com

Landing site for my apps. Static HTML served by GitHub Pages.

```
_src/apps.json              app list: name, accent colour, App Store link, screenshot count
_src/layout.html            page shell
_src/home.html              hub page body
_src/<slug>/*.html          overview, support and privacy bodies per app
assets/site.css             all styles (light/dark follow the system)
<slug>/icon.png, favicon.png, screenshots/N.jpg
```

Build after editing anything in `_src/` or `assets/site.css`:

```sh
python3 _src/build.py
```

It regenerates every `index.html`; commit the output. No dependencies.

Add an app: add an entry to `_src/apps.json`, create `_src/<slug>/{overview,support,privacy}.html`,
put `icon.png`, `favicon.png` and `screenshots/` in `/<slug>/`, then build.
