from flask import Response, redirect, render_template, request, url_for, abort, session
from . import assessments
from ..models import Assessment, QuestionT2, Module, User, ResponseT2
from .forms import DeleteQuestionsForm, AnswerType2Form, AssessmentForm
from .. import db
from flask_login import current_user


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


# Matt ---> You  could probably adapt this for your assessment CRUD
# as it will let you remove multiple questions from an assessment.
@assessments.route("/<int:id>/delete_questions", methods=["GET", "POST"])
def delete_questions(id):
    assessment = Assessment.query.get_or_404(id)
    questions_t2 = QuestionT2.query.filter_by(assessment_id=id).all()
    form = DeleteQuestionsForm()
    form.questions_to_delete.choices = [
        (question.q_t2_id, question.question_text[:20]) for question in questions_t2
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


@assessments.route("/assessment/new", methods=["GET", "POST"])
def new_assessment():
    form = AssessmentForm()
    is_summative_1 = ""
    if request.method == "POST":
        lecturer_id = session["user"]
        is_summative = False
        title = request.form["title"]
        due_date = request.form["due_date"]
        time_limit = request.form["time_limit"]
        num_of_credits = request.form["num_of_credits"]
        try:
            is_summative_1 = request.form["is_summative"]
        except:
                pass
        if is_summative_1 == "y":
            is_summative = True
        new_assessment = Assessment(
            title=title,
            due_date=due_date,
            time_limit=int(time_limit) * 60,
            num_of_credits=num_of_credits,
            is_summative=is_summative,
            lecturer_id=lecturer_id
        )
        db.session.add(new_assessment)
        db.session.commit()
        return redirect(url_for("assessments.index"))
    return render_template("new_assessment.html", form=form)


## example of how to filter response table
@assessments.route("/test_response_model/<int:assessment_id>/<int:question_id>")
def test_response_model(assessment_id, question_id):
    results = (
        current_user.t2_responses.filter_by(assessment_id=assessment_id)
        .filter_by(question_id=question_id)
        .all()
    )
    return render_template("results.html", results=results)


@assessments.route("/assessment_summary/<int:assessment_id>", methods=["GET", "POST"])
def assessment_summary(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    ## query to find all questions in assessment, so can be used to find their ID's and store these in session variable
    ## session variable is then accessed throughout the process to find questions and store their responses
    questions = QuestionT2.query.filter_by(assessment_id=assessment_id).all()
    question_ids = []
    for question in questions:
        question_ids.append(question.q_t2_id)
    session["user"] = current_user.id
    session["questions"] = question_ids
    session["past_questions"] = []
    session["no_questions"] = len(question_ids)
    session["assessment"] = assessment_id
    first_question = session["questions"][0]
    return render_template(
        "assessment_summary.html",
        assessment=assessment,
        questions=questions,
        question_ids=question_ids,
        first_question=first_question,
    )


@assessments.route("/answer_question/<int:question_id>", methods=["GET", "POST"])
def answer_question(question_id):
    form = AnswerType2Form(answer=None)
    assessment = Assessment.query.get_or_404(session.get("assessment"))
    question = QuestionT2.query.get_or_404(question_id)
    if current_user.has_answered(question, assessment):
        if request.method == "GET":
            previous_response = (
                current_user.t2_responses.filter_by(
                    assessment_id=session.get("assessment")
                )
                .filter_by(t2_question_id=question_id)
                .first()
            )
            previous_given_answer = previous_response.response_content
            form.answer.data = previous_given_answer
    if request.method == "POST":
        if current_user.has_answered(question, assessment):
            current_user.remove_answer(question, assessment)
            db.session.commit()
        given_answer = form.answer.data.strip()
        if given_answer == question.correct_answer:
            result = True
        else:
            result = False
        response = ResponseT2(
            user_id=current_user.id,
            assessment_id=assessment.assessment_id,
            t2_question_id=question_id,
            response_content=given_answer,
            is_correct=result,
        )
        db.session.add(response)
        db.session.commit()
        return redirect(url_for("assessments.mark_answer", question_id=question_id))
    current_questions = session.get("questions")
    previous = current_questions.pop(0)
    session["past_questions"].append(previous)
    session["questions"] = current_questions
    return render_template(
        "answer_question.html", question=question, assessment=assessment, form=form
    )


@assessments.route("/previous_question")
def previous_question():
    next_question = session["past_questions"].pop(-1)
    prev_question = session["past_questions"].pop(-1)
    session["questions"].insert(0, next_question)
    session["questions"].insert(0, prev_question)
    # copy and overwrite existing session variables as otherwise insert would not remain permanent on next loaded page
    copy_list_next = session["questions"]
    copy_list_prev = session["past_questions"]
    session["questions"] = copy_list_next
    session["past_questions"] = copy_list_prev
    return redirect(
        url_for("assessments.answer_question", question_id=session["questions"][0])
    )


@assessments.route("/mark_answer/<int:question_id>", methods=["GET", "POST"])
def mark_answer(question_id):
    question = QuestionT2.query.get_or_404(question_id)
    assessment = Assessment.query.get_or_404(session.get("assessment"))
    response = (
        current_user.t2_responses.filter_by(assessment_id=session.get("assessment"))
        .filter_by(t2_question_id=question_id)
        .first()
    )
    return render_template(
        "mark_answer.html", question=question, response=response, assessment=assessment
    )


@assessments.route("/results/<int:assessment_id>")
def results(assessment_id):
    all_responses = current_user.t2_responses.filter_by(
        assessment_id=assessment_id
    ).all()
    assessment = Assessment.query.get_or_404(session.get("assessment"))
    no_of_questions = session.pop("no_questions", None)
    questions = QuestionT2.query.filter_by(assessment_id=assessment_id).all()
    possible_total = 0
    for question in questions:
        possible_total += question.num_of_marks
    result = 0
    for response in all_responses:
        if response.is_correct:
            answered_question = QuestionT2.query.filter_by(
                q_t2_id=response.t2_question_id
            ).first()
            result += answered_question.num_of_marks
    return render_template(
        "results.html",
        no_of_questions=no_of_questions,
        assessment=assessment,
        result=result,
        possible_total=possible_total,
    )


@assessments.route("/exit_assessment")
def exit_assessment():
    ## wipes all session variables and returns to assessment list
    session.pop("user", None)
    session.pop("questions", None)
    session.pop("no_questions", None)
    session.pop("assessment", None)
    session.pop("takes_assessment_id", None)
    return redirect(url_for("assessments.index"))
