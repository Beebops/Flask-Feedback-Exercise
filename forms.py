from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    """Form to register a new User"""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])


class UserLoginForm(FlaskForm):
    """Form for an existing User to sign in"""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    """Form for logged in User to provide feedback"""
    title = StringField('Title', validators=[InputRequired(),Length(max=100)])
    content = StringField('Content', validators=[InputRequired()])    