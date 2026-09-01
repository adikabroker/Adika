# -*- coding: utf-8 -*-
"""Adika Tools Hub module (Module 2 of 5).

Contains:
  - Tools Hub + Smart Search overlay HTML
  - Purchase & Budget Advisor markup
  - 3-way investment calculator JS (auto / real-estate / business ROI)
  - Pure-Python amortization helpers (Ethiopian commercial-bank defaults)

Chat window markup lives in ui_chat.py.
Marketplace cards live in ui_market.py.
"""

from __future__ import annotations

# Ethiopian commercial-bank financing defaults
DOWN_PAYMENT_PCT = 0.30
APR_DEFAULT = 0.18
AUTO_LOAN_YEARS = 5
MORTGAGE_YEARS = 15
ROI_BAND_LOW = 0.15
ROI_BAND_HIGH = 0.35


def monthly_payment(principal: float, annual_rate: float = APR_DEFAULT, years: int = AUTO_LOAN_YEARS) -> float:
    """Standard amortization: M = P * r(1+r)^n / ((1+r)^n - 1)."""
    principal = max(0.0, float(principal or 0))
    if principal <= 0 or years <= 0:
        return 0.0
    r = float(annual_rate) / 12.0
    n = int(years) * 12
    if r == 0:
        return principal / n
    factor = (1 + r) ** n
    return principal * (r * factor) / (factor - 1)


def split_budget(budget: float) -> dict:
    """70 / 15 / 15 purchase-fees-reserve split used by the advisor bar."""
    b = max(0.0, float(budget or 0))
    purchase = round(b * 0.70)
    fees = round(b * 0.15)
    reserve = max(0.0, b - purchase - fees)
    return {"budget": b, "purchase": purchase, "fees": fees, "reserve": reserve}


def loan_package(price: float, years: int = AUTO_LOAN_YEARS, apr: float = APR_DEFAULT, down_pct: float = DOWN_PAYMENT_PCT) -> dict:
    price = max(0.0, float(price or 0))
    down = price * down_pct
    principal = max(0.0, price - down)
    return {
        "price": price,
        "down_payment": down,
        "principal": principal,
        "monthly": monthly_payment(principal, apr, years),
        "years": years,
        "apr": apr,
        "down_pct": down_pct,
    }

TOOLS_HUB_HTML = r"""
  <!-- ================================================================= -->
  <!-- 4. DEDICATED AI HUB & SMART FILTER MODAL                          -->
  <!-- ================================================================= -->
  <div id="aiModal" class="fixed inset-0 z-[220] hidden items-stretch justify-center" style="background:rgba(2,6,23,0.55);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);">
    <div class="w-full max-w-md h-full max-h-screen flex flex-col shadow-2xl overflow-hidden relative border-0 sm:border border-white/20"
         style="background:rgba(15,23,42,0.92);backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px);">
      <!-- Dedicated Tools Hub Header (no Marketplace chrome) -->
      <div class="px-2.5 py-1.5 text-white flex flex-col gap-1 shrink-0 border-b border-white/20"
           style="background:rgba(255,255,255,0.06);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);">
        <div class="flex items-center justify-between gap-2">
          <button type="button" id="aiHubBackBtn" onclick="(function(){try{document.getElementById('aiModalClose').onclick();}catch(e){var m=document.getElementById('aiModal');if(m){m.classList.add('hidden');m.classList.remove('flex');m.style.display='none';}var n=document.getElementById('adikaBottomNav');var f=document.getElementById('fabBtn');if(n)n.style.display='';if(f)f.style.display='';}})()"
            class="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white text-sm font-semibold transition-all active:scale-95 shrink-0">
            ← <span class="lang-am">ወደ ዋና ገፅ</span><span class="lang-en">Home</span>
          </button>
          <h3 class="font-extrabold text-sm tracking-wide text-white drop-shadow-md text-center flex-1 truncate">
            Adika Digital Hub 🛠️
          </h3>
          <button id="aiModalClose" type="button"
            class="w-9 h-9 rounded-full bg-white/10 hover:bg-white/25 backdrop-blur-md border border-white/25 text-white flex items-center justify-center font-bold text-sm transition-all active:scale-95 shrink-0">
            ✕
          </button>
        </div>
        <!-- Sub-tabs -->
        <div class="grid grid-cols-2 gap-1 bg-white/10 p-0.5 rounded-xl text-xs font-bold border border-white/10">
          <button id="aiTabTools" type="button" class="py-1.5 rounded-lg bg-cyan-400/25 text-cyan-100 border border-cyan-400/30 shadow-sm transition-all text-center font-semibold">
            <span class="lang-am">🛠️ መሳሪያዎች</span>
            <span class="lang-en">🛠️ Tools Hub</span>
          </button>
          <button id="aiTabSearch" type="button" class="py-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-all text-center">
            <span class="lang-am">🔍 ፈጣን ፍለጋ</span>
            <span class="lang-en">🔍 Smart Search</span>
          </button>
        </div>
      </div>

      <!-- Tab 1: AI Tools Hub -->
      <div id="aiToolsView" class="flex-1 flex flex-col min-h-0 overflow-y-auto custom-scrollbar p-3 space-y-4 tools-ambient-wrap" style="background:transparent;">
        <div class="tools-ambient-blob cyan"></div>
        <div class="tools-ambient-blob indigo"></div>
        <!-- Smart Budget & Purchase Advisor -->
        <div class="budget-glass-card py-2 px-3 mb-2 space-y-1 relative z-10 shrink-0">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5 text-white font-extrabold text-xs drop-shadow-md">
              <span>💡</span>
              <span class="lang-am">የግዢና የበጀት አማካሪ</span>
              <span class="lang-en">Purchase & Budget Advisor</span>
            </div>
            <span class="text-[9px] font-black uppercase px-2 py-0.5 rounded-full bg-cyan-400/20 text-cyan-100 border border-cyan-400/30 whitespace-nowrap shrink-0 drop-shadow-sm">Adika Advisor</span>
          </div>

          <!-- 1. Budget + Monthly Income inputs -->
          <div class="grid grid-cols-2 gap-2">
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-[10px] font-bold text-white drop-shadow-md">ጠቅላላ በጀት (ETB)</label>
              </div>
              <input id="advisorBudget" type="number" value="2000000" placeholder="2,000,000" class="w-full py-1.5 px-2.5 rounded-lg bg-white/15 border border-white/25 text-xs font-normal text-slate-400/80 placeholder-slate-500 outline-none focus:ring-2 focus:ring-cyan-400/40 focus:text-white" />
              <div id="advisorBudgetFormatted" class="hidden text-[9px] font-medium text-slate-400/70 mt-0.5">2,000,000 ETB</div>
            </div>
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-[10px] font-bold text-white drop-shadow-md">ወርሃዊ ገቢ (ETB)</label>
              </div>
              <input id="advisorMonthlyIncome" type="number" value="25000" placeholder="25,000" class="w-full py-1.5 px-2.5 rounded-lg bg-white/15 border border-white/25 text-xs font-normal text-slate-400/80 placeholder-slate-500 outline-none focus:ring-2 focus:ring-cyan-400/40 focus:text-white" />
              <div id="advisorIncomeFormatted" class="hidden text-[9px] font-medium text-slate-400/70 mt-0.5">25,000 / ወር</div>
            </div>
          </div>
          <div class="flex gap-1 overflow-x-auto no-scrollbar">
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="70000">70k</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="500000">500k</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="1500000">1.5M</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="3000000">3M</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="6000000">6M</button>
          </div>

          <!-- Generate opportunity cards (does NOT jump to chat) -->
          <button id="advisorBtn" type="button" class="w-full py-1 rounded-xl bg-cyan-400/25 hover:bg-cyan-400/35 text-cyan-100 font-black text-xs shadow-md active:scale-95 transition-all flex items-center justify-center gap-1.5 border border-cyan-400/40 backdrop-blur-md">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
            <span>የኢንቨስትመንት አማራጮች አሳይ</span>
          </button>

          <!-- 3 Investment Opportunity Cards -->
          <div id="opportunityCards" class="hidden space-y-1.5">
            <div class="opp-card" data-opp="auto">
              <div class="opp-label text-amber-400">A · Automotive</div>
              <div class="opp-title">ተሽከርካሪ + የባንክ ብድር</div>
              <div id="oppAutoBody" class="opp-body">ከቀጥታ ገበያ እየተጫነ…</div>
              <button type="button" class="opp-cta opp-chat-cta pointer-events-auto relative z-20" data-context="auto" onclick="event.stopPropagation();if(window.setActiveTab){window.setActiveTab('chat');}if(window.handleStartAiChat){window.handleStartAiChat({optionType:'መኪና'});}">ጥልቅ የፋይናንስ ትንተና ከ Adika ዲጂታል አማካሪ Live Chat ያድርጉ →</button>
            </div>
            <div class="opp-card" data-opp="property">
              <div class="opp-label text-sky-400">B · Real Estate</div>
              <div class="opp-title">ሪል እስቴት · ቅድመ ክፍያ</div>
              <div id="oppPropBody" class="opp-body">ከቀጥታ ገበያ እየተጫነ…</div>
              <button type="button" class="opp-cta opp-chat-cta pointer-events-auto relative z-20" data-context="property" onclick="event.stopPropagation();if(window.setActiveTab){window.setActiveTab('chat');}if(window.handleStartAiChat){window.handleStartAiChat({optionType:'ቤት'});}">ጥልቅ የፋይናንስ ትንተና ከ Adika ዲጂታል አማካሪ Live Chat ያድርጉ →</button>
            </div>
            <div class="opp-card" data-opp="roi">
              <div class="opp-label text-emerald-400">C · Business ROI</div>
              <div class="opp-title">ንግድ / Startup · ዓመታዊ ROI</div>
              <div id="oppRoiBody" class="opp-body">ከበጀት ቀመር እየተሰላ…</div>
              <button type="button" class="opp-cta opp-chat-cta pointer-events-auto relative z-20" data-context="roi" onclick="event.stopPropagation();if(window.setActiveTab){window.setActiveTab('chat');}if(window.handleStartAiChat){window.handleStartAiChat({optionType:'ንግድ'});}">ጥልቅ የፋይናንስ ትንተና ከ Adika ዲጂታል አማካሪ Live Chat ያድርጉ →</button>
            </div>
          </div>

          <!-- Result Container -->
          <div id="advisorResult" class="hidden p-3 bg-white rounded-2xl border border-slate-200 text-xs text-slate-700 leading-relaxed font-medium shadow-sm space-y-3"></div>

          <!-- Extra filters: shown only AFTER analysis -->
          <div id="advisorExtraFilters" class="hidden space-y-2.5 pt-1">
            <div>
              <label class="text-[10px] font-bold text-slate-700 block mb-1">የግዢ አላማ (Purchase Purpose)</label>
              <div class="grid grid-cols-2 gap-1 bg-white/80 p-1 rounded-xl border border-slate-200">
                <button id="advisorPurposeBiz" type="button" class="advisor-purpose-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1" data-purpose="business">
                  <span>🚕</span>
                  <span>ለስራ / ንግድ (Ride/Cargo)</span>
                </button>
                <button id="advisorPurposeFam" type="button" class="advisor-purpose-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1" data-purpose="personal">
                  <span>🏠</span>
                  <span>ለግል / ቤተሰብ (Personal)</span>
                </button>
              </div>
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-700 block mb-1">የግዢ መንገድ (Payment Strategy)</label>
              <div class="grid grid-cols-2 gap-1 bg-white/80 p-1 rounded-xl border border-slate-200">
                <button id="advisorPayCash" type="button" class="advisor-pay-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1" data-pay="cash">
                  <span>💵</span>
                  <span>ባለኝ በጀት (Cash Buy)</span>
                </button>
                <button id="advisorPayLoan" type="button" class="advisor-pay-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1" data-pay="loan">
                  <span>🏦</span>
                  <span>በባንክ ብድር (Down Payment)</span>
                </button>
              </div>
            </div>
            <div id="advisorIncomeRow" class="hidden">
              <label class="text-[10px] font-bold text-slate-700 block mb-1">ወርሃዊ የተጣራ ገቢ (Monthly Net Income in ETB)</label>
              <input id="advisorIncome" type="number" placeholder="80,000" value="80000" class="w-full px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-800 outline-none" />
            </div>
          </div>
        </div>

        <!-- Tools Grid + Finance Banner — stacked flow, no overlap -->
        <div class="flex flex-col space-y-4 relative z-10 shrink-0">
          <h4 class="text-[10px] font-extrabold text-white drop-shadow-md mb-1.5 shrink-0">
            <span class="lang-am">ተጨማሪ የፋይናንስና የህግ መሳሪያዎች</span>
            <span class="lang-en">Financial, Legal & Diagnostic Tools</span>
          </h4>
          <div class="tools-grid-compact text-xs shrink min-h-0">
            <button id="toolDutyBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.0s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h5"/></svg></span>
              <span class="tool-title">የቀረጥ ስሌት</span>
              <span class="tool-sub">Customs Duty & Taxes</span>
            </button>
            <button id="toolLoanBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.08s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10h18M5 10V8a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v2M5 10v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8"/><circle cx="12" cy="14" r="1.5"/></svg></span>
              <span class="tool-title">የባንክ ብድር</span>
              <span class="tool-sub">Mortgage & Auto Loan</span>
            </button>
            <button id="toolCompareBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.16s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 7h8M8 12h8M8 17h5"/><path d="M4 4v16M20 4v16"/></svg></span>
              <span class="tool-title">የመኪና ንጽጽር</span>
              <span class="tool-sub">Vehicle Comparison</span>
            </button>
            <button id="toolContractBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.24s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 15l2 2 4-4"/></svg></span>
              <span class="tool-title">የሽያጭ ውል</span>
              <span class="tool-sub">Legal Sales Contract</span>
            </button>
            <button id="toolPoaBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.32s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg></span>
              <span class="tool-title">ውክልና ማረጋገጫ</span>
              <span class="tool-sub">Verify Power of Attorney</span>
            </button>
            <button id="toolDiagBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.4s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9c.3.6.9 1 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg></span>
              <span class="tool-title">የምርመራ ወረቀት</span>
              <span class="tool-sub">Garage Diagnostic Sheet</span>
            </button>
            <button id="toolChassisBtn" type="button" class="tool-card-pro stagger-in flex flex-col justify-between py-2 px-2 min-h-0" style="animation-delay:0.48s">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><circle cx="12" cy="11" r="3"/><path d="M12 14v3"/></svg></span>
              <span class="tool-title">የሻሲ ማረጋገጫ</span>
              <span class="tool-sub">Chassis / VIN Specs</span>
            </button>
            <button id="toolLandMapBtn" type="button" class="tool-card-pro flex flex-col justify-between py-2 px-2">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/><circle cx="12" cy="10" r="2"/></svg></span>
              <span class="tool-title">የዲጂታል ካርታ ማጣሪያ</span>
              <span class="tool-sub">Cadastral Map Verification</span>
            </button>
          </div>
          <button type="button" id="hubFinanceAdvisorBanner" onclick="event.preventDefault();event.stopPropagation();if(window.setActiveTab){window.setActiveTab('chat');}if(window.openAiChat){window.openAiChat('ስለ በጀት፣ ብድር እና የገበያ ዋጋ ጥልቅ የፋይናንስ ምክር እፈልጋለሁ።');}"
            class="w-full bg-gradient-to-r from-cyan-500/20 via-slate-900/60 to-indigo-500/20 backdrop-blur-2xl border border-cyan-400/50 rounded-2xl p-3 mt-2 flex items-center justify-between shadow-lg shadow-cyan-500/20 hover:border-cyan-400 transition-all cursor-pointer relative z-10 shrink-0">
            <div class="min-w-0 text-left pr-2">
              <div class="text-white font-extrabold text-[12px] leading-tight drop-shadow-md">💡 ዲጂታል የፋይናንስ አማካሪ</div>
              <div class="text-cyan-300 text-[10px] font-semibold drop-shadow-[0_0_8px_rgba(34,211,238,0.45)] mt-0.5">Adika AI Financial Advisor</div>
            </div>
            <span class="bg-cyan-400 text-slate-950 px-3 py-1.5 rounded-xl font-bold text-xs shrink-0 shadow-md shadow-cyan-400/30">አሁኑኑ አማክር →</span>
          </button>
        </div>
      </div>

      <!-- Smart Search glass overlay (sits on Tools Hub; Back/X only close this panel) -->
      <div id="aiSearchView" class="hidden absolute inset-0 z-30 flex items-end sm:items-center justify-center p-0 sm:p-4"
           style="background:rgba(2,6,23,0.50);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);">
        <div class="relative w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-5 transition-all shadow-[0_10px_40px_rgba(6,182,212,0.2)] border border-white/30"
             style="background:rgba(255,255,255,0.15);backdrop-filter:blur(32px);-webkit-backdrop-filter:blur(32px);">
          <div class="flex items-center justify-between gap-2 mb-4">
            <button type="button" id="aiSearchBackBtn"
              class="bg-white/20 hover:bg-white/30 backdrop-blur-md text-white border border-white/30 px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1 active:scale-95">
              ← <span class="lang-am">መመለስ</span><span class="lang-en">Back</span>
            </button>
            <h3 class="text-cyan-300 font-bold text-sm drop-shadow-[0_0_10px_rgba(34,211,238,0.5)] text-center flex-1">
              🔍 AI Smart Search
            </h3>
            <button type="button" id="aiSearchCloseBtn"
              class="bg-white/20 hover:bg-white/30 text-white rounded-full p-1.5 border border-white/30 w-8 h-8 flex items-center justify-center active:scale-95">
              ✕
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="text-cyan-300 font-semibold text-xs drop-shadow-md mb-1.5 block">
                <span class="lang-am">ምን አይነት ንብረት ይፈልጋሉ?</span>
                <span class="lang-en">What are you looking for?</span>
              </label>
              <textarea id="aiPrompt" rows="2"
                placeholder="Toyota Vitz, Automatic, under 2M ETB..."
                class="w-full bg-white/20 backdrop-blur-md border border-white/40 rounded-2xl px-4 py-3.5 text-white placeholder-slate-300 focus:outline-none focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/50 shadow-inner text-xs resize-none"></textarea>
            </div>

            <div>
              <label class="text-cyan-300 font-semibold text-xs drop-shadow-md mb-1.5 block">
                <span class="lang-am">ፈጣን አማራጮች</span>
                <span class="lang-en">Quick Tags</span>
              </label>
              <div class="flex flex-wrap gap-1.5">
                <button type="button" class="ai-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95" data-q="መኪና">🚗 Cars / መኪኖች</button>
                <button type="button" class="ai-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95" data-q="ቤት">🏠 House / ቤቶች</button>
                <button type="button" class="ai-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95" data-q="ኦቶማቲክ">⚙️ Automatic</button>
                <button type="button" class="ai-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95" data-q="አዲስ">✨ Brand New</button>
                <button type="button" class="ai-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95" data-q="ቪላ">🏡 Villa</button>
              </div>
            </div>

            <div>
              <label class="text-cyan-300 font-semibold text-xs drop-shadow-md mb-1.5 block">
                <span class="lang-am">የበጀት መጠን</span>
                <span class="lang-en">Budget Range</span>
              </label>
              <div class="grid grid-cols-3 gap-1.5 text-xs">
                <button type="button" class="price-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95 text-center" data-price="< 1M">&lt; 1M ETB</button>
                <button type="button" class="price-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95 text-center" data-price="1M - 3M">1M - 3M ETB</button>
                <button type="button" class="price-chip bg-white/15 hover:bg-cyan-500/20 backdrop-blur-md border border-white/30 text-white rounded-xl px-3.5 py-2 text-xs font-medium transition-all active:scale-95 text-center" data-price="> 3M">&gt; 3M ETB</button>
              </div>
            </div>

            <div class="pt-1 flex gap-2">
              <button id="aiResetBtn" type="button" class="w-1/3 py-2.5 rounded-xl bg-white/15 border border-white/30 text-white font-bold text-xs backdrop-blur-md active:scale-95">
                <span class="lang-am">አጽዳ</span><span class="lang-en">Reset</span>
              </button>
              <button id="aiApplyBtn" type="button" class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 font-bold text-xs shadow-md active:scale-95 flex items-center justify-center gap-1.5">
                <span>✨ <span class="lang-am">አጣራ</span><span class="lang-en">Apply</span></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
"""

TOOLS_HUB_JS = r"""
    function renderBudgetBar(budget) {
      var b = Math.max(0, Number(budget) || 0);
      var purchase = Math.round(b * 0.70);
      var fees = Math.round(b * 0.15);
      var reserve = Math.max(0, b - purchase - fees);
      var el = document.getElementById("analysisBudgetTotal");
      if (el) el.textContent = b.toLocaleString() + " ETB";
      var set = function(id, text) { var n = document.getElementById(id); if (n) n.textContent = text; };
      set("pctPurchase", "70% · " + purchase.toLocaleString() + " ብር");
      set("pctFees", "15% · " + fees.toLocaleString() + " ብር");
      set("pctReserve", "15% · " + reserve.toLocaleString() + " ብር");
      var bp = document.getElementById("barPurchase");
      var bf = document.getElementById("barFees");
      var br = document.getElementById("barReserve");
      if (bp) bp.style.width = "70%";
      if (bf) bf.style.width = "15%";
      if (br) br.style.width = "15%";
      return { budget: b, purchase: purchase, fees: fees, reserve: reserve };
    }

    function renderAnalysisDashboard(d, budget) {
      showAnalysisView(true);
      var log = document.getElementById("advisorChatLog");
      if (log && !log.dataset.seeded) {
        log.innerHTML = "";
        advisorChatHistory = [];
        var initMsg = "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። ስለ መኪና ወይም የቤት ግዢ፣ የቀረጥ ስሌት፣ የባንክ ብድር ወይም ማንኛውም የፋይናንስ ምክር ምን ማወቅ ይፈልጋሉ? ጥያቄዎን እዚህ ይጠይቁኝ።";
        appendAdvisorChat("advisor", initMsg);
        advisorChatHistory.push({ role: "advisor", content: initMsg });
        log.dataset.seeded = "1";
      }
    }


    // Advisor Button Action — render 3 investment opportunity cards (no direct jump to chat)
    function formatEtb(n) {
      n = Math.max(0, Number(n) || 0);
      return n.toLocaleString() + " ብር";
    }
    function renderOpportunityCards() {
      var budgetEl = document.getElementById("advisorBudget");
      var incomeEl = document.getElementById("advisorMonthlyIncome");
      var budget = Math.max(0, Number(budgetEl && budgetEl.value) || 0);
      var income = Math.max(0, Number(incomeEl && incomeEl.value) || 0);
      var autoBody = document.getElementById("oppAutoBody");
      var propBody = document.getElementById("oppPropBody");
      var roiBody = document.getElementById("oppRoiBody");
      var box = document.getElementById("opportunityCards");
      if (box) box.classList.remove("hidden");
      if (autoBody) autoBody.innerHTML = "ከአዲካ ገበያ እየተጫነ…";
      if (propBody) propBody.innerHTML = "ከአዲካ ገበያ እየተጫነ…";
      if (roiBody) roiBody.innerHTML = "እየተሰላ…";

      // Ethiopian commercial bank defaults
      var DOWN_PCT = 0.30;
      var APR = 0.18;
      var AUTO_YEARS = 5;
      var MORTGAGE_YEARS = 15;

      function parsePrice(v) {
        if (v == null) return 0;
        var n = Number(String(v).replace(/[^\d.]/g, ""));
        return isFinite(n) ? n : 0;
      }
      function fmt(n) {
        n = Math.round(Number(n) || 0);
        return n.toLocaleString() + " ብር";
      }
      // Standard amortization: M = P * r(1+r)^n / ((1+r)^n - 1)
      function monthlyPayment(principal, annualRate, years) {
        if (principal <= 0) return 0;
        var r = annualRate / 12;
        var n = years * 12;
        if (r === 0) return principal / n;
        var factor = Math.pow(1 + r, n);
        return principal * (r * factor) / (factor - 1);
      }
      function titleOf(it) {
        var extra = it.extra_data || {};
        if (typeof extra === "string") {
          try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
        }
        return extra.car_model || it.sub_category || extra.house_type || it.main_category || ("#ADK-" + (it.id || ""));
      }
      function isCar(it) {
        var c = String(it.main_category || it.category || "");
        return c === "መኪና" || /car|vehicle/i.test(c);
      }
      function isHouse(it) {
        var c = String(it.main_category || it.category || "");
        return c === "ቤት" || c === "house" || /ቤት|property|house|land|መሬት/i.test(c);
      }

      // Fetch live SELL listings (real Adika DB via existing API)
      fetch("/api/explorer/listings?page=1&limit=40&order=DESC&active_only=1&type=SELL")
        .then(function(r){ return r.json(); })
        .then(function(data){
          var items = data.items || data.listings || [];
          var cars = [];
          var props = [];
          for (var i = 0; i < items.length; i++) {
            var it = items[i];
            var price = parsePrice(it.price);
            if (price <= 0) continue;
            if (isCar(it) && price <= budget) cars.push(it);
            if (isHouse(it) && (price <= budget || price * DOWN_PCT <= budget)) props.push(it);
          }
          cars.sort(function(a,b){ return parsePrice(b.price) - parsePrice(a.price); });
          props.sort(function(a,b){ return parsePrice(b.price) - parsePrice(a.price); });

          // --- Option A: Automotive ---
          if (autoBody) {
            if (cars.length === 0) {
              autoBody.innerHTML = budget > 0
                ? "በ <b>" + fmt(budget) + "</b> በጀት ውስጥ በአሁኑ ገበያ ላይ ተሽከርካሪ አልተገኘም። Mini App ገበያውን ይመልከቱ።"
                : "በጀት ያስገቡ።";
            } else {
              var top = cars.slice(0, 3);
              var lines = top.map(function(it){
                var p = parsePrice(it.price);
                var down = p * DOWN_PCT;
                var loan = p - down;
                var mpay = monthlyPayment(loan, APR, AUTO_YEARS);
                return "• <b>" + titleOf(it) + "</b> — " + fmt(p) +
                  "<br><span style='opacity:.85'>ቅድመ 30%: " + fmt(down) + " · ብድር: " + fmt(loan) +
                  " · ወርሃዊ (~18%/5ዓመት): " + fmt(mpay) + "</span>";
              });
              autoBody.innerHTML = "ከአዲካ ገበያ (" + cars.length + " ተሽከርካሪ ≤ በጀት):<br>" + lines.join("<br>");
            }
          }

          // --- Option B: Real Estate ---
          if (propBody) {
            if (props.length === 0) {
              propBody.innerHTML = budget > 0
                ? "በ <b>" + fmt(budget) + "</b> (ዋጋ ወይም 30% ቅድመ ክፍያ) የሚገኝ ቤት/መሬት በአሁኑ ገበያ አልተገኘም።"
                : "በጀት ያስገቡ።";
            } else {
              var topP = props.slice(0, 3);
              var linesP = topP.map(function(it){
                var p = parsePrice(it.price);
                var down = p * DOWN_PCT;
                var loan = Math.max(0, p - down);
                var mpay = monthlyPayment(loan, APR, MORTGAGE_YEARS);
                return "• <b>" + titleOf(it) + "</b> — " + fmt(p) +
                  "<br><span style='opacity:.85'>ቅድመ 30%: " + fmt(down) + " · ብድር: " + fmt(loan) +
                  " · ወርሃዊ (~18%/15ዓመት): " + fmt(mpay) + "</span>";
              });
              propBody.innerHTML = "ከአዲካ ገበያ (" + props.length + " ንብረት):<br>" + linesP.join("<br>");
            }
          }

          // --- Option C: Business ROI (formula-based Ethiopian benchmarks 15–35%) ---
          if (roiBody) {
            if (budget <= 0) {
              roiBody.innerHTML = "በጀት ያስገቡ።";
            } else {
              // Tier by budget size using fixed benchmark bands (not random)
              var lowY = 0.15, midY = 0.22, highY = 0.30;
              if (budget < 200000) { lowY = 0.20; midY = 0.28; highY = 0.35; }
              else if (budget < 1000000) { lowY = 0.18; midY = 0.25; highY = 0.32; }
              else { lowY = 0.15; midY = 0.22; highY = 0.28; }
              var ideas = [];
              if (budget < 150000) {
                ideas = ["ትንሽ የቁሳቁስ/ሞባይል መለዋወጫ ንግድ", "የምግብ/ጭማቂ ማስረጃ ኪዮስክ", "የመላኪያ (delivery) አገልግሎት"];
              } else if (budget < 800000) {
                ideas = ["የመኪና ኪራይ (ride) አንድ ተሽከርካሪ", "ትንሽ ሱፐርማርኬት/ሱቅ", "የጋራዥ ቀላል ጥገና አገልግሎት"];
              } else {
                ideas = ["ባለብዙ መኪና የኪራይ መርሃግብር", "ትንሽ የማከማቻ/ዌርሃውስ ኪራይ", "የሪል እስቴት ኪራይ ፖርትፎሊዮ"];
              }
              var yLow = Math.round(budget * lowY);
              var yMid = Math.round(budget * midY);
              var yHigh = Math.round(budget * highY);
              roiBody.innerHTML =
                "በጀት <b>" + fmt(budget) + "</b> — የኢትዮጵያ ገበያ ባንድ (15–35% ዓመታዊ):<br>" +
                "• " + ideas[0] + " · ROI ~" + Math.round(lowY*100) + "% → <b>" + fmt(yLow) + "/ዓመት</b><br>" +
                "• " + ideas[1] + " · ROI ~" + Math.round(midY*100) + "% → <b>" + fmt(yMid) + "/ዓመት</b><br>" +
                "• " + ideas[2] + " · ROI ~" + Math.round(highY*100) + "% → <b>" + fmt(yHigh) + "/ዓመት</b>" +
                (income > 0 ? "<br><span style='opacity:.85'>የእርስዎ ወርሃዊ ገቢ: " + fmt(income) + " (DTI ≤35% ለብድር)</span>" : "");
            }
          }
        })
        .catch(function(){
          if (autoBody) autoBody.innerHTML = "ገበያውን ማግኘት አልተቻለም። እንደገና ይሞክሩ ወይም Mini App ገበያ ይመልከቱ።";
          if (propBody) propBody.innerHTML = "ገበያውን ማግኘት አልተቻለም።";
          if (roiBody && budget > 0) {
            var y = Math.round(budget * 0.22);
            roiBody.innerHTML = "ግምታዊ መካከለኛ ROI 22%: <b>" + Math.round(budget * 0.22).toLocaleString() + " ብር/ዓመት</b> (ከበጀት ቀመር)።";
          }
        });
    }

    var advBtnEl = document.getElementById("advisorBtn");
    if (advBtnEl) {
      advBtnEl.onclick = function() {
        renderOpportunityCards();
      };
    }
    function chatPromptForContext(ctx) {
      var budget = Number((document.getElementById("advisorBudget") || {}).value) || 0;
      var income = Number((document.getElementById("advisorMonthlyIncome") || {}).value) || 0;
      var prompts = {
        auto: "በጀቴ " + budget.toLocaleString() + " ብር ነው፣ ወርሃዊ ገቢዬ " + income.toLocaleString() + " ብር ነው። በዚህ በጀት የትኛውን ተሽከርካሪ መምረጥ እችላለሁ? የባንክ ብድር አማራጭም አብረው ያብራሩልኝ።",
        property: "በጀቴ " + budget.toLocaleString() + " ብር ነው፣ ወርሃዊ ገቢዬ " + income.toLocaleString() + " ብር ነው። ለቤት/መሬት የመግቢያ ቅድመ ክፍያ እና የብድር አሰራር ያብራሩልኝ።",
        roi: "በጀቴ " + budget.toLocaleString() + " ብር ነው። የሪል እስቴት ወይም የንግድ ኢንቨስትመንት ዓመታዊ ROI እና የኪራይ ገቢ ግምት ያሳዩኝ።"
      };
      return prompts[ctx] || prompts.auto;
    }
    var hubFinBanner = document.getElementById("hubFinanceAdvisorBanner");
    if (hubFinBanner) {
      hubFinBanner.onclick = function(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        openAiChat("ስለ በጀት፣ ብድር እና የገበያ ዋጋ ጥልቅ የፋይናንስ ምክር እፈልጋለሁ።");
      };
    }
    document.querySelectorAll(".opp-chat-cta").forEach(function(btn) {
      btn.onclick = function(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        openAiChat(chatPromptForContext(btn.getAttribute("data-context") || "auto"));
      };
    });
    document.addEventListener("click", function(e) {
      var t = e.target;
      if (!t || !t.closest) return;
      var cta = t.closest(".opp-chat-cta");
      if (cta) {
        e.preventDefault();
        e.stopPropagation();
        openAiChat(chatPromptForContext(cta.getAttribute("data-context") || "auto"));
        return;
      }
      if (t.closest("#hubFinanceAdvisorBanner") || t.closest("#compareLiveChatCta")) {
        /* handled by dedicated handlers; keep stop so overlays cannot swallow */
        e.stopPropagation();
      }
    }, true);
"""
