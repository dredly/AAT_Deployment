from tkinter import N
from flask import redirect, render_template, request, url_for
from . import assessments
from ..models import Assessment
from .forms import QuestionForm, DeleteQuestionsForm
from .. import db


@assessments.route("/")
def index():
    assessments = Assessment.query.all()
    return render_template("index.html", assessments=assessments)


# @assessments.route("/<int:id>")
# def show_assessment(id):
#     assessment = Assessment.query.get_or_404(id)
#     # TODO make a combined list of T1 and T2 questions and order by their question index
#     questions = QuestionT2.query.filter_by(assessment_id=id).all()
#     return render_template(
#         "show_assessment.html", assessment=assessment, questions=questions
#     )


# @assessments.route("/<int:id>/new_question", methods=["GET", "POST"])
# def new_question(id):
#     assessment = Assessment.query.get_or_404(id)
#     form = QuestionForm()
#     if request.method == "POST":
#         question_text = request.form["question_text"]
#         correct_answer = request.form["correct_answer"]
#         weighting = request.form["weighting"]
#         new_question = QuestionT2(
#             question_text=question_text,
#             correct_answer=correct_answer,
#             weighting=weighting,
#             assessment_id=id,
#         )
#         db.session.add(new_question)
#         db.session.commit()
#         return redirect(url_for("assessments.show_assessment", id=id))

#     return render_template("new_question.html", assessment=assessment, form=form)


# @assessments.route("/<int:id>/edit_question/<int:q_id>", methods=["GET", "POST"])
# def edit_question(id, q_id):
#     assessment = Assessment.query.get_or_404(id)
#     question = QuestionT2.query.get_or_404(q_id)
#     form = QuestionForm()
#     if request.method == "POST":
#         question.question_text = form.question_text.data
#         question.correct_answer = form.correct_answer.data
#         question.weighting = form.weighting.data
#         db.session.commit()
#         return redirect(url_for("assessments.show_assessment", id=id))
#     form.question_text.data = question.question_text
#     form.correct_answer.data = question.correct_answer
#     form.weighting.data = question.weighting
#     return render_template("edit_question.html", assessment=assessment, form=form)


# @assessments.route("/<int:id>/delete_questions", methods=["GET", "POST"])
# def delete_questions(id):
#     assessment = Assessment.query.get_or_404(id)
#     questions = QuestionT2.query.filter_by(assessment_id=id).all()
#     form = DeleteQuestionsForm()
#     form.questions_to_delete.choices = [
#         (question.id, question.question_text[:15]) for question in questions
#     ]
#     if request.method == "POST":
#         # Query which returns the questions that were selected for deletion
#         for_deletion = [int(q) for q in form.questions_to_delete.data]
#         questions_to_delete = QuestionT2.query.filter(
#             QuestionT2.id.in_(for_deletion)
#         ).all()
#         for question in questions_to_delete:
#             db.session.delete(question)
#         db.session.commit()
#         return redirect(url_for("assessments.show_assessment", id=id))
#     return render_template("delete_questions.html", assessment=assessment, form=form)


@assessments.route("/new")
def new_assessment():
    return render_template("new_assessment.html")
