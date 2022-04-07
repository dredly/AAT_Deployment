from flask import Blueprint

staff_stats = Blueprint("staff_stats", __name__, template_folder="templates",static_folder="static")

from . import routes
