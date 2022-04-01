from aat import db, app
from aat.models import *

with app.app_context():
    q = (
        db.session.query(User, ResponseT2, QuestionT2, Assessment, Module)
        .select_from(User)
        .join(ResponseT2)
        .join(QuestionT2)
        .join(Assessment)
        .join(Module)
        .all()
    )
    print(q)
