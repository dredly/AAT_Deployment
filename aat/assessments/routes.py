from flask import render_template
from . import assessments
from ..models import Assessment, QuestionT2


@assessments.route("/")
def index():
    assessments = Assessment.query.all()
    return render_template("index.html", assessments=assessments)


@assessments.route("/<int:id>")
def show_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    # TODO make a combined list of T1 and T2 questions and order by their question index
    questions = QuestionT2.query.filter_by(assessment_id=id).all()
    return render_template(
        "show_assessment.html", assessment=assessment, questions=questions
    )


@assessments.route("/new")
def new_assessment():
    return render_template("new_assessment.html")


# Just for testing
@assessments.route("/showallquestionst2")
def allt2():
    t2questions = QuestionT2.query.all()
    print(t2questions)
    return "All t2 questions"
