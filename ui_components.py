# -*- coding: utf-8 -*-
"""Adika Mini App — Module 3 aggregator.

Loads sibling modules from THIS file's directory so Render/Gunicorn
never raises ModuleNotFoundError (cwd-independent).

Also accepts the GitHub typo filename `ui_jtyles.py` as a fallback.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE and _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    from ui_styles import (
        BUYER_FORM_STYLE_TAG,
        EXPLORER_STYLE_TAG,
        SELLER_FORM_STYLE_TAG,
    )
except ImportError:
    from ui_jtyles import (  # noqa: F401 — typo-filename fallback
        BUYER_FORM_STYLE_TAG,
        EXPLORER_STYLE_TAG,
        SELLER_FORM_STYLE_TAG,
    )

from ui_tools import TOOLS_HUB_HTML, TOOLS_HUB_JS


SELLER_FORM_HTML = (
    "<!DOCTYPE html><html lang=\"am\"><head><meta charset=\"UTF-8\"/>"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>"
    "<script src=\"https://telegram.org/js/telegram-web-app.js\"></script>"
    "<script src=\"https://cdn.tailwindcss.com\"></script>"
    + SELLER_FORM_STYLE_TAG
    + "</head><body class=\"bg-[#b5eff3] min-h-screen\"></body></html>"
)

BUYER_FORM_HTML = (
    "<!DOCTYPE html><html lang=\"am\"><head><meta charset=\"UTF-8\"/>"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>"
    "<script src=\"https://telegram.org/js/telegram-web-app.js\"></script>"
    "<script src=\"https://cdn.tailwindcss.com\"></script>"
    + BUYER_FORM_STYLE_TAG
    + "</head><body class=\"bg-[#b5eff3] min-h-screen\"></body></html>"
)

EXPLORER_HTML = f"""<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
  <title>Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  {EXPLORER_STYLE_TAG}
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
{TOOLS_HUB_HTML}
<script>
window.setActiveTab = window.setActiveTab || function(tab) {{
  if (tab === "chat" && typeof window.openAiChat === "function") window.openAiChat();
}};
{TOOLS_HUB_JS}
</script>
</body>
</html>
"""
