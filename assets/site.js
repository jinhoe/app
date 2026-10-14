// Screenshot carousel: show prev/next buttons when the strip overflows.
for (const root of document.querySelectorAll("[data-carousel]")) {
  const track = root.querySelector(".shots-track");
  const nav = root.querySelector(".shots-nav");
  const [prev, next] = nav.querySelectorAll("button");
  const smooth = matchMedia("(prefers-reduced-motion: no-preference)").matches ? "smooth" : "auto";

  const update = () => {
    const max = track.scrollWidth - track.clientWidth - 2;
    nav.hidden = max <= 0;
    prev.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft >= max;
  };

  for (const btn of [prev, next]) {
    btn.addEventListener("click", () =>
      track.scrollBy({ left: Number(btn.dataset.dir) * track.clientWidth * 0.8, behavior: smooth }));
  }
  track.addEventListener("scroll", update, { passive: true });
  addEventListener("resize", update);
  update();
}

// Appearance toggle: light → dark → auto, remembered per visitor (same as jinhoe.com).
(function () {
  const root = document.documentElement;
  const order = ["light", "dark", "auto"];
  const names = { light: "Light", dark: "Dark", auto: "Auto" };
  const colors = { light: "#EBEAE6", dark: "#161615" };
  const metas = document.querySelectorAll('meta[name="theme-color"]');
  const current = () => (order.includes(root.dataset.theme) ? root.dataset.theme : "auto");
  const next = (m) => order[(order.indexOf(m) + 1) % order.length];

  const sync = () => {
    const m = current();
    const text = `Appearance: ${names[m]}. Switch to ${names[next(m)]}`;
    for (const btn of document.querySelectorAll(".theme-toggle")) {
      btn.setAttribute("aria-label", text);
      btn.title = text;
    }
    // Keep the browser toolbar colour in step with a forced theme.
    metas.forEach((meta, i) => meta.setAttribute("content", m === "auto" ? Object.values(colors)[i] : colors[m]));
  };

  for (const btn of document.querySelectorAll(".theme-toggle")) {
    btn.addEventListener("click", () => {
      const m = next(current());
      root.dataset.theme = m;
      try { localStorage.setItem("theme", m); } catch (e) {}
      sync();
    });
  }
  sync();
})();
