from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length

class register(FlaskForm):
    """form for registering a new user"""

    username = StringField("Username",
                        validators=[Length(max=20)])
    password = PasswordField("Password")
    email = StringField("Email",
                        validators=[Length(max=50)])
    first_name = StringField("First_name",
                        validators=[Length(max=30)])
    last_name = StringField("Last_name",
                        validators=[Length(max=30)])

class login(FlaskForm):
    """form for logging in"""

    username = StringField("Username",
                        validators=[Length(max=20)])
    password = PasswordField("Password")

class feedback(FlaskForm):
    """form for adding a user's feedback"""

    title = StringField("Title",
                        validators=[Length(max=100)])
    content = StringField("Content")