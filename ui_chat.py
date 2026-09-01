# -*- coding: utf-8 -*-
"""Adika Live Chat module (Module 3 of 5).

Exports the full-screen advisor chat overlay, routing helpers, and
floating diagnostic CTA markup.

Routing contract (do not invert):
  openAiChat(prefill) / handleStartAiChat(opts) / setActiveTab('chat')
    -> hideAllToolOverlays()
    -> #analysisView visible at z-index 280
"""

from __future__ import annotations

DEFAULT_ADVISOR_GREETING = (
    "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። "
    "ስለ መኪና ወይም የቤት ግዢ፣ የቀረጥ ስሌት፣ የባንክ ብድር ወይም ማንኛውም የፋይናንስ ምክር ምን ማወቅ ይፈልጋሉ?"
)

CHAT_ENDPOINT = "/api/advisor/chat"

CHAT_WINDOW_HTML = r"""
  <!-- DEDICATED LIVE ADVISOR CHAT (full-screen view state) -->
  <div id="analysisView" class="fixed inset-0 z-[280] bg-[#b5eff3] hidden flex-col max-w-md mx-auto w-full" style="z-index:280;">
    <div class="shrink-0 px-3 py-2 bg-[#16acbd] text-white flex items-center justify-between shadow-md">
      <div class="flex items-center gap-2 min-w-0">
        <button id="analysisBackBtn" type="button" class="btn-back flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-white/20 hover:bg-white/30 text-[11px] font-bold">← ተመለስ</button>
        <div class="min-w-0 flex-1">
          <div class="font-black text-xs truncate">Adika Senior Financial Advisor</div>
          <div class="text-[10px] text-white/85 truncate">Live Advisor Chat</div>
        </div>
      </div>
      <div class="flex items-center gap-1.5 shrink-0">
        <span class="text-[9px] font-extrabold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">ዝግጁ</span>
        <button type="button" onclick="navigateBack('analysisView')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">✕</button>
      </div>
    </div>
    <div class="chat-shell flex-1 flex flex-col min-h-0 bg-slate-50/70">
      <div class="px-3 pt-2 pb-1 shrink-0">
        <div class="rounded-xl px-3 py-1.5 bg-slate-900/80 text-white flex items-center justify-between">
          <div class="text-[11px] font-black flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/></svg>
            <span>የቀጥታ ውይይት</span>
          </div>
          <span class="text-[9px] font-bold text-emerald-300">ፈጣን ምላሽ</span>
        </div>
      </div>
      <div id="advisorChatLog" class="flex-1 overflow-y-auto px-3 pt-2 space-y-2.5 text-xs scroll-smooth"></div>
      <div class="chat-input-sticky chat-input-bar">
        <textarea id="advisorChatInput" rows="1" placeholder="ስለ መኪና፣ ቤት፣ ቀረጥ ወይም የባንክ ብድር ይጠይቁ..."></textarea>
        <button id="advisorChatSend" type="button" class="chat-send-btn" aria-label="Send">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
        </button>
      </div>
    </div>
  </div>
"""

CHAT_JS = r"""
    function hideAllToolOverlays() {
      ["aiModal","dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","aiSearchView"].forEach(function(mid){
        var m = document.getElementById(mid);
        if (!m) return;
        m.classList.add("hidden");
        m.classList.remove("flex");
        try { m.style.display = "none"; } catch (e) {}
      });
      try {
        var nav = document.getElementById("adikaBottomNav");
        var fab = document.getElementById("fabBtn");
        if (nav) nav.style.display = "none";
        if (fab) fab.style.display = "none";
      } catch (e) {}
    }
    function showAnalysisView(show) {
      var v = document.getElementById("analysisView");
      if (!v) return;
      if (show) {
        hideAllToolOverlays();
        v.classList.remove("hidden");
        v.classList.add("flex");
        v.style.display = "flex";
        v.style.zIndex = "280";
        document.body.style.overflow = "hidden";
      } else {
        v.classList.add("hidden");
        v.classList.remove("flex");
        v.style.display = "none";
        document.body.style.overflow = "";
      }
    }
    function seedAdvisorChat(initMsg) {
      var log = document.getElementById("advisorChatLog");
      if (!log) return;
      if (!log.dataset.seeded) {
        log.innerHTML = "";
        advisorChatHistory = [];
        var msg = initMsg || "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። ስለ መኪና ወይም የቤት ግዢ፣ የቀረጥ ስሌት፣ የባንክ ብድር ወይም ማንኛውም የፋይናንስ ምክር ምን ማወቅ ይፈልጋሉ?";
        if (typeof appendAdvisorChat === "function") appendAdvisorChat("advisor", msg);
        advisorChatHistory.push({ role: "advisor", content: msg });
        log.dataset.seeded = "1";
      }
    }
    function openAiChat(prefill) {
      try { showAnalysisView(true); } catch (e) { console.error(e); }
      try { seedAdvisorChat(); } catch (e) {}
      var input = document.getElementById("advisorChatInput");
      if (input && prefill) {
        input.value = prefill;
        if (input.tagName === "TEXTAREA") {
          input.style.height = "auto";
          input.style.height = Math.min(input.scrollHeight, 110) + "px";
        }
        setTimeout(function(){ try { input.focus(); } catch (e) {} }, 80);
      }
    }
    window.openAiChat = openAiChat;
    window.handleStartAiChat = function(opts) {
      opts = opts || {};
      var budget = opts.budget || Number((document.getElementById("advisorBudget") || {}).value) || 0;
      var income = opts.income || Number((document.getElementById("advisorMonthlyIncome") || {}).value) || 0;
      var cat = opts.optionType || opts.category || "ፋይናንስ";
      var prompt = "በ " + Number(budget).toLocaleString() + " ETB በጀት እና በ " + Number(income).toLocaleString() + " ETB ወርሃዊ ገቢ የተመረጡትን የ" + cat + " የፋይናንስ አማራጮች ማብራሪያ እፈልጋለሁ።";
      openAiChat(prompt);
    };
    window.setActiveTab = function(tab) {
      if (tab === "chat" || tab === "advisor") openAiChat("");
    };
    var analysisBackBtn = document.getElementById("analysisBackBtn");
    if (analysisBackBtn) analysisBackBtn.onclick = function() { showAnalysisView(false); if (typeof returnToToolsHub === "function") returnToToolsHub(); };

    var advisorChatHistory = [];

    function appendAdvisorChat(role, text) {
      var log = document.getElementById("advisorChatLog");
      if (!log) return;
      var row = document.createElement("div");
      if (role === "user") {
        row.className = "chat-bubble-user text-right";
        row.innerHTML = '<div class="text-[9px] font-bold text-white/80 mb-0.5">እርስዎ</div><div class="text-xs font-semibold whitespace-pre-wrap leading-relaxed text-left">' + esc(String(text || "")) + '</div>';
      } else {
        row.className = "chat-bubble-ai text-left";
        row.innerHTML = '<div class="text-[9px] font-black text-teal-700 mb-0.5 flex items-center gap-1"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l2.4 7.2H22l-6 4.8 2.4 7.2L12 16.4 5.6 21.2 8 14 2 9.2h7.6z"/></svg><span>Adika Senior Financial Advisor</span></div><div class="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">' + esc(String(text || "")) + '</div>';
      }
      log.appendChild(row);
      setTimeout(function() { log.scrollTop = log.scrollHeight; }, 50);
    }

    (function(){
      function bindAdvisorChat() {
        var sendBtn = document.getElementById("advisorChatSend");
        var input = document.getElementById("advisorChatInput");
        if (!sendBtn || !input || sendBtn.dataset.bound === "1") return;
        sendBtn.dataset.bound = "1";
        function removeTyping() {
          var log = document.getElementById("advisorChatLog");
          if (!log) return;
          var nodes = log.querySelectorAll("[data-typing='1']");
          for (var i = 0; i < nodes.length; i++) nodes[i].parentNode.removeChild(nodes[i]);
        }
        function showTyping() {
          var log = document.getElementById("advisorChatLog");
          if (!log) return;
          removeTyping();
          var row = document.createElement("div");
          row.setAttribute("data-typing", "1");
          row.className = "mr-6 p-3 rounded-2xl bg-white text-slate-600 border border-slate-200/90 shadow-sm text-xs font-bold flex items-center gap-2 animate-in fade-in";
          row.innerHTML = '<span class="inline-flex gap-1 items-center"><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse"></span><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:200ms"></span><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:400ms"></span></span><span>አማካሪው መልስ በመጻፍ ላይ ነው...</span>';
          log.appendChild(row);
          setTimeout(function() { log.scrollTop = log.scrollHeight; }, 30);
        }
        function sendChat() {
          var text = (input.value || "").trim();
          if (!text) return;
          if (typeof appendAdvisorChat === "function") appendAdvisorChat("user", text);
          advisorChatHistory.push({ role: "user", content: text });
          input.value = "";
          if (input.tagName === "TEXTAREA") { input.style.height = "38px"; }
          showTyping();
          
          fetch("/api/advisor/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: text,
              history: advisorChatHistory
            })
          })
          .then(function(r){ return r.json(); })
          .then(function(d){
            removeTyping();
            var msg = d.reply || d.response || d.message || "ጥያቄዎን ተረድቻለሁ፤ በደስታ እርሶን ለማገዝ ዝግጁ ነኝ።";
            msg = String(msg).replace(/\bAI\b/gi, "እኛ").replace(/language model/gi, "እኛ").replace(/\bbot\b/gi, "እኛ");
            if (typeof appendAdvisorChat === "function") appendAdvisorChat("advisor", msg);
            advisorChatHistory.push({ role: "advisor", content: msg });
          })
          .catch(function(){
            removeTyping();
            if (typeof appendAdvisorChat === "function") {
              appendAdvisorChat("advisor", "መልስ ማግኘት አልተቻለም። እባክዎን ትንሽ ቆይተው እንደገና ይሞክሩ።");
            }
          });
        }
        sendBtn.onclick = sendChat;
        input.addEventListener("keydown", function(ev){
          if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); sendChat(); }
        });
        if (input.tagName === "TEXTAREA") {
          input.addEventListener("input", function() {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 110) + "px";
          });
        }
      }
      bindAdvisorChat();
      setTimeout(bindAdvisorChat, 500);
    })();

    function adikaAdvisorCtaHtml(carModel, summary) {
      var model = (carModel || "መኪናዎ").toString().trim() || "መኪናዎ";
      var sum = (summary || "").toString().trim();
      return (
        '<div class="mt-3 p-3 rounded-2xl border border-teal-200 bg-gradient-to-r from-teal-50 via-cyan-50 to-sky-50 shadow-sm space-y-2">' +
          '<div class="flex items-start gap-2">' +
            '<span class="text-lg shrink-0">🤖</span>' +
            '<p class="text-[11px] text-slate-700 leading-relaxed font-medium">' +
              'ስለ <span class="font-black text-[#0e7490]">' + esc(model) + '</span> ተጨማሪ መረጃ ወይም የባለሙያ ምክር ይፈልጋሉ? ' +
              '<span class="font-bold">Adika Digital Adviser</span>ን ያነጋግሩ!' +
            '</p>' +
          '</div>' +
          '<button type="button" class="adika-advisor-cta-btn w-full text-center py-2.5 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold text-[11px] shadow-md active:scale-[0.98]" ' +
            'data-car="' + esc(model).replace(/"/g, '&quot;') + '" data-summary="' + esc(sum).replace(/"/g, '&quot;') + '">' +
            '💬 አሁኑኑ አማክር (Chat Now)' +
          '</button>' +
        '</div>'
      );
    }

    window.openAdviserChat = function(carModelName, diagnosticSummary) {
      var model = (carModelName || "መኪና").toString().trim() || "መኪና";
      var summary = (diagnosticSummary || "").toString().trim();
      // Close any open tool modals first
      ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","aiModal"].forEach(function(mid) {
        try { closeToolModal(mid); } catch (e) {}
      });
      showAnalysisView(true);
      var prompt = "ሰላም፣ ስለ " + model + " የምርመራ ውጤት ምክር እፈልጋለሁ።";
      if (summary) prompt += "\n\nማጠቃለያ:\n" + summary;
      else prompt += " Hello, I need advice regarding the diagnostic results for " + model + ".";
      var input = document.getElementById("advisorChatInput");
      if (input) {
        input.value = prompt;
        try {
          input.style.height = "auto";
          input.style.height = Math.min(input.scrollHeight, 120) + "px";
        } catch (e) {}
        input.focus();
      }
      // Ensure chat log has a welcome if empty
      var log = document.getElementById("advisorChatLog");
      if (log && !log.children.length) {
        appendAdvisorChat("advisor", "ሰላም! እኔ Adika Senior Financial Advisor ነኝ። ስለ " + model + " ጥያቄዎን ይላኩ — ወይም ከታች ያለውን ቅድመ-ጥያቄ ይላኩ።");
      }
    };

    // Delegate clicks on Advisor CTA buttons (works for dynamically injected HTML)
    document.addEventListener("click", function(ev) {
      var btn = ev.target && ev.target.closest ? ev.target.closest(".adika-advisor-cta-btn") : null;
      if (!btn) return;
      ev.preventDefault();
      openAdviserChat(btn.getAttribute("data-car") || "", btn.getAttribute("data-summary") || "");
    });
"""
