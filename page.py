from flask import Flask, render_template, request, session, abort, redirect, url_for,flash
from forms import LoginForm, NewRentalForm
from database import Users, Building, Room, init_db
from flask.ext.login import LoginManager,login_user


app = Flask(__name__)
app.secret_key = "heartbleed"
login_manager = LoginManager()

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
    
    if form.validate():
        pass    
    return render_template('search.html', form=form)

@app.route('/results', methods=['POST', 'GET'])
def results():
    res = []
    
    res = [['Brandt', '123', 'Now', 'later', "john doe"]]

    return render_template('output.html', reservationList = res)

@login_manager.user_loader
def load_user(username):
    return Users.get(username)

if __name__ == '__main__':
	app.debug =True 
	app.run()	
