from flask import Blueprint

student_stats = Blueprint(
    "student_stats", __name__, template_folder="templates", static_folder="static"
)


from . import routes
