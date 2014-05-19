from flask import Flask, render_template, request, session, abort, redirect, url_for,flash,jsonify
from forms import LoginForm, NewRenterForm,FullSearchForm,BookForm
from database import User, Building, Room, Reservation, Client, init_db
from sqlalchemy import desc, exc
from flask.ext.login import LoginManager,login_user,login_required,logout_user
from flask.ext.sqlalchemy import SQLAlchemy

from dateutil import parser
import os
import json
import pg8000
import datetime

app = Flask(__name__)
app.secret_key = "heartbleed"
app.debug=True


basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://ctpdjcyslddqaj:q-DEgthTl0_YwQP5njwdCCZsuq@ec2-54-83-9-127.compute-1.amazonaws.com:5432/d2avi0qi33gj0p?ssl=true'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
		if user.is_authenticated():
			login_user(user)
			return redirect(url_for('search'))
		else:
			return render_template('login.html',form=form)

	return render_template('login.html',form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect('/login')

@app.route('/book', methods=['POST', 'GET'])
@login_required
def book():
	form = BookForm(request.form)
	if request.method == 'POST' and form.validate():
		building = form.building.data
		roomNum = form.room.data
		client = form.renter.data
		startDate = form.startDate.data
		endDate = form.endDate.data

		#write to database
		aRoom = db.session.query(Room).filter_by(building_id = building, number = roomNum).first()
		if not aRoom:
			err = "Room number " + str(roomNum) + " is not valid for the building " + str(building)
			return render_template('error.html', msg=err)
		aClient = db.session.query(Client).filter_by(name = client).first()
		if not aClient:
			session['bookInfo'] = json.dumps({'room' : roomNum, 'newRenterName':client, 'bookRoomId':xstr(aRoom.roomId), 'stDate':xstr(startDate), 'endDate':xstr(endDate)})
			return redirect(url_for('newRenter'))
		res = Reservation(arrive = startDate, depart = endDate, roomId = aRoom.roomId, clientId = aClient.clientId)

		termsDict = {'building': xstr(building), 'room':roomNum, 'client': '', 'stDate':xstr(startDate), 'endDate':xstr(endDate)}
		preRes = doSearch(termsDict)
		if bookDateCompare(preRes, termsDict):
			return render_template('error.html', msg="There is an issue with that room and date combination")
		try:
			db.session.add(res)
			db.session.commit()
		except (exc.InvalidRequestError, exc.ProgrammingError):
			db.session.rollback()
			err = "There is an issue booking that room for that set of dates, please try again. It is most likely there is a record for this user on those dates already."
			return render_template('error.html', msg=err)
		
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
		db.session.commit()
		
		newRes = Reservation(arrive = parser.parse(cookieDir['stDate']), depart = parser.parse(cookieDir['endDate']), roomId = int(cookieDir['bookRoomId']), clientId = newClientId)
		cookieDir['building'] = 'None'
		cookieDir['client'] = ''
		#cOPY From book
		cookieDir['building'] = 'None'
		preRes = doSearch(cookieDir)	
		if bookDateCompare(preRes, cookieDir):
			return render_template('error.html', msg="There is an issue with that room and date combination. The new client was still added to the database.")
		try:
			db.session.add(newRes)
			db.session.commit()
		except (exc.InvalidRequestError, exc.ProgrammingError):
			db.session.rollback()
			err = "There is an issue booking that room for that set of dates, please try again. It is most likely there is a record for this user on those dates already."
			return render_template('error.html', msg=err)
			
		return redirect(url_for('book'))

	return render_template('newClient.html', form=form)

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
	form = FullSearchForm(request.form)
	
	if request.method == 'POST' and form.validate():
		building = form.building.data
		room = form.room.data
		client = form.renter.data
		stDate = form.startDate.data
		endDate = form.endDate.data
		session['searchTerms'] = json.dumps({'building':building, 'room':room, 'client':client, 'stDate':xstr(stDate), 'endDate':xstr(endDate)})
		return redirect(url_for('results'))
	return render_template('search.html', form=form)

@app.route('/results', methods=['POST', 'GET'])
@login_required
def results():
	if 'searchTerms' in session:
		searchDict = json.loads(session['searchTerms'])	
	else:
		searchDict = {'building' : 'None', 'client': None, 'room': "", 'stDate' : None, 'endDate' : None}
	res = []
	data = doSearch(searchDict)
	data = searchDateCompare(data, searchDict)
	if type(data) is str:
		return render_template('error.html', msg=data)
	for item in data.all():	
		res.append(item.asList())

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

@app.route('/api/numberOfRooms')
def apiNumOfRooms():
	building = request.args.get('building','Brandt',type=str)
	numOfRooms = db.session.query(Room).filter_by(building_id=building).count()
	return jsonify(result=numOfRooms)

@app.route('/buildingSpec')
def buildingSpec():
	return render_template('buildingSpec.html')

def doSearch(paramDict):
	data = db.session.query(Reservation)
	if paramDict['building'] != 'None':
		aBuilding = db.session.query(Building).filter_by(name = paramDict['building']).first()
		if paramDict['room']:
			theRoomId = None
			for room in aBuilding.rooms:
				if room.number == paramDict['room']:
					theRoomId = room.roomId
			data = data.filter(Reservation.roomId == theRoomId) 
		else:
			idList = []
			for room in aBuilding.rooms:
				idList.append(room.roomId)
			data = data.filter(Reservation.roomId.in_(idList))
	print(len(data.all()))
	if paramDict['client']:
		aClient = db.session.query(Client).filter_by(name = paramDict['client']).first()
		if aClient:
			aClientId = aClient.clientId
			data = data.filter_by(clientId = aClientId)
		else:
			data = "There is no client named " + str(paramDict['client'])
	return data

def searchDateCompare(data, paramDict):
	if paramDict['stDate']:
		data = data.filter(Reservation.arrive > parser.parse(paramDict['stDate']))
	if paramDict['endDate']:
		data = data.filter(parser.parse(paramDict['endDate']) > Reservation.depart)
	return data	

def bookDateCompare(data, paramDict):
	for res in data:
		if res.arrive < parser.parse(paramDict['stDate']).date() and res.depart > parser.parse(paramDict['stDate']).date():
			return True
		if res.arrive > parser.parse(paramDict['stDate']).date() and res.arrive < parser.parse(paramDict['endDate']).date():
			return True
		if res.depart > parser.parse(paramDict['stDate']).date() and res.depart < parser.parse(paramDict['endDate']).date():
			return True
	return False

def xstr(s):
	if not s:
		return ''
	return str(s)


if __name__ == '__main__':
	app.debug = True 
	app.run()	
