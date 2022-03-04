from . import stats
from flask import render_template


@stats.route("/")
def index():
    return render_template("allstats.html")
