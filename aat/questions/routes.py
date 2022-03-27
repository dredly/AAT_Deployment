from flask import request, redirect, url_for, render_template
from .forms import QuestionT2Form, QuestionT1Form
from .forms import QuestionT2Form, FilterForm, RadioField
from ..models import QuestionT1, QuestionT2, Option
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
    form = QuestionT1Form()
    if request.method == "POST":
        question_text = request.form["question_text"]
        option_a_text = request.form["option_a"]
        option_b_text = request.form["option_b"]
        option_c_text = request.form["option_c"]
        correct_option = request.form["correct_option"]
        num_of_marks = request.form["num_of_marks"]
        difficulty = request.form["difficulty"]
        feedback_if_correct = request.form["feedback_if_correct"]
        feedback_if_wrong = request.form["feedback_if_wrong"]
        new_question = QuestionT1(
            question_text=question_text,
            num_of_marks=num_of_marks,
            difficulty=difficulty,
            feedback_if_correct=feedback_if_correct,
            feedback_if_wrong=feedback_if_wrong,
        )
        db.session.add(new_question)
        found_question = QuestionT1.query.filter(
            QuestionT1.question_text == new_question.question_text
        ).first()
        option_a = Option(q_t1_id=found_question.q_t1_id, option_text=option_a_text)
        option_b = Option(q_t1_id=found_question.q_t1_id, option_text=option_b_text)
        option_c = Option(q_t1_id=found_question.q_t1_id, option_text=option_c_text)
        if correct_option == "a":
            option_a.is_correct = True
        elif correct_option == "b":
            option_b.is_correct = True
        elif correct_option == "c":
            option_c.is_correct = True
        db.session.add(option_a)
        db.session.add(option_b)
        db.session.add(option_c)
        db.session.commit()
        return redirect(url_for("questions.index"))
    return render_template("new_question_t1.html", form=form)


@questions.route("/type1/<int:id>", methods=["GET", "POST"])
def show_question_t1(id):
    return "Show a type 1 question here"


@questions.route("/type1/<int:id>/edit", methods=["GET", "POST"])
def edit_question_t1(id):
    question = QuestionT1.query.get_or_404(id)
    options = Option.query.filter_by(q_t1_id=id).all()
    correct_option = Option.query.filter(
        Option.q_t1_id == id and Option.is_correct
    ).first()
    form = QuestionT1Form()
    if request.method == "POST":
        question.question_text = form.question_text.data
        options[0].option_text = form.option_a.data
        options[1].option_text = form.option_b.data
        options[2].option_text = form.option_c.data
        correct_option_index = int(form.correct_option.data)
        for i in range(len(options)):
            if i == correct_option_index:
                options[i].is_correct = True
            else:
                options[i].is_correct = False

        question.num_of_marks = form.num_of_marks.data
        question.difficulty = form.difficulty.data
        question.feedback_if_correct = form.feedback_if_correct.data
        question.feedback_if_wrong = form.feedback_if_wrong.data
        db.session.commit()
        return redirect(url_for("questions.index", id=id))
    form.question_text.data = question.question_text
    form.num_of_marks.data = question.num_of_marks
    form.difficulty.data = question.difficulty
    form.feedback_if_correct.data = question.feedback_if_correct
    form.feedback_if_wrong.data = question.feedback_if_wrong
    form.correct_option.default = options.index(correct_option)

    form.option_a.data = options[0]
    form.option_b.data = options[1]
    form.option_c.data = options[2]
    return render_template("edit_question_t1.html", form=form)


@questions.route("/type1/<int:id>/delete", methods=["GET", "POST"])
def delete_question_t1(id):
    return "Delete form will go here"


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


@questions.route("/type2/<int:id>", methods=["GET", "POST"])
def show_question_t2(id):
    question = QuestionT2.query.get_or_404(id)
    return render_template("show_question_t2.html", question=question)


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
        return redirect(url_for("questions.index", id=id))
    form.question_text.data = question.question_text
    form.correct_answer.data = question.correct_answer
    form.num_of_marks.data = question.num_of_marks
    form.difficulty.data = question.difficulty
    form.feedback_if_correct.data = question.feedback_if_correct
    form.feedback_if_wrong.data = question.feedback_if_wrong
    return render_template("edit_question_t2.html", form=form)


@questions.route("/type2/<int:id>/delete", methods=["GET", "POST"])
def delete_question_t2(id):
    return "Delete form will go here"
