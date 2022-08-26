from flask import Flask, render_template, request, session, redirect
import json
import datetime

app = Flask(__name__)
app.secret_key = 'my_super_secret_key'

def read_base(name_of_base):
	file = open(name_of_base, "r")
	data = file.read()
	data = json.loads(data)
	return data

def generate_id():
	now = datetime.datetime.now()
	ident = json.dumps(now.strftime('%H:%M:%S, %d.%m.%y'))
	return ident

def save_base(name_of_base, login, save_content):
	file_content = read_base(name_of_base)
	if name_of_base == 'user_base':
		file_content[login] = save_content
	else:
		ident = generate_id()
		print(ident)
		file_content[ident] = [login, save_content]
	content_as_json = json.dumps(file_content)
	file = open(name_of_base, 'w')
	file.write(content_as_json)
	file.close()

@app.route('/register', methods = ['POST', 'GET'])
def register():
	if request.method == 'GET':
		return render_template("register.html")
	elif request.method == 'POST':
		errors = []
		if request.form.get('password') != request.form.get('password_double'):
			errors.append('Hasła nie są identyczne!')
		data = read_base('user_base')
		if request.form.get('login') in data:
			errors.append('Nieprawidłowe dane!') #użytkonik istnieje
		if not errors:
			login = request.form.get('login')
			password = request.form.get('password')
			save_base('user_base', login, password)
		return render_template("registered_or_not.html", errors=errors)


@app.route("/", methods = ['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('start.html')
	elif request.method == 'POST':
		errors = []
		presence = False
		data = read_base('user_base')
		login =  request.form.get('login')
		password = request.form.get('password')
		password_from_db = data.get(login)
		if login not in data:
			errors.append('fail')
		if password_from_db != password:
			errors.append('fail')
		if not errors:
			presence = True
			session['logged'] = request.form['login']
		return render_template('logged_or_not.html', presence = presence)

@app.route('/create_post', methods = ['POST', 'GET'])
def create_post():
	if request.method == 'GET':
		if session.get('logged'):
			logged = True
		else:
			logged = None
		return render_template('create_post.html', logged = logged)
	elif request.method == 'POST':
		save_base('post_base', session['logged'], request.form.get('post'))
		#print(session['logged'], request.form.get('post'))
		return render_template('logged_or_not.html', logged = session['logged'])

@app.route('/my_posts', methods = ['GET'])
def show_my_posts():
	if request.method == 'GET':
		errors = []
		posts_box = []
		if not session.get('logged'):
			errors.append('Jesteś niezalogowany!')
		else:
			post_base = read_base('post_base')
			for timestamp, values_list in post_base.items():
				if values_list[0] == session.get('logged'):
					posts_box.append(values_list[1])
				else:
					errors.append('Nie masz jeszcze postów! Napisz pierwszy!')
	return render_template('wall.html', logged = session['logged'], posts_box = posts_box, errors = errors)

@app.route('/show_wall', methods = ['GET'])
def show_wall():
	if request.method == 'GET':
		posts_box = []
		if not session.get('logged'):
			posts_box.append('Jesteś niezalogowany!')
		else:
			post_base = read_base('post_base')
			for timestamp, values_list in post_base.items():
				if values_list[0] != session.get('logged'):
					posts_box.append(values_list[1])
					return render_template('wall.html', logged = session['logged'], posts_box = posts_box)
			if posts_box == []:
				posts_box = ['Nie ma postów twoich znajomych! Znajdź nowych!']
				return render_template('wall.html', logged = session['logged'], posts_box = posts_box)
	
@app.route('/delete_post', methods = ['GET', 'POST'])
def delete_post():
	if request.method == 'GET':
		post_base = read_base('post_base')
		posts_box = []
		for timestamp, data in post_base.items():
			login, post_content = data
			if login == session.get('logged'):
				posts_box.append([post_content, timestamp])
				print(request.form.keys())
		return render_template("delete_post.html", logged = session['logged'], posts_box = posts_box)
	elif request.method == 'POST':
		file_content = read_base('post_base')
		for post in file_content:
			if request.form.keys():
				pass
############usuwanie postów do dokończenia!


		return render_template("deleted_post.html", logged = session['logged'], deleted_post=deleted_posts)


#########WYLOGOWYWANIE DO DOKOŃCZENIA
"""
@app.route('/unlogged', methods = ['GET', 'POST'])
def logged_out():
	if request.method == 'GET':
		del session['logged']
	return render_template('unlogged.html')
"""

###### PRZEMYŚLEĆ CAŁĄ LOGIKĘ CO KIEDY SIĘ POJAWIA (np. jak się zarejestrowałem, to może na stronę główną od razu)
#PRZEPISAĆĆ NA ANGIELSKI WSZYSTKO
#USTAWIANIE STATUSU ?!?!?!?
#WYGLĄD STRONY podstawowy, żeby jakkolwiek się to prezentowało, css i takie tam
if __name__ == "__main__":
	app.run()


