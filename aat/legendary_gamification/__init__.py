from flask import Blueprint

legendary_gamification = Blueprint("legendary_gamification", __name__, template_folder="templates", static_folder="static")

from . import routes
