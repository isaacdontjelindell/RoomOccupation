__author__ = 'Joe'

from wtforms import Form, BooleanField, TextField, PasswordField, validators

class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
