from flask import Blueprint

questions = Blueprint(
    "questions", __name__, template_folder="templates", static_folder="static"
)

from . import routes
