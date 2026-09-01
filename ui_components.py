# -*- coding: utf-8 -*-
"""Adika Mini App templates.

Edit the HTML in ./static/ (or next to this file):
  static/index.html        -> marketplace (EXPLORER_HTML)
  static/seller_form.html  -> seller form (SELLER_FORM_HTML)
  static/buyer_form.html   -> buyer form (BUYER_FORM_HTML)

webapp.py keeps importing the same names.
"""
from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_STATIC = os.path.join(_HERE, "static")


def _read(name: str, fallback: str = "") -> str:
    for folder in (_STATIC, _HERE):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
    return fallback


SELLER_FORM_HTML = _read("seller_form.html")
BUYER_FORM_HTML = _read("buyer_form.html")
EXPLORER_HTML = _read("index.html")
