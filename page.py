from flask import Flask, render_template, request, session, abort, redirect, url_for,flash
from forms import LoginForm, SearchForm, FullSearchForm 
from database import User, Building, Room, Reservation, Client, init_db
from flask.ext.login import LoginManager,login_user,login_required,logout_user
from flask.ext.sqlalchemy import SQLAlchemy
import os
import json
import pg8000
import datetime

app = Flask(__name__)
app.secret_key = "heartbleed"


basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://ctpdjcyslddqaj:q-DEgthTl0_YwQP5njwdCCZsuq@ec2-54-83-9-127.compute-1.amazonaws.com:5432/d2avi0qi33gj0p?ssl=true'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):

    return db.session.query(User).get(username)


@app.route('/')
def index():
	return redirect(url_for('login'))


@app.route('/login',methods=['POST','GET'])
def login():

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # user = Users(request.form['username'],request.form['password'])
        # user = db.session.query(User).filter_by(username=request.form['username'],password=request.form['password']).first()
        user = User(username=request.form['username'],password=request.form['password'])

        print(user.username,user.password,user.get_id(),user.is_active(),user.is_anonymous(),user.is_authenticated())
        login_user(user)


        #return render_template('success.html')
        return redirect(url_for('search'))

    return render_template('login.html',form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/book', methods=['POST', 'GET'])
def book():
	form = FullSearchForm(request.form)
	if request.method == 'POST' and form.validate():
		building = form.buildingForm.building.data
		roomNum = form.buildingForm.room.data
		client = form.buildingForm.renter.data
		startDate = form.startDate.data
		endDate = form.endDate.data

		#write to database
		aRoom = db.session.query(Room).filter_by(building_id = building, number = roomNum).first()
		aClient = db.session.query(Client).filter_by(name = client).first()
		res = Reservation(arrive = startDate, depart = endDate, roomId = aRoom.roomId, clientId = aClient.clientId)
		db.session.add(res)
		db.session.commit()

	return render_template('book.html', form=form)

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
	form = FullSearchForm(request.form)
	
	if request.method == 'POST' and form.validate():
		building = form.buildingForm.building.data
		room = form.buildingForm.room.data
		client = form.buildingForm.renter.data
		session['searchTerms'] = json.dumps({'building':building, 'room':str(room), 'client':str(client)})
		return redirect(url_for('results'))
	return render_template('search.html', form=form)

@app.route('/results', methods=['POST', 'GET'])
def results():
	searchDict = json.loads(session['searchTerms'])	
	res = []
	##database query
	data = db.session.query(Reservation).filter_by(clientId = 1) #=searchDict['building'])
	info = data.first()	
	for row in data:
		res.append(str(row))
	##format results
	#res = [[searchDict['building'], searchDict['room'], 'Now', 'later', searchDict['client']]]
	building = db.session.query(Room).filter_by(roomId = info.roomId).first()
	res = [[building.name, info.roomId, info.arrive, info.depart, info.clientId]]
	return render_template('output.html', reservationList = res)

@app.route('/initdb')
def initdb():
	init_db()
	res = [['a', 'b']]	
	
	data = db.session.query(Reservation)
	for row in data:
		res.append(str(row))

	return render_template('output.html', reservationList = res)




if __name__ == '__main__':
	app.debug =True 
	app.run()	
