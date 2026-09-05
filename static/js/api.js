/* static/js/api.js — UTF-8 */
(function (w) {
  "use strict";
  function sb() {
    try { return (w.supabase && w.supabase.from) ? w.supabase : null; } catch (e) { return null; }
  }
  w.fetchListings = function (opts) {
    opts = opts || {};
    var limit = opts.limit || 20, offset = opts.offset || 0;
    var page = Math.floor(offset / limit) + 1;
    var type = opts.type || "SELL";
    return fetch("/api/listings?page=" + page + "&limit=" + limit + "&order=DESC&active_only=1&type=" + encodeURIComponent(type), { credentials: "same-origin" })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (j) { return j.data || j.listings || j.items || []; })
      .catch(function () { return []; });
  };
  w.fetchBuyers = function () {
    return fetch("/api/listings?type=BUY&page=1&limit=40&order=DESC&active_only=1", { credentials: "same-origin" })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (j) {
        var rows = j.data || j.listings || j.items || [];
        if (rows && rows.length) return rows;
        var c = sb();
        if (!c) return [];
        return c.from("buyer_requests").select("*").order("created_at", { ascending: false }).limit(40)
          .then(function (res) { return (res && res.data) || []; });
      })
      .catch(function () { return []; });
  };
  w.deleteListing = function (id) {
    if (id == null || id === "") return Promise.resolve({ ok: false });
    var msg = "ይህን ማስታወቂያ ማጥፋት ይፈልጋሉ?";
    function go() {
      return fetch("/api/items/" + encodeURIComponent(id), { method: "DELETE", credentials: "same-origin" })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok && j.status === "success", data: j }; }); })
        .catch(function (e) { return { ok: false, error: String(e) }; });
    }
    return new Promise(function (resolve) {
      try {
        if (w.Telegram && Telegram.WebApp && Telegram.WebApp.showConfirm) {
          Telegram.WebApp.showConfirm(msg, function (ok) { resolve(ok ? go() : { ok: false, cancelled: true }); });
          return;
        }
      } catch (e) {}
      resolve(w.confirm(msg) ? go() : { ok: false, cancelled: true });
    });
  };
})(window);
