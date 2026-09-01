# -*- coding: utf-8 -*-
"""Thin Flask UI loader. HTML lives in static/*.html — do not embed templates here."""
from __future__ import annotations

import logging
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_STATIC = os.path.join(_HERE, "static")
if not os.path.isdir(_STATIC):
    _STATIC = _HERE  # fallback: html files next to this module


def _load(name: str) -> str:
    for folder in (_STATIC, _HERE):
        path = os.path.join(folder, name)
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    html = f.read()
                if html.lstrip().startswith("<"):
                    return html
        except Exception as exc:
            logging.getLogger(__name__).warning("failed reading %s: %s", path, exc)
    return (
        "<!DOCTYPE html><html><body style='font-family:sans-serif;padding:24px'>"
        "<h1>UI file missing</h1><p>Place index.html next to ui_components.py or in static/</p>"
        "</body></html>"
    )


EXPLORER_HTML = _load("index.html")
if EXPLORER_HTML.startswith("<!DOCTYPE html><html><body") and "missing" in EXPLORER_HTML:
    EXPLORER_HTML = _load("ui_templates.html")

SELLER_FORM_HTML = _load("seller_form.html")
BUYER_FORM_HTML = _load("buyer_form.html")
