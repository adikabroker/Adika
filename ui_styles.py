# -*- coding: utf-8 -*-
"""Adika Mini App CSS modules (Module 1 of 5).

Extracted from the monolithic ui_components.py templates.
Z-index contract (do not invert):
  Marketplace chrome / bottom nav ........ 40–100
  Tools Hub overlay (#aiModal) ........... 220
  AI Live Chat overlay (#analysisView) ... 280
"""

# ---------------------------------------------------------------------------
# Seller / Post Listing form
# ---------------------------------------------------------------------------
SELLER_FORM_CSS = r"""
    body { margin:0; background:#b5eff3; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .lang-en { display: none !important; }
    .lang-am { display: inline-block !important; }
    body.lang-en-active .lang-en { display: inline-block !important; }
    body.lang-en-active .lang-am { display: none !important; }
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 600; }
    input, textarea, select { font-size: 15px !important; }

    .promo-slide { will-change: opacity, transform; }
    .promo-slide .promo-orb {
      transition: opacity 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) 0ms,
                  transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) 0ms;
    }
    .promo-slide .promo-icon {
      transition: opacity 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 80ms,
                  transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 80ms;
    }
    .promo-slide .promo-title,
    .promo-slide .promo-sub {
      transition: opacity 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 160ms,
                  transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 160ms;
    }
    .promo-slide .promo-cta {
      transition: opacity 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 240ms,
                  transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 240ms;
    }
    .promo-slide:not(.is-active) .promo-orb,
    .promo-slide:not(.is-active) .promo-icon,
    .promo-slide:not(.is-active) .promo-title,
    .promo-slide:not(.is-active) .promo-sub,
    .promo-slide:not(.is-active) .promo-cta {
      opacity: 0;
      transform: scale(0.85) translateY(12px);
    }
    .promo-slide.is-active .promo-orb {
      opacity: 1;
      transform: scale(1);
      animation: adikaGlowOrb 2s ease-in-out infinite;
    }
    .promo-slide.is-active .promo-icon {
      opacity: 1;
      transform: scale(1) rotateY(0deg);
    }
    .promo-slide.is-active .promo-title,
    .promo-slide.is-active .promo-sub {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    .promo-slide.is-active .promo-cta {
      opacity: 1;
      transform: translateY(0) scale(1);
      animation: adikaHeartbeat 1.6s ease-in-out infinite;
      animation-delay: 0.4s;
    }
    .promo-slide.is-active {
      opacity: 1 !important;
      transform: scale(1) translateY(0) !important;
      pointer-events: auto !important;
      z-index: 2;
    }
    .promo-slide.is-exit {
      opacity: 0 !important;
      transform: scale(0.92) translateY(-22px) !important;
      pointer-events: none !important;
      z-index: 1;
    }
    .promo-slide.is-active .promo-letter {
      animation: adikaLetterIn 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
    #adikaPromoBanner {
      animation: adikaNeonPulse 2.2s ease-in-out infinite;
    }

    @keyframes adikaShimmer {
      0% { transform: translateX(-120%); }
      100% { transform: translateX(120%); }
    }
    @keyframes adikaNeonPulse {
      0%, 100% { box-shadow: 0 0 10px rgba(34,211,238,0.35), 0 0 18px rgba(56,189,248,0.2), inset 0 1px 0 rgba(255,255,255,0.1); }
      50% { box-shadow: 0 0 16px rgba(45,212,191,0.45), 0 0 24px rgba(34,211,238,0.28), inset 0 1px 0 rgba(255,255,255,0.12); }
    }
    @keyframes adikaGlowOrb {
      0%, 100% { transform: scale(1); opacity: 0.5; }
      50% { transform: scale(1.18); opacity: 0.85; }
    }
    @keyframes adikaHeartbeat {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.06); }
    }
    @keyframes adikaLetterIn {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }
"""

# ---------------------------------------------------------------------------
# Buyer request form
# ---------------------------------------------------------------------------
BUYER_FORM_CSS = r"""
    body { margin:0; background:#b5eff3; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .lang-en { display: none !important; }
    .lang-am { display: inline-block !important; }
    body.lang-en-active .lang-en { display: inline-block !important; }
    body.lang-en-active .lang-am { display: none !important; }
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 600; }
    input, textarea { font-size: 15px !important; }
  """

# ---------------------------------------------------------------------------
# Marketplace explorer + Tools Hub + Live Chat
# ---------------------------------------------------------------------------
EXPLORER_CSS = r"""
    html, body {
      margin: 0; padding: 0; width: 100%; max-width: 100vw;
      overflow-x: hidden; box-sizing: border-box;
      font-family: system-ui, -apple-system, sans-serif;
      background: #b5eff3; color: #0f172a;
      -webkit-tap-highlight-color: transparent;
    }
    *, *::before, *::after { box-sizing: border-box; }

    /* Bulletproof CSS Dual-Class Language Switcher */
    .lang-en { display: none !important; }
    .lang-am { display: inline-block !important; }
    body.lang-en-active .lang-en { display: inline-block !important; }
    body.lang-en-active .lang-am { display: none !important; }

    .adika-card {
      background: #ffffff;
      border: 1px solid rgba(226, 232, 240, 0.8);
      border-radius: 1rem;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
      position: relative;
    }
    .adika-card:active {
      transform: scale(0.98);
    }

    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

    /* Executive hero carousel — compact max 110px */
    
    /* vibrant-cat-tabs */
    #feedModes button, .feed-mode-btn, [data-feed-mode], #catsRow button, .cat-pill {
      font-weight: 800 !important;
      box-shadow: 0 2px 8px rgba(0, 96, 100, 0.25) !important;
    }
    #feedModes button.active, .feed-mode-btn.active, [data-feed-mode].active,
    #catsRow button.active, .cat-pill.active {
      background: #006064 !important;
      color: #fff !important;
      box-shadow: 0 3px 12px rgba(0, 96, 100, 0.45) !important;
      ring: 2px solid rgba(255,255,255,0.8);
      transform: scale(1.04);
    }
    #feedModes button:not(.active), .feed-mode-btn:not(.active),
    #catsRow button:not(.active), .cat-pill:not(.active) {
      background: rgba(255,255,255,0.92) !important;
      color: #006064 !important;
      border: 1px solid rgba(255,255,255,0.7) !important;
    }

    .smart-dot {
      width: 6px; height: 6px; border-radius: 999px;
      background: rgba(255,255,255,0.25); transition: all 0.3s ease;
      border: none; padding: 0; cursor: pointer;
    }
    .smart-dot.active {
      width: 18px; background: #22d3ee;
    }
    .smart-slide { display: none; }
    .smart-slide.active { display: block; animation: smartFade 0.4s ease; }
    @keyframes smartFade {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    #smartToolsBanner { max-height: 78px; }
    .line-clamp-1 { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .hero-carousel {
      display: flex; gap: 0.4rem; overflow-x: auto; scroll-snap-type: x mandatory;
      -webkit-overflow-scrolling: touch; padding-bottom: 0;
      max-height: 110px;
    }
    .hero-carousel::-webkit-scrollbar { display: none; }
    .hero-slide {
      scroll-snap-align: start; flex: 0 0 72%; min-width: 72%;
      max-height: 96px; border-radius: 0.7rem; border: 1px solid rgb(30 41 59);
      background: linear-gradient(90deg, #020617 0%, #0f172a 50%, #020617 100%);
      padding: 0.4rem 0.65rem; color: #f8fafc;
      box-shadow: 0 4px 12px rgba(2, 6, 23, 0.28);
      transition: transform 0.12s ease;
      display: flex; flex-direction: column; justify-content: center;
    }
    .hero-slide:active { transform: scale(0.985); }
    .hero-slide .accent { color: #fbbf24; font-size: 9px; }
    .hero-slide .hero-title { font-size: 11px; font-weight: 900; line-height: 1.2; }
    .hero-slide .hero-sub { font-size: 8px; color: #94a3b8; line-height: 1.25; margin-top: 2px; }
    .hero-slide .hero-cta-line { font-size: 8px; font-weight: 700; margin-top: 4px; }
    .hero-dots { display: flex; justify-content: center; gap: 4px; margin-top: 4px; }
    .hero-dot { width: 4px; height: 4px; border-radius: 999px; background: rgba(15,23,42,0.25); }
    .hero-dot.active { background: #0e7490; width: 12px; }

    /* Instagram-style listing photo auto-enhancement (zero-cost CSS) */
    .listing-photo-frame {
      position: relative;
      width: 100%;
      aspect-ratio: 4 / 3;
      overflow: hidden;
      border-radius: 0.75rem;
      background: #e2e8f0;
    }
    .listing-photo-frame::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 0;
      background: linear-gradient(145deg, #cbd5e1, #94a3b8);
      filter: blur(12px);
      transform: scale(1.08);
    }
    .listing-photo-enhance {
      position: relative;
      z-index: 1;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      border-radius: 0.75rem;
      filter: contrast(108%) brightness(102%) saturate(110%);
      -webkit-filter: contrast(108%) brightness(102%) saturate(110%);
      transition: filter 0.2s ease, transform 0.2s ease;
    }
    .adika-card:active .listing-photo-enhance {
      transform: scale(1.02);
    }


    /* Glass chat bubbles */
    .chat-bubble-user {
      margin-left: 1.5rem; padding: 0.7rem 0.85rem; border-radius: 1rem;
      background: linear-gradient(135deg, #0d9488, #059669);
      color: #fff; box-shadow: 0 8px 24px rgba(13, 148, 136, 0.25);
      border: 1px solid rgba(255,255,255,0.15);
      backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    }
    .chat-bubble-ai {
      margin-right: 1.5rem; padding: 0.7rem 0.85rem; border-radius: 1rem;
      background: rgba(255,255,255,0.55);
      border: 1px solid rgba(255,255,255,0.45);
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      color: #0f172a;
    }
    .chat-input-bar {
      display: flex; align-items: flex-end; gap: 0.4rem;
      padding: 0.55rem; border-top: 1px solid rgba(226,232,240,0.9);
      background: rgba(255,255,255,0.85);
      backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    }
    .chat-input-bar textarea {
      flex: 1; min-height: 38px; max-height: 110px; resize: none;
      border-radius: 0.85rem; padding: 0.55rem 0.75rem;
      font-size: 12px; line-height: 1.4; border: 1px solid #e2e8f0;
      background: #f8fafc; outline: none;
    }
    .chat-input-bar textarea:focus { border-color: #14b8a6; box-shadow: 0 0 0 2px rgba(20,184,166,0.2); }
    .chat-send-btn {
      width: 38px; height: 38px; border-radius: 999px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, #0d9488, #059669); color: #fff;
      border: none; box-shadow: 0 4px 12px rgba(13,148,136,0.35);
    }
    .chat-send-btn:active { transform: scale(0.94); }

    /* Corporate tool cards */
    .tool-card-pro {
      padding: 0.4rem 0.45rem; border-radius: 0.75rem; text-align: left;
      background: rgba(6, 182, 212, 0.08);
      border: 1px solid rgba(34, 211, 238, 0.28);
      color: #e2e8f0;
      backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
      transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
      display: flex; flex-direction: column; justify-content: space-between; gap: 0.28rem;
      box-shadow: 0 4px 14px rgba(2, 6, 23, 0.15);
      min-height: 0; height: auto; position: relative; overflow: hidden;
    }
    .tool-card-pro:hover {
      transform: translateY(-3px) scale(1.015);
      background: rgba(34, 211, 238, 0.12);
      border-color: rgba(34, 211, 238, 0.4);
      box-shadow: 0 8px 22px rgba(6, 182, 212, 0.22);
    }
    .tool-card-pro:active { transform: scale(0.97); }
    .tool-card-pro .tool-title {
      font-weight: 800; font-size: 0.75rem; color: #ffffff; line-height: 1.15;
      text-shadow: 0 1px 3px rgba(0,0,0,0.55);
    }
    .tool-card-pro .tool-sub {
      font-size: 7px; font-weight: 600; line-height: 1.15;
      color: #22d3ee; opacity: 0.92;
      filter: drop-shadow(0 0 6px rgba(34, 211, 238, 0.35));
    }
    .tool-icon-wrap {
      width: 1.75rem; height: 1.75rem; border-radius: 0.45rem;
      display: flex; align-items: center; justify-content: center;
      background: rgba(34, 211, 238, 0.12);
      border: 1px solid rgba(34, 211, 238, 0.30);
      color: #67e8f9;
    }
    .tool-icon-wrap svg { width: 11px; height: 11px; }
    #aiToolsView {
      position: relative; z-index: 1;
      display: flex; flex-direction: column;
      overflow-y: auto !important;
      min-height: 0;
    }
    .tools-ambient-wrap { position: relative; overflow: hidden; }
    .tools-ambient-blob {
      position: absolute; width: 11rem; height: 11rem; border-radius: 9999px;
      filter: blur(48px); pointer-events: none; z-index: 0;
    }
    .tools-ambient-blob.cyan { top: 1.5rem; left: -1rem; background: rgba(6, 182, 212, 0.32); }
    .tools-ambient-blob.indigo { bottom: 2rem; right: -1rem; background: rgba(99, 102, 241, 0.28); }
    .budget-glass-card {
      position: relative; z-index: 1;
      background: rgba(255,255,255,0.12);
      backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.28);
      border-radius: 1.25rem;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .budget-glass-card input {
      background: rgba(255,255,255,0.18) !important;
      border: 1px solid rgba(255,255,255,0.28) !important;
      color: #fff !important;
      backdrop-filter: blur(8px);
    }
    .budget-glass-card label, .budget-glass-card .text-slate-700 { color: rgba(255,255,255,0.9) !important; }
    .advisor-preset-chip {
      background: rgba(255,255,255,0.14) !important;
      border: 1px solid rgba(255,255,255,0.25) !important;
      color: #e0f2fe !important;
    }
    @keyframes toolCardIn {
      from { opacity: 0; transform: translateY(14px) scale(0.96); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .tool-card-pro.stagger-in { animation: toolCardIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both; }

    .adika-success-pulse {
      animation: adikaPulse 1.2s ease-in-out infinite;
    }
    @keyframes adikaPulse {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(16,185,129,0.35); }
      50% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(16,185,129,0); }
    }
    .land-scan-laser {
      background: linear-gradient(180deg, transparent 0%, rgba(34,211,238,0.15) 48%, rgba(34,211,238,0.55) 50%, rgba(34,211,238,0.15) 52%, transparent 100%);
      background-size: 100% 200%;
      animation: landScan 1.4s linear infinite;
    }
    @keyframes landScan {
      0% { background-position: 0% 0%; }
      100% { background-position: 0% 100%; }
    }

    .tools-grid-compact {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem;
      flex: 0 1 auto; height: auto; align-items: start;
    }
    @media (max-width: 340px) {
      .tools-grid-compact { grid-template-columns: repeat(2, 1fr); }
    }
    .opp-card {
      border-radius: 0.65rem; padding: 0.45rem 0.55rem;
      background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
      border: 1px solid #334155; color: #e2e8f0;
      box-shadow: 0 4px 12px rgba(2,6,23,0.2);
    }
    .opp-card .opp-label { font-size: 8px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
    .opp-card .opp-title { font-size: 11px; font-weight: 900; color: #fff; margin-top: 1px; line-height: 1.2; }
    .opp-card .opp-body { font-size: 9px; color: #94a3b8; margin-top: 3px; line-height: 1.35; }
    .opp-card .opp-cta {
      margin-top: 0.35rem; width: 100%; padding: 0.35rem 0.4rem;
      border-radius: 0.45rem; font-size: 8px; font-weight: 800; line-height: 1.25;
      background: linear-gradient(90deg, #0d9488, #0891b2); color: #fff;
      border: none; text-align: center;
    }
    /* Sticky chat input at absolute bottom of analysis view */
    .custom-scrollbar { -webkit-overflow-scrolling: touch; scrollbar-width: thin; scrollbar-color: rgba(34,211,238,0.45) transparent; }
    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(34,211,238,0.4); border-radius: 999px; }
    #analysisView { display: none; flex-direction: column; z-index: 280 !important; }
    #analysisView.flex { display: flex !important; z-index: 280 !important; }
    #analysisView .chat-shell {
      flex: 1; display: flex; flex-direction: column; min-height: 0;
      position: relative; padding-bottom: 0;
    }
    #analysisView .chat-input-sticky {
      position: fixed; bottom: 0; left: 0; right: 0;
      max-width: 28rem; margin: 0 auto;
      z-index: 70;
      background: rgba(255,255,255,0.95);
      backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      border-top: 1px solid rgba(226,232,240,0.95);
      padding: 0.5rem 0.65rem calc(0.5rem + env(safe-area-inset-bottom, 0px));
      box-shadow: 0 -4px 16px rgba(15,23,42,0.08);
    }
    #analysisView .analysis-body {
      flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch;
      padding-bottom: 120px !important;
    }
    #analysisView #advisorChatLog {
      padding-bottom: 5.5rem !important;
    }
  """


def style_tag(css: str) -> str:
    """Wrap a CSS blob in a <style> element for HTML templates."""
    return "<style>\n" + css + "\n  </style>"


SELLER_FORM_STYLE_TAG = style_tag(SELLER_FORM_CSS)
BUYER_FORM_STYLE_TAG = style_tag(BUYER_FORM_CSS)
EXPLORER_STYLE_TAG = style_tag(EXPLORER_CSS)
