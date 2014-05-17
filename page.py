from flask import Flask, render_template, request, session, abort, redirect, url_for,flash
from forms import LoginForm, NewRenterForm, SearchForm, FullSearchForm 
from database import User, Building, Room, Reservation, Client, init_db
from sqlalchemy import desc
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
@login_required
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
		if not aClient:
			session['bookInfo'] = json.dumps({'newRenterName':client, 'bookRoomId':str(aRoom.roomId), 'stDate':str(startDate), 'endDate':str(endDate)})
			return redirect(url_for('newRenter'))
		res = Reservation(arrive = startDate, depart = endDate, roomId = aRoom.roomId, clientId = aClient.clientId)
		db.session.add(res)
		db.session.commit()

	return render_template('book.html', form=form)

@app.route('/newRenter', methods=['POST', 'GET'])
@login_required
def newRenter():
	form = NewRenterForm(request.form)
	cookieDir = json.loads(session['bookInfo'])
	form.name.data = cookieDir['newRenterName'] 
	if request.method == 'POST' and form.validate():
		aName = form.name.data
		aNumber = form.phone.data
		aEmail = form.email.data
		
		#get next client id from table
		newClientId = db.session.query(Client).order_by(desc(Client.clientId)).first().clientId + 1
		newClient = Client(name=aName, clientId = newClientId, phone = aNumber, email = aEmail)
		db.session.add(newClient)
		newRes = Reservation(arrive = cookieDir['stDate'], depart = cookieDir['endDate'], roomId = int(cookieDir['bookRoomId']), clientId = newClientId)
		db.session.add(newRes)
		db.session.commit()
			
		return redirect(url_for('book'))

	return render_template('newClient.html', form=form)

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
	form = FullSearchForm(request.form)
	
	if request.method == 'POST' and form.validate():
		building = form.buildingForm.building.data
		room = form.buildingForm.room.data
		client = form.buildingForm.renter.data
		stDate = form.startDate.data
		endDate = form.endDate.data
		session['searchTerms'] = json.dumps({'building':building, 'room':room, 'client':client, 'stDate':stDate, 'endDate':endDate})
		return redirect(url_for('results'))
	return render_template('search.html', form=form)

@app.route('/results', methods=['POST', 'GET'])
@login_required
def results():
	searchDict = json.loads(session['searchTerms'])	
	print(searchDict)
	res = []
	##database query
	#data = db.session.query(Reservation) #.filter_by(clientId = 1) #=searchDict['building'])
	data = doSearch(searchDict)
	for item in data.all():	
		res.append(item.asList())

	#info = data.first()	
	#for row in data:
	#	res.append(str(row))
	##format results
	#res = [[searchDict['building'], searchDict['room'], 'Now', 'later', searchDict['client']]]
	#building = db.session.query(Room).filter_by(roomId = info.roomId).first()
	#res = [[building.name, info.roomId, info.arrive, info.depart, info.clientId]]
	return render_template('output.html', reservationList = res)

@app.route('/initdb')
@login_required
def initdb():
	init_db()

	res = []
	data = db.session.query(Reservation) 
	for item in data.all():	
		res.append(item.asList())
	
	return render_template('output.html', reservationList = res)


def doSearch(paramDict):
	data = db.session.query(Reservation)
	if paramDict['client']:
		aClientId = db.session.query(Client).filter_by(name = paramDict['client']).first().clientId
		data = data.filter_by(clientId = aClientId)
	return data


if __name__ == '__main__':
	app.debug =True 
	app.run()	
