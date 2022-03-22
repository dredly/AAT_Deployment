from aat import db
from aat import Role
from aat import app

from aat.models import *


with app.app_context():
    db.drop_all()
    db.create_all()
    Role.insert_roles()

    # Create some assessments
    assessment1 = Assessment(
        module_id=1,
        lecturer_id=1,
        title="Git Basics",
        due_date=None,
        time_limit=60 * 60 * 30,
        num_of_credits=12,
        is_summative=True,
    )
    assessment2 = Assessment(
        module_id=1,
        lecturer_id=2,
        title="Advanced Git",
        due_date=None,
        time_limit=60 * 60 * 45,
        num_of_credits=10,
        is_summative=True,
    )
    assessment3 = Assessment(
        module_id=1,
        lecturer_id=3,
        title="DOM Manipulation in JS",
        due_date=None,
        time_limit=60 * 60 * 20,
        num_of_credits=0,
        is_summative=False,
    )

    # Create some Type 1 Questions
    question_t1_1 = QuestionT1(
        assessment_id=1,
        num_of_marks=2,
        question_text="Which command do use use to view a particular commit?",
    )
    question_t1_2 = QuestionT1(
        assessment_id=2,
        num_of_marks=5,
        question_text="What does git rebase do?",
    )
    question_t1_3 = QuestionT1(
        assessment_id=2,
        num_of_marks=5,
        question_text="What does git stash do?",
    )

    # Create some Options
    option1 = Option(q_t1_id=1, option_text="checkout", is_correct=True)
    option2 = Option(q_t1_id=1, option_text="reset")
    option3 = Option(q_t1_id=1, option_text="commit")

    option4 = Option(q_t1_id=2, option_text="wrong answer")
    option5 = Option(q_t1_id=2, option_text="right answer", is_correct=True)

    option6 = Option(q_t1_id=3, option_text="wrong answer")
    option7 = Option(q_t1_id=3, option_text="right answer", is_correct=True)
    option8 = Option(q_t1_id=3, option_text="another wrong answer")

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

    # Create modules
    module_1 = Module(
        module_id=1,
        title="Databases and Modelling",
        total_credits=120,
    )

    # create some users 

    jim = User(
        id = 1,
        name = 'Jim',
        hashed_password = 'j',
        is_admin = True,
        role_id = 1,
    )

    # Add assessments, questions, options and modules
    db.session.add(assessment1)
    db.session.add(assessment2)
    db.session.add(assessment3)

    db.session.add(question_t1_1)
    db.session.add(question_t1_2)
    db.session.add(question_t1_3)

    db.session.add(option1)
    db.session.add(option2)
    db.session.add(option3)
    db.session.add(option4)
    db.session.add(option5)
    db.session.add(option6)
    db.session.add(option7)
    db.session.add(option8)

    db.session.add(question_t2_1)
    db.session.add(question_t2_2)
    db.session.add(question_t2_3)

    db.session.add(module_1)

    db.session.add(jim)

    db.session.commit()

