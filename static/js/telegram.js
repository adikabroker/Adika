/* static/js/telegram.js — UTF-8 */
(function (w) {
  "use strict";
  w.ADMIN_IDS = w.ADMIN_IDS || [7030641737];
  w.ADMIN_TELEGRAM_ID = w.ADMIN_TELEGRAM_ID || 7030641737;
  w.__ADIKA_ADMIN_ID = w.__ADIKA_ADMIN_ID || 7030641737;
  try {
    var lib = w.supabase || (typeof supabase !== "undefined" ? supabase : null);
    w.__supabaseLib = lib;
    var cfg = w.__ADIKA_SUPABASE || {};
    var url = cfg.url || w.SUPABASE_URL || "";
    var key = cfg.anonKey || cfg.key || w.SUPABASE_ANON_KEY || "";
    if (url && key && lib && typeof lib.createClient === "function") {
      w.supabase = lib.createClient(url, key);
      w.__adikaSbReady = true;
    }
  } catch (e) { w.__adikaSbReady = false; }

  function rawUser() {
    try {
      return (w.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) || null;
    } catch (e) { return null; }
  }
  function build() {
    var u = rawUser() || {};
    var id = u.id != null ? String(u.id) : "";
    w.currentUser = {
      id: id, telegram_id: id, user_id: id,
      username: u.username ? String(u.username).replace(/^@/, "") : "",
      first_name: u.first_name || "", last_name: u.last_name || ""
    };
  }
  try {
    if (w.Telegram && Telegram.WebApp) {
      Telegram.WebApp.ready();
      try { Telegram.WebApp.expand(); } catch (e) {}
    }
  } catch (e) {}
  build();
  w.tgUser = rawUser;
  w.tgId = function () { return (w.currentUser && w.currentUser.telegram_id) || ""; };
  w.isAdikaAdmin = function (id) {
    return String(id || w.tgId()) === String(w.ADMIN_TELEGRAM_ID);
  };
})(window);
