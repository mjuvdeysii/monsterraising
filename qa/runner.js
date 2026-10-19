/* QA runner for the app's own WebView (Android WebView / iOS WKWebView). Injected only by debug builds
 * driven by qa/android_qa.py or qa/ios_qa.py. It walks a plan kept in localStorage (so it survives reloads,
 * process kills and relaunches), reports each result as one console line "QA:RES:{...}", asks the native side
 * for a screenshot with "QA:SNAP:{name}" and for device actions with "QA:NATIVE:{...}". */
(function () {
  if (window.__qaRunner) return; window.__qaRunner = 1;
  var LS = window.localStorage, SS = window.sessionStorage;
  function g(k) { try { return LS.getItem(k); } catch (e) { return null; } }
  function s(k, v) { try { if (v === null) LS.removeItem(k); else LS.setItem(k, v); } catch (e) {} }
  function out(type, o) {
    var line = "QA:" + type + ":" + JSON.stringify(o);
    try { if (window.webkit && webkit.messageHandlers && webkit.messageHandlers.qa) webkit.messageHandlers.qa.postMessage(line); } catch (e) {}
    try { console.log(line); } catch (e) {}
  }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function $(q) { return document.querySelector(q); }
  function $$(q) { return [].slice.call(document.querySelectorAll(q)); }
  function vis(el) { if (!el) return false; var r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== "hidden"; }
  function txt(el) { return el ? el.textContent.replace(/\s+/g, " ").trim() : ""; }
  function plat() { try { return HBApp.platform(); } catch (e) { return "web"; } }
  function curId() { var v = window.HB && HB.cur && HB.cur(); return v ? v.id : ""; }
  function go(h) { if (location.hash !== "#" + h) location.hash = h; return wait(1300); }
  function keys() { return window.HB_RECKEYS ? HB_RECKEYS() : Object.keys(JSON.parse(g("hb:rec") || "{}")); }
  function kind(k) { return (String(k).split(":")[1] || "").charAt(0); }
  function iso(d) { var p = function (n) { return (n < 10 ? "0" : "") + n; }; return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()); }

  // ---------- the app state a step starts from ----------
  function seed() {
    var D = 864e5, H = 36e5, now = Date.now(), ev = [], t0 = new Date(); t0.setHours(0, 0, 0, 0); var b = t0.getTime();
    for (var d = 12; d >= 0; d--) {
      var z = b - d * D;
      [[0, 3], [4.5, 7], [9.5, 11], [13, 14.5], [16.5, 17.5], [20, 23.9]].forEach(function (x, i) { var st = z + x[0] * H, en = z + x[1] * H - (d % 3) * 0.3 * H; if (en < now) ev.push({ id: "s" + d + i, k: "sleep", t: st, e: en, v: {} }); });
      [1, 4, 7, 10, 13, 16, 19, 22].forEach(function (h, i) { var t = z + h * H; if (t < now) { if (i % 2) ev.push({ id: "b" + d + i, k: "bottle", t: t, v: { ml: 90 + (i * 10) % 40, src: "fm" } }); else ev.push({ id: "n" + d + i, k: "nurse", t: t, e: t + 18 * 6e4, v: { l: 600, r: 480 } }); } });
      [2, 5, 8, 11, 14, 17, 20].forEach(function (h, i) { var t = z + h * H; if (t < now) ev.push({ id: "d" + d + i, k: "diaper", t: t, v: { w: 1, d: i % 3 ? 0 : 1 } }); });
      if (d % 2 == 0 && z + 9 * H < now) ev.push({ id: "v" + d, k: "vitd", t: z + 9 * H, v: {} });
      if (d % 3 == 0 && z + 18 * H < now) ev.push({ id: "h" + d, k: "bath", t: z + 18 * H, v: {} });
    }
    var bb = new Date(g("hb:birth"));
    [[0, 3.3, 50, 34.5], [30, 4.4, 54, 37], [61, 5.6, 58, 39], [92, 6.4, 61.2, 40.4], [122, 7.0, 63.5, 41.5]].forEach(function (x, i) { var t = bb.getTime() + x[0] * D; if (t < now) ev.push({ id: "g" + i, k: "grow", t: t, v: { kg: x[1], cm: x[2], hc: x[3] } }); });
    ev.sort(function (a, c) { return a.t - c.t; });
    s("hb:jr:ev", JSON.stringify(ev)); s("hb:jr:on", "1"); s("hb:jr:sex", "m");
  }
  function applyState(flags) {
    var f = {}; String(flags || "").split(",").forEach(function (x) { if (x) f[x] = 1; });
    var keep = {}; for (var i = 0; i < LS.length; i++) { var k = LS.key(i); if (k.indexOf("qa:") === 0) keep[k] = LS.getItem(k); }
    try { LS.clear(); SS.clear(); } catch (e) {}
    Object.keys(keep).forEach(function (k) { s(k, keep[k]); });
    if (!f.first) s("hb:ok", "1");
    if (!f.nobirth && !f.first) s("hb:birth", iso(new Date(Date.now() - 200 * 864e5)));
    if (!f.nobulk) s("hb:bulkDone", "1");
    if (f.dark) s("hb:theme", "dark");
    if (f.eye) s("hb:ip", "eye");
    try { s("hb:seenNew", HBApp.versionName()); } catch (e) {}
    if (!f.nojr && !f.first) seed();
    if (f.nojr) s("hb:jr:on", null);
    if (f.run) s("hb:jr:run", JSON.stringify({ sleep: { start: Date.now() - 42 * 6e4 } }));
    try { if (f.grid) SS.setItem("hb:mview", "grid"); if (f.map) SS.setItem("hb:mview", "map"); } catch (e) {}
  }

  // ---------- checks ----------
  function res(id, pass, detail, extra) { var o = { id: id, pass: !!pass, detail: detail || "", platform: plat(), at: new Date().toISOString() }; if (extra) o.data = extra; out("RES", o); return o; }
  var T = {
    today_focus: async function () {
      var pick = $("#today .t-pick"), go2 = $("#today .t-go"), more = $$("#today .t-more a"), hist = $("#today .t-go .tg-c");
      var r1 = vis(pick) && !!pick.querySelector(".pk-art svg") && !!pick.querySelector(".pk-need") && !!pick.querySelector(".pk-sw") && !!pick.querySelector(".pk-skip");
      var head = $("#today .t-h h1"), r0 = /今天满 \d+ 个月/.test(txt(head));
      res("T001", r0 && r1 && vis(go2) && more.length >= 4, "月龄=" + txt(head) + "；推荐卡=" + r1 + "；看本月=" + !!$("#today .tg-s") + "；更多工具 " + more.length + " 项", { more: more.map(txt) });
      res("T003", !hist && !!$('#today .tg-s[href^="#m"]'), hist ? "有继续卡：" + txt(hist) : "无阅读/计时历史时不显示继续卡，以「看本月」整行替代");
      var bad = more.filter(function (a) { var h = a.getAttribute("href") || "#"; return h !== "#" && !document.getElementById(h.slice(1).split("-")[0]) && !document.getElementById(h.slice(1)); });
      res("T005", more.length >= 4 && !bad.length, "更多工具：" + more.map(txt).join("、") + (bad.length ? "；失效链接 " + bad.length : ""));
    },
    pick_skip: async function () {
      var k0 = keys().length, t0 = txt($("#today .pk-t b")); $("#today .pk-sw").click(); await wait(500);
      var t1 = txt($("#today .pk-t b")); $("#today .pk-skip").click(); await wait(500);
      var off = $("#today .t-pick").classList.contains("off"), k1 = keys().length;
      res("T004", t0 !== t1 && off && k0 === k1, "换一个：" + t0 + " → " + t1 + "；今天先不做后收起=" + off + "；勾选数 " + k0 + " → " + k1);
      $("#today .pk-back").click(); await wait(300);
    },
    browsed: async function () {
      await go("m9"); await wait(800);
      var st = $("#m9 .mstat"), cur = $(".top .chain a.cur"), now = $(".top .chain a.now");
      var ok = st && /以后的内容/.test(txt(st)) && /宝宝现在满 6 个月/.test(txt(st)) && cur && cur.getAttribute("data-cm") === "9" && now && now.getAttribute("data-cm") === "6" && vis(now);
      res("T010", ok, "浏览满 9 个月：状态=" + txt(st) + "；顶部选中=" + (cur && cur.getAttribute("data-cm")) + "；现在=" + (now && now.getAttribute("data-cm")));
      res("T017", ok && !!$("#m9 .mstat .ms-go"), "「回到现在」按钮=" + !!$("#m9 .mstat .ms-go"));
    },
    all_months: async function () {
      await go("m6"); var seq = [0, 3, 6, 12, 36], got = [], n = 0;
      for (var i = 0; i < seq.length; i++) {
        $(".top .ch-all").click(); await wait(700); n = $$(".sheet-m .mp-t").length;
        var t = $('.sheet-m .mp-t[href="#m' + seq[i] + '"]'); if (!t) break; t.click(); await wait(1500); got.push(curId());
      }
      res("T011", n === 37 && got.join() === seq.map(function (m) { return "m" + m; }).join(), "全部月份 " + n + " 格；依次打开 " + got.join(" → "));
    },
    rapid: async function () {
      location.hash = "m2"; await wait(70); location.hash = "m12"; await wait(70); location.hash = "m5"; await wait(2600);
      var shown = $$("[data-view]").filter(function (v) { return !v.hidden; }).map(function (v) { return v.id; });
      var where = txt($("#where")), cur = $(".top .chain a.cur"), st = $("#m5 .mstat");
      res("T012", curId() === "m5" && shown.join() === "m5" && where === "满 5 个月" && cur && cur.getAttribute("data-cm") === "5" && st && /以前的内容/.test(txt(st)), "2→12→5 快速切换后：可见页=" + shown.join() + "；标题=" + where + "；顶部选中=" + (cur && cur.getAttribute("data-cm")) + "；状态=" + txt(st));
    },
    edges: async function () {
      await go("m0"); await wait(400); var a = $$(".top .chain a.w").map(function (x) { return +x.getAttribute("data-cm"); });
      await go("m36"); await wait(400); var b = $$(".top .chain a.w").map(function (x) { return +x.getAttribute("data-cm"); });
      res("T013", [0, 1, 2, 3, 4].every(function (m) { return a.indexOf(m) >= 0; }) && [32, 33, 34, 35, 36].every(function (m) { return b.indexOf(m) >= 0; }), "满 0 个月时显示 " + a.join(",") + "；满 36 个月时显示 " + b.join(","));
    },
    map_jump: async function () {
      await go("home"); await wait(600); window.scrollTo(0, document.documentElement.scrollHeight); await wait(700);
      var j = $("#home-map .mg-jump"); if (!j) return res("T014", false, "没有「跳到」按钮");
      j.click(); await wait(1600); var n = $('#home-map a[href="#m6"]'), r = n && n.getBoundingClientRect();
      res("T014", r && r.top > 0 && r.bottom < innerHeight, "从地图底部点「" + txt(j) + "」后满 6 个月节点位置 top=" + (r && Math.round(r.top)) + "（视口高 " + innerHeight + "）");
    },
    map_return: async function () {
      await go("home"); await wait(600); var n = $('#home-map a[href="#m12"]'); if (!n) return res("T015", false, "没有满 12 个月节点");
      window.scrollTo(0, n.getBoundingClientRect().top + scrollY - 300); await wait(600); var y = Math.round(n.getBoundingClientRect().top);
      n.click(); await wait(1600); var mid = curId(); history.back(); await wait(1800);
      var y2 = Math.round(n.getBoundingClientRect().top), mv = $("#home") && $("#home").getAttribute("data-mview");
      res("T015", mid === "m12" && curId() === "home" && mv === "map" && Math.abs(y2 - y) < 60, "满 12 个月节点在屏幕上的位置 " + y + "px → 进入 " + mid + " → 返回后 " + y2 + "px（页面顶部新加的「接着读」由浏览器滚动锚定补偿），视图=" + mv);
    },
    act_safety: async function () {
      await go("m6"); await wait(1200); var acs = $$("#m6 article.ac"), bad = [];
      acs.forEach(function (a) { var sf = a.querySelector(".safe"), fr = a.querySelector(".frames"); if (sf && fr && !(sf.getBoundingClientRect().top < fr.getBoundingClientRect().top)) bad.push(a.id); if (!sf) bad.push(a.id + "(无安全)"); });
      res("T020", acs.length && !bad.length, "满 6 个月 " + acs.length + " 个活动，安全提示都在步骤图之前" + (bad.length ? "；不符合：" + bad.join(",") : ""));
    },
    rec_first: async function () {
      await go("rec"); await wait(1500); var sum = $("#rec .r-sum"), stk = $("#rec .r-stk");
      var before = sum && stk && (sum.compareDocumentPosition(stk) & Node.DOCUMENT_POSITION_FOLLOWING);
      var cells = $$("#rec .r-sum .rs-g a").map(txt);
      res("T031", !!before && vis(sum) && sum.getBoundingClientRect().top < innerHeight && cells.length === 3, "记录首屏：" + cells.join(" | ") + "；贴纸册在其后=" + !!before);
    },
    bulk: async function () {
      await go("today"); await wait(1200); var b = $('#today .t-bulk [data-bulk="all"]'); if (!b) return res("A4", false, "首次补录卡未出现");
      var vbox = $('#today .t-bulk [data-bk="v"]'), vDef = vbox && vbox.checked; b.click(); await wait(4500);
      var ks = keys(), by = {}; ks.forEach(function (k) { var c = kind(k); by[c] = (by[c] || 0) + 1; });
      var health = (by.v || 0) + (by.k || 0);
      res("A4", vDef === false && health === 0 && (by.c || 0) > 0 && (by.a || 0) > 0, "接种儿保默认勾选=" + vDef + "；写入：观察 " + (by.c || 0) + "、活动 " + (by.a || 0) + "、接种儿保 " + health);
      res("T009", health === 0, "批量补录后接种儿保记录数=" + health + "（须逐项确认）");
    },
    did_semantics: async function () {
      await go("m6"); await wait(1200); var cnt = function () { var o = { c: 0, a: 0, h: 0 }; keys().forEach(function (k) { if (k.indexOf("6:") !== 0) return; var c = kind(k); o[c === "c" ? "c" : c === "a" ? "a" : "h"]++; }); return o; };
      var b0 = cnt(), inp = $("#m6 .ac .did input[data-mk]"), lb = inp && $('label[for="' + inp.id + '"]'); if (!lb) return res("T054", false, "找不到「记为本月做过」");
      lb.click(); await wait(700); var b1 = cnt(), sn = txt($(".snack, .sn, [class*=snack]"));
      res("T054", b1.a === b0.a + 1 && b1.c === b0.c && b1.h === b0.h, "记为做过前后：活动 " + b0.a + "→" + b1.a + "，观察 " + b0.c + "→" + b1.c + "，接种儿保 " + b0.h + "→" + b1.h + "；按钮文字=" + txt(lb) + "；提示=" + sn.slice(0, 40));
    },
    timer_start: async function () {
      await go("journal"); await wait(1000); if (window.HB_START) HB_START("nurse"); await wait(800);
      var sd = $('.sheet-m [data-ss="l"]'); if (sd) sd.click(); await wait(1200);
      var run = JSON.parse(g("hb:jr:run") || "{}"); s("qa:nurseN", String(JSON.parse(g("hb:jr:ev") || "[]").filter(function (e) { return e.k === "nurse"; }).length));
      res("T055a", !!run.nurse, "开始亲喂（左侧）后本机计时记录=" + JSON.stringify(run.nurse || null));
    },
    timer_after_kill: async function () {
      await go("journal"); await wait(1500); var run = JSON.parse(g("hb:jr:run") || "{}"), card = $(".jr-run-nurse"), n0 = +g("qa:nurseN");
      var b = $('[data-stop="nurse"]'); if (b) { b.click(); b.click(); } await wait(1200); var b2 = $('[data-stop="nurse"]'); if (b2) b2.click(); await wait(1200);
      var ev = JSON.parse(g("hb:jr:ev") || "[]").filter(function (e) { return e.k === "nurse"; }), run2 = JSON.parse(g("hb:jr:run") || "{}");
      res("T055", !!run.nurse && !!card && ev.length === n0 + 1 && !run2.nurse, "杀进程重启后计时仍在=" + !!run.nurse + "，卡片=" + !!card + "；连点结束三次后亲喂记录 " + n0 + " → " + ev.length + "；计时已清=" + !run2.nurse);
    },
    bg_start: async function () {
      await go("journal"); await wait(1000); if (window.HB_START) HB_START("sleep"); await wait(800); var sd = $('.sheet-m [data-ss]'); if (sd) sd.click(); await wait(1000);
      var run = JSON.parse(g("hb:jr:run") || "{}"); await go("today"); await wait(800); res("T002a", !!run.sleep, "开始睡眠计时=" + !!run.sleep);
    },
    bg_back: async function () {
      await wait(800); if (window.HB && HB.buildToday) HB.buildToday(); await wait(900); var c = $("#today .tg-c.run");
      var ok1 = c && /睡眠/.test(txt(c)); if (c) { c.click(); await wait(1500); }
      var ok2 = curId() === "journal" && !!$(".jr-run-sleep"); await go("today"); await wait(900);
      res("T002", ok1 && ok2 && !!JSON.parse(g("hb:jr:run") || "{}").sleep, "切到后台再回来：继续卡=" + txt(c) + "；点开后手帐计时卡=" + ok2);
    },
    hit: async function () {
      var min = plat() === "ios" ? 44 : 48, small = [], seen = 0;
      async function scan(where) {
        $$(".tabbar a, .btn, .ch-all, .pk-sw, .pk-skip, .pk-back, .tg-c, .tg-s, .t-more a, .ms-go, .seg button, .rp-seg button, .jr-b, .mg-jump, .shelf button, .tmap, .srch, #back, .rs-g a, .rs-q a, .rs-q button").forEach(function (e) {
          if (!vis(e)) return; var r = e.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight * 3) return; seen++;
          if (Math.round(r.height) < min || Math.round(r.width) < min) small.push(where + " " + (e.className || e.tagName).toString().split(" ")[0] + " " + Math.round(r.width) + "×" + Math.round(r.height) + " " + txt(e).slice(0, 8));
        });
      }
      await go("today"); await wait(900); await scan("今天"); await go("m6"); await wait(900); await scan("月份页"); await go("journal"); await wait(900); await scan("手帐"); await go("rec"); await wait(900); await scan("记录");
      res("T041", !small.length, "检查 " + seen + " 个可点元素（≥" + min + (min === 48 ? "dp" : "pt") + "，按 CSS 像素=dp/pt 计）" + (small.length ? "；偏小 " + small.length + "：" + small.slice(0, 12).join("；") : ""), { small: small });
    },
    back_a: async function () { await go("home"); await wait(700); await go("m6"); await wait(900); $(".top .ch-all").click(); await wait(800); s("qa:backA", $(".sheet-m") ? "1" : "0"); },
    back_b: async function () { await wait(800); s("qa:backB", (!$(".sheet-m.on") && curId() === "m6") ? "1" : "0"); },
    back_c: async function () {
      await wait(900); var ok = g("qa:backA") === "1" && g("qa:backB") === "1" && curId() === "home";
      res("T057", ok, "系统返回键：先关闭全部月份面板（仍在满 6 个月）=" + (g("qa:backB") === "1") + "；再按一次回到目录=" + (curId() === "home"));
      res("T034", ok && curId() === "home", "月份页按系统返回回到来源页：" + curId());
    },
    overflow: async function () {
      var bad = [];
      for (var h of ["today", "journal", "m6", "rec", "home"]) { await go(h); await wait(1000); var w = document.documentElement.scrollWidth; if (w > innerWidth + 1) bad.push(h + " " + w + ">" + innerWidth); }
      var fs = parseFloat(getComputedStyle(document.body).fontSize);
      res("T037", !bad.length, "系统大字体下正文计算字号 " + fs + "px；横向溢出：" + (bad.join("；") || "无"), { bodyPx: fs });
    },
    search_restore: async function () {
      await go("search"); await wait(800); var q = $("#q"); q.value = "辅食"; q.dispatchEvent(new Event("input")); await wait(1500);
      var chip = $$(".q-chips button").filter(function (b) { return b.getAttribute("data-k") !== "all"; })[0], want = chip && chip.getAttribute("data-k"); if (chip) { chip.click(); await wait(500); }
      var first = $("#qr li a"); var href = first && first.getAttribute("href"); if (first) first.click(); await wait(1500); var mid = curId(); history.back(); await wait(1500);
      var on = $(".q-chips button.on");
      res("T048", curId() === "search" && $("#q").value === "辅食" && on && on.getAttribute("data-k") === want && !!href, "搜索「辅食」筛选「" + (chip && txt(chip)) + "」→ 打开 " + href + "（" + mid + "）→ 返回：关键词=" + $("#q").value + "，筛选=" + (on && txt(on)));
    },
    perf_scroll: async function () {
      await go("m6"); await wait(1500); var ts = [], t0 = performance.now(), y = 0, H = document.documentElement.scrollHeight - innerHeight;
      await new Promise(function (r) { function f(t) { ts.push(t); y += 22; window.scrollTo(0, Math.min(H, y)); if (t - t0 < 4000) requestAnimationFrame(f); else r(); } requestAnimationFrame(f); });
      var d = []; for (var i = 1; i < ts.length; i++) d.push(ts[i] - ts[i - 1]); d.sort(function (a, b) { return a - b; });
      var p = function (q) { return Math.round(d[Math.min(d.length - 1, Math.floor(d.length * q))] * 10) / 10; }, jank = d.filter(function (x) { return x > 33.4; }).length;
      res("PERF", true, "月份页 4 秒程序滚动：帧间隔 p50 " + p(.5) + "ms，p95 " + p(.95) + "ms，>33ms 帧 " + jank + "/" + d.length + "（模拟器，非真机，仅作相对基线）", { p50: p(.5), p95: p(.95), jank: jank, n: d.length });
      window.scrollTo(0, 0);
    }
  };

  // ---------- the plan ----------
  function plan() { try { return JSON.parse(g("qa:plan") || "null"); } catch (e) { return null; } }
  async function step() {
    var P = plan(); if (!P) return; var i = +(g("qa:i") || 0), sub = g("qa:sub") || "0";
    while (i < P.length && P[i].only && P[i].only !== plat()) i++;
    s("qa:i", String(i));
    if (i >= P.length) { out("DONE", { n: P.length }); s("qa:plan", null); return; }
    var st = P[i];
    if (st.t === "native") { s("qa:i", String(i + 1)); s("qa:sub", "0"); out("NATIVE", { cmd: st.cmd, i: i }); await wait(st.wait || 9000); return step(); }
    if (sub === "0" && !st.keep) { applyState(st.flags); s("qa:sub", "1"); if (location.hash !== "#" + st.hash) location.hash = st.hash; await wait(50); location.reload(); return; }
    // the page has been reloaded into this step's state (or the step keeps the state it found)
    s("qa:sub", "0"); s("qa:i", String(i + 1));
    try {
      if (st.keep && st.hash) await go(st.hash); else await wait(1900);
      if (st.t === "frame") {
        for (var a of String(st.act || "").split("||").filter(Boolean)) { try { (0, eval)(a); } catch (e) { out("LOG", { i: i, err: String(e) }); } await wait(900); }
        await wait(500);
      } else if (st.t === "test") { await T[st.fn](); }
    } catch (e) { res(st.id || st.fn, false, "脚本异常：" + e); }
    if (st.snap) { window.__qaAck = 0; out("SNAP", { name: st.snap, id: st.id || "", label: st.label || "" }); for (var w = 0; w < 60 && !window.__qaAck; w++) await wait(100); }
    return step();
  }
  function boot() {
    if (window.QA_BOOT && !plan()) { s("qa:plan", JSON.stringify(window.QA_BOOT)); s("qa:i", "0"); s("qa:sub", "0"); }
    if (!plan()) return;
    var n = 0; (function ready() { if (window.HB && document.readyState === "complete") return setTimeout(step, 600); if (++n > 80) { out("LOG", { err: "page not ready" }); return step(); } setTimeout(ready, 200); })();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
