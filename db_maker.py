from aat import db
from aat import Role
from aat import app

from aat.models import *


with app.app_context():
    db.drop_all()
    db.create_all()
    Role.insert_roles()

    ###############
    # ASSESSMENTS #
    ###############
    db.session.add_all(
        [
            Assessment(
                module_id=1,
                lecturer_id=1,
                title="Git Basics",
                due_date=None,
                time_limit=60 * 60 * 30,
                num_of_credits=12,
                is_summative=True,
            ),
            Assessment(
                module_id=1,
                lecturer_id=2,
                title="Advanced Git",
                due_date=None,
                time_limit=60 * 60 * 45,
                num_of_credits=10,
                is_summative=True,
            ),
            Assessment(
                module_id=1,
                lecturer_id=3,
                title="DOM Manipulation in JS",
                due_date=None,
                time_limit=60 * 60 * 20,
                num_of_credits=0,
                is_summative=False,
            ),
        ]
    )

    #####################
    # QUESTIONS: TYPE 1 #
    #####################
    db.session.add_all(
        [
            QuestionT1(
                assessment_id=1,
                num_of_marks=2,
                question_text="Which command do use use to view a particular commit?",
                difficulty=1,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT1(
                assessment_id=2,
                num_of_marks=5,
                question_text="What does git rebase do?",
                difficulty=3,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT1(
                assessment_id=2,
                num_of_marks=5,
                question_text="What does git stash do?",
                difficulty=2,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
        ]
    )

    ###########
    # OPTIONS #
    ###########
    db.session.add_all(
        [
            Option(q_t1_id=1, option_text="checkout", is_correct=True),
            Option(q_t1_id=1, option_text="reset"),
            Option(q_t1_id=1, option_text="commit"),
            Option(q_t1_id=2, option_text="wrong answer"),
            Option(q_t1_id=2, option_text="right answer", is_correct=True),
            Option(q_t1_id=3, option_text="wrong answer"),
            Option(q_t1_id=3, option_text="right answer", is_correct=True),
            Option(q_t1_id=3, option_text="another wrong answer"),
        ]
    )

    #####################
    # QUESTIONS: TYPE 2 #
    #####################
    db.session.add_all(
        [
            QuestionT2(
                assessment_id=1,
                num_of_marks=5,
                question_text="What flag do you use to add a commit message?",
                correct_answer="-m",
                difficulty=1,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT2(
                assessment_id=1,
                num_of_marks=10,
                question_text="which command is used to upload your commits to a remote repository?",
                correct_answer="push",
                difficulty=1,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
            QuestionT2(
                assessment_id=3,
                num_of_marks=10,
                question_text="Which symbol is used to select by class using document.querySelector()?",
                correct_answer=".",
                difficulty=2,
                feedback_if_correct="Well done!",
                feedback_if_wrong="Better luck next time :)",
            ),
        ]
    )

    ###########
    # MODULES #
    ###########

    db.session.add_all(
        [
            Module(
                module_id=1,
                title="Databases and Modelling",
                total_credits=120,
            )
        ]
    )

    #########
    # USERS #
    #########
    db.session.add_all(
        [
            User(
                id=1,
                name="Jim",
                hashed_password="j",
                is_admin=True,
                role_id=1,
            ),
            User(
                id=2,
                name="Kate",
                hashed_password="k",
                is_admin=True,
                role_id=1,
            ),
            User(
                id=3,
                name="Al",
                hashed_password="a",
                is_admin=True,
                role_id=1,
            ),
        ]
    )

    #####################
    # RESPONSES: TYPE 2 #
    #####################

    db.session.add_all(
        [
            ResponseT2(
                user_id=1,
                assessment_id=1,
                t2_question_id=1,
                response_content="-m",
                is_correct=True,
            ),
            ResponseT2(
                user_id=1,
                assessment_id=1,
                t2_question_id=2,
                response_content="push",
                is_correct=True,
            ),
            ResponseT2(
                user_id=2,
                assessment_id=1,
                t2_question_id=1,
                response_content="-m",
                is_correct=True,
            ),
        ]
    )

    db.session.commit()
