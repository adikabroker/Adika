import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.join(BASE_DIR, "ui_templates.html")

def load_ui_template():
    try:
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error loading UI Template: {str(e)}</h1>"

# Main HTML string consumed by webapp.py
EXPLORER_HTML = load_ui_template()

# Fallback/Aliases for secondary HTML imports expected by webapp.py
SELLER_FORM_HTML = EXPLORER_HTML
MAIN_LAYOUT_HTML = EXPLORER_HTML
