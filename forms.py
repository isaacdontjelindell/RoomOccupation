__author__ = 'Joe'

from wtforms import Form, FormField, DateTimeField, BooleanField, TextField, PasswordField, validators, SelectField, IntegerField, StringField

class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

class SearchForm(Form):
    building = SelectField('Building', choices = [('Brandt', 'Brandt'), ('Dieseth', 'Dieseth'), ('Miller', 'Miller'), ('Yilvi', 'Ylvisaker'), ('Olson','Olson')])
    room = IntegerField('Room number')
    renter = StringField('Renter name')

class FullSearchForm(Form):
    startDate = DateTimeField('Start date', format='%Y-%m-%d %H:%M:%S')
    endDate = DateTimeField('End date', format='%Y-%m-%d %H:%M:%S')
    buildingForm = FormField(SearchForm)

