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
    user = User.query.filter_by(name = current_user.name).first()
    user_id = user.id
    name = user.name
    print(user_id)

    Assessments = Assessment.query.all()
    Modules = Module.query.all()

    print(Assessments)
    lecturersModules = []
    lecturersAssessments = []
    for assessment in Assessments:
        if assessment.lecturer_id == user_id:
            lecturersAssessments.append(assessment)
            moduleId = assessment.module_id
            for module in Modules:
                print(module)
                if moduleId == module.module_id and module.title not in lecturersModules:
                        lecturersModules.append(module.title)
    print(lecturersAssessments)
    print(lecturersModules)

    return render_template("Staff-stats.html", name = name, lecturersModules = lecturersModules)

@staff_stats.route("/test")
def test():
    return render_template("test.html")



@staff_stats.route("/module/<string:Module_title>")
def module(Module_title):
    user = User.query.filter_by(name = current_user.name).first()
    user_id = user.id
    module = Module.query.filter_by(title = Module_title).first()
    moduleId = module.module_id

    Assessments = Assessment.query.all()

    lecturersAssessments = []
    for assessment in Assessments:
        if assessment.lecturer_id == user_id and assessment.module_id == moduleId:
            lecturersAssessments.append(assessment)
    return render_template("module.html", module_title = Module_title, lecturersAssessments = lecturersAssessments )

