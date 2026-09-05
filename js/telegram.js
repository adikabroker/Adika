/* telegram.js — Telegram WebApp bootstrap + currentUser */
(function (w) {
  "use strict";

  w.ADMIN_IDS = w.ADMIN_IDS || [7030641737];
  if (w.ADMIN_IDS.indexOf(7030641737) < 0) w.ADMIN_IDS.push(7030641737);
  w.ADMIN_TELEGRAM_ID = w.ADMIN_TELEGRAM_ID || 7030641737;
  w.__ADIKA_ADMIN_ID = w.__ADIKA_ADMIN_ID || 7030641737;

  function rawUser() {
    try {
      return (w.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) || null;
    } catch (e) {
      return null;
    }
  }

  function asStringId(v) {
    if (v == null || v === "") return "";
    return String(v);
  }

  function buildCurrentUser() {
    var u = rawUser() || {};
    var id = asStringId(u.id || u.telegram_id || w.__ADIKA_DEV_USER_ID || "");
    return {
      id: id,
      telegram_id: id,
      user_id: id,
      username: u.username ? String(u.username).replace(/^@/, "") : "",
      first_name: u.first_name || "",
      last_name: u.last_name || "",
      full_name: [u.first_name, u.last_name].filter(Boolean).join(" "),
      language_code: u.language_code || "am",
      raw: u
    };
  }

  function initTelegram() {
    try {
      if (w.Telegram && Telegram.WebApp) {
        Telegram.WebApp.ready();
        try { Telegram.WebApp.expand(); } catch (e1) {}
        try { Telegram.WebApp.disableVerticalSwipes && Telegram.WebApp.disableVerticalSwipes(); } catch (e2) {}
      }
    } catch (e) {}
    w.currentUser = buildCurrentUser();
    w.tgUser = function () { return rawUser(); };
    w.tgId = function () { return w.currentUser && w.currentUser.telegram_id ? String(w.currentUser.telegram_id) : ""; };
    w.isAdikaAdmin = function (id) {
      var sid = asStringId(id || w.tgId());
      var admins = (w.ADMIN_IDS || []).map(asStringId);
      return admins.indexOf(sid) >= 0 || sid === asStringId(w.ADMIN_TELEGRAM_ID);
    };
  }

  initTelegram();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTelegram);
  }
})(window);
