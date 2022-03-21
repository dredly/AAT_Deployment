from tkinter import N
from flask import redirect, render_template, request, url_for, abort
from . import assessments
from ..models import Assessment, QuestionT2, Module, User 
from .forms import QuestionForm, DeleteQuestionsForm, AnswerType2Form
from .. import db


@assessments.route("/")
def index():
    assessments = Assessment.query.all()
    modules = Module.query.all()
    return render_template("index.html", assessments=assessments, modules=modules)


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
    form = QuestionForm()
    if request.method == "POST":
        question_text = request.form["question_text"]
        correct_answer = request.form["correct_answer"]
        num_of_marks = request.form["num_of_marks"]
        new_question = QuestionT2(
            question_text=question_text,
            correct_answer=correct_answer,
            num_of_marks=num_of_marks,
            assessment_id=id,
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("assessments.show_assessment", id=id))

    return render_template("new_question.html", assessment=assessment, form=form)


@assessments.route("/<int:id>/edit_question/<int:q_id>", methods=["GET", "POST"])
def edit_question(id, q_id):
    assessment = Assessment.query.get_or_404(id)
    question = QuestionT2.query.get_or_404(q_id)
    form = QuestionForm()
    if request.method == "POST":
        question.question_text = form.question_text.data
        question.correct_answer = form.correct_answer.data
        question.num_of_marks = form.num_of_marks.data
        db.session.commit()
        return redirect(url_for("assessments.show_assessment", id=id))
    form.question_text.data = question.question_text
    form.correct_answer.data = question.correct_answer
    form.num_of_marks.data = question.num_of_marks
    return render_template("edit_question.html", assessment=assessment, form=form)


@assessments.route("/<int:id>/delete_questions", methods=["GET", "POST"])
def delete_questions(id):
    assessment = Assessment.query.get_or_404(id)
    questions = QuestionT2.query.filter_by(assessment_id=id).all()
    form = DeleteQuestionsForm()
    form.questions_to_delete.choices = [
        (question.q_t2_id, question.question_text[:20]) for question in questions
    ]
    if request.method == "POST":
        # Query which returns the questions that were selected for deletion
        for_deletion = [int(q) for q in form.questions_to_delete.data]
        questions_to_delete = QuestionT2.query.filter(
            QuestionT2.q_t2_id.in_(for_deletion)
        ).all()
        for question in questions_to_delete:
            db.session.delete(question)
        db.session.commit()
        return redirect(url_for("assessments.show_assessment", id=id))
    return render_template("delete_questions.html", assessment=assessment, form=form)


@assessments.route("/new")
def new_assessment():
    return render_template("new_assessment.html")


# Linsey Routes:

# @assessments.route("/<username>/assessments")
# def list_assessments(username): 
#     user = User.query.filter_by(name=username).first()
#     if user is None: 
#         abort(404)
#     assessments = user.assessments.order_by(Assessment.due_date.desc()).all()

@assessments.route("/take_assessment/<int:id>")
def take_assessment(id): 
    assessment = Assessment.query.get_or_404(id)
    questions = QuestionT2.query.filter_by(assessment_id=id).all()
    question_ids = []
    for question in questions: 
        question_ids.append(question.q_t2_id)
    return render_template("assessment_summary.html", 
                title="Complete Assessment", 
                assessment=assessment, 
                questions=question_ids)


@assessments.route("/take_assessment/question/<int:assessment_id>/<question_ids>", methods=['GET', 'POST'])
def answer_question(assessment_id, question_ids):
    form = AnswerType2Form()
    assessment = Assessment.query.get_or_404(assessment_id)
    list_version = question_ids.replace("[", "").replace("]", "").split(",")
    question_numbers = [int(x) for x in list_version]
    if len(question_numbers) >= 1:
        question_id = question_numbers.pop(0)
    else: 
        question_id = question_numbers[0]
    question = QuestionT2.query.filter_by(q_t2_id=question_id).first()
    if request.method == 'POST':
        print(form.answer.data)
        return render_template("mark_answer.html", 
                assessment_id=assessment_id, 
                question_ids=question_numbers)
    return render_template("answer_question.html", 
                question=question, 
                assessment=assessment, 
                form=form,  
                question_ids=question_numbers)

@assessments.route("/take_assesssment/answer/<int:assessment_id>/<question_ids>")
def mark_answer(assessment_id, question_ids): 
    return render_template("mark_answer.html", 
                assessment_id=assessment_id, 
                question_ids=question_ids)