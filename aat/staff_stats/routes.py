from . import staff_stats
from flask_login import current_user
from flask import render_template, url_for, session

from ..models import (
    Module,
    Assessment,
    QuestionT1,
    QuestionT2,
    ResponseT1,
    User,
    ResponseT2,
)
from ..db_utils import *


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





@staff_stats.route("/module/<string:Module_title>")
def module(Module_title):
    # restablish user lecturer_id
    user = User.query.filter_by(name = current_user.name).first()
    user_id = user.id
    module = Module.query.filter_by(title = Module_title).first()
    moduleId = module.module_id

    

    Assessments = Assessment.query.all()

    lecturersAssessments = []
    modulesOtherAssessments = []
    for assessment in Assessments:
        if assessment.lecturer_id == user_id and assessment.module_id == moduleId:
            lecturersAssessments.append(assessment)
        if assessment.module_id == moduleId and assessment not in lecturersAssessments:
            modulesOtherAssessments.append(assessment) 
    
    print("lecturers Assessments", lecturersAssessments)
    print("Modules other assessments", modulesOtherAssessments)


# finding the info of assessments assigned to / created by logged Lecturer 
    assessmentIds = []
    formOrSumm = []
    for assessment in lecturersAssessments:
        assessmentId = assessment.assessment_id
        assessmentIds.append(assessmentId)

        if assessment.is_summative == 1:
            formOrSumm.append("Summative")
        else:
            formOrSumm.append("Formative")
    
    
    modulesOtherAssessmentIds = []
    OtherAssessmentsFormOrSumm = []
    for assessment in modulesOtherAssessments:
        assessmentId = assessment.assessment_id
        modulesOtherAssessmentIds.append(assessmentId)

        if assessment.is_summative == 1:
            OtherAssessmentsFormOrSumm.append("Summative")
        else:
            OtherAssessmentsFormOrSumm.append("Formative")
    
    print("modulesOtherassessmentIds", modulesOtherAssessmentIds)
    print("Other modules form or Sum", OtherAssessmentsFormOrSumm)

    questionT1s = QuestionT1.query.all()
    t1questions = []
    for question in questionT1s:
        if question.assessment_id in assessmentIds:
            t1questions.append(question)
    print ("t1questions",t1questions)
    lengthT1questions = len(t1questions)
    
    otherAssessmentsQT1s = []
    for question in questionT1s:
        if question.assessment_id in modulesOtherAssessmentIds:
            otherAssessmentsQT1s.append(question)
    print ("other t1questions",otherAssessmentsQT1s)
    lengthOtherT1questions = len(otherAssessmentsQT1s)

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


    OtherT1Correct = {}
    OtherT1Wrong = {}
    for response in t1Responses:
        if response.t1_question_id not in OtherT1Correct:
            OtherT1Correct[response.t1_question_id] = 0
        if response.t1_question_id not in OtherT1Wrong:
            OtherT1Wrong[response.t1_question_id] = 0
    
    for response2 in t1Responses:
        newResponse = response2.t1_question_id
        if response2.is_correct == True:
            OtherT1Correct[newResponse] += 1
        else:
            OtherT1Wrong[newResponse] += 1
    print ("Other t1Correct",OtherT1Correct)
    print ("Other t1Wrong",OtherT1Wrong)

# T1 percentages
    t1correctAnswers = []
    t1wrongAnswers = []

    for question in questionT1s:
        if question in t1questions:
            correctAnswer = t1Correct.get(question.q_t1_id)
            wrongAnswer = t1Wrong.get(question.q_t1_id)
            if correctAnswer != None:
                t1correctAnswers.append(correctAnswer)
            if wrongAnswer != None:
                t1wrongAnswers.append(wrongAnswer)
    print("t1correct Answers", t1correctAnswers )
    print("t1wrong Answers", t1wrongAnswers)

    OtherT1correctAnswers = []
    OtherT1wrongAnswers = []

    for question in questionT1s:
        if question in t1questions:
            correctAnswer = OtherT1Correct.get(question.q_t1_id)
            wrongAnswer = OtherT1Wrong.get(question.q_t1_id)
            if correctAnswer != None:
                OtherT1correctAnswers.append(correctAnswer)
            if wrongAnswer != None:
                OtherT1wrongAnswers.append(wrongAnswer)
    print("other t1correct Answers", OtherT1correctAnswers )
    print("other t1wrong Answers", OtherT1wrongAnswers)

    t1TotalAnswers = []
    count = 0
    for answer in t1correctAnswers:
        t1TotalAnswers.append(t1wrongAnswers[count] + answer) 
        count += 1
        
    print ("t1 total answers =",t1TotalAnswers)

    OtherT1TotalAnswers = []
    count = 0
    for answer in OtherT1correctAnswers:
        OtherT1TotalAnswers.append(OtherT1wrongAnswers[count] + answer) 
        count += 1
        
    print ("Other t1 total answers =",OtherT1TotalAnswers)

    t1percentages = []
    count = 0
    for answer2 in t1TotalAnswers:
        if t1correctAnswers[count] == 0:
            percentage = 0
        if t1wrongAnswers[count] == 0:
            percentage = 100
        else:
            percentage = (t1correctAnswers[count]/answer2) * 100
        t1percentages.append(int(percentage))
        count += 1
    print("t1 percentages",t1percentages)

    OtherT1percentages = []
    count = 0
    for answer2 in OtherT1TotalAnswers:
        if OtherT1correctAnswers[count] == 0:
            percentage = 0
        if OtherT1wrongAnswers[count] == 0:
            percentage = 100
        else:
            percentage = (OtherT1correctAnswers[count]/answer2) * 100
        OtherT1percentages.append(int(percentage))
        count += 1
    print("other t1 percentages",OtherT1percentages)

    questionT2s = QuestionT2.query.all()
    t2questions = []
    for question in questionT2s:
        if question.assessment_id in assessmentIds:
            t2questions.append(question)
    print("t2questions", t2questions)
    lengthT2questions = len(t2questions)

    OtherT2questions = []
    for question in questionT2s:
        if question.assessment_id in modulesOtherAssessmentIds:
            OtherT2questions.append(question)
    print("Other t2questions", OtherT2questions)
    lengthOtherT2questions = len(OtherT2questions)


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

    OtherT2Correct = {}
    OtherT2Wrong = {}
    for response in t2Responses:
        if response.t2_question_id not in OtherT2Correct:
            OtherT2Correct[response.t2_question_id] = 0
        if response.t2_question_id not in OtherT2Wrong:
            OtherT2Wrong[response.t2_question_id] = 0


    for response2 in t2Responses:
        newResponse = response2.t2_question_id 
        #print(newResponse)
        if response2.is_correct == True:
            OtherT2Correct[newResponse] += 1
        else:
            OtherT2Wrong[newResponse] += 1    
        
    print ("Other t2Correct",OtherT2Correct)
    print ("Other t2Wrong",OtherT2Wrong)

# T2 percentages
    t2correctAnswers = []
    t2wrongAnswers = []

    for question in questionT2s:
        
        if question in t2questions:           
            correctAnswer = t2Correct.get(question.q_t2_id)
            wrongAnswer = t2Wrong.get(question.q_t2_id)          
            if correctAnswer != None:
                t2correctAnswers.append(correctAnswer)
            if wrongAnswer != None:
                t2wrongAnswers.append(wrongAnswer)
    print("t2correct Answers", t2correctAnswers )
    print("t2wrong Answers", t2wrongAnswers)

    OtherT2correctAnswers = []
    OtherT2wrongAnswers = []

    for question in questionT2s:
        
        if question in OtherT2questions:           
            correctAnswer = OtherT2Correct.get(question.q_t2_id)
            wrongAnswer = OtherT2Wrong.get(question.q_t2_id)          
            if correctAnswer != None:
                OtherT2correctAnswers.append(correctAnswer)
            if wrongAnswer != None:
                OtherT2wrongAnswers.append(wrongAnswer)
    print("other t2correct Answers", OtherT2correctAnswers )
    print("other t2wrong Answers", OtherT2wrongAnswers)

    t2TotalAnswers = []
    count = 0
    for answer in t2correctAnswers:
        t2TotalAnswers.append(t2wrongAnswers[count] + answer) 
        count += 1
        
    print ("T2 total answers =",t2TotalAnswers)

    OtherT2TotalAnswers = []
    count = 0
    for answer in OtherT2correctAnswers:
        OtherT2TotalAnswers.append(OtherT2wrongAnswers[count] + answer) 
        count += 1
        
    print ("Other T2 total answers =",OtherT2TotalAnswers)

    t2percentages = []
    count = 0
    for answer2 in t2TotalAnswers:
        if t2correctAnswers[count] == 0:
            percentage = 0
        if t2wrongAnswers[count] == 0:
            percentage = 100
        else:
            percentage = (t2correctAnswers[count]/answer2) * 100
        t2percentages.append(int(percentage))
        count += 1
    print("T2 percentages",t2percentages)

    OtherT2percentages = []
    count = 0
    for answer2 in OtherT2TotalAnswers:
        if OtherT2correctAnswers[count] == 0:
            percentage = 0
        if OtherT2wrongAnswers[count] == 0:
            percentage = 100
        else:
            percentage = (OtherT2correctAnswers[count]/answer2) * 100
        OtherT2percentages.append(int(percentage))
        count += 1
    print("Other T2 percentages",OtherT2percentages)

    return render_template("module.html",
     
        module_title = Module_title,
        lecturersAssessments = lecturersAssessments,
        modulesOtherAssessments = modulesOtherAssessments,
        assessmentIds = assessmentIds,
        modulesOtherAssessmentIds = modulesOtherAssessmentIds,
        formOrSumm = formOrSumm,
        OtherAssessmentsFormOrSumm = OtherAssessmentsFormOrSumm,
        t1questions = t1questions,
        otherAssessmentsQT1s = otherAssessmentsQT1s,
        lengthT1questions = lengthT1questions,
        lengthOtherT1questions = lengthOtherT1questions,
        t1Correct = t1Correct,
        OtherT1Correct = OtherT1Correct,
        t1Wrong = t1Wrong,
        OtherT1Wrong = OtherT1Wrong,
        t1percentages = t1percentages,
        OtherT1percentages = OtherT1percentages,
        t2questions = t2questions,
        OtherT2questions = OtherT2questions,
        lengthT2questions = lengthT2questions,
        lengthOtherT2questions = lengthOtherT2questions,
        t2Correct = t2Correct,
        OtherT2Correct = OtherT2Correct,
        t2Wrong = t2Wrong,
        OtherT2Wrong = OtherT2Wrong,  
        t2percentages = t2percentages,
        OtherT2percentages = OtherT2percentages)



@staff_stats.route("/view-students/<string:assessment>")
def view_students(assessment):
    if "name" in session:
        print(session["name"])
    assessments= Assessment.query.all()
    assessmentID = 0
    for assessment2 in assessments:
        if assessment2.title == assessment:         
            assessmentID = assessment2.assessment_id
    print(assessmentID)
    
    users = User.query.all()
    users2 = []
    for user in users:
        if user.role_id == 1:
            userInfo = get_all_response_details(user.id, None, None, assessmentID )
          
            userInfo2 = []
            userInfo2.append(user.name)
            for question in userInfo:
                questions = []   
                questions.append(question.get("question_text"))
                questions.append(question.get("question_difficulty"))
                questions.append(question.get("answer_given"))
                questions.append(question.get("is_correct"))
                questions.append(question.get("attempt_number"))
                questions.append(question.get("question_type"))

                userInfo2.append(questions)
            
            users2.append(userInfo2)
    print("users2",users2)            
    

    return render_template("view-students.html", 
    assessment = assessment,
    assessmentID = assessmentID,
    users2 = users2,)