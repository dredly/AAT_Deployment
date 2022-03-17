from . import app
from flask import render_template


@app.route("/")
def initial_home():
    return render_template("landing_page.html")
