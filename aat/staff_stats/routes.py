from . import staff_stats
from flask import render_template


@staff_stats.route("/")
def index():
    return render_template("Staff-stats.html")

@staff_stats.route("/test")
def test():
    return render_template("test.html")

