from flask import Flask, render_template, request, session, abort, redirect, url_for,flash
from forms import LoginForm, NewRentalForm
from database import Users, Building, Room, Reservation, init_db
from flask.ext.login import LoginManager,login_user
from flask.ext.sqlalchemy import SQLAlchemy
import os
import pg8000
import datetime

app = Flask(__name__)
app.secret_key = "heartbleed"
login_manager = LoginManager()

basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://ctpdjcyslddqaj:q-DEgthTl0_YwQP5njwdCCZsuq@ec2-54-83-9-127.compute-1.amazonaws.com:5432/d2avi0qi33gj0p?ssl=true'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)



@app.route('/')
def index():
	return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
# 	error = None
# 	if request.method == 'POST':
# 		pass
# 	else:
# 		abort(401)

@app.route('/login',methods=['POST','GET'])
def login():

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # LoginForm = Users(request.form['username'],request.form['password'])
        # user =Users.query.filter_by(username=request.form['username']).first()
        # user = Users(username=request.form['username'],password=request.form['password'])
        # login_user(user)


        #return render_template('success.html')
        return redirect(url_for('search'))

    return render_template('login.html',form=form)

@app.route('/search', methods=['POST', 'GET'])
def search():
	form = NewRentalForm(request.form)
	
	if request.method == 'POST' and form.validate():
		building = form.buildingForm.building.data
		room = form.buildingForm.room.data
		client = form.buildingForm.renter.data
		print(building, " | ", room, " | ", client)
		return redirect(url_for('results'))
	return render_template('search.html', form=form)

@app.route('/results', methods=['POST', 'GET'])
def results():
	print('in results')
	res = []
	
	res = [['Brandt', '123', 'Now', 'later', "john doe"]]

	return render_template('output.html', reservationList = res)

@app.route('/initdb')
def initdb():
	init_db()
	res = [['a', 'b']]	
	
	data = db.session.query(Reservation)
	for row in data:
		res.append(str(row))

	return render_template('output.html', reservationList = res)

@app.route('/testQ')
def testQ():
	res = [['a', 'b']]	
	
	#db.session.add(Building(name='miller'))
	
	data = db.session.query(Building)
	for row in data:
		res.append(str(row))

	return render_template('output.html', reservationList = res)


@login_manager.user_loader
def load_user(username):
    return Users.get(username)

if __name__ == '__main__':
	app.debug =True 
	app.run()	
