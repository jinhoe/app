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
