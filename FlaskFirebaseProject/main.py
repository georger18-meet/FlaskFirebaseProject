from flask import Flask, render_template, url_for, flash, jsonify, request, redirect
from forms import *
import random
import requests,json
import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyCD01SvtNWxOV_Mip7vOl3U374nXfzgrlU",
  "authDomain": "flaskfirebase-db196.firebaseapp.com",
  "projectId": "flaskfirebase-db196",
  "storageBucket": "flaskfirebase-db196.appspot.com",
  "messagingSenderId": "588875081912",
  "appId": "1:588875081912:web:b88f8965a8f84b62f52c4d",
  "measurementId": "G-H2MQD00P28"
}

# firebase = pyrebase.initialize_app(firebaseConfig)
# auth = firebase.auth()


app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

app.config['SECRET_KEY'] = 'e483ff5f4735476cf0e10c9b4f88e38d'

formpy = ValidationForms("","","","")

@app.route('/')  # '/' for the default page
@app.route('/home')
def home():
    return render_template('home.html')
        
@app.route('/about')
def about():
    return render_template('about.html', title = "About")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title = "Log In")
    else:
        if formpy.ValidateLogIn(request.form.get("email"),request.form.get("psw")):
            flash(f'Loged In Successfuly!', 'success')
            return redirect(url_for('home')) 
        else:
            flash(f'Check Your Credintials! Invalid Email or Password.', 'danger')
            return render_template('login.html', title = "Log In")
    
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', title = "Sign Up")
    else:
        if formpy.ValidateSignUp(request.form.get("username"),request.form.get("email"),request.form.get("psw"),request.form.get("confirm-psw")):
            flash(f'Account created for { request.form.get("username") }!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Check Your Credintials! Invalid Username, Email or Password.', 'danger')
            return render_template('signup.html', title = "Sign Up")



if __name__ == "__main__":  # Makes sure this is the main process
    app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000),  # Randomly select the port the machine hosts on.
    debug=True)