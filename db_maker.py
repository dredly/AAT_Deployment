from aat import db
from aat import app
from aat.models import *

with app.app_context():
    db.create_all()

    # Create some assessments
    assessment1 = Assessment(
        module_id=1,
        staff_id=1,
        title="Git Basics",
        due_date=None,
        time_limit=60 * 60 * 30,
        num_of_credits=12,
        is_summative=True,
    )
    assessment2 = Assessment(
        module_id=1,
        staff_id=2,
        title="Advanced Git",
        due_date=None,
        time_limit=60 * 60 * 45,
        num_of_credits=10,
        is_summative=True,
    )
    assessment3 = Assessment(
        module_id=2,
        staff_id=3,
        title="DOM Manipulation in JS",
        due_date=None,
        time_limit=60 * 60 * 20,
        num_of_credits=0,
        is_summative=False,
    )

    # Create some Type 2 Questions
    question_t2_1 = QuestionT2(
        assessment_id=1,
        num_of_marks=5,
        question_text="What flag do you use to add a commit message?",
        correct_answer="-m",
    )
    question_t2_2 = QuestionT2(
        assessment_id=1,
        num_of_marks=10,
        question_text="which command is used to upload your commits to a remote repository?",
        correct_answer="push",
    )
    question_t2_3 = QuestionT2(
        assessment_id=3,
        num_of_marks=10,
        question_text="Which symbol is used to select by class using document.querySelector()?",
        correct_answer=".",
    )

    # Add assessments and questions
    db.session.add(assessment1)
    db.session.add(assessment2)
    db.session.add(assessment3)

    db.session.add(question_t2_1)
    db.session.add(question_t2_2)
    db.session.add(question_t2_3)

    db.session.commit()
