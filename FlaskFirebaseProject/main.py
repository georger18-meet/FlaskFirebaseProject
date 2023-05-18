from flask import Flask, render_template, url_for, flash, jsonify, request, redirect, abort
from flask import session as login_session
from forms import *
import random
import requests,json
import pyrebase

from datetime import datetime


firebaseConfig = {
  "apiKey": "AIzaSyCD01SvtNWxOV_Mip7vOl3U374nXfzgrlU",
  "authDomain": "flaskfirebase-db196.firebaseapp.com",
  "projectId": "flaskfirebase-db196",
  "storageBucket": "flaskfirebase-db196.appspot.com",
  "messagingSenderId": "588875081912",
  "appId": "1:588875081912:web:b88f8965a8f84b62f52c4d",
  "measurementId": "G-H2MQD00P28",
  "databaseURL": "https://flaskfirebase-db196-default-rtdb.europe-west1.firebasedatabase.app"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
currentUser = None

formpy = ValidationForms("","","","")

posts = None

app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

app.config['SECRET_KEY'] = 'e483ff5f4735476cf0e10c9b4f88e38d'



@app.route('/')  # '/' for the default page
@app.route('/home')
def home():
    cu = None
    posts = db.child("Posts").get().val()
    allUsers = db.child("Users")
    try:
        if login_session["user"] != None:
            cu = db.child("Users").child(login_session['user']['localId']).get().val()
        else:
            cu = None
    except:
        cu = None
    return render_template('home.html', login_session = login_session, posts = posts, user = cu, db = allUsers)
 
 
@app.route('/about')
def about():
    return render_template('about.html', login_session = login_session, title = "About")


@app.route('/login', methods=['GET','POST'])
def login():
    if login_session["user"] != None:
        return redirect(url_for('home'))
    else:        
        if request.method == 'GET':
            return render_template('login.html', login_session = login_session, title = "Log In")
        else:
            try:
                login_session["user"] = auth.sign_in_with_email_and_password(request.form.get("email"),request.form.get("psw"))
                currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
                flash(f'Loged In Successfuly!', 'success')
                return redirect(url_for('home'))
            except:
                flash(f'Check Your Credintials! Invalid Email or Password.', 'danger')
                return render_template('login.html', login_session = login_session, title = "Log In")
    
    
@app.route('/signup', methods=['GET','POST'])
def signup():
    if login_session["user"] != None:
        return redirect(url_for('home'))
    else:
        if request.method == 'GET':
            return render_template('signup.html', login_session = login_session, title = "Sign Up")
        else:
            fullname = request.form.get("fullname")
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("psw")
            confirm_psw = request.form.get("confirm-psw")
            if formpy.ValidateSignUp(username,email,password,confirm_psw):            
                try:
                    login_session["user"] = auth.create_user_with_email_and_password(request.form.get("email"),request.form.get("psw"))
                    user = {"fullname":fullname,"username":username,"email":email,"password":password,"pfp":""}
                    db.child("Users").child(login_session["user"]["localId"]).set(user)
                    currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
                    flash(f'Account created for { username }!', 'success')
                    return redirect(url_for('home'))
                except:
                    flash(f'Check Your Credintials! Invalid Username, Email or Password.', 'danger')
                    return render_template('signup.html', login_session = login_session, title = "Sign Up")
            else:            
                flash(f'Check Your Credintials! Invalid Username, Email or Password.', 'danger')
                return render_template('signup.html', login_session = login_session, title = "Sign Up")

@app.route('/logout')
def logout():
    login_session["user"] = None
    auth.current_user = None
    currentUser = None
    return redirect(url_for('login'))


@app.route('/account', methods=['GET','POST'])
def account():
    if login_session["user"] != None:
        currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
        if request.method == 'GET':
            return render_template('account.html', login_session = login_session, title = "Account", user = currentUser)
        else:
            username = request.form.get("username")
            pfp = request.form.get("pfp")
            updated = {}
            if username != "":
                updated["username"] = username                       
            if pfp != "":
                if pfp == "0":
                    updated["pfp"] = ""
                else:
                    updated["pfp"] = pfp
            if updated:
                try:
                    db.child("Users").child(login_session["user"]["localId"]).update(updated)
                    flash(f'Account info updated successfuly!', 'success')
                    return redirect(url_for('account'))
                except:
                    flash(f'Failed to update account info', 'danger')
                    return redirect(url_for('account'))
            else:
                flash(f'Nothing was updated', 'info')
                return redirect(url_for('account'))

    else:
        return redirect(url_for('home'))

@app.route('/remove', methods=['GET','POST'])
def remove():
    if request.method == 'POST':
        if reauthenticate(request.form.get("email"),request.form.get("psw")):
            login_session["user"] = auth.sign_in_with_email_and_password(request.form.get("email"), request.form.get("psw"))
        
            delete_url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={firebaseConfig['apiKey']}"
        
            response = requests.post(delete_url, json={'idToken': login_session["user"]['idToken']})
            if response.ok:
                db.child("Users").child(login_session['user']['localId']).remove()
                flash(f'Account Deleted Successfuly!', 'info')
                return redirect(url_for('logout'))
            else:
                flash(f'An error occurred while deleting the account.', 'danger')
                return redirect(url_for('home'))
        else:
            flash(f'Account Deletion Reauthentication Failed.', 'danger')
            return redirect(url_for('account'))  
    else:
        return redirect(url_for('home'))
        
def reauthenticate(reauth_email,reauth_password):
    try:
        auth.current_user = login_session['user']['idToken']
        auth.refresh(login_session['user']['refreshToken'])
        auth.sign_in_with_email_and_password(reauth_email, reauth_password)
        print ("Reauthentication Succeded")
        return True
    except Exception as e:
        print ("Reauthentication Failed")
        return False
     

@app.route('/post/new', methods=['GET','POST'])
def new_post():
    if login_session["user"] != None:
        currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
        if request.method == 'GET':
            return render_template('create_post.html', login_session = login_session, title = "New Post", user = currentUser, newPost = True)
        else:
            title = request.form.get("title")
            content = request.form.get("content")
            username = currentUser["username"]
            userID = login_session['user']['localId']
            attachedImg = request.form.get("img")
            nowtoday = datetime.now()
            timestamp = nowtoday.strftime("%d/%m/%Y %H:%M:%S")
            post = {"title":title,"content":content,"author":username,"timestamp":timestamp, "uid":userID,"attachedImg":attachedImg}
            print(post)
            post_ref = db.child("Posts").push(post)
            post_key = post_ref["name"]
            db.child("Posts").child(post_key).update({"postId":post_key})
            flash(f'Your post was creted!', 'success')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
  
@app.route('/post/<post_id>')
def post(post_id):
    if login_session["user"] != None:
        posts = db.child("Posts").get().val()
        currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
        try:
            post = posts[post_id]
            print(post)
            return render_template('post.html', login_session = login_session, user=currentUser, title = post["title"], post = post, db=db)
        except:
            abort(404)
    
@app.route('/post/<post_id>/update', methods=['GET','POST'])
def update_post(post_id):
    if login_session["user"] != None:
        currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
        posts = db.child("Posts").get().val()
        if request.method == 'GET':
            try:
                post = posts[post_id]
                if post["author"] == currentUser["username"]:
                    return render_template('create_post.html', login_session = login_session, title = "Update Post", post = post, user = currentUser, newPost = False)
                else:
                    abort(403)
            except:
                abort(403)
        else:
            title = request.form.get("title")
            content = request.form.get("content")
            attachedImg = request.form.get("img")
            post_key = request.form.get("custId")
            updated = {"title":title,"content":content,"attachedImg":attachedImg}
            db.child("Posts").child(post_key).update(updated)
            flash(f'Post updated successfuly!', 'success')
            return redirect(url_for('post',post_id=post_key))
   
@app.route('/post/<post_id>/delete')
def delete_post(post_id):
    if login_session["user"] != None:
        currentUser = db.child("Users").child(login_session['user']['localId']).get().val()
        post = db.child("Users").child(post_id).get().val()
        try:
            db.child("Posts").child(post_id).remove()
            flash(f'Post Deleted Successfuly', 'info')
            return redirect(url_for('home'))
        except:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

            
# Makes sure this is the main process
if __name__ == "__main__":
    app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000),  # Randomly select the port the machine hosts on.
    debug=True)