# This is literally just for admin
from flask_admin.contrib.sqla import ModelView
import flask_login as login
from .models import User


class AdminView(ModelView):
    # If we want the admin panel to be accessed ONLY if admin then uncomment the below:
    # def is_accessible(self):
    #     if login.current_user.is_authenticated:
    #         if login.current_user.get_id():
    #             user = User.query.get(login.current_user.get_id())
    #             return user.is_admin
    #     return False
    pass
