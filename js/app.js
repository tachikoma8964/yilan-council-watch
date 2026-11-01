(function () {
  "use strict";

  var PAGE = 25;
  var GROUP = { 1: "c", 2: "n", 3: "n", 4: "c", 5: "c", 6: "s", 7: "s", 8: "s", 9: "w", 10: "s", 11: "i", 12: "i", 13: "i" };
  var SHORT = { 1: "宜蘭市", 2: "頭城", 3: "礁溪", 4: "員山", 5: "壯圍", 6: "羅東", 7: "五結", 8: "冬山", 9: "三星大同", 10: "蘇澳南澳", 11: "平地原住民", 12: "山地原住民", 13: "山地原住民" };
  var PARTY = { "民主進步黨": "ddp", "中國國民黨": "kmt", "台灣民眾黨": "tpp", "時代力量": "npp" };
  var app = document.getElementById("main");
  var data = null;

  function h(tag, attrs) {
    var el = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === "class") el.className = v;
      else el.setAttribute(k, v === true ? "" : v);
    });
    for (var i = 2; i < arguments.length; i++) append(el, arguments[i]);
    return el;
  }
  function append(el, kid) {
    if (kid === null || kid === undefined || kid === false) return;
    if (Array.isArray(kid)) return kid.forEach(function (k) { append(el, k); });
    el.appendChild(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function district(n) { return data.districts.filter(function (d) { return d.n === n; })[0]; }
  function member(id) { return data.members.filter(function (m) { return m.id === id; })[0]; }
  function membersOf(n) { return data.members.filter(function (m) { return m.district === n; }); }
  function partyText(m) { return m.party || ""; }
  function partyChip(m) { return m.party ? h("span", { class: "party " + (PARTY[m.party] || "") }, m.party) : null; }

  function billRow(b) {
    return h("li", { class: "bill" },
      h("p", { class: "date what" }, b.on, h("span", { class: "result" + (b.result === "照案通過" ? " ok" : "") }, b.result)),
      h("p", { class: "title what" }, h("span", { class: "no" }, b.no.replace("議字第", "").replace("號", "") ), " ", b.title),
      h("p", { class: "meta" },
        "提案：" + b.by.join("、") + (b.with.length ? "，連署 " + b.with.length + " 人" : ""),
        "，" + b.session,
        h("a", { href: b.url, rel: "noopener", target: "_blank" }, "官網原文"),
        b.issue ? h("span", { class: "issue" }, " （" + b.issue + "）") : null));
  }
  function sect(title, level) { return h("h" + (level || 3), { class: "block-title" }, title); }
  function billList(list, newFrom) {
    return h("ul", { class: "rows" }, list.map(function (b, i) {
      var li = billRow(b);
      if (i >= (newFrom === undefined ? Infinity : newFrom)) { li.classList.add("is-new"); li.style.setProperty("--k", i - newFrom); }
      return li;
    }));
  }
  function face(m, size) {
    if (!m.photo) return h("span", { class: "face none face-" + size, "aria-hidden": "true" }, m.name.charAt(0));
    var w = size === "l" ? 160 : 56;
    return h("img", { class: "face face-" + size, src: "photos/" + m.id + (size === "l" ? "" : "-s") + ".jpg", alt: "", width: w, height: Math.round(w * 1.25), loading: size === "l" ? null : "lazy", decoding: "async" });
  }
  function memberRow(m) {
    return h("li", { class: "person" },
      face(m, "s"),
      h("span", { class: "name" }, h("a", { href: "#/m/" + m.id }, m.name)),
      h("span", { class: "count" }, m.proposed + " ", h("span", null, "件提案")),
      h("span", { class: "meta" }, h("span", null, "第 " + m.district + " 選區"), partyChip(m), h("span", null, "連署 " + m.cosigned + " 件")));
  }
  function head(title, lede, mark) {
    return h("div", { class: "head" }, h("h1", { id: "page-title", tabindex: "-1" }, title, mark ? h("span", { class: "mark" }, mark) : null), lede ? h("p", { class: "lede" }, lede) : null);
  }
  function yuan(n) {
    if (n >= 100000000) return "約 " + (Math.round(n / 1000000) / 100).toLocaleString("zh-TW") + " 億元";
    if (n >= 10000) return "約 " + Math.round(n / 10000).toLocaleString("zh-TW") + " 萬元";
    return n.toLocaleString("zh-TW") + " 元";
  }
  function assetsBlock(m) {
    var a = m.assets;
    if (!a) return h("div", { class: "block" }, sect("財產申報", 2), h("p", { class: "sub" }, "尚未整理。請到", h("a", { href: data.assetSource, rel: "noopener", target: "_blank" }, "監察院財產申報查詢"), "搜尋姓名。"));
    var land = a.land.self + a.land.family, building = a.building.self + a.building.family;
    var row = function (label, value) { return h("div", null, h("dt", null, label), h("dd", null, value)); };
    var page = a.pages ? "，第 " + a.pages[0] + (a.pages[1] !== a.pages[0] ? "–" + a.pages[1] : "") + " 頁" : "";
    return h("div", { class: "block" }, sect("財產申報", 2),
      h("p", { class: "sub" }, a.declaredOn + " 申報，含配偶及未成年子女。廉政專刊第 " + a.period + " 期" + page + "。"),
      h("dl", { class: "facts" },
        row("土地、建物", "土地 " + land + " 筆、建物 " + building + " 筆"),
        row("股票（票面價額，不是市價）", a.stock ? yuan(a.stock) : "沒有申報"),
        row("現金", a.cash ? yuan(a.cash) : "沒有申報"),
        row("存款", a.deposit ? yuan(a.deposit) : "沒有申報")),
      h("details", { class: "full" }, h("summary", null, "看更多"),
        h("dl", { class: "facts small" },
          row("土地", "本人 " + a.land.self + " 筆，配偶及未成年子女 " + a.land.family + " 筆"),
          row("建物", "本人 " + a.building.self + " 筆，配偶及未成年子女 " + a.building.family + " 筆"),
          row("汽車", "本人 " + a.vehicle.self + " 輛，配偶及未成年子女 " + a.vehicle.family + " 輛"),
          row("現金", a.cash.toLocaleString("zh-TW") + " 元"),
          row("存款", a.deposit.toLocaleString("zh-TW") + " 元"),
          row("股票票面價額", a.stock.toLocaleString("zh-TW") + " 元"),
          a.bond || a.fund ? row("債券、基金", (a.bond + a.fund).toLocaleString("zh-TW") + " 元") : null,
          row("事業投資", a.business.toLocaleString("zh-TW") + " 元"),
          row("債務", a.debt.toLocaleString("zh-TW") + " 元")),
        h("p", { class: "sub" }, "完整申報書：", h("a", { href: data.assetSource, rel: "noopener", target: "_blank" }, "監察院財產申報查詢"), "，搜尋姓名，下載廉政專刊第 " + a.period + " 期的一般申報。")));
  }
  function billsOfMember(name) { return data.bills.filter(function (b) { return b.by.indexOf(name) >= 0; }); }

  /* ---- views ---- */
  function searchForm() {
    var input = h("input", { type: "search", id: "home-q", name: "q", autocomplete: "off", enterkeyhint: "search" });
    var form = h("form", { class: "field search home-search", role: "search" },
      h("label", { for: "home-q" }, "找議員，輸入姓名"),
      h("div", { class: "search-row" }, input, h("button", { class: "btn", type: "submit" }, "搜尋")));
    form.addEventListener("submit", function (e) { e.preventDefault(); location.hash = "#/members?q=" + encodeURIComponent(input.value.trim()); });
    return form;
  }
  function toMap() {
    var b = h("button", { class: "to-map", type: "button" }, "選其他選區");
    b.addEventListener("click", function () {
      var sheet = document.querySelector(".sheet");
      sheet.scrollIntoView({ block: "start" });
      sheet.querySelector("[aria-current]").focus({ preventScroll: true });
    });
    return b;
  }
  function viewHome(n) {
    var d = district(n) || data.districts[0];
    var tiles = function (list) {
      return list.map(function (x) {
        return h("a", { href: "#/d/" + x.n, class: "parcel p" + x.n + " g-" + GROUP[x.n], "aria-current": x.n === d.n ? "true" : null },
          h("b", null, pad(x.n)), SHORT[x.n]);
      });
    };
    var main = data.districts.filter(function (x) { return x.n <= 10; });
    var native = data.districts.filter(function (x) { return x.n > 10; });
    var ms = membersOf(d.n);
    var latest = data.bills.filter(function (b) { return b.by.some(function (p) { return ms.some(function (m) { return m.name === p; }); }); });
    return [
      head("選區", "點一塊地，看那個選區的議員與提案。第 " + data.term + " 屆（" + data.termYears + "）。", "示意圖"),
      h("div", { class: "split" },
        h("section", { class: "sticky", "aria-label": "選區示意圖" },
          h("div", { class: "sheet" }, tiles(main)),
          h("p", { class: "legend-group" }, "原住民選區"),
          h("div", { class: "sheet strip" }, tiles(native)),
          h("p", { class: "swatches" }, [["n", "北"], ["c", "中"], ["s", "南"], ["w", "西"], ["i", "原住民選區"]].map(function (g) { return h("span", { class: "g-" + g[0] }, h("i"), g[1]); })),
          h("p", { class: "legend" }, "顏色只表示大致方位。紅色是選區號。圖形是示意，不是實際地界。"),
          searchForm()),
        h("section", { class: "detail g-" + GROUP[d.n], "aria-labelledby": "dist-title" },
          h("p", { class: "no" }, "地號 " + pad(d.n), toMap()),
          h("h2", { id: "dist-title" }, "第 " + d.n + " 選區"),
          h("p", { class: "sub" }, d.area + "，" + d.seats + " 席"),
          h("div", { class: "block" }, sect("議員（" + ms.length + " 位）"), h("ul", { class: "rows" }, ms.map(memberRow))),
          h("div", { class: "block" }, sect("最新提案"),
            billList(latest.slice(0, 3)),
            h("a", { class: "more", href: "#/bills?d=" + d.n }, "此選區全部 " + latest.length + " 件"))))
    ];
  }

  var SCOPE = "提案數只算議員提案，不含質詢與臨時動議。";
  function viewMembers(q) {
    var term = q.get("q") || "";
    var list = h("ul", { class: "rows" });
    var empty = h("p", { class: "sub" }, "沒有符合的議員。");
    var fill = function (v) {
      var hit = data.members.filter(function (m) { return !v.trim() || m.name.indexOf(v.trim()) >= 0; });
      list.textContent = "";
      append(list, hit.map(memberRow));
      empty.hidden = hit.length > 0;
    };
    var input = h("input", { type: "search", id: "member-q", value: term, autocomplete: "off", enterkeyhint: "search" });
    input.addEventListener("input", function () { fill(input.value); });
    fill(term);
    return [
      head("議員", "第 " + data.term + " 屆現任名單，共 " + data.members.length + " 位，依選區排列，不做排名。" + SCOPE),
      h("div", { class: "field search" }, h("label", { for: "member-q" }, "找議員，輸入姓名"), input),
      list, empty,
      data.outsiders.length ? h("div", { class: "block" },
        sect("本屆曾提案，但不在現任名單", 2),
        h("p", { class: "sub" }, "官網現任名單沒有這些名字。本站不推測他們的狀況。"),
        h("ul", { class: "rows" }, data.outsiders.map(function (o) {
          return h("li", null, h("span", { class: "name" }, h("a", { href: "#/o/" + encodeURIComponent(o.name) }, o.name)), h("span", { class: "count" }, o.proposed + " ", h("span", null, "件提案")));
        }))) : null
    ];
  }

  function viewOutsider(name) {
    var o = data.outsiders.filter(function (x) { return x.name === name; })[0];
    if (!o) return viewMissing();
    var mine = billsOfMember(name);
    return [
      head(name, "不在現任名單"),
      h("p", null, "第 " + data.term + " 屆提案 " + o.proposed + " 件。官網現任名單沒有這個名字，本站不推測原因。" + SCOPE),
      h("div", { class: "block" }, sect("提案", 2), billList(mine.slice(0, 25))),
      h("p", { class: "block" }, h("a", { href: "#/members" }, "回到議員"))
    ];
  }

  function viewSessions() {
    return [
      head("會期", "只列有議員提案的會期。日期是議案登錄日，不是開會日；正式日程看議會官網。"),
      h("p", null, h("a", { href: "https://www.ilcc.gov.tw/Incfiles/PBrowse.aspx?Sys_id=PC_0620", rel: "noopener", target: "_blank" }, "議會官網預定日程表")),
      h("ul", { class: "rows" }, data.sessions.map(function (s) {
        return h("li", null,
          h("span", { class: "name" }, h("a", { href: "#/bills?s=" + encodeURIComponent(s.label) }, s.label)),
          h("span", { class: "count" }, s.n + " ", h("span", null, "件議案")),
          h("span", { class: "meta" }, h("span", null, s.from === s.to ? s.from : s.from + " 至 " + s.to), h("span", null, s.members + " 位議員提案")));
      }))
    ];
  }

  function viewMember(id) {
    var m = member(id);
    if (!m) return viewMissing();
    var cats = Object.keys(m.categories).map(function (k) { return [k, m.categories[k]]; }).sort(function (a, b) { return b[1] - a[1]; });
    var max = cats.length ? cats[0][1] : 1;
    var mine = billsOfMember(m.name);
    return [
      head(m.name, [h("a", { href: "#/d/" + m.district }, "第 " + m.district + " 選區"), "（" + district(m.district).area + "）"]),
      h("div", { class: "profile" },
        h("figure", { class: "portrait" }, face(m, "l"),
          h("figcaption", null, m.photo.from === "council" ? "照片：" : "照片：111 年選舉公報，", h("a", { href: m.photo.source, rel: "noopener", target: "_blank" }, m.photo.from === "council" ? "議會官網" : "中選會原件"))),
        h("div", null,
          m.party ? h("p", null, partyChip(m)) : null,
          h("p", null, "第 " + data.term + " 屆提案 " + m.proposed + " 件，連署 " + m.cosigned + " 件。"),
          h("p", { class: "sub" }, SCOPE))),
      assetsBlock(m),
      h("div", { class: "block" }, sect("提案類別", 2),
        cats.length ? h("ul", { class: "bars" }, cats.map(function (c) {
          var li = h("li", null, h("span", null, c[0]), h("b", null, c[1] + " 件"), h("span", { class: "track", "aria-hidden": "true" }, h("span", { class: "fill" })));
          li.style.setProperty("--v", Math.round(c[1] / max * 100));
          li.style.setProperty("--k", cats.indexOf(c));
          return li;
        })) : h("p", { class: "sub" }, "官網沒有這位議員的提案紀錄。")),
      mine.length ? h("div", { class: "block" }, sect("最新提案", 2), billList(mine.slice(0, 8)),
        h("a", { class: "more", href: "#/bills?m=" + encodeURIComponent(m.name) }, "全部 " + mine.length + " 件")) : null,
      h("p", { class: "block" }, h("a", { href: "#/d/" + m.district }, "回到第 " + m.district + " 選區"))
    ];
  }

  function options(values, current, allLabel) {
    return [h("option", { value: "" }, allLabel)].concat(values.map(function (v) {
      var value = typeof v === "object" ? v.value : v, label = typeof v === "object" ? v.label : v;
      return h("option", { value: value, selected: String(current) === String(value) ? true : null }, label);
    }));
  }
  function uniq(list) { return list.filter(function (v, i) { return v && list.indexOf(v) === i; }); }

  function viewBills(q) {
    var cur = { c: q.get("c") || "", s: q.get("s") || "", d: q.get("d") || "", m: q.get("m") || "", k: q.get("k") || "", p: parseInt(q.get("p") || "1", 10) };
    var cats = uniq(data.bills.map(function (b) { return b.cat; })).sort();
    var sess = uniq(data.bills.map(function (b) { return b.session; }));
    var names = data.members.map(function (m) { return m.name; });
    function matches(b) {
      if (cur.c && b.cat !== cur.c) return false;
      if (cur.s && b.session !== cur.s) return false;
      if (cur.m && b.by.indexOf(cur.m) < 0) return false;
      if (cur.d && !b.by.some(function (p) { var m = data.members.filter(function (x) { return x.name === p; })[0]; return m && String(m.district) === cur.d; })) return false;
      if (cur.k && (b.title + b.by.join("") + b.no).indexOf(cur.k) < 0) return false;
      return true;
    }
    var found = data.bills.filter(matches);
    var shown = found.slice(0, cur.p * PAGE);
    var form = h("form", { class: "filters", role: "search" },
      h("label", { class: "field" }, "類別", h("select", { name: "c" }, options(cats, cur.c, "全部"))),
      h("label", { class: "field" }, "會次", h("select", { name: "s" }, options(sess, cur.s, "全部"))),
      h("label", { class: "field" }, "選區", h("select", { name: "d" }, options(data.districts.map(function (d) { return { value: d.n, label: "第 " + d.n + " 選區" }; }), cur.d, "全部"))),
      h("label", { class: "field" }, "議員", h("select", { name: "m" }, options(names, cur.m, "全部"))),
      h("label", { class: "field wide" }, "關鍵字",
        h("div", { class: "search-row" }, h("input", { name: "k", type: "search", value: cur.k, autocomplete: "off", enterkeyhint: "search" }), h("button", { class: "btn", type: "submit" }, "查詢"))));
    form.addEventListener("change", function (e) { if (e.target.tagName === "SELECT") form.requestSubmit(); });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var p = new URLSearchParams();
      new FormData(form).forEach(function (v, k) { if (v) p.set(k, v); });
      location.hash = "#/bills" + (p.toString() ? "?" + p.toString() : "");
    });
    var more = null;
    if (shown.length < found.length) {
      var next = new URLSearchParams(q); next.set("p", cur.p + 1);
      more = h("div", { class: "btn-row" }, h("a", { class: "btn more-btn", href: "#/bills?" + next.toString() }, "再看 " + Math.min(PAGE, found.length - shown.length) + " 件"));
    }
    var filtered = cur.c || cur.s || cur.d || cur.m || cur.k;
    return [
      head("議案", "第 " + data.term + " 屆議員提案，共 " + data.bills.length + " 件。政府提案不在這裡。"),
      form,
      h("p", { class: "count-line", role: "status" }, "符合 " + found.length + " 件，顯示 " + shown.length + " 件", filtered ? [" ", h("a", { href: "#/bills" }, "清除篩選")] : null),
      found.length ? billList(shown, cur.p > 1 ? (cur.p - 1) * PAGE : undefined) : h("p", null, "沒有符合的議案。換個條件，或", h("a", { href: "#/bills" }, "看全部 " + data.bills.length + " 件"), "。"), more
    ];
  }

  function viewAbout() {
    return [
      head("關於"),
      h("div", { class: "prose" },
        h("p", null, "宜蘭縣議會觀測把議會網站上的公開紀錄整理成容易查的樣子，只呈現件數、日期和原文連結，不做評價或排名。這是民間整理，不是宜蘭縣議會官方網站。"),
        h("h2", null, "資料來源"),
        h("ul", null,
          h("li", null, "議員名單：", h("a", { href: data.sources.members, rel: "noopener" }, "宜蘭縣議會官網議員頁")),
          h("li", null, "議員提案：", h("a", { href: data.sources.bills, rel: "noopener" }, "宜蘭縣議會議案資料庫"), "，每筆都連回原文。"),
          h("li", null, "選區範圍：維基百科「宜蘭縣議會」，各選區席次與官網名單相符，尚待與中央選舉委員會公告核對。"),
          h("li", null, "議員照片：", h("a", { href: "https://bulletin.cec.gov.tw/", rel: "noopener" }, data.photoCredit), "。是 111 年參選時刊登的照片。"),
          h("li", null, "黃雯如 2024 年補選才就任，不在 111 年公報裡，照片取自", h("a", { href: "https://www.ilcc.gov.tw/Html/H_05/H_05.asp", rel: "noopener" }, "議會官網"), "。"),
          h("li", null, "財產申報：", h("a", { href: data.assetSource, rel: "noopener" }, "監察院公職人員財產申報查詢"), "，取每位議員最新一份一般申報。股票欄是票面價額，不是股價；金額含配偶與未成年子女。"),
          h("li", null, "資料擷取日：" + data.retrieved + "。")),
        h("h2", null, "目前沒有的"),
        h("ul", null,
          h("li", null, "第 19 屆：官網議案資料庫沒有這一屆的議員提案，因此尚未收錄。"),
          h("li", null, "政府提案（含總預算與自治條例）：本站目前只收議員提案。"),
          h("li", null, "出席率、表決紀錄、質詢內容：官網沒有可整理的結構化資料，因此不顯示。"),
          h("li", null, "財產申報的歷年對照：目前只收最新一份。"),
          h("li", null, "選區圖形是示意，不是實際地界。")),
        h("h2", null, "資料處理"),
        h("ul", null,
          h("li", null, "提案數與連署數，都是按官網提案人與連署人欄位的姓名計算，只計議員提案，不含質詢與臨時動議。"),
          h("li", null, "會期頁的日期是議案登錄日，不是開會日。"),
          h("li", null, "官網現任名單沒有標黨籍的議員，本站不顯示黨籍。"),
          h("li", null, "有 2 位提案人不在現任名單，原因官網沒說明，本站不推測。"),
          h("li", null, "有幾筆提案人欄位疑似筆誤，已在該筆標示，未計入任何議員。"),
          h("li", null, "決議欄把「照案通過」等明顯同義寫法合併顯示，其餘照原文。")),
        h("h2", null, "回報錯誤"),
        h("p", null, "資料有錯，請到", h("a", { href: "https://github.com/tachikoma8964/yilan-council-watch/issues", rel: "noopener", target: "_blank" }, "GitHub 議題頁"), "留言，附上議員姓名與錯在哪裡。"))
    ];
  }
  function viewMissing() { return [head("找不到這個頁面"), h("p", null, h("a", { href: "#/" }, "回到選區"))]; }

  /* ---- router ---- */
  var TITLES = { home: "選區", members: "議員", bills: "議案", sessions: "會期", about: "關於" };
  function route() {
    if (!data) return;
    var hash = location.hash.replace(/^#/, "") || "/";
    var parts = hash.split("?");
    var path = parts[0].split("/").filter(Boolean);
    var q = new URLSearchParams(parts[1] || "");
    var key = "home", view;
    if (!path.length) view = viewHome(1);
    else if (path[0] === "d") view = viewHome(parseInt(path[1], 10));
    else if (path[0] === "members") { key = "members"; view = viewMembers(q); }
    else if (path[0] === "m") { key = "members"; view = viewMember(path[1]); }
    else if (path[0] === "o") { key = "members"; view = viewOutsider(decodeURIComponent(path[1] || "")); }
    else if (path[0] === "sessions") { key = "sessions"; view = viewSessions(); }
    else if (path[0] === "bills") { key = "bills"; view = viewBills(q); }
    else if (path[0] === "about") { key = "about"; view = viewAbout(); }
    else view = viewMissing();
    app.textContent = "";
    append(app, view);
    document.querySelectorAll("[data-nav]").forEach(function (a) {
      if (a.dataset.nav === key) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    var title = document.getElementById("page-title");
    document.title = (title ? title.textContent.replace("示意圖", "") : TITLES[key]) + "｜宜蘭縣議會觀測";
    if (path[0] === "d") {
      var detail = document.getElementById("dist-title");
      var stacked = window.matchMedia("(max-width: 899px)").matches;
      if (stacked && detail) detail.scrollIntoView({ block: "start" });
      if (detail) { detail.setAttribute("tabindex", "-1"); detail.focus({ preventScroll: true }); }
    } else if (!q.get("p")) { window.scrollTo(0, 0); if (title) title.focus({ preventScroll: true }); }
  }

  fetch("data/data.json").then(function (r) { return r.json(); }).then(function (d) {
    data = d;
    var foot = document.getElementById("foot-meta");
    foot.textContent = "";
    append(foot, ["議案與名單：宜蘭縣議會官網，擷取日 " + d.retrieved + "。財產申報：監察院廉政專刊。", " ",
      h("a", { href: "https://github.com/tachikoma8964/yilan-council-watch/issues", rel: "noopener", target: "_blank" }, "回報錯誤")]);
    route();
  }).catch(function () {
    app.textContent = "資料載入失敗，請稍後再試。";
  });
  window.addEventListener("hashchange", route);
})();
