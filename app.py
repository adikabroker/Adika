# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, send_from_directory, jsonify, request

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def home():
    return render_template("index.html")

# Flat fallbacks if Mini App requests /style.css or /script.js
@app.route("/style.css")
def style_root():
    return send_from_directory(app.static_folder, "style.css")

@app.route("/script.js")
def script_root():
    return send_from_directory(os.path.join(app.static_folder, "js"), "ui.js")

@app.route("/telegram.js")
def tg_root():
    return send_from_directory(os.path.join(app.static_folder, "js"), "telegram.js")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
