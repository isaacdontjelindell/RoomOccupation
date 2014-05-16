from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Date, MetaData, create_engine
import datetime
import os
from flask.ext.login import UserMixin


Base = declarative_base()
engine = create_engine('postgresql+pg8000://ctpdjcyslddqaj:q-DEgthTl0_YwQP5njwdCCZsuq@ec2-54-83-9-127.compute-1.amazonaws.com:5432/d2avi0qi33gj0p?ssl=true')


class User(Base):
	'''
	This allows login verification
	'''
	__tablename__= 'user'
	username = Column(Text, primary_key=True)
	password = Column(Text)

	def __init__(self,username,password):
		self.username = username
		self.password = password

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.username






class Building(Base):
	"""
	This holds all the rooms in a buildings
	"""
	__tablename__ = 'building'
	name = Column(String(64), primary_key=True)
	rooms = relationship('Room', backref='building', lazy='dynamic')

	def __repr__(self):
		return '<Building %r>' % self.name

class Room(Base):
	"""
	This table represents one building. Each row is a reservation
	"""
	__tablename__ = 'room'
	roomId = Column(Integer, primary_key = True)
	number = Column(Integer, index=True)
	building_id = Column(ForeignKey('building.name'))
	def __repr__(self):
		return '<Room %r >' % self.roomId

class Reservation(Base):
	'''
	Many to many solution (room - client)
	'''
	__tablename__ = 'reservation'
	arrive = Column(Date, primary_key = True)
	depart = Column(Date, primary_key = True)	
	clientId = Column(ForeignKey('client.clientId'), primary_key = True)
	roomId = Column(ForeignKey('room.roomId'), primary_key = True)
	room = relationship("Room", backref="res")
	def __repr__(self):
		return '<Reservation %r>' % self.arrive
	def asList(self):
		Session = sessionmaker(bind=engine)
		querySession = Session()
		cli = querySession.query(Client).filter_by(clientId = self.clientId).first().name
		return [self.room.building_id, self.room.number, self.arrive, self.depart, cli]

class Client(Base):
	'''
	holds client info
	'''
	__tablename__= 'client'
	name = Column(String(64), index=True)
	clientId = Column(Integer, primary_key=True)
	reservations = relationship('Reservation', backref='client', lazy='dynamic')
	phone = Column(String(13))
	email = Column(String(200))
	def __repr__(self):
		return '<Client %r>' % self.description

def init_db():

	metaData = MetaData()
	Session = sessionmaker(bind=engine)
	initSession = Session()

	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	# user = Users(name='lanejo01',password='asdf')


	miller = Building(name='Miller')
	brandt = Building(name='Brandt')

	isaac = Client(clientId = 1, name = "Isaac Davis")
	joe = Client(clientId = 2, name = "Joe Lane")

	r1 = Room(roomId = 1, number = 1, building_id = miller.name)
	r2 = Room(roomId = 2, number = 2, building_id = miller.name)
	r3 = Room(roomId = 3, number = 1, building_id = brandt.name)

	res1 = Reservation(arrive = datetime.date(2012, 1, 2), depart = datetime.date(2012, 1, 3), clientId = isaac.clientId, roomId = r1.roomId)
	res2 = Reservation(arrive = datetime.date(2012, 1, 5), depart = datetime.date(2012, 1, 7), clientId = joe.clientId, roomId = r1.roomId)


	initSession.add_all([miller, brandt, isaac, joe, r1, r2, r3, res1, res2])
	#fix mixing flask sqlalchmey with plain sqlalchemy
	initSession._model_changes = {}
	#end fix
	initSession.commit()


	#allproj = Project.query.all()
	#for p in allproj:
#		print(p.tasks.all())

#	lproj = Project.query.filter_by(name='Luther').first()
#	lproj = Project.query.filter(Project.name=='Luther')
	# filter
	# filter_by
	# limit
	# order_by
	# group_by
	#
	#print(str(lproj))

	# query executors
	# all()
	# first()
	# get(id)
	# count()

	#
	# http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#common-filter-operators
	#

	# raw sql
	#res = engine.execute('select * from building')
	#for row in res:
	#	print(row)

