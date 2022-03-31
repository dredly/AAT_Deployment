from datetime import datetime
import math
import random 
from stringprep import in_table_d2
from flask import Response, redirect, render_template, request, url_for, abort, session
from . import assessments

from ..models import Assessment, QuestionT1, QuestionT2, Module, User, ResponseT2, ResponseT2, ResponseT1, Option, Tag
from .forms import AddQuestionToAssessmentForm, DeleteQuestionsForm, AnswerType1Form, AnswerType2Form, AssessmentForm, DeleteAssessmentForm, EditAssessmentForm, FinishForm, RemoveQuestionForm
from .. import db
from flask_login import current_user


@assessments.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    assessments = Assessment.query.all()
    modules = Module.query.all()
    return render_template("index.html", assessments=assessments, modules=modules)

@assessments.route("/view_module/<int:module_id>")
def view_module(module_id): 
    session["module_id"] = module_id 
    module = Module.query.filter_by(module_id=module_id).first()
    assessments = Assessment.query.filter_by(module_id=module.module_id).all()
    summatives = []
    formatives = []
    marks_achieved = dict()
    # ----> find all tags 
    assess_tags = dict()
    for assessment in assessments:
        # ----> find all questions
        qs = QuestionT1.query.filter_by(assessment_id=assessment.assessment_id).all(
        ) + QuestionT2.query.filter_by(assessment_id=assessment.assessment_id).all()

        #---> calculate marks available 
        marks_av = 0

        for q in qs: 
            tag = Tag.query.filter_by(id=q.tag_id).first()
            if tag is not None: 
                if assessment.title in assess_tags: 
                    if not tag.name in assess_tags[assessment.title]:
                        assess_tags[assessment.title].append(tag.name)
                else: 
                    assess_tags[assessment.title] = [tag.name]

            marks_av += q.num_of_marks 

        # ---> check if user has responded to assessment 
        if current_user.has_taken(assessment): 
            attempts_taken = current_user.current_attempts(assessment)
            result_of_attempts = dict()
            highest_result = 0 

            # --- > break out achieved result for each attempt 
            for attempt in range(1, attempts_taken + 1):
                t1_responses = current_user.t1_responses.filter_by(
                assessment_id=assessment.assessment_id
                ).filter_by(attempt_number=attempt
                ).all()
                t2_responses = current_user.t2_responses.filter_by(
                    assessment_id=assessment.assessment_id
                ).filter_by(attempt_number=attempt
                ).all()

                # ---> find what user's result was 
                res = 0
                for response in t1_responses:
                    if response.is_correct:
                        answered_question = QuestionT1.query.filter_by(
                            q_t1_id=response.t1_question_id
                        ).first()
                        res += answered_question.num_of_marks
                for response in t2_responses:
                    if response.is_correct:
                        answered_question = QuestionT2.query.filter_by(
                            q_t2_id=response.t2_question_id
                        ).first()
                        res += answered_question.num_of_marks
                result_of_attempts[attempt] = res
            
            # --- > find the highest result achieved across all attempts 
            d_ref = max(result_of_attempts, key=result_of_attempts.get)
            result = result_of_attempts[d_ref]
        else: 
            result = 0
    
        marks_achieved[assessment.title] = f"{result}/{marks_av}"

        if assessment.is_summative: 
            summatives.append(assessment)
        else: 
            formatives.append(assessment)
    session["assessment_tags"] = assess_tags 
    return render_template("view_module.html", 
        module=module, 
        assessments=assessments,
        summatives=summatives,
        formatives=formatives,
        marks_achieved=marks_achieved,
        assess_tags=assess_tags
        )


@assessments.route("/<int:id>")
def show_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    try:
        time_limit_minutes = math.floor(int(assessment.time_limit) / 60)
    except:
        time_limit_minutes = None
    try:
        current_date = assessment.due_date.strftime("%d/%m/%Y")
    except:
        current_date = None
    if assessment.is_summative == False:
        assessment_type = "Formative"
    elif assessment.is_summative == True:
        assessment_type = "Summative"
    # TODO make a combined list of T1 and T2 questions and order by their question index
    questions = QuestionT1.query.filter_by(assessment_id=id).all() + QuestionT2.query.filter_by(assessment_id=id).all()
    return render_template(
        "show_assessment.html", assessment=assessment, questions=questions, current_date=current_date, time_limit_minutes=time_limit_minutes, assessment_type=assessment_type
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

# ---------------------------------  CRUD For Assessments ---------------------------------------

@assessments.route("/assessment/new", methods=["GET", "POST"])
def new_assessment():
    session.pop("assessment_edit", None)
    form = AssessmentForm()
    is_summative_1 = ""
    session["user"] = current_user.id 
    if request.method == "POST":
        lecturer_id = session["user"]
        is_summative = False
        title = request.form["title"]
        total_date = request.form["due_date"]
        year = int(total_date[:4])
        month = int(total_date[5:7])
        day = int(total_date[8:10])
        due_date = datetime(year, month, day)
        time_limit = request.form["time_limit"]
        num_of_credits = request.form["num_of_credits"]
        module_id = request.form["module_id"]
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
            lecturer_id=lecturer_id,
            module_id=module_id
        )
        db.session.add(new_assessment)
        db.session.commit()
        id = new_assessment.assessment_id
        session["assessment_add"]= id
        return redirect(url_for("assessments.add_questions", id=id))
    return render_template("new_assessment.html", form=form )

@assessments.route("/<int:id>/edit_assessment", methods=["GET", "POST"])
def edit_assessment(id):
    session.pop("assessment_add", None)
    assessment = Assessment.query.get_or_404(id)
    form = EditAssessmentForm()
    session["assessment_edit"] = id
    print(id)
    if request.method == "POST":
        assessment.title = form.title.data
        assessment.module_id = form.module_id.data
        try:
            total_date = request.form["due_date"]
            year = int(total_date[:4])
            month = int(total_date[5:7])
            day = int(total_date[8:10])
            assessment.due_date = datetime(year, month, day)
        except:
            assessment.due_date = None  
        assessment.num_of_credits = form.num_of_credits.data
        assessment.time_limit = form.time_limit.data
        assessment.is_summative = form.is_summative.data
        db.session.commit()
        return redirect(url_for("assessments.index"))
    form.title.data = assessment.title
    form.module_id.data = assessment.module_id
    form.due_date.data = assessment.due_date
    form.num_of_credits.data = assessment.num_of_credits
    try:
        form.time_limit.data = math.floor(int(assessment.time_limit) / 60)
    except:
        form.time_limit.data = None
    form.is_summative.data = assessment.is_summative
    return render_template("edit_assessments.html", form=form, assessment=assessment, id=id)
    


@assessments.route("/<int:id>/delete_assessment", methods=["GET", "POST"])
def delete_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    form = DeleteAssessmentForm()
    if request.method == "POST":
        try: 
            request.form['submit']
            db.session.delete(assessment)
            db.session.commit()
            return redirect(url_for("assessments.index"))
        except:
            request.form['cancel']
            return redirect(url_for("assessments.index"))
    return render_template("delete_assessment.html", assessment=assessment, form=form, id=id)

@assessments.route("/<int:id>/edit_assessment/remove/t2/<int:id2>", methods=["GET", "POST"])
def remove_question_t2(id, id2):
    question = QuestionT2.query.get_or_404(id2)
    assessment = Assessment.query.get_or_404(id)
    form = RemoveQuestionForm()
    if request.method == "POST" and form.is_submitted:
        question.assessment_id = None
        db.session.commit()
        return redirect(url_for("assessments.edit_assessment", id=id))
    return render_template("remove_question.html", question=question, form=form, assessment=assessment, id=id)

@assessments.route("/<int:id>/edit_assessment/remove/t1/<int:id3>", methods=["GET", "POST"])
def remove_question_t1(id, id3):
    question = QuestionT1.query.get_or_404(id3)
    assessment = Assessment.query.get_or_404(id)
    form = RemoveQuestionForm()
    if request.method == "POST" and form.is_submitted:
        question.assessment_id = None
        db.session.commit()
        return redirect(url_for("assessments.edit_assessment", id=id))
    return render_template("remove_question.html", question=question, form=form, assessment=assessment)



@assessments.route("/add_questions/<int:id>", methods=["GET", "POST"])
def add_questions(id):
    if session.get("assessment_add") != None:
        id = session.get("assessment_add")
        print(session.get("assessment_add"))
    elif session.get("assessment_edit") != None:
        id = session.get("assessment_edit")
        print(session.get("assessment_edit"))
    form=FinishForm()
    addQuestionForm = AddQuestionToAssessmentForm()
    questions = (
            QuestionT1.query.filter(QuestionT1.assessment_id.is_(None)).all()
            + QuestionT2.query.filter(QuestionT2.assessment_id.is_(None)).all()
        )
    for question in questions:
        if addQuestionForm.validate_on_submit() and addQuestionForm.add.data:
            question.assessment_id = id
            db.session.commit()
            return render_template("add_questions.html", questions=questions, id=id, addQuestionForm=addQuestionForm, form=form)   

    if form.validate_on_submit() and form.finish.data:
        if session.get("assessment_edit") != None:
            session.pop("assessment_edit", None)
            return redirect(url_for("assessments.edit_assessment", id=id))
        elif session.get("assessment_add") != None:
            session.pop("assessment_add", None)
            return redirect(url_for("assessments.index"))
            
    return render_template("add_questions.html", questions=questions, id=id, addQuestionForm=addQuestionForm, form=form)

# ---------------------------------  End Of CRUD For Assessments ---------------------------------------


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ---------------------------------  Start of TAKE ASSESSMENT  ---------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------



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
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment is None: 
        return redirect(url_for("assessments"))
    session["is_summative"] = assessment.is_summative  
    ## query to find all questions in assessment, so can be used to find their ID's and store these in session variable
    ## session variable is then accessed throughout the process to find questions and store their responses
    questions_t1 = QuestionT1.query.filter_by(assessment_id=assessment_id).all()
    questions_t2 = QuestionT2.query.filter_by(assessment_id=assessment_id).all()
    if len(questions_t1) == 0 and len(questions_t2) == 0: 
        return redirect(url_for("assessments.empty_assessment"))

    # ---- > create list of questions to cover in assessment 
    question_ids = []
    difficulties = []
    print(question_ids)
    for question in questions_t1:
        print("now adding type 1...")
        difficulties.append(question.difficulty)
        question_info = (1, question.q_t1_id)
        question_ids.append(question_info)
        print(question_info)
    for question in questions_t2:
        print("now adding type 2...")
        difficulties.append(question.difficulty)
        question_info = (2, question.q_t2_id)
        question_ids.append(question_info)
        print(question_info)
    random.shuffle(question_ids)
    print(question_ids)
    final_difficulty = round(sum(difficulties) / len(difficulties))
    session["user"] = current_user.id
    session["questions"] = question_ids
    session["past_questions"] = []
    session["no_questions"] = len(question_ids)
    session["assessment"] = assessment_id
    first_question = session["questions"][0][0]
    first_question_type = session["questions"][0][0]
    first_question_id = session["questions"][0][1]

    # ---- > calculate which attempt this is for user 
    if not current_user.has_taken(assessment): 
        session["attempt_number"] = 1
    else: 
        current_no_attempts = current_user.current_attempts(assessment)
        print(f"current number of attempts is: {current_no_attempts}")
        session["attempt_number"] = current_no_attempts + 1
        print(session["attempt_number"])

    return render_template(
        "assessment_summary.html",
        assessment=assessment,
        questions_t1=questions_t1,
        questions_t2=questions_t2,
        question_ids=question_ids,
        first_question=first_question,
        type=first_question_type,
        first_question_id=first_question_id, 
        difficulty=final_difficulty
    )


@assessments.route("/answer_question/<int:type>/<int:question_id>", methods=["GET", "POST"])
def answer_question(type, question_id):
    ## find question to be answered 
    assessment = Assessment.query.get_or_404(session.get("assessment"))
    if type == 1: 
        question = QuestionT1.query.get_or_404(question_id)
        form = AnswerType1Form()
        # QuestionT1.query.filter_by(assessment_id=id).all()
        form.chosen_option.choices = [(option.option_id, option.option_text) for option in Option.query.filter_by(q_t1_id=question_id).all() ]
    elif type == 2: 
        question = QuestionT2.query.get_or_404(question_id)
        form = AnswerType2Form(answer=None)

    ## check if there's a previous answer to prepopulate 
    if request.method == "GET":
        print("The current user has answered this question in this attempt: ")
        print(current_user.has_answered(type, question, assessment, session["attempt_number"]))
        if current_user.has_answered(type, question, assessment, session["attempt_number"]):
        
            if type == 1: 
                previous_response = (
                current_user.t1_responses.filter_by(
                    assessment_id=session.get("assessment")
                )
                .filter_by(t1_question_id=question_id)
                .filter_by(attempt_number=session["attempt_number"])
                .first()
                )
                # find id of option chosen 
                selected_option_id = previous_response.selected_option 
                # then set default of form 
                form.chosen_option.default = selected_option_id
                # then run form.process()
                form.process()
            elif type == 2: 
                previous_response = (
                    current_user.t2_responses.filter_by(
                        assessment_id=session.get("assessment")
                    )
                    .filter_by(t2_question_id=question_id)
                    .filter_by(attempt_number=session["attempt_number"])
                    .first()
                )
                previous_given_answer = previous_response.response_content
                form.answer.data = previous_given_answer
    
    ## actions to take on a post method - i.e. when user submits an answer to their question
    if request.method == "POST":
        ## if changing / resubmitting answer, ensures no duplicate responses by deleting the old
        if current_user.has_answered(type, question, assessment, session["attempt_number"]):
            current_user.remove_answer(type, question, assessment, session["attempt_number"])
            db.session.commit()
        if type == 1:
            given_answer = Option.query.filter_by(option_id=form.chosen_option.data).first()
            if given_answer.is_correct:
                result = True
            else: 
                result = False 
            response = ResponseT1(
                attempt_number=session["attempt_number"],
                user_id=current_user.id,
                assessment_id=assessment.assessment_id,
                t1_question_id=question_id,
                selected_option=given_answer.option_id,
                is_correct=result,
            )
        elif type == 2: 
            given_answer = form.answer.data.strip().lower()
            if given_answer == question.correct_answer.lower():
                result = True
            else:
                result = False
            response = ResponseT2(
                attempt_number=session["attempt_number"],
                user_id=current_user.id,
                assessment_id=assessment.assessment_id,
                t2_question_id=question_id,
                response_content=given_answer,
                is_correct=result,
            )
        db.session.add(response)
        db.session.commit()
        if session['is_summative']:
            if len(session['questions']) < 1: 
                return redirect(url_for("assessments.results", 
                    assessment_id=assessment.assessment_id
                    ))
            else: 
                return redirect(url_for("assessments.answer_question", 
                    type=session['questions'][0][0], 
                    question_id=session['questions'][0][1]
                ))
        else: 
            return redirect(url_for("assessments.mark_answer", 
                type=type, 
                question_id=question_id
            ))
    current_questions = session.get("questions")
    previous = current_questions.pop(0)
    session["past_questions"].append(previous)
    session["questions"] = current_questions
    return render_template(
        "answer_question.html", question=question, assessment=assessment, form=form, type=type
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
        url_for("assessments.answer_question", type=session["questions"][0][0], question_id=session["questions"][0][1])
    )


@assessments.route("/mark_answer/<int:type>/<int:question_id>", methods=["GET", "POST"])
def mark_answer(type, question_id):
    assessment = Assessment.query.get_or_404(session.get("assessment"))
    if type == 1: 
        question = QuestionT1.query.get_or_404(question_id)
        right_answer = Option.query.filter_by(q_t1_id=question.q_t1_id).filter_by(is_correct=True).first()
        chosen_option = (
        current_user.t1_responses.filter_by(assessment_id=session.get("assessment"))
        .filter_by(t1_question_id=question_id)
        .filter_by(attempt_number=session["attempt_number"])
        .first()
        )
        response = Option.query.filter_by(option_id=chosen_option.selected_option).first()
        print(response)
    elif type == 2: 
        question = QuestionT2.query.get_or_404(question_id)
        right_answer = question.correct_answer
        response = (
            current_user.t2_responses.filter_by(assessment_id=session.get("assessment"))
            .filter_by(t2_question_id=question_id)
            .filter_by(attempt_number=session["attempt_number"])
            .first()
        )
    return render_template(
        "mark_answer.html", 
        question=question, 
        response=response, 
        assessment=assessment, 
        right_answer=right_answer, 
        type=type
    )


@assessments.route("/results/<int:assessment_id>")
def results(assessment_id):
    assessment = Assessment.query.get_or_404(session.get("assessment"))
    no_of_questions = session.pop("no_questions", None)

    # ----- Find all the responses given during assessment session 
    t1_responses = current_user.t1_responses.filter_by(
        assessment_id=assessment_id
    ).filter_by(attempt_number=session["attempt_number"]
    ).all()
    t2_responses = current_user.t2_responses.filter_by(
        assessment_id=assessment_id
    ).filter_by(attempt_number=session["attempt_number"]
    ).all()

    # ----- find all questions asked 
    questions = QuestionT1.query.filter_by(assessment_id=assessment_id).all(
        ) + QuestionT2.query.filter_by(assessment_id=assessment_id).all()

    # ----- find possible total marks 
    possible_total = 0
    for question in questions:
        possible_total += question.num_of_marks

    # ----- find actual result achieved 
    result = 0
    for response in t1_responses:
        if response.is_correct:
            answered_question = QuestionT1.query.filter_by(
                q_t1_id=response.t1_question_id
            ).first()
            result += answered_question.num_of_marks
    for response in t2_responses:
        if response.is_correct:
            answered_question = QuestionT2.query.filter_by(
                q_t2_id=response.t2_question_id
            ).first()
            result += answered_question.num_of_marks
    # ---- 1. create list of numbers representing indexes 
    no_questions = [i for i in range(0, no_of_questions)]

    # ---- 2. create lists to store relevant variables to be entered into template 
    ordered_questions = []
    given_answers = []
    correct_answers = []
    is_correct = []

    # ---- 3. iterate over the index list 
    for idx in no_questions: 
        current_question = session["past_questions"][idx]
        if current_question[0] == 1: 
            q = QuestionT1.query.filter_by(q_t1_id=current_question[1]).first()
            related_response = current_user.t1_responses.filter_by(assessment_id=assessment.assessment_id
                ).filter_by(t1_question_id=q.q_t1_id
                ).filter_by(attempt_number=session["attempt_number"]
                ).first()
            answer_content = Option.query.filter_by(option_id=related_response.selected_option).first().option_text
            correct_answer = Option.query.filter_by(q_t1_id=q.q_t1_id).filter_by(is_correct=True).first().option_text
            correct_test = related_response.is_correct 
        elif current_question[0] == 2:
            q = QuestionT2.query.filter_by(q_t2_id=current_question[1]).first()
            related_response = current_user.t2_responses.filter_by(assessment_id=assessment.assessment_id
            ).filter_by(t2_question_id=q.q_t2_id
            ).filter_by(attempt_number=session["attempt_number"]
            ).first()
            answer_content = related_response.response_content
            correct_answer = q.correct_answer 
            correct_test = related_response.is_correct
        
        ordered_questions.append(q)
        given_answers.append(answer_content)
        correct_answers.append(correct_answer)
        is_correct.append(correct_test)
    print("Ordered questions are: ", str(ordered_questions))
    return render_template(
        "results.html",
        no_questions=no_questions,
        assessment=assessment,
        result=result,
        possible_total=possible_total,
        ordered_questions=ordered_questions,
        given_answers=given_answers,
        correct_answers=correct_answers,
        is_correct=is_correct 

    )


@assessments.route("/exit_assessment")
def exit_assessment():
    ## wipes all session variables and returns to assessment list
    session.pop("user", None)
    session.pop("questions", None)
    session.pop("no_questions", None)
    session.pop("assessment", None)
    session.pop("takes_assessment_id", None)
    module = session.pop("module_id", None)
    return redirect(url_for("assessments.view_module", module_id=module))


# ----------------------------------------------------------------------------------------------------
# ---------------------------------  END of TAKE ASSESSMENT  ---------------------------------------
# ----------------------------------------------------------------------------------------------------

@assessments.route("/empty_assessment")
def empty_assessment():
    return render_template("empty_assessment.html")