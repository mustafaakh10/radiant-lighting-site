"use strict";
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const fmt = (n) => "PKR " + Number(n).toLocaleString("en-US");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Header: mega menu, search, drawer */
  const hdr = $("#hdr"), mega = $("#mega"), megaBtn = $("#megaBtn"), shade = $("#megaShade");
  const search = $("#search"), searchBtn = $("#searchBtn"), q = $("#q"), sres = $("#sres");
  const drawer = $("#drawer"), menuBtn = $("#menuBtn");
  function closeAll() {
    if (mega) { mega.hidden = true; shade.hidden = true; megaBtn.setAttribute("aria-expanded", "false"); }
    if (search) { search.hidden = true; searchBtn.setAttribute("aria-expanded", "false"); }
  }
  megaBtn && megaBtn.addEventListener("click", () => {
    const open = mega.hidden; closeAll();
    if (open) { shade.style.setProperty("--mega-top", hdr.getBoundingClientRect().bottom + "px"); shade.hidden = false; mega.hidden = false; megaBtn.setAttribute("aria-expanded", "true"); }
  });
  shade && shade.addEventListener("click", closeAll);
  let sTimer;
  async function suggest() {
    try {
      const r = await fetch(sres.dataset.suggest + "?q=" + encodeURIComponent(q.value));
      const { results } = await r.json();
      sres.innerHTML = results.length ? results.map((p) => `<a href="${esc(p.url)}"><span class="th">${p.thumb ? `<img src="${esc(p.thumb)}" alt="">` : ""}</span><span>${esc(p.name)}<small>${esc(p.short)}</small></span></a>`).join("")
        : `<span class="fine">No products found for “${esc(q.value)}”. Try a type such as “strip” or “track”.</span>`;
    } catch (e) { sres.innerHTML = ""; }
  }
  searchBtn && searchBtn.addEventListener("click", () => {
    const open = search.hidden; closeAll();
    if (open) { search.hidden = false; searchBtn.setAttribute("aria-expanded", "true"); suggest(); q.focus(); }
  });
  q && q.addEventListener("input", () => { clearTimeout(sTimer); sTimer = setTimeout(suggest, 180); });
  menuBtn && menuBtn.addEventListener("click", () => { closeAll(); drawer.hidden = false; menuBtn.setAttribute("aria-expanded", "true"); $("#closeBtn").focus(); });
  $("#closeBtn") && $("#closeBtn").addEventListener("click", () => { drawer.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); menuBtn.focus(); });
  drawer && drawer.addEventListener("click", (e) => { if (e.target.closest("a")) { drawer.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); } });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const wasMega = mega && !mega.hidden; closeAll();
    if (drawer && !drawer.hidden) { drawer.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); }
    if (wasMega) megaBtn.focus();
  });

  /* Home on phones: header sits over the hero and turns solid once you scroll */
  if (document.body.classList.contains("home") && hdr) {
    const solid = () => hdr.classList.toggle("solid", scrollY > 24 || (search && !search.hidden));
    addEventListener("scroll", solid, { passive: true });
    searchBtn && searchBtn.addEventListener("click", () => setTimeout(solid));
    solid();
  }

  /* Rails and hero carousel */
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-rail]"); if (!b) return;
    const r = document.getElementById(b.dataset.rail); r.scrollBy({ left: +b.dataset.dir * r.clientWidth * 0.8, behavior: reduced ? "auto" : "smooth" });
  });
  const slides = $$(".hero .slide");
  if (slides.length > 1) {
    let idx = 0, timer;
    const show = (i) => {
      idx = (i + slides.length) % slides.length;
      slides.forEach((s, k) => { s.classList.toggle("on", k === idx); s.setAttribute("aria-hidden", String(k !== idx)); $$("a", s).forEach((a) => a.tabIndex = k === idx ? 0 : -1); });
      $$(".hero .dots button").forEach((b, k) => b.setAttribute("aria-current", String(k === idx)));
    };
    $$(".hero .dots button").forEach((b) => b.addEventListener("click", () => { clearInterval(timer); show(+b.dataset.slide); }));
    if (!reduced) timer = setInterval(() => show(idx + 1), 7000);
  }

  /* Catalogue filters: apply on change, mobile sheet */
  const form = $("#filterForm");
  if (form) {
    form.addEventListener("change", () => form.requestSubmit ? form.requestSubmit() : form.submit());
    const sort = $("#sort"); sort && sort.addEventListener("change", () => { form.querySelector('input[name="sort"]').remove(); form.requestSubmit ? form.requestSubmit() : form.submit(); });
    const sheet = $("#filters");
    $$("[data-fopen]").forEach((b) => b.addEventListener("click", () => sheet.classList.add("open")));
    $$("[data-fclose]").forEach((b) => b.addEventListener("click", () => sheet.classList.remove("open")));
  }

  /* Product page */
  const dataEl = $("#product-data");
  if (dataEl) {
    const D = JSON.parse(dataEl.textContent);
    const st = { v: D.default, fin: null, o: {}, pic: 0 };
    const pics = D.pics;
    const v = () => D.variants[st.v];
    const finishes = () => Object.keys(v().prices || {});
    const price = () => { const f = finishes(); return f.length ? v().prices[st.fin] : v().price; };
    const opts = () => D.options.filter((o) => !o.only.length || o.only.includes(v().label));
    function waText() {
      const choice = [v().label, finishes().length ? st.fin : null, ...opts().map((o) => st.o[o.name])].filter(Boolean).join(" · ");
      const p = price();
      return { choice, order: `Hello Radiant Lighting, I'd like to order:\n${D.name}: ${choice}\nQuantity: \n${p ? "Price shown: " + fmt(p) + " each" : "Please share the price."}` };
    }
    function gallery() {
      const cur = pics[st.pic], main = $("#gmain");
      if (!cur) return;
      const img = main.querySelector("img:not(.badge)") || main.insertBefore(document.createElement("img"), main.firstChild);
      img.src = cur.src; img.alt = D.name; img.className = cur.kind === "cut" ? "" : "room-img";
      let note = main.querySelector(".render-note");
      if (cur.render && !note) { note = document.createElement("span"); note.className = "render-note"; note.textContent = "Visualisation"; main.appendChild(note); }
      if (!cur.render && note) note.remove();
      $$("#thumbs button").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.pic === st.pic)));
    }
    if (pics.length > 1) {
      const main = $("#gmain");
      main.insertAdjacentHTML("beforeend", `<button class="nav-b prev" data-gal="-1" aria-label="Previous image"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button><button class="nav-b next" data-gal="1" aria-label="Next image"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>`);
    }
    function render() {
      const fs = finishes();
      if (fs.length && !fs.includes(st.fin)) st.fin = fs[0];
      opts().forEach((o) => { if (!o.values.includes(st.o[o.name])) st.o[o.name] = o.values[0]; });
      const finOpt = opts().find((o) => o.name === "Finish");
      const finNow = fs.length ? st.fin : finOpt ? st.o.Finish : (D.fixedFinishes.length === 1 ? D.fixedFinishes[0] : "");
      const sw = (attr, f) => `<button ${attr} aria-pressed="${f === finNow}" aria-label="${esc(f)}" title="${esc(f)}"><i style="background:${esc(D.swatches[f] || "#ddd")}"></i></button>`;
      $("#fsw").innerHTML = fs.length ? fs.map((f) => sw(`data-fin="${esc(f)}"`, f)).join("") : finOpt ? finOpt.values.map((f) => sw(`data-on="Finish" data-ov="${esc(f)}"`, f)).join("") : "";
      $("#subline").innerHTML = [finNow, v().model, D.typeName].filter(Boolean).map((x) => `<span>${esc(x)}</span>`).join("");
      const p = price();
      $("#price").innerHTML = p ? `${fmt(p)} <small>each</small>` : "Price on request";
      let html = "";
      if (D.variants.length > 1) html += `<div class="opt"><span>${esc(D.variantLabel)}<b>${esc(v().label)}</b></span><div class="pills">${D.variants.map((x, i) => `<button class="pill" data-v="${i}" aria-pressed="${i === st.v}">${esc(x.label)}</button>`).join("")}</div></div>`;
      opts().filter((o) => o.name !== "Finish").forEach((o) => { html += `<div class="opt"><span>${esc(o.name)}<b>${esc(st.o[o.name])}</b></span><div class="pills">${o.values.map((x) => `<button class="pill" data-on="${esc(o.name)}" data-ov="${esc(x)}" aria-pressed="${x === st.o[o.name]}">${esc(x)}</button>`).join("")}</div></div>`; });
      $("#choices").innerHTML = html;
      const rows = [[D.variantLabel, v().label], ...(v().details ? [["Details", v().details]] : []), ...(v().model ? [["Model", v().model]] : []), ...(finNow ? [["Finish", finNow]] : [])];
      $("#specDyn").innerHTML = rows.map(([k, val]) => `<div><dt>${esc(k)}</dt><dd>${esc(val)}</dd></div>`).join("");
      $("#fsDyn").innerHTML = rows.map(([k, val]) => `<dt>${esc(k)}</dt><dd>${esc(val)}</dd>`).join("");
      const { order, choice } = waText();
      const link = "https://wa.me/" + D.wa + "?text=" + encodeURIComponent(order);
      $("#waOrder").href = link; $("#waOrderM").href = link;
      $("#waTrade").href = "https://wa.me/" + D.wa + "?text=" + encodeURIComponent(`Hello Radiant Lighting, I'd like project / trade pricing for ${D.name} (${choice}).`);
      $("#mbarSub").textContent = v().label + (p ? " · " + fmt(p) : "");
    }
    $("#prod").addEventListener("click", (e) => {
      const t = e.target.closest("button"); if (!t) return;
      if (t.dataset.pic) { st.pic = +t.dataset.pic; gallery(); return; }
      if (t.dataset.gal) { st.pic = (st.pic + +t.dataset.gal + pics.length) % pics.length; gallery(); return; }
      if (t.dataset.v) { st.v = +t.dataset.v; const i = pics.findIndex((x) => x.variant === v().label); if (i >= 0) { st.pic = i; gallery(); } }
      else if (t.dataset.fin) st.fin = t.dataset.fin;
      else if (t.dataset.on) st.o[t.dataset.on] = t.dataset.ov;
      else return;
      const sel = t.dataset.v ? `[data-v="${t.dataset.v}"]` : t.dataset.fin ? `[data-fin="${CSS.escape(t.dataset.fin)}"]` : `[data-on="${CSS.escape(t.dataset.on)}"][data-ov="${CSS.escape(t.dataset.ov)}"]`;
      render(); const again = $(sel, $("#prod")); again && again.focus({ preventScroll: true });
    });
    $$('.ptabs [role="tab"]').forEach((tab) => tab.addEventListener("click", () => {
      $$('.ptabs [role="tab"]').forEach((t) => { const on = t === tab; t.setAttribute("aria-selected", String(on)); document.getElementById(t.getAttribute("aria-controls")).hidden = !on; });
    }));
    render();
  }
})();
