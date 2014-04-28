from flask import Flask, render_template, request, session, abort, redirect, url_for
app = Flask(__name__)
app.secret_key = "heartbleed"

@app.route('/')
def index():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		pass
	else:
		abort(401)	

if __name__ == '__main__':
	app.debug = True
	app.run()	
