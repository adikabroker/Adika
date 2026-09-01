# -*- coding: utf-8 -*-
"""Adika Mini App HTML templates — main entry (Module 5 of 5).

Public API expected by webapp.py / handlers.py:
    SELLER_FORM_HTML, BUYER_FORM_HTML, EXPLORER_HTML

Submodules (edit these for targeted UI work):
    ui_styles.py   CSS + z-index contract (chat overlay = 280)
    ui_tools.py    Tools Hub + budget / investment calculators
    ui_chat.py     Live Advisor chat window + openAiChat routing
    ui_market.py   Marketplace hero + listing cards

The assembled page strings still come from ui_templates_full.py so
Render deploys stay byte-compatible with the last working Mini App.
Fragments below are re-exported so future assembly can swap sections
without touching the Flask import path.
"""

from __future__ import annotations

from ui_styles import (  # noqa: F401
    BUYER_FORM_CSS,
    BUYER_FORM_STYLE_TAG,
    EXPLORER_CSS,
    EXPLORER_STYLE_TAG,
    SELLER_FORM_CSS,
    SELLER_FORM_STYLE_TAG,
    style_tag,
)
from ui_tools import (  # noqa: F401
    APR_DEFAULT,
    AUTO_LOAN_YEARS,
    DOWN_PAYMENT_PCT,
    MORTGAGE_YEARS,
    TOOLS_HUB_HTML,
    TOOLS_HUB_JS,
    loan_package,
    monthly_payment,
    split_budget,
)
from ui_chat import (  # noqa: F401
    CHAT_ENDPOINT,
    CHAT_JS,
    CHAT_WINDOW_HTML,
    DEFAULT_ADVISOR_GREETING,
)
from ui_market import (  # noqa: F401
    LISTINGS_ENDPOINT,
    MARKET_FEED_HTML,
    MARKET_JS,
    first_photo_url,
    format_listing_price,
)

from ui_templates_full import (  # production templates
    BUYER_FORM_HTML,
    EXPLORER_HTML,
    SELLER_FORM_HTML,
)

__all__ = [
    "SELLER_FORM_HTML",
    "BUYER_FORM_HTML",
    "EXPLORER_HTML",
    "EXPLORER_STYLE_TAG",
    "TOOLS_HUB_HTML",
    "TOOLS_HUB_JS",
    "CHAT_WINDOW_HTML",
    "CHAT_JS",
    "MARKET_FEED_HTML",
    "MARKET_JS",
    "monthly_payment",
    "loan_package",
    "format_listing_price",
    "first_photo_url",
]
