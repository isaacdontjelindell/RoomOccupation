__author__ = 'Joe'

from wtforms import Form, FormField, DateTimeField, BooleanField, TextField, PasswordField, validators, SelectField, IntegerField, StringField

class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

class SearchForm(Form):
    building = SelectField('Building', choices = [('br', 'Brandt'), ('di', 'Dieseth'), ('mi', 'Miller'), ('yl', 'Ylvisaker'), ('ol','Olson')])
    room = IntegerField('Room number')
    renter = StringField('Renter name')

class NewRentalForm(Form):
    startDate = DateTimeField('Start date', format='%Y-%m-%d %H:%M:%S')
    endDate = DateTimeField('End date', format='%Y-%m-%d %H:%M:%S')
    buildingForm = FormField(SearchForm)
