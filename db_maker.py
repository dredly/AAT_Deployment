from aat import db
from aat import app
from aat import Role

with app.app_context():
    db.create_all()
    Role.insert_roles()
