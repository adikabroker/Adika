# -*- coding: utf-8 -*-
"""Compatibility alias for the mistyped GitHub filename `ui_jtyles.py`.

Canonical module is `ui_styles.py`. Keep this file so Render never dies
if the typo filename is still present in the repo.
"""
from ui_styles import *  # noqa: F401,F403
from ui_styles import (
    BUYER_FORM_CSS,
    BUYER_FORM_STYLE_TAG,
    EXPLORER_CSS,
    EXPLORER_STYLE_TAG,
    SELLER_FORM_CSS,
    SELLER_FORM_STYLE_TAG,
    style_tag,
)
