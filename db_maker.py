from aat import db
from aat import app

with app.app_context():
    db.create_all()
