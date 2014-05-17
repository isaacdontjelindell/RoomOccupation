__author__ = 'Joe'

from wtforms import Form, FormField, DateTimeField, BooleanField, TextField, PasswordField, validators, SelectField, IntegerField, StringField
from wtforms import Form, BooleanField, TextField, PasswordField, validators,SubmitField

class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    submit = SubmitField("Login")

class SearchForm(Form):
    building = SelectField('Building', choices = [('Brandt', 'Brandt'), ('Dieseth', 'Dieseth'), ('Miller', 'Miller'), ('Yilvi', 'Ylvisaker'), ('Olson','Olson')])
    room = IntegerField('Room number', [validators.optional()])
    renter = StringField('Renter name', [validators.optional()])

class FullSearchForm(Form):
    startDate = DateTimeField('Start date', [validators.optional()],format='%Y-%m-%d')
    endDate = DateTimeField('End date', [validators.optional()], format='%Y-%m-%d')
    buildingForm = FormField(SearchForm)

class NewRenterForm(Form):
    name = TextField('Name')
    phone = IntegerField('Phone Number, numbers only')
    email = TextField('Email')
