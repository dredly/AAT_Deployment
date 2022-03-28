from . import student_stats
from flask_login import current_user
from flask import render_template, redirect, url_for

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
    student_id = current_user.id

    sum_of_total_marks = 0
    sum_of_possible_marks = 0

    for response in current_user.t2_responses:
        print(f"Module: {response.assessment.module}")
        print(f"Assessment: {response.assessment}")
        print(f"{response.question} ({response.question.num_of_marks})")
        print(f"> {response.response_content} ({response.is_correct})")
        sum_of_total_marks += (
            response.question.num_of_marks if response.is_correct else 0
        )
        sum_of_possible_marks += response.question.num_of_marks

    overall_results = (sum_of_total_marks, sum_of_possible_marks)
    # How many marks
    # Each question
    return render_template("testing.html", overall_results=overall_results)


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
