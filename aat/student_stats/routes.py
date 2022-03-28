from . import student_stats
from flask_login import current_user
from flask import render_template, redirect, url_for
from sqlalchemy import func

# MODELS
from ..models import (
    Module,
    Assessment,
    QuestionT1,
    QuestionT2,
    Option,
    User,
    ResponseT2,
)


@student_stats.route("/")
def course_view():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    query = ResponseT2.query.filter_by(user_id=current_user.id).all()
    for i in query:
        print(i)

    student_id = current_user.id

    # GET SUM OF QUESTIONS FOR EACH ASSESSMENT
    assessment_marks_dict = {}

    for response in current_user.t2_responses:
        if response.assessment not in assessment_marks_dict:
            assessment_marks_dict[response.assessment] = {
                "marks_awarded": response.question.num_of_marks
                if response.is_correct
                else 0,
                "marks_possible": response.question.num_of_marks,
            }
        else:
            assessment_marks_dict[response.assessment]["marks_awarded"] += (
                response.question.num_of_marks if response.is_correct else 0
            )
            assessment_marks_dict[response.assessment][
                "marks_possible"
            ] += response.question.num_of_marks

    # ADD THAT TO THE MODULE DICT
    module_dict = {}

    for module in Module.query.all():
        for assessment, data in assessment_marks_dict.items():
            if assessment.module_id == module.module_id:
                module_dict[module] = {assessment: data}

    print(module_dict)

    sum_of_marks_awarded = 0
    sum_of_marks_possible = 0

    for module in module_dict:
        for assessment, data in assessment_marks_dict.items():
            sum_of_marks_awarded += data["marks_awarded"]
            sum_of_marks_possible += data["marks_possible"]

    if sum_of_marks_possible == 0:
        return render_template("no_questions_answered.html")

    overall_results = {
        "sum_of_marks_awarded": sum_of_marks_awarded,
        "sum_of_marks_possible": sum_of_marks_possible,
    }
    # How many marks
    # Each question
    return render_template(
        "student_stats_home.html",
        overall_results=overall_results,
        module_dict=module_dict,
    )


@student_stats.route("/old_route/")
def old_course_view():
    """
    Queries StudentAnswers table (using student_id)
    Makes [...]
    """
    if not current_user.is_authenticated:
        return render_template("please_log_in.html")
    try:
        # This value would come from Logged In user.
        student_id = 1

        list_of_student_answers = StudentAnswers.query.filter_by(
            student_id=student_id
        ).all()

        total_marks = sum([answer.marks for answer in list_of_student_answers])

        correct_marks = sum(
            [
                answer.marks
                for answer in list_of_student_answers
                if answer.correct_answer
            ]
        )

        headline_marks = (correct_marks, total_marks)

        list_of_all_modules_in_course = list(
            set([answer.module_id for answer in list_of_student_answers])
        )

        dictionary_of_marks = {}
        for module in list_of_all_modules_in_course:
            correct_marks = sum(
                [
                    answer.marks
                    for answer in list_of_student_answers
                    if answer.correct_answer and answer.module_id == module
                ]
            )
            total_marks = sum(
                [
                    answer.marks
                    for answer in list_of_student_answers
                    if answer.module_id == module
                ]
            )

            dictionary_of_marks[module] = (correct_marks, total_marks)
    except:
        headline_marks = (9, 12)
        dictionary_of_marks = {1: (2, 3), 2: (3, 4), 3: (4, 5)}

    return render_template(
        "course_view.html",
        headline_marks=headline_marks,
        dictionary_of_marks=dictionary_of_marks,
    )


@student_stats.route("/module/<int:module_id>")
def module_view(module_id):
    """
    Queries StudentAnswers table (using student_id)
    Makes [...]
    """
    try:
        # This value would come from Logged In user.
        student_id = 1

        list_of_student_answers = (
            StudentAnswers.query.filter_by(student_id=student_id)
            .filter_by(module_id=module_id)
            .all()
        )

        total_marks = sum([answer.marks for answer in list_of_student_answers])

        correct_marks = sum(
            [
                answer.marks
                for answer in list_of_student_answers
                if answer.correct_answer
            ]
        )

        headline_marks = (correct_marks, total_marks)

        list_of_all_assessment_in_course = list(
            set([answer.assessment_id for answer in list_of_student_answers])
        )

        dictionary_of_marks = {}
        for assessment in list_of_all_assessment_in_course:
            correct_marks = sum(
                [
                    answer.marks
                    for answer in list_of_student_answers
                    if answer.correct_answer and answer.assessment_id == assessment
                ]
            )
            total_marks = sum(
                [
                    answer.marks
                    for answer in list_of_student_answers
                    if answer.assessment_id == assessment
                ]
            )

            dictionary_of_marks[assessment] = (correct_marks, total_marks)
    except:
        headline_marks = (2, 3)
        dictionary_of_marks = {1: (2, 2), 2: (0, 1)}

    return render_template(
        "module_view.html",
        module_id=module_id,
        headline_marks=headline_marks,
        dictionary_of_marks=dictionary_of_marks,
    )


@student_stats.route("/module/<int:module_id>/assessment/<int:assessment_id>")
def assessment_view(module_id, assessment_id):
    try:
        # This value would come from Logged In user.
        student_id = 1

        list_of_student_answers = (
            StudentAnswers.query.filter_by(student_id=student_id)
            .filter_by(module_id=module_id)
            .filter_by(assessment_id=assessment_id)
            .all()
        )

        total_marks = sum([answer.marks for answer in list_of_student_answers])

        correct_marks = sum(
            [
                answer.marks
                for answer in list_of_student_answers
                if answer.correct_answer
            ]
        )

        headline_marks = (correct_marks, total_marks)

        list_of_all_assessment_in_course = list(
            set([answer.question_id for answer in list_of_student_answers])
        )

        dictionary_of_marks = {}
        for question in list_of_all_assessment_in_course:
            correct_marks = sum(
                [
                    answer.marks
                    for answer in list_of_student_answers
                    if answer.correct_answer and answer.question_id == question
                ]
            )
            total_marks = sum(
                [
                    answer.marks
                    for answer in list_of_student_answers
                    if answer.question_id == question
                ]
            )

            dictionary_of_marks[question] = (correct_marks, total_marks)
    except:
        headline_marks = (2, 2)
        dictionary_of_marks = {1: (2, 2)}

    return render_template(
        "assessment_view.html",
        module_id=module_id,
        assessment_id=assessment_id,
        headline_marks=headline_marks,
        dictionary_of_marks=dictionary_of_marks,
    )
