/*!
 * lokta.js · Book Nepal Trip front-end behaviour.
 * Plain ES2017, no build step. GSAP, ScrollTrigger and Lenis are optional
 * enhancements: everything here works without them and respects
 * prefers-reduced-motion.
 */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var body = doc.body;

  /* ------------------------------------------------------------------ helpers */
  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function on(el, ev, fn, opts) { if (el) el.addEventListener(ev, fn, opts || false); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }
  function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }
  function num(n) { return Math.round(n).toLocaleString("en-US"); }
  function safe(name, fn) {
    try { fn(); } catch (err) { if (window.console && console.error) console.error("[lokta] " + name, err); }
  }
  function store(key, val) {
    try {
      if (arguments.length > 1) { window.localStorage.setItem(key, val); return val; }
      return window.localStorage.getItem(key);
    } catch (e) { return null; }
  }
  function rafThrottle(fn) {
    var queued = false;
    return function () {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(function () { queued = false; fn(); });
    };
  }
  var mqReduce = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  // Ambient animations (flags, shine) pause while scrolling so the browser spends the frame on scrolling.
  (function () {
    var t = 0, root = document.documentElement;
    window.addEventListener("scroll", function () {
      if (!root.classList.contains("is-scrolling")) root.classList.add("is-scrolling");
      window.clearTimeout(t);
      t = window.setTimeout(function () { root.classList.remove("is-scrolling"); }, 160);
    }, { passive: true });
  })();
  function reduced() { return !!(mqReduce && mqReduce.matches); }
  function canHover() { return !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches); }
  var gsap = window.gsap || null;
  var ScrollTrigger = window.ScrollTrigger || null;
  if (gsap && ScrollTrigger && gsap.registerPlugin) { try { gsap.registerPlugin(ScrollTrigger); } catch (e) { ScrollTrigger = null; } }

  var FOCUSABLE = 'a[href], area[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';
  function focusables(ctx) {
    return $$(FOCUSABLE, ctx).filter(function (el) {
      if (el.closest("[inert]")) return false;
      if (el.getAttribute("aria-hidden") === "true") return false;
      return el.offsetWidth > 0 || el.offsetHeight > 0 || el === doc.activeElement;
    });
  }
  function trapTab(e, ctx) {
    if (e.key !== "Tab") return;
    var f = focusables(ctx);
    if (!f.length) { e.preventDefault(); return; }
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && (doc.activeElement === first || !ctx.contains(doc.activeElement))) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
  }
  function isTyping(el) {
    if (!el) return false;
    var t = (el.tagName || "").toLowerCase();
    return t === "input" || t === "textarea" || t === "select" || el.isContentEditable;
  }

  /* ------------------------------------------------------------- smooth scroll */
  var lenis = null;
  safe("lenis", function () {
    return; // native scrolling: JS smoothing added lag and fought the browser; kept off on purpose
    if (!window.Lenis || reduced()) return;
    lenis = new window.Lenis({ lerp: 0.12, smoothWheel: true });
    // Scrollable overlays keep their native scrolling.
    $$(".sheet, .search, .mega__in, .fab__panel, .search__results, .table-wrap").forEach(function (el) {
      el.setAttribute("data-lenis-prevent", "");
    });
    if (gsap && ScrollTrigger) {
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      var loop = function (t) { lenis.raf(t); window.requestAnimationFrame(loop); };
      window.requestAnimationFrame(loop);
    }
  });

  function headerOffset() {
    var m = $(".mast");
    return (m ? m.offsetHeight : 0) + 16;
  }

  // In-page anchors: route through Lenis when it runs, and move focus for keyboard users.
  on(doc, "click", function (e) {
    if (!lenis || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute("href").slice(1);
    if (!id) return;
    var target = doc.getElementById(decodeURIComponent(id));
    if (!target) return;
    e.preventDefault();
    lenis.scrollTo(target, { offset: -headerOffset() });
    if (window.history && history.pushState) history.pushState(null, "", "#" + id);
    if (!target.hasAttribute("tabindex") && !/^(a|button|input|select|textarea)$/i.test(target.tagName)) target.setAttribute("tabindex", "-1");
    try { target.focus({ preventScroll: true }); } catch (err) { /* old browsers */ }
  });

  /* ---------------------------------------------------------------- scroll lock */
  var lockCount = 0, lockPad = "";
  function lockScroll() {
    if (lockCount++ > 0) return;
    var sbw = window.innerWidth - root.clientWidth;
    lockPad = body.style.paddingRight;
    if (sbw > 0) body.style.paddingRight = sbw + "px";
    body.style.overflow = "hidden";
    if (lenis) lenis.stop();
  }
  function unlockScroll() {
    if (lockCount === 0 || --lockCount > 0) return;
    body.style.overflow = "";
    body.style.paddingRight = lockPad;
    if (lenis) lenis.start();
  }

  /* --------------------------------------------------------------- mobile sheet */
  var sheetApi = { close: function () {} };
  safe("sheet", function () {
    var sheet = $(".sheet");
    if (!sheet) return;
    var openers = $$("[data-sheet-open]");
    var lastFocus = null, isOpen = false;
    if (!sheet.id) sheet.id = "site-sheet";
    openers.forEach(function (b) { b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-controls", sheet.id); });

    function setClosedState() { sheet.inert = true; sheet.setAttribute("aria-hidden", "true"); }
    setClosedState();

    function open(from) {
      if (isOpen) return;
      isOpen = true;
      lastFocus = from || doc.activeElement;
      sheet.inert = false;
      sheet.removeAttribute("aria-hidden");
      sheet.classList.add("is-open");
      openers.forEach(function (b) { b.setAttribute("aria-expanded", "true"); });
      lockScroll();
      var first = $("[data-sheet-close]", sheet) || focusables(sheet)[0];
      window.setTimeout(function () { if (first) first.focus(); }, 30);
    }
    function close(restore) {
      if (!isOpen) return;
      isOpen = false;
      sheet.classList.remove("is-open");
      openers.forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
      setClosedState();
      unlockScroll();
      if (restore !== false && lastFocus && lastFocus.focus) lastFocus.focus();
    }
    sheetApi.close = close;
    sheetApi.isOpen = function () { return isOpen; };

    openers.forEach(function (b) { on(b, "click", function () { open(b); }); });
    $$("[data-sheet-close]", sheet).forEach(function (b) { on(b, "click", function () { close(); }); });
    on(sheet, "keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); close(); return; }
      trapTab(e, sheet);
    });
    on(sheet, "click", function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      if (a) close(false);
    });
    // Close if the viewport grows to desktop while open.
    if (window.matchMedia) {
      var mq = window.matchMedia("(min-width: 1021px)");
      var onMq = function () { if (mq.matches) close(false); };
      if (mq.addEventListener) mq.addEventListener("change", onMq); else if (mq.addListener) mq.addListener(onMq);
    }
  });

  /* ----------------------------------------------------------------- mega menus */
  safe("mega", function () {
    var drops = $$(".nav__drop");
    if (!drops.length) return;
    var timers = new WeakMap();
    function btn(d) { return $(":scope > button", d) || d.querySelector("button"); }
    function setOpen(d, open) {
      var b = btn(d);
      d.classList.toggle("is-open", open);
      if (b) b.setAttribute("aria-expanded", open ? "true" : "false");
    }
    function closeAll(except) { drops.forEach(function (d) { if (d !== except) setOpen(d, false); }); }
    drops.forEach(function (d, i) {
      var b = btn(d), panel = $(".mega", d);
      if (!b) return;
      if (panel) {
        if (!panel.id) panel.id = "mega-" + (i + 1);
        b.setAttribute("aria-controls", panel.id);
      }
      var hoverOpenedAt = 0;
      on(b, "click", function (e) {
        e.preventDefault();
        var openNow = d.classList.contains("is-open");
        if (openNow && Date.now() - hoverOpenedAt < 400) return; // hover just opened it
        closeAll(d);
        setOpen(d, !openNow);
      });
      on(d, "mouseenter", function () {
        if (!canHover()) return;
        clearTimeout(timers.get(d));
        timers.set(d, setTimeout(function () {
          if (!d.classList.contains("is-open")) hoverOpenedAt = Date.now();
          closeAll(d); setOpen(d, true);
        }, 80));
      });
      on(d, "mouseleave", function () {
        if (!canHover()) return;
        clearTimeout(timers.get(d));
        timers.set(d, setTimeout(function () { setOpen(d, false); }, 180));
      });
      on(d, "keydown", function (e) {
        if (e.key === "Escape" && d.classList.contains("is-open")) {
          e.preventDefault(); setOpen(d, false); b.focus();
        } else if (e.key === "ArrowDown" && e.target === b) {
          e.preventDefault(); closeAll(d); setOpen(d, true);
          var f = panel && focusables(panel)[0];
          if (f) window.setTimeout(function () { f.focus(); }, 30);
        }
      });
      on(d, "focusout", function (e) {
        if (e.relatedTarget && !d.contains(e.relatedTarget)) setOpen(d, false);
      });
    });
    on(doc, "click", function (e) {
      if (!e.target.closest || !e.target.closest(".nav__drop")) closeAll();
    });
    on(doc, "keydown", function (e) { if (e.key === "Escape") closeAll(); });
  });

  /* ------------------------------------------------------------- search overlay */
  safe("search", function () {
    var overlay = $(".search");
    var input = overlay && $("input[data-search-url]", overlay);
    var list = overlay && $(".search__results", overlay);
    if (!overlay || !input || !list) return;
    var hint = $(".search__hint", overlay);
    var rows = null, loading = null, failed = false, active = -1, results = [], lastFocus = null;

    list.id = list.id || "search-results";
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", "Search results");
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-controls", list.id);
    input.setAttribute("aria-expanded", "false");
    var status = doc.createElement("p");
    status.className = "sr-only";
    status.setAttribute("aria-live", "polite");
    list.parentNode.insertBefore(status, list.nextSibling);
    list.removeAttribute("aria-live");

    function norm(s) {
      s = String(s || "").toLowerCase();
      if (s.normalize) s = s.normalize("NFD").replace(/[̀-ͯ]/g, "");
      return s.replace(/[^\w\s\u0900-\u097F]/g, " ").replace(/\s+/g, " ").trim();
    }
    function load() {
      if (rows || loading) return loading;
      var url = input.getAttribute("data-search-url");
      loading = fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(function (data) {
          rows = (Array.isArray(data) ? data : []).map(function (r) {
            return { t: r[0] || "", u: r[1] || "#", k: r[2] || "", c: r[3] || "", nt: norm(r[0]), nk: norm(r[2]), nc: norm(r[3]) };
          });
          failed = false;
          run();
          return rows;
        })
        .catch(function () { failed = true; loading = null; run(); });
      return loading;
    }
    // Subsequence match with a bonus for tight runs: tolerant of small typos and gaps.
    function fuzzy(q, s) {
      if (!q) return 0;
      var qi = 0, run = 0, score = 0;
      for (var i = 0; i < s.length && qi < q.length; i++) {
        if (s.charAt(i) === q.charAt(qi)) { qi++; run++; score += run; } else { run = 0; }
      }
      return qi === q.length ? score / (s.length + 4) : 0;
    }
    function scoreToken(tok, r) {
      var t = r.nt, sc = 0;
      if (t === tok) sc = 120;
      else if (t.indexOf(tok) === 0) sc = 90;
      else if ((" " + t).indexOf(" " + tok) > -1) sc = 70;
      else if (t.indexOf(tok) > -1) sc = 45;
      else if (r.nc.indexOf(tok) > -1) sc = 22;
      else if (r.nk.indexOf(tok) > -1) sc = 16;
      else if (tok.length >= 3) { var f = fuzzy(tok, t); if (f > 0.35) sc = Math.round(f * 30); }
      return sc;
    }
    var KIND_W = { Region: 8, Place: 6, Trip: 5, Experience: 3, Festival: 3, Guide: 2, Story: 1, Stay: 2, Style: 2 };
    function search(q) {
      var nq = norm(q);
      if (!nq || !rows) return [];
      var toks = nq.split(" ").filter(Boolean);
      var out = [];
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i], total = 0, ok = true;
        for (var j = 0; j < toks.length; j++) {
          var s = scoreToken(toks[j], r);
          if (!s) { ok = false; break; }
          total += s;
        }
        if (!ok) continue;
        if (toks.length > 1 && r.nt.indexOf(nq) > -1) total += 40;
        total += KIND_W[String(r.k).split(" ")[0]] || 0;
        total -= Math.min(r.nt.length, 60) / 20;
        out.push({ r: r, s: total });
      }
      out.sort(function (a, b) { return b.s - a.s; });
      return out.slice(0, 12).map(function (x) { return x.r; });
    }
    function mark(text, q) {
      var toks = norm(q).split(" ").filter(function (t) { return t.length > 1; });
      var safeText = esc(text);
      if (!toks.length) return safeText;
      var lower = String(text).toLowerCase(), pos = -1, len = 0;
      toks.forEach(function (t) { var p = lower.indexOf(t); if (p > -1 && (pos < 0 || p < pos)) { pos = p; len = t.length; } });
      if (pos < 0) return safeText;
      return esc(text.slice(0, pos)) + "<mark>" + esc(text.slice(pos, pos + len)) + "</mark>" + esc(text.slice(pos + len));
    }
    function setActive(i) {
      var opts = $$("[role=option]", list);
      active = opts.length ? (i + opts.length) % opts.length : -1;
      opts.forEach(function (o, k) {
        var on_ = k === active;
        o.setAttribute("aria-selected", on_ ? "true" : "false");
        var a = o.querySelector("a");
        if (a) a.style.background = on_ ? "var(--paper-2)" : "";
        if (on_) o.scrollIntoView({ block: "nearest" });
      });
      if (active > -1) input.setAttribute("aria-activedescendant", opts[active].id);
      else input.removeAttribute("aria-activedescendant");
    }
    function run() {
      var q = input.value;
      if (!norm(q)) {
        list.innerHTML = ""; results = []; active = -1;
        input.setAttribute("aria-expanded", "false");
        input.removeAttribute("aria-activedescendant");
        if (hint) hint.hidden = false;
        status.textContent = "";
        return;
      }
      if (hint) hint.hidden = true;
      if (!rows) {
        list.innerHTML = failed
          ? '<li class="small muted" style="padding:10px 12px">Search is not available right now. Try the menu, or <a href="' + esc(($("a[href*='sitemap']") || {}).href || "/sitemap/") + '">the sitemap</a>.</li>'
          : '<li class="small muted" style="padding:10px 12px">Loading…</li>';
        if (!failed) load();
        return;
      }
      results = search(q);
      input.setAttribute("aria-expanded", results.length ? "true" : "false");
      if (!results.length) {
        list.innerHTML = '<li class="small muted" style="padding:10px 12px">Nothing found for “' + esc(q) + '”. Try a region, a place or a month.</li>';
        status.textContent = "No results";
        active = -1;
        return;
      }
      list.innerHTML = results.map(function (r, i) {
        var meta = [r.k, r.c].filter(Boolean).map(esc).join(" · ");
        return '<li role="option" id="sr-' + i + '" aria-selected="false"><a href="' + esc(r.u) + '" tabindex="-1"><b>' + mark(r.t, q) + "</b>" + (meta ? "<small>" + meta + "</small>" : "") + "</a></li>";
      }).join("");
      status.textContent = results.length + (results.length === 1 ? " result" : " results");
      setActive(0);
    }

    var isOpen = false;
    function open(from) {
      if (isOpen) return;
      if (sheetApi.isOpen && sheetApi.isOpen()) sheetApi.close(false);
      isOpen = true;
      lastFocus = from || doc.activeElement;
      overlay.hidden = false;
      lockScroll();
      load();
      input.focus();
      if (input.value) input.select();
      run();
    }
    function close() {
      if (!isOpen) return;
      isOpen = false;
      overlay.hidden = true;
      unlockScroll();
      if (lastFocus && lastFocus.focus && doc.contains(lastFocus) && !lastFocus.closest("[inert]")) lastFocus.focus();
    }
    $$("[data-search-open]").forEach(function (b) {
      on(b, "click", function (e) { e.preventDefault(); open(b); });
      // Warm the index when someone is about to open search.
      on(b, "pointerenter", function () { load(); }, { once: true });
    });
    $$("[data-search-close]", overlay).forEach(function (b) { on(b, "click", close); });
    on(overlay, "click", function (e) { if (e.target === overlay) close(); });
    var debounce = 0;
    on(input, "input", function () { clearTimeout(debounce); debounce = setTimeout(run, 60); });
    on(overlay, "keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); close(); return; }
      if (e.target === input) {
        if (e.key === "ArrowDown") { e.preventDefault(); setActive(active + 1); return; }
        if (e.key === "ArrowUp") { e.preventDefault(); setActive(active - 1); return; }
        if (e.key === "Enter") {
          var opts = $$("[role=option] a", list);
          var pick = opts[active > -1 ? active : 0];
          if (pick) { e.preventDefault(); window.location.href = pick.href; }
          return;
        }
      }
      trapTab(e, overlay);
    });
    on(list, "mousemove", function (e) {
      var li = e.target.closest && e.target.closest("[role=option]");
      if (!li) return;
      var idx = $$("[role=option]", list).indexOf(li);
      if (idx !== active) setActive(idx);
    });
    on(doc, "keydown", function (e) {
      if (isOpen || e.defaultPrevented || isTyping(e.target)) return;
      if ((e.key === "/" && !e.metaKey && !e.ctrlKey && !e.altKey) || ((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K"))) {
        e.preventDefault();
        open(doc.activeElement);
      }
    });
  });

  /* ---------------------------------------------------------------------- FAB */
  safe("fab", function () {
    var fab = $("[data-fab]");
    if (!fab) return;
    var toggle = $(".fab__toggle", fab);
    var panel = toggle && doc.getElementById(toggle.getAttribute("aria-controls") || "") || $(".fab__panel", fab);
    function set(open) {
      if (!panel || !toggle) return;
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) { var f = focusables(panel)[0]; if (f) f.focus(); }
    }
    on(toggle, "click", function () { set(panel.hidden); });
    on(fab, "keydown", function (e) {
      if (e.key === "Escape" && panel && !panel.hidden) { e.preventDefault(); set(false); toggle.focus(); }
    });
    on(doc, "click", function (e) { if (panel && !panel.hidden && !fab.contains(e.target)) set(false); });

    // The button slides in once the reader is past the first screen (or straight away on short pages).
    var show = function () {
      var short = root.scrollHeight < window.innerHeight * 1.6;
      var past = (window.pageYOffset || root.scrollTop) > Math.min(360, window.innerHeight * 0.4);
      fab.classList.toggle("is-on", short || past || (panel && !panel.hidden));
    };
    on(window, "scroll", rafThrottle(show), { passive: true });
    on(window, "resize", rafThrottle(show));
    show();
  });

  /* -------------------------------------------------------------- header state */
  safe("mast", function () {
    var mast = $(".mast");
    if (!mast) return;
    var upd = function () { mast.classList.toggle("is-scrolled", (window.pageYOffset || root.scrollTop) > 8); };
    on(window, "scroll", rafThrottle(upd), { passive: true });
    upd();
  });

  /* -------------------------------------------------------------------- nudge */
  safe("nudge", function () {
    var nudge = $("[data-nudge]");
    if (!nudge) return;
    var KEY = "bnt:nudge-dismissed";
    var WEEK = 7 * 24 * 3600 * 1000;
    var was = +(store(KEY) || 0);
    if (was && Date.now() - was < WEEK) return;
    var shown = false, done = false;
    function dismiss() {
      done = true;
      nudge.hidden = true;
      store(KEY, String(Date.now()));
    }
    var check = rafThrottle(function () {
      if (shown || done) return;
      var max = root.scrollHeight - window.innerHeight;
      if (max <= 0) return;
      if ((window.pageYOffset || root.scrollTop) / max > 0.45) {
        shown = true;
        nudge.hidden = false;
        if (gsap && !reduced()) gsap.from(nudge, { y: 24, opacity: 0, duration: 0.5, ease: "power2.out" });
      }
    });
    on(window, "scroll", check, { passive: true });
    $$("[data-nudge-close]", nudge).forEach(function (b) { on(b, "click", dismiss); });
    $$("a[href]", nudge).forEach(function (a) { on(a, "click", function () { store(KEY, String(Date.now())); }); });
    on(nudge, "keydown", function (e) { if (e.key === "Escape") dismiss(); });
  });

  /* ------------------------------------------------------------------ buy bar */
  safe("buybar", function () {
    var bar = $("[data-buybar]");
    if (!bar) return;
    var trigger = $(".phead") || $("main h1");
    var stop = $(".cta") || $(".foot");
    var on_ = false, hideTimer = 0;
    function set(v) {
      if (v === on_) return;
      on_ = v;
      clearTimeout(hideTimer);
      if (v) {
        bar.hidden = false;
        body.classList.add("has-buybar");
        window.requestAnimationFrame(function () { window.requestAnimationFrame(function () { bar.classList.add("is-on"); }); });
      } else {
        bar.classList.remove("is-on");
        body.classList.remove("has-buybar");
        hideTimer = setTimeout(function () { if (!on_) bar.hidden = true; }, reduced() ? 0 : 450);
      }
    }
    var upd = rafThrottle(function () {
      var vh = window.innerHeight;
      var past = trigger ? trigger.getBoundingClientRect().bottom < 0 : (window.pageYOffset || root.scrollTop) > vh;
      var atEnd = stop ? stop.getBoundingClientRect().top < vh : false;
      set(past && !atEnd);
    });
    on(window, "scroll", upd, { passive: true });
    on(window, "resize", upd);
    upd();
  });

  /* -------------------------------------------------- home cross-section readout */
  safe("xsec", function () {
    $$("[data-xsec]").forEach(function (fig) {
      var dataEl = $("#xs-data", fig) || $("#xs-data");
      var svg = $("svg", fig), hit = $("[data-xsec-hit]", fig);
      if (!dataEl || !svg || !hit) return;
      var D;
      try { D = JSON.parse(dataEl.textContent); } catch (e) { return; }
      var S = D.s || [], n = S.length - 1;
      if (n < 1) return;
      var W = +D.w || 1600, base = +D.base, top = +D.top, MAX = +D.max || 8849;
      var places = (D.places || []).filter(function (p) { return typeof p.a === "number"; });
      var belts = D.belts || [];
      var cursor = $(".xsec__cursor", svg), dot = $(".xsec__dot", svg), read = $(".xsec__read", fig);
      var rAlt = $("[data-r-alt]", fig), rBelt = $("[data-r-belt]", fig), rLike = $("[data-r-like]", fig);
      var idx = -1, hideT = 0;

      function yOf(a) { return base - a * (base - top) / MAX; }
      function beltOf(a) {
        for (var i = 0; i < belts.length; i++) if (a >= belts[i][0] && a < belts[i][1]) return belts[i];
        return belts[belts.length - 1];
      }
      function nearest(a) {
        var best = null, d = Infinity;
        for (var i = 0; i < places.length; i++) { var dd = Math.abs(places[i].a - a); if (dd < d) { d = dd; best = places[i]; } }
        return best;
      }
      function toSvgX(clientX) {
        var ctm = svg.getScreenCTM && svg.getScreenCTM();
        if (ctm && svg.createSVGPoint) {
          var pt = svg.createSVGPoint(); pt.x = clientX; pt.y = 0;
          return pt.matrixTransform(ctm.inverse()).x;
        }
        var r = svg.getBoundingClientRect();
        return (clientX - r.left) / r.width * W;
      }
      function show(i) {
        i = clamp(Math.round(i), 0, n);
        idx = i;
        var a = S[i], x = W * i / n, y = yOf(a);
        if (cursor) { cursor.setAttribute("x1", x); cursor.setAttribute("x2", x); }
        if (dot) { dot.setAttribute("cx", x); dot.setAttribute("cy", y); }
        var b = beltOf(a), p = nearest(a);
        if (rAlt) rAlt.textContent = num(a) + " m";
        if (rBelt) rBelt.textContent = b ? b[2] + " · " + b[3] : "";
        if (rLike) rLike.textContent = p ? "Sleep near this height: " + p.n + ", " + num(p.a) + " m" : "";
        if (read) {
          var fr = fig.getBoundingClientRect(), sr = svg.getBoundingClientRect();
          var scale = sr.width / W;
          var left = sr.left - fr.left + x * scale;
          var half = (read.offsetWidth || 200) / 2;
          left = clamp(left, half + 4, fr.width - half - 4);
          read.style.left = left + "px";
          read.style.top = (sr.top - fr.top + y * scale) + "px";
        }
        fig.classList.add("is-live");
        svg.setAttribute("aria-valuenow", String(a));
        svg.setAttribute("aria-valuetext", num(a) + " metres, " + (b ? b[2] : ""));
      }
      function hide() { fig.classList.remove("is-live"); }

      svg.style.touchAction = "pan-y";
      hit.style.cursor = "crosshair";
      on(hit, "pointermove", function (e) { clearTimeout(hideT); show(toSvgX(e.clientX) / W * n); });
      on(hit, "pointerdown", function (e) { clearTimeout(hideT); show(toSvgX(e.clientX) / W * n); });
      on(hit, "pointerleave", function (e) { if (e.pointerType === "mouse") hide(); });
      on(hit, "pointerup", function (e) { if (e.pointerType !== "mouse") { clearTimeout(hideT); hideT = setTimeout(hide, 2600); } });
      on(hit, "pointercancel", function () { hideT = setTimeout(hide, 1200); });

      // Keyboard: the drawing works as a slider along the ridge.
      svg.setAttribute("tabindex", "0");
      svg.setAttribute("role", "slider");
      svg.setAttribute("aria-valuemin", "0");
      svg.setAttribute("aria-valuemax", String(MAX));
      svg.setAttribute("aria-describedby", (read && (read.id || (read.id = "xsec-read"))) || "");
      var peakI = S.indexOf(Math.max.apply(null, S));
      on(svg, "focus", function () { show(idx < 0 ? peakI : idx); });
      on(svg, "blur", hide);
      on(svg, "keydown", function (e) {
        var step = e.shiftKey ? 10 : 2, i = idx < 0 ? peakI : idx;
        if (e.key === "ArrowRight" || e.key === "ArrowUp") i += step;
        else if (e.key === "ArrowLeft" || e.key === "ArrowDown") i -= step;
        else if (e.key === "Home") i = 0;
        else if (e.key === "End") i = n;
        else if (e.key === "Escape") { hide(); return; }
        else return;
        e.preventDefault();
        show(i);
      });

      // Ridge line: give the dash the true length, and draw it in once.
      var draw = $(".draw", svg);
      if (draw && draw.getTotalLength) {
        var len = Math.ceil(draw.getTotalLength());
        draw.style.setProperty("--len", len);
        if (gsap && !reduced()) gsap.fromTo(draw, { strokeDashoffset: len }, { strokeDashoffset: 0, duration: 2.4, ease: "power2.inOut", delay: 0.2 });
      }
    });
  });

  /* ------------------------------------------------- maps: pin and legend sync */
  safe("atlas", function () {
    $$(".atlas").forEach(function (fig) {
      function hot(n, v) {
        $$('[data-n="' + n + '"]', fig).forEach(function (el) { el.classList.toggle("is-hot", v); });
      }
      $$(".atlas__pin[data-n], .atlas__legend li[data-n]", fig).forEach(function (el) {
        var n = el.getAttribute("data-n");
        on(el, "mouseenter", function () { hot(n, true); });
        on(el, "mouseleave", function () { hot(n, false); });
        on(el, "focusin", function () { hot(n, true); });
        on(el, "focusout", function () { hot(n, false); });
      });
    });
  });

  /* --------------------------------------------------------- list page filters */
  safe("filters", function () {
    var params = new URLSearchParams(window.location.search);
    $$("[data-filter-group]").forEach(function (group, gi) {
      var sel = group.getAttribute("data-filter-group");
      var target = null;
      try { target = sel ? doc.querySelector(sel) : null; } catch (e) { target = null; }
      if (!target) target = group.nextElementSibling;
      if (!target) return;
      var items = $$("[data-item]", target);
      if (!items.length) return;
      var sections = $$("[data-section]", target);
      var counts = $$("[data-filter-count]", group);
      if (!counts.length) counts = $$("[data-filter-count]").filter(function (c) { return !c.closest("[data-filter-group]"); });
      var controls = $$("[data-key]", group);
      var syncUrl = group.getAttribute("data-filter-url") !== "off";

      var empty = doc.createElement("div");
      empty.className = "empty";
      empty.hidden = true;
      empty.style.display = "none";
      empty.setAttribute("role", "status");
      empty.innerHTML = 'Nothing matches these filters. <button type="button" class="chip" style="margin-left:8px">Clear filters</button>';
      target.parentNode.insertBefore(empty, target.nextSibling);
      on($("button", empty), "click", function () { reset(); });

      function isText(c) { return c.tagName === "INPUT" && /^(search|text)$/i.test(c.type || "text"); }
      function isToggle(c) { return c.tagName === "BUTTON" || (c.tagName === "A" && c.hasAttribute("data-value")); }
      function isCheck(c) { return c.tagName === "INPUT" && /^(checkbox|radio)$/i.test(c.type); }

      // state: key -> {type, values[]}
      function readState() {
        var st = {};
        controls.forEach(function (c) {
          var k = c.getAttribute("data-key");
          if (!k) return;
          var entry = st[k] || (st[k] = { text: false, values: [] });
          var v = "";
          if (isText(c)) { entry.text = true; v = c.value.trim(); }
          else if (isToggle(c)) { if (c.getAttribute("aria-pressed") === "true") v = c.getAttribute("data-value") || ""; }
          else if (isCheck(c)) { if (c.checked) v = c.value; }
          else if ("value" in c) v = c.value;
          if (v) entry.values.push(v);
        });
        return st;
      }
      function matches(item, st) {
        for (var k in st) {
          if (!Object.prototype.hasOwnProperty.call(st, k)) continue;
          var e = st[k];
          if (!e.values.length) continue;
          var attr = item.getAttribute("data-" + k);
          if (e.text) {
            var hay = (attr != null ? attr : item.textContent).toLowerCase();
            var ok = e.values.every(function (v) {
              return v.toLowerCase().split(/\s+/).every(function (w) { return hay.indexOf(w) > -1; });
            });
            if (!ok) return false;
          } else {
            if (attr == null) return false;
            var toks = attr.toLowerCase().split(/\s+/);
            var any = e.values.some(function (v) { return toks.indexOf(String(v).toLowerCase()) > -1; });
            if (!any) return false;
          }
        }
        return true;
      }
      function apply(fromUser) {
        var st = readState(), shown = 0;
        items.forEach(function (it) {
          var m = matches(it, st);
          it.hidden = !m;
          it.style.display = m ? "" : "none";
          if (m) shown++;
        });
        sections.forEach(function (s) {
          var any = $$("[data-item]", s).some(function (it) { return !it.hidden; });
          s.hidden = !any;
          s.style.display = any ? "" : "none";
        });
        counts.forEach(function (c) { c.textContent = String(shown); });
        empty.hidden = shown > 0;
        empty.style.display = shown > 0 ? "none" : "";
        if (fromUser && syncUrl && window.history && history.replaceState) {
          var p = new URLSearchParams(window.location.search);
          Object.keys(st).forEach(function (k) {
            if (st[k].values.length) p.set(k, st[k].values.join(",")); else p.delete(k);
          });
          var qs = p.toString();
          history.replaceState(history.state, "", window.location.pathname + (qs ? "?" + qs : "") + window.location.hash);
        }
        group.dispatchEvent(new CustomEvent("filters:change", { bubbles: true, detail: { shown: shown, state: st } }));
      }
      function reset() {
        controls.forEach(function (c) {
          if (isText(c)) c.value = "";
          else if (isToggle(c)) c.setAttribute("aria-pressed", (c.getAttribute("data-value") || "") === "" ? "true" : "false");
          else if (isCheck(c)) c.checked = false;
          else if (c.tagName === "SELECT") c.selectedIndex = 0;
        });
        apply(true);
      }

      // Seed from the query string (?height=high, ?length=short, ?region=…, ?themes=…).
      var seeded = false;
      controls.forEach(function (c) {
        var k = c.getAttribute("data-key");
        if (!k || !params.has(k)) return;
        var vals = String(params.get(k) || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
        if (!vals.length) return;
        if (c.tagName === "SELECT") {
          var opt = Array.prototype.find.call(c.options, function (o) { return o.value === vals[0]; });
          if (opt) { c.value = opt.value; seeded = true; }
        } else if (isText(c)) { c.value = vals.join(" "); seeded = true; }
        else if (isToggle(c)) {
          var pressed = vals.indexOf(c.getAttribute("data-value") || "") > -1;
          c.setAttribute("aria-pressed", pressed ? "true" : "false");
          seeded = true;
        } else if (isCheck(c)) { c.checked = vals.indexOf(c.value) > -1; seeded = true; }
      });

      controls.forEach(function (c) {
        if (isToggle(c)) {
          if (!c.hasAttribute("aria-pressed")) c.setAttribute("aria-pressed", "false");
          on(c, "click", function (e) {
            e.preventDefault();
            var k = c.getAttribute("data-key");
            var multi = group.getAttribute("data-filter-multi") === "true" || c.hasAttribute("data-multi");
            var pressed = c.getAttribute("aria-pressed") === "true";
            if (multi) c.setAttribute("aria-pressed", pressed ? "false" : "true");
            else {
              controls.forEach(function (o) { if (isToggle(o) && o.getAttribute("data-key") === k) o.setAttribute("aria-pressed", "false"); });
              // Pressing an active chip again clears it, unless it is the "all" chip.
              var v = c.getAttribute("data-value") || "";
              if (!pressed || v === "") c.setAttribute("aria-pressed", "true");
              else {
                var all = controls.filter(function (o) { return isToggle(o) && o.getAttribute("data-key") === k && (o.getAttribute("data-value") || "") === ""; })[0];
                if (all) all.setAttribute("aria-pressed", "true");
              }
            }
            apply(true);
          });
        } else if (isText(c)) {
          var t = 0;
          on(c, "input", function () { clearTimeout(t); t = setTimeout(function () { apply(true); }, 120); });
        } else {
          on(c, "change", function () { apply(true); });
        }
      });
      on(group, "submit", function (e) { e.preventDefault(); apply(true); });
      apply(false);
      if (seeded) group.setAttribute("data-seeded", "");
      group.setAttribute("data-filter-ready", String(gi));
    });
  });

  /* --------------------------------------------------------------- plan wizard */
  safe("wizard", function () {
    $$("[data-wizard]").forEach(function (form) {
      var steps = $$("[data-step]", form);
      if (steps.length < 2) return;
      var labels = $$(".wizard__steps li", form);
      var bar = $(".wizard__bar span", form);
      var cur = 0;

      function fields(step) { return $$("input, select, textarea", step).filter(function (f) { return f.type !== "hidden" && !f.disabled && f.name !== "website"; }); }
      function validate(step) {
        var bad = null;
        fields(step).forEach(function (f) {
          var ok = f.checkValidity ? f.checkValidity() : true;
          if (ok) f.removeAttribute("aria-invalid"); else { f.setAttribute("aria-invalid", "true"); if (!bad) bad = f; }
        });
        if (bad) {
          if (bad.reportValidity) bad.reportValidity();
          bad.focus();
          return false;
        }
        return true;
      }
      function go(i, focus) {
        cur = clamp(i, 0, steps.length - 1);
        steps.forEach(function (s, k) {
          var active = k === cur;
          s.classList.toggle("is-on", active);
          s.setAttribute("aria-hidden", active ? "false" : "true");
          s.inert = !active;
        });
        labels.forEach(function (l, k) {
          l.classList.toggle("is-on", k <= cur);
          if (k === cur) l.setAttribute("aria-current", "step"); else l.removeAttribute("aria-current");
        });
        if (bar) bar.style.width = ((cur + 1) / steps.length * 100) + "%";
        if (focus) {
          var step = steps[cur];
          var lg = $("legend", step);
          var target = lg || fields(step)[0];
          if (target) {
            if (target === lg) lg.setAttribute("tabindex", "-1");
            try { target.focus({ preventScroll: true }); } catch (e) { target.focus(); }
          }
          var top = form.getBoundingClientRect().top;
          if (top < 0 || top > window.innerHeight * 0.6) {
            var y = (window.pageYOffset || root.scrollTop) + top - headerOffset();
            if (lenis) lenis.scrollTo(y); else window.scrollTo({ top: y, behavior: reduced() ? "auto" : "smooth" });
          }
        }
        form.setAttribute("data-current-step", String(cur + 1));
      }

      form.setAttribute("data-ready", "");
      // Server-side errors: start on the first step that shows one.
      var startAt = 0;
      var errStep = steps.findIndex(function (s) { return $(".errorlist", s); });
      if (errStep > -1) startAt = errStep;
      go(startAt, false);

      form.addEventListener("click", function (e) {
        var t = e.target.closest && e.target.closest("[data-next], [data-prev]");
        if (!t || !form.contains(t)) return;
        e.preventDefault();
        if (t.hasAttribute("data-next")) { if (validate(steps[cur])) go(cur + 1, true); }
        else go(cur - 1, true);
      });
      // Enter in a text field moves forward rather than submitting from step one.
      form.addEventListener("keydown", function (e) {
        if (e.key !== "Enter" || e.target.tagName === "TEXTAREA" || e.target.tagName === "BUTTON") return;
        if (cur < steps.length - 1 && steps[cur].contains(e.target)) {
          e.preventDefault();
          if (validate(steps[cur])) go(cur + 1, true);
        }
      });
      form.addEventListener("input", function (e) {
        if (e.target.getAttribute && e.target.getAttribute("aria-invalid") === "true" && e.target.checkValidity && e.target.checkValidity()) e.target.removeAttribute("aria-invalid");
      });
      form.addEventListener("submit", function (e) {
        for (var i = 0; i < steps.length; i++) {
          steps[i].inert = false;
          var bad = fields(steps[i]).filter(function (f) { return f.checkValidity && !f.checkValidity(); })[0];
          if (bad) {
            e.preventDefault();
            e.stopImmediatePropagation();
            go(i, false);
            validate(steps[i]);
            return;
          }
        }
        var submit = $("[type=submit]", form);
        if (submit) { submit.disabled = true; submit.setAttribute("aria-busy", "true"); setTimeout(function () { submit.disabled = false; submit.removeAttribute("aria-busy"); }, 8000); }
      }, true);
      // bfcache: re-enable the submit button when the page is shown again.
      on(window, "pageshow", function () { var s = $("[type=submit]", form); if (s) { s.disabled = false; s.removeAttribute("aria-busy"); } });
    });
  });

  /* -------------------------------------------- chapter and contents scrollspy */
  safe("scrollspy", function () {
    var navs = $$(".chapters__nav, .toc-side");
    if (!navs.length) return;
    navs.forEach(function (nav) {
      var links = $$('a[href^="#"]', nav).map(function (a) {
        var id = decodeURIComponent(a.getAttribute("href").slice(1));
        return { a: a, el: id ? doc.getElementById(id) : null };
      }).filter(function (x) { return x.el; });
      if (!links.length) return;
      var last = null;
      var upd = rafThrottle(function () {
        var line = headerOffset() + window.innerHeight * 0.18, cur = null;
        links.forEach(function (x) { if (x.el.getBoundingClientRect().top <= line) cur = x; });
        if (cur === last) return;
        last = cur;
        links.forEach(function (x) {
          var a = x === cur;
          x.a.classList.toggle("is-on", a);
          if (a) x.a.setAttribute("aria-current", "true"); else x.a.removeAttribute("aria-current");
        });
      });
      on(window, "scroll", upd, { passive: true });
      on(window, "resize", upd);
      upd();
    });
  });

  /* ------------------------------------------------------------ CTA analytics */
  safe("cta", function () {
    function track(name, params) {
      if (typeof window.gtag !== "function") return;
      try { params.transport_type = "beacon"; params.page_path = window.location.pathname; window.gtag("event", name, params); } catch (e) { /* ignore */ }
    }
    on(doc, "click", function (e) {
      var el = e.target.closest && e.target.closest("[data-cta]");
      if (!el) return;
      var p = { cta: el.getAttribute("data-cta") };
      if (el.href) p.link_url = el.href;
      track("cta_click", p);
    }, true);
    on(doc, "submit", function (e) {
      var f = e.target;
      if (!f || !f.getAttribute || !f.hasAttribute("data-cta-form")) return;
      if (e.defaultPrevented) return;
      track("form_submit", { form: f.getAttribute("data-cta-form") });
    });
  });

  /* ------------------------------------------------------- reveal on scroll */
  safe("reveal", function () {
    var els = $$(".rv");
    if (!els.length) return;
    function showNow(el) { el.style.opacity = "1"; el.style.transform = "none"; el.classList.add("is-in"); }
    if (reduced() || !("IntersectionObserver" in window)) { els.forEach(showNow); return; }
    var batch = [], flushT = 0;
    function flush() {
      var list = batch.splice(0);
      if (gsap) {
        gsap.to(list, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out", stagger: 0.08, clearProps: "transform", onComplete: function () { list.forEach(function (el) { el.classList.add("is-in"); }); } });
      } else {
        list.forEach(function (el, i) {
          el.style.transition = "opacity .7s ease " + (i * 0.07) + "s, transform .7s cubic-bezier(.2,.7,.2,1) " + (i * 0.07) + "s";
          window.requestAnimationFrame(function () { showNow(el); });
        });
      }
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting && en.boundingClientRect.top > 0) return;
        io.unobserve(en.target);
        batch.push(en.target);
      });
      if (batch.length) { clearTimeout(flushT); flushT = setTimeout(flush, 16); }
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.01 });
    els.forEach(function (el) {
      // Anything already above the viewport (deep link, restored scroll) shows at once.
      if (el.getBoundingClientRect().bottom < 0) showNow(el); else io.observe(el);
    });
    // Safety net: never leave content invisible.
    setTimeout(function () { els.forEach(function (el) { if (getComputedStyle(el).opacity === "0" && el.getBoundingClientRect().top < window.innerHeight) showNow(el); }); }, 3000);
  });

  // Keep ScrollTrigger in step after fonts and images settle.
  if (ScrollTrigger) on(window, "load", function () { try { ScrollTrigger.refresh(); } catch (e) { /* ignore */ } });

  root.classList.add("js-ready");
})();
