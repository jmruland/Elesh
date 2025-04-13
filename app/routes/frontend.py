from flask import Blueprint, render_template, current_app
import os
import json
from config import SUMMARY_FILE

frontend_bp = Blueprint("frontend", __name__, template_folder="../templates")

@frontend_bp.route("/")
def index():
    lore_data = []
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            lore_data = json.load(f)
    return render_template("index.html", lore=lore_data)