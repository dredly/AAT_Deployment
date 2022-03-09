from tkinter import N
from flask import redirect, render_template, request, url_for
from . import assessments
from ..models import Assessment, QuestionT2
from .forms import NewQuestionForm
from .. import db


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


@assessments.route("/<int:id>/new_question", methods=["GET", "POST"])
def new_question(id):
    assessment = Assessment.query.get_or_404(id)
    form = NewQuestionForm()
    if request.method == "POST":
        question_text = request.form["question_text"]
        correct_answer = request.form["correct_answer"]
        weighting = request.form["weighting"]
        new_question = QuestionT2(
            question_text=question_text,
            correct_answer=correct_answer,
            weighting=weighting,
            assessment_id=id,
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("assessments.show_assessment", id=id))

    return render_template("new_question.html", assessment=assessment, form=form)


@assessments.route("/new")
def new_assessment():
    return render_template("new_assessment.html")


# Just for testing
@assessments.route("/showallquestionst2")
def allt2():
    t2questions = QuestionT2.query.all()
    print(t2questions)
    return "All t2 questions"
