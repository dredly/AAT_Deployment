from tracemalloc import stop
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
    session["Module_title"] = Module_title
    user = User.query.filter_by(name = current_user.name).first()
    t1Response = ResponseT1.query.all()
    t2Response = ResponseT2.query.all()
    users = User.query.all()
    module = Module.query.filter_by(title = Module_title).first()
    moduleId = module.module_id
    #print("moduleId",moduleId)
    #print("user id", user.id)
    userInfo = get_all_response_details(None,user.id,)
    #print(userInfo)
    
  

    moduleAssessments = []
    assessments = Assessment.query.filter_by(module_id = moduleId).all()
    for assessment in assessments:
        assessmentInfo = []
        if assessment.module_id == moduleId:
            assessmentInfo.append(assessment.title)
            if assessment.lecturer_id == user.id:
                assessmentInfo.append("Your assessment")
            else:
                assessmentInfo.append("NOT your assessment")
            assessmentInfo.append(assessment.num_of_credits)
            assessmentInfo.append(assessment.is_summative)
            assessmentInfo.append(assessment.assessment_id)
            moduleAssessments.append(assessmentInfo)

    
    moduleAssessmentIds = []
    for assessment in moduleAssessments:
        moduleAssessmentIds.append(assessment[4])
    NoOfAssessments = len(moduleAssessments)
    #print("number of assessments is", NoOfAssessments)
    
    questions = [[]for i in range(NoOfAssessments)]
    
    for question in userInfo:
        questionDetails = []
        questionAssessmentId = question.get("assessment_id")
        questionId = question.get("q_t2_id")
        #print("question ID",questionId, "assessmentId",questionAssessmentId)

        questionInfo = get_all_assessment_marks(None,None,None,questionAssessmentId,True)
        for stat in questionInfo:
            if stat.get("assessment_id") == questionAssessmentId:
                assId = stat.get("assessment_id")
                user = stat.get("user_id")
                attempt = stat.get("attempt_number")
                bestAttempt = stat.get("highest_scoring_attempt")
                marks = stat.get("correct_marks")
                if bestAttempt == True:
                    bestAttempt = attempt
                #print("user",user,"assId",assId,"best attempt",bestAttempt, marks)
                
                for response in t2Response:                    
                        if response.user_id == user:
                            if response.attempt_number == bestAttempt:
                                if response.assessment_id == assId:
                                    if response.is_correct == True:
                                        #print("yay")
                                        pass
                                    else:
                                        #print("nay")
                                        pass


                        
        questionDetails.append(questionAssessmentId)
        questionDetails.append(question.get("question_text"))
        questionDetails.append(question.get("question_difficulty"))
        questionDetails.append(question.get("question_type"))
        
        for bracket in questions:
            
            if len(bracket) == 0:
                bracket.append(questionDetails)                
                break
            if questionDetails[0] == bracket[0][0]:
                bracket.append(questionDetails)
                break


    #gets rid of empty lists ([])
    questions2 = []
    for question in questions:
        if len(question) == 0:
            questions2.append(["No questions set"])
        else:
            questions2.append(question)  
              
    # gets rid of dupped questions
    questions3 = []
    for question in questions2:
        dup_free = []
        for question2 in question:
            if question2 not in dup_free:
                dup_free.append(question2)
        questions3.append(dup_free)
             
    print(moduleAssessmentIds)
    print("questions3", questions3)
    


    return render_template("module.html",
        Module_title = Module_title,
        moduleAssessments = moduleAssessments,
        questions = questions3,
        )









@staff_stats.route("/view-students/<string:assessment>")
def view_students(assessment):
    Module_title = session["Module_title"]
    assessments= Assessment.query.all()
    assessmentID = 0
    for assessment2 in assessments:
        if assessment2.title == assessment:         
            assessmentID = assessment2.assessment_id
    
    users = User.query.all()
    users2 = []

    for user in users:
        if user.role_id == 1:
            userInfo = get_all_response_details(user.id, None, None, assessmentID )
          
            attempts = 1
            for question in userInfo:
                if question.get("attempt_number") > attempts:
                    attempts = question.get("attempt_number")
            attemptLists = [[]for i in range(attempts)]
            attemptLists.append(user.name)
            for question in userInfo:
                questions = []   
                questions.append(question.get("question_text"))
                questions.append(question.get("question_difficulty"))
                questions.append(question.get("answer_given"))
                questions.append(question.get("is_correct"))
                questions.append(question.get("attempt_number"))
                questions.append(question.get("question_type"))
                attemptLists[question.get("attempt_number")-1].append(questions)          
            users2.append(attemptLists)
    print(users2)
    return render_template("view-students.html", Module_title = Module_title,
    assessment = assessment,
    users2 = users2,)