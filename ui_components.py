import os
import re

# Absolute path configuration to safely find ui_templates.html on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "ui_templates.html")

def load_full_template():
    if not os.path.exists(HTML_FILE_PATH):
        return f"<h1>Error: ui_templates.html not found at {HTML_FILE_PATH}</h1>"
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()

# Load full UI HTML string
EXPLORER_HTML = load_full_template()

# Fallback definitions for components expected by webapp.py
# If specific forms are embedded inside ui_templates.html, export EXPLORER_HTML
BUYER_FORM_HTML = EXPLORER_HTML
SELLER_FORM_HTML = EXPLORER_HTML
