from flask import request, redirect, url_for, render_template
from .forms import QuestionT2Form, FilterForm
from ..models import QuestionT1, QuestionT2
from . import questions
from .. import db


@questions.route("/")
def index():
    form = FilterForm()
    filter = request.args.get("filter", "all")
    form.filter.data = filter
    if request.method == "POST":
        filter = request.form["filter"]
        return redirect(url_for("questions.index", filter=filter))
    if filter == "type1":
        questions = QuestionT1.query.all()
    elif filter == "type2":
        questions = QuestionT2.query.all()
    elif filter == "floating":
        questions = (
            QuestionT1.query.filter(QuestionT1.assessment_id.is_(None)).all()
            + QuestionT2.query.filter(QuestionT2.assessment_id.is_(None)).all()
        )
    elif filter == "assigned":
        questions = (
            QuestionT1.query.filter(QuestionT1.assessment_id.isnot(None)).all()
            + QuestionT2.query.filter(QuestionT2.assessment_id.isnot(None)).all()
        )
    else:
        questions = QuestionT1.query.all() + QuestionT2.query.all()
    return render_template("questions_index.html", questions=questions, form=form)


# --- Type 1 routes ---


@questions.route("/type1/new", methods=["GET", "POST"])
def new_question_t1():
    return "Add a type 1 question here"


@questions.route("/type1/<int:id>/edit", methods=["GET", "POST"])
def edit_question_t1(id):
    return "Edit a type 1 question here"


# --- Type 2 routes ---


@questions.route("/type2/new", methods=["GET", "POST"])
def new_question_t2():
    form = QuestionT2Form()
    if request.method == "POST":
        question_text = request.form["question_text"]
        correct_answer = request.form["correct_answer"]
        num_of_marks = request.form["num_of_marks"]
        difficulty = request.form["difficulty"]
        feedback_if_correct = request.form["feedback_if_correct"]
        feedback_if_wrong = request.form["feedback_if_wrong"]
        new_question = QuestionT2(
            question_text=question_text,
            correct_answer=correct_answer,
            num_of_marks=num_of_marks,
            difficulty=difficulty,
            feedback_if_correct=feedback_if_correct,
            feedback_if_wrong=feedback_if_wrong,
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("questions.index"))
    return render_template("new_question_t2.html", form=form)


@questions.route("/type2/<int:id>/edit", methods=["GET", "POST"])
def edit_question_t2(id):
    question = QuestionT2.query.get_or_404(id)
    form = QuestionT2Form()
    if request.method == "POST":
        question.question_text = form.question_text.data
        question.correct_answer = form.correct_answer.data
        question.num_of_marks = form.num_of_marks.data
        question.difficulty = form.difficulty.data
        question.feedback_if_correct = form.feedback_if_correct.data
        question.feedback_if_wrong = form.feedback_if_wrong.data
        db.session.commit()
        return redirect(url_for("assessments.show_assessment", id=id))
    form.question_text.data = question.question_text
    form.correct_answer.data = question.correct_answer
    form.num_of_marks.data = question.num_of_marks
    form.difficulty.data = question.difficulty
    form.feedback_if_correct.data = question.feedback_if_correct
    form.feedback_if_wrong.data = question.feedback_if_wrong
    return render_template("edit_question_t2.html", form=form)
