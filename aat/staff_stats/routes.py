from . import staff_stats
from flask_login import current_user
from flask import render_template, url_for

from ..models import (
    Module,
    Assessment,
    QuestionT1,
    QuestionT2,
    Option,
    ResponseT1,
    User,
    ResponseT2,
)



@staff_stats.route("/")
def index():
    # establish user's lecturer_id, used throughout Assessment db
    user = User.query.filter_by(name = current_user.name).first()
    user_id = user.id
    name = user.name

    # establish assessments linked to user within Assessment db
    Assessments = Assessment.query.all()
    Modules = Module.query.all() 

    lecturersModules = []
    lecturersAssessments = []
    for assessment in Assessments:
        if assessment.lecturer_id == user_id:
            lecturersAssessments.append(assessment)

    # establish Modules associated with selected assessments and therefore user.
            moduleId = assessment.module_id
            for module in Modules:
                if moduleId == module.module_id and module.title not in lecturersModules:
                        lecturersModules.append(module.title)

    return render_template("Staff-stats.html", name = name, lecturersModules = lecturersModules)

@staff_stats.route("/test")
def test():
    return render_template("test.html")



@staff_stats.route("/module/<string:Module_title>")
def module(Module_title):
    # restablish user lecturer_id
    user = User.query.filter_by(name = current_user.name).first()
    user_id = user.id
    module = Module.query.filter_by(title = Module_title).first()
    moduleId = module.module_id

    

    Assessments = Assessment.query.all()

    lecturersAssessments = []
    for assessment in Assessments:
        if assessment.lecturer_id == user_id and assessment.module_id == moduleId:
            lecturersAssessments.append(assessment)
    
    assessmentIds = []
    formOrSumm = []
    for assessment in lecturersAssessments:
        assessmentId = assessment.assessment_id
        assessmentIds.append(assessmentId)

        if assessment.is_summative == 1:
            formOrSumm.append("Summative")
        else:
            formOrSumm.append("Formative")
    print("lecturers Assessments", lecturersAssessments)
    print("assessmentIds", assessmentIds)
    print("form or Sum", formOrSumm)
    
    questionT1s = QuestionT1.query.all()
    t1questions = []
    for question in questionT1s:
        if question.assessment_id in assessmentIds:
            t1questions.append(question)
    print ("t1questions",t1questions)

    t1Responses = ResponseT1.query.all()

    t1Correct = {}
    t1Wrong = {}
    for response in t1Responses:
        if response.t1_question_id not in t1Correct:
            t1Correct[response.t1_question_id] = 0
        if response.t1_question_id not in t1Wrong:
            t1Wrong[response.t1_question_id] = 0
    
    for response2 in t1Responses:
        newResponse = response2.t1_question_id
        if response2.is_correct == True:
            t1Correct[newResponse] += 1
        else:
            t1Wrong[newResponse] += 1

    print ("t1Correct",t1Correct)
    print ("t1Wrong",t1Wrong)



    questionT2s = QuestionT2.query.all()
    t2questions = []
    for question in questionT2s:
        if question.assessment_id in assessmentIds:
            t2questions.append(question)
    print("t2questions", t2questions)

    t2Responses = ResponseT2.query.all()

    t2Correct = {}
    t2Wrong = {}
    for response in t2Responses:
        if response.t2_question_id not in t2Correct:
            t2Correct[response.t2_question_id] = 0
        if response.t2_question_id not in t2Wrong:
            t2Wrong[response.t2_question_id] = 0


    for response2 in t2Responses:
        newResponse = response2.t2_question_id 
        #print(newResponse)
        if response2.is_correct == True:
            t2Correct[newResponse] += 1
        else:
            t2Wrong[newResponse] += 1    
        
    print ("t2Correct",t2Correct)
    print ("t2Wrong",t2Wrong)

    t2correctAnswers = []
    t2wrongAnswers = []

    for question in questionT2s:
        if question.assessment_id == assessment.assessment_id:
            print("yay")
            correctAnswer = t2Correct.get(question.q_t2_id)
            wrongAnswer = t2Wrong.get(question.q_t2_id)
            t2correctAnswers.append(correctAnswer)
            t2wrongAnswers.append(wrongAnswer)
    print("t2correct Answers", t2correctAnswers )
    print("t2wrong Answers", t2wrongAnswers)

    totalAnswers = []
    count = 0
    for answer in t2correctAnswers:
        totalAnswers.append(t2wrongAnswers[count] + answer) 
        count += 1
    print ("total answers =",totalAnswers)

    percentages = []
    count = 0
    for answer2 in totalAnswers:
        if t2correctAnswers[count] == 0:
            percentage = 0
        if t2wrongAnswers[count] == 0:
            percentage = 100
        else:
            percentage = (t2correctAnswers[count]/answer2) * 100
        percentages.append(int(percentage))
        count += 1
    print("percentages",percentages)

    return render_template("module.html",
     
      
        questionT1s = questionT1s,
        questionT2s = questionT2s,

        module_title = Module_title,
        lecturersAssessments = lecturersAssessments,
        assessmentIds = assessmentIds,
        formOrSumm = formOrSumm,
        t1questions = t1questions,
        t1Correct = t1Correct,
        t1Wrong = t1Wrong,
        t2questions = t2questions,
        t2Correct = t2Correct,
        t2Wrong = t2Wrong)

