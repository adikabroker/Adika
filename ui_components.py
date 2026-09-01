# -*- coding: utf-8 -*-
"""Adika Mini App — loads HTML from ui_templates.html (no Python-in-HTML)."""
from __future__ import annotations

import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "ui_templates.html")
SELLER_PATH = os.path.join(BASE_DIR, "seller_form.html")
BUYER_PATH = os.path.join(BASE_DIR, "buyer_form.html")

def _read_html(path: str, fallback: str = "") -> str:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as exc:
        logging.getLogger(__name__).warning("html load failed %s: %s", path, exc)
    return fallback

def load_full_template() -> str:
    html = _read_html(HTML_FILE_PATH)
    if html and html.lstrip().startswith("<"):
        return html
    return "<!DOCTYPE html><html><body><h1>Error: ui_templates.html not found</h1></body></html>"

EXPLORER_HTML = load_full_template()
_seller = _read_html(SELLER_PATH)
_buyer = _read_html(BUYER_PATH)
SELLER_FORM_HTML = _seller if _seller.lstrip().startswith("<") else EXPLORER_HTML
BUYER_FORM_HTML = _buyer if _buyer.lstrip().startswith("<") else EXPLORER_HTML
