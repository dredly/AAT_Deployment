from flask import render_template
from . import app

# Currently not used due to issues with imports.
# Error handling defined in __init__.py

# https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_handling/404.html"), 404
