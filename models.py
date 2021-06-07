"""Models for feedback."""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username'), nullable=False)

class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email =  db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    feedback_given = db.relationship('Feedback', backref='users', lazy=True)

    #two class methods inspired by the demo code
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register user with hashed password then return the user"""

        hashed_password = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed_password.decode("utf8")

        # return instance of user with form data and a hash password
        return cls(username=username,
        password=hashed_utf8,
        email=email,
        first_name=first_name,
        last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """Validates that user exists and password is correct.
        Return True if valid; else return False."""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return True
        else:
            return False

def connect_db(app):
    """Connect to database."""
    
    db.app = app
    db.init_app(app)