__author__ = 'Joe'

from wtforms import Form, BooleanField, TextField, PasswordField, validators,SubmitField

class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    submit = SubmitField("Login")