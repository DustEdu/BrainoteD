from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,  BooleanField, PasswordField
from wtforms.validators import DataRequired, ValidationError

import sqlalchemy as db
from main import session
from ormmodels import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, name: str):
        existing_user = session.execute(db.select(User).where(User.username == name)).one_or_none()
        if existing_user:
            raise ValidationError("Such user already exists. Please choose another username or login instead.")
