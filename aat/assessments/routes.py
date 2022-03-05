from flask import render_template
from . import assessments
from ..models import QuestionT2


@assessments.route("/")
def index():
    return render_template("index.html")


# Just for testing
@assessments.route("/showallquestionst2")
def allt2():
    t2questions = QuestionT2.query.all()
    print(t2questions)
    return "All t2 questions"
