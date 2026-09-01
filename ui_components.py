import os

# Set absolute path to ensure Render/Flask finds the HTML file safely
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
