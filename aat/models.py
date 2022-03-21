from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


class Assessment(db.Model):
    __tablename__ = "Assessment"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    questiont2 = db.relationship("QuestionT2", backref="assessment", lazy=True)

    def __repr__(self):
        return f"Assessment - {self.title}"


class QuestionT2(db.Model):
    __tablename__ = "QuestionT2"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    weighting = db.Column(db.Integer, nullable=False)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("Assessment.id"), nullable=False
    )

    def __repr__(self):
        return f"Question id={self.id} on assessment id={self.assessment_id}"



# temporary while waiting for model 

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs): 
        super(User, self).__init__(**kwargs)
        if self.role is None: 
            if self.is_admin:
                self.role = Role.query.filter_by(name='Teacher').first()
            if self.role is None: 
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError("Password is not readable.") 

    @password.setter
    def password(self, password):
        self.hashed_password=generate_password_hash(password)        

    def verify_password(self, password): 
        return check_password_hash(self.hashed_password, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self): 
        return self.can(Permission.ADMIN)

    def __repr__(self): 
        return f"User: {self.name}"

class AnonymousUser(AnonymousUserMixin): 
    def can(self, permissions): 
        return False 

    def is_administrator(self): 
        return False 

class Role(db.Model): 
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None: 
            self.permissions = 0 

    def add_permission(self, perm): 
        if not self.has_permission(perm): 
            self.permissions += perm 

    def remove_permission(self, perm): 
        if self.has_permission(perm):
            self.permissions -= perm 

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm 

    @staticmethod
    def insert_roles(): 
        roles = {
            'Student': [Permission.ANSWER_ASSESSMENT], 
            'Teacher': [Permission.WRITE_ASSESSMENT, Permission.ADMIN], 
            'Admin': [Permission.ADMIN]
        }
        default_role = 'Student'
        for r in roles: 
            role = Role.query.filter_by(name=r).first()
            if role is None: 
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]: 
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self): 
        return f"Role: {self.name}"

class Permission: 
    WRITE_ASSESSMENT = 1
    ANSWER_ASSESSMENT = 2
    ADMIN = 4

# class Student(db.Model): 
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30), unique=True, nullable=False)
#     hashed_password = db.Column(db.String(128))
#     is_admin = db.Column(db.Boolean, nullable=False, default=False)

#     @property
#     def password(self):
#         raise AttributeError("Password is not readable.") 

#     @password.setter
#     def password(self, password):
#         self.hashed_password=generate_password_hash(password)        

#     def verify_password(self, password): 
#         return check_password_hash(self.hashed_password, password)

#     def __repr__(self): 
#         return f"User: {self.name}"

# class Teacher(db.Model): 
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30), unique=True, nullable=False)
#     hashed_password = db.Column(db.String(128))
#     is_admin = db.Column(db.Boolean, nullable=False, default=False)

#     @property
#     def password(self):
#         raise AttributeError("Password is not readable.") 

#     @password.setter
#     def password(self, password):
#         self.hashed_password=generate_password_hash(password)        

#     def verify_password(self, password): 
#         return check_password_hash(self.hashed_password, password)

#     def __repr__(self): 
#         return f"User: {self.name}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
