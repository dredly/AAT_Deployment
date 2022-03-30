from asyncio.windows_events import NULL
from pickle import FALSE
from . import staff_stats
from flask_login import current_user
from flask import render_template, url_for

from ..models import (
    Module,
    Assessment,
    QuestionT1,
    QuestionT2,
    Option,
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
    
    
    
    questionT1s = QuestionT1.query.all()

    questionT2s = QuestionT2.query.all()
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
        print(newResponse)
        if response2.is_correct == True:
            t2Correct[newResponse] += 1
        else:
            t2Wrong[newResponse] += 1
            
        
      
    print (t2Correct)
    print (t2Wrong)


    return render_template("module.html",
     module_title = Module_title,
      lecturersAssessments = lecturersAssessments,
        questionT1s = questionT1s,
        questionT2s = questionT2s,
         t2Responses = t2Responses,
         t2Correct = t2Correct,
         t2Wrong = t2Wrong)

