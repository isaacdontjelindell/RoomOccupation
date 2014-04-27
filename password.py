from flask import Flask, render_template, request, session
import random
app = Flask(__name__)
app.secret_key = "heartbleed"

@app.route('/xkcd')
def xkcd():
	return render_template('form.html')

@app.route('/display')
def display():
	wordsToUse = []
	try:
		shortLen = int(request.args['wordMinLen'])
		longLen = int(request.args['wordMaxLen'])
		totalLen = int(request.args['totalLen'])
	except Exception as e:
		return render_template('error.html', errorCause=e)
	capWords = request.args.getlist('cap')
	subLetters = getSubs(request)	

	#check for failure before
	failure = False 
	cause = "being a bitch"
	if totalLen < shortLen *4:
		cause = "Your minimum word lenght will not work"	
		failure = True	
	if failure:
		return render_template('error.html', errorCause=cause)

	#were ok keep going so find the acceptable words
	wordFile = open('words.dat')
	for line in wordFile:
		striped = line.strip()
		trimed = striped.lower()
		if len(trimed) >= shortLen and len(trimed) <= longLen:
			wordsToUse.append(trimed)
	#find passwords
	passwordList = []
	for _ in range(10):
		passwordParts = []
		newPassword = ""
		usedWords = []
		for wordIndex in range(4):
			nextWord = ""
			nextIndex = random.randint(0, len(wordsToUse))-1
			if nextIndex not in usedWords:
				usedWords.append(nextIndex)
				if str(wordIndex) in capWords:
					nextWord = wordsToUse[nextIndex].title()		 
				else:
					nextWord = wordsToUse[nextIndex]
			for letter in subLetters:
				if letter == "three":
					nextWord = nextWord.replace('e', '3')	
				elif letter == "zero":		
					nextWord = nextWord.replace('o', '0')	
				elif letter == "one":		
					nextWord = nextWord.replace('l', '1')	
				elif letter == "five":		
					nextWord = nextWord.replace('s', '5')	
				elif letter == "four":	
					nextWord = nextWord.replace('a', '4')	
			passwordParts.append(nextWord)
			newPassword += nextWord
		passwordParts.append(newPassword)
		passwordList.append(passwordParts)
	#make the view
	if not passwordList:
		passwordList = [["something broke use"], ["changeme"]]
	wordFile.close()
	return render_template('output.html', passwords=passwordList)



def getSubs(req):
	aList = []
	options = ['three', 'zero', 'one', 'five', 'four']
	try:
		for item in options:
			if req.args.get(item, ''):
				aList.append(item)
	except KeyError as e:
		pass
	return aList

if __name__ == '__main__':
	app.debug = True
	app.run()	
