curr_user = "guest" #Stores the username of the current username


from logging import currentframe
from typing import SupportsRound
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '33e0a108'
app.config['MYSQL_DB'] = 'reddit2'

mysql = MySQL(app)

#Below, we have our member/helper functions

def joinSubreddit(subreddit_name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username FROM reddit2.active_users")
    curr_user = cursor.fetchone()[0]
    inpUsername = curr_user
    
    #Check if the subreddit that the user wants to join exists or not
    cursor.execute("SELECT name FROM reddit2.subreddits WHERE name=%s", (subreddit_name,))
    if(cursor.rowcount == 0):
        print("Subreddit does not exist")
        return False
    
    #Check if the user is already a member of the subreddit
    cursor.execute("SELECT roles FROM reddit2.joined WHERE username=%s AND subreddit=%s", (inpUsername, subreddit_name))
    if(cursor.rowcount != 0):
        print("You are already a member of this subreddit")    
        return False
    
    try:
        cursor.execute("INSERT INTO reddit2.joined VALUES(%s, %s, %s)", (inpUsername, subreddit_name, "Member"))    
        mysql.connection.commit()
    except Exception as rip:
        return False
        
    
    return True

def createSubreddit(subreddit_name, description):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username FROM reddit2.active_users")
    curr_user = cursor.fetchone()[0]
    
    inpUsername = curr_user
    
    cursor.execute("SELECT name FROM reddit2.subreddits WHERE name=%s", (subreddit_name,))
    if(cursor.fetchone() != None):
        print("Subreddit with this name already exists")
        return False
    
    #Insert into the subreddit table
    cursor.execute("INSERT INTO reddit2.subreddits VALUES(%s, %s)", (subreddit_name, description))
    mysql.connection.commit()

    #Insertion into the Joined table, to show that the user has created the subreddit
    cursor.execute("INSERT INTO reddit2.joined VALUES(%s, %s, %s)", (inpUsername, subreddit_name, "Subreddit Owner"))
    mysql.connection.commit()
    
    return True    
    
def leaveSubredditCase(subreddit_name):

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username FROM reddit2.active_users")
    curr_user = cursor.fetchone()[0]
    
    username = curr_user
    
    cursor.execute("SELECT name FROM reddit2.subreddits WHERE name= %s", (subreddit_name,))
    if(cursor.fetchone() == None):
        print("Subreddit does not exist")
        return False
    
    #Check if the user is the owner of the subreddit
    cursor.execute("SELECT roles FROM reddit2.joined WHERE username=%s AND subreddit=%s", (username, subreddit_name))
    
    if(cursor.rowcount == 0): #The user is not a member of the subreddit
        #If thr user is not a member of the subreddit, they're made to join the subreddit
        #return joinSubreddit(subreddit_name)
        return False
    if(cursor.fetchone()[0] == "Subreddit Owner"):
        print("You are the owner of this subreddit, you cannot leave :>")
        return False
    #Remove from the joined table
    cursor.execute("DELETE FROM reddit2.joined WHERE username=%s AND name=%s", (username, subreddit_name))
    
    return True

def signup_case(username, passwd):
    cursor = mysql.connection.cursor()
    success = 0
    
    
    try:
        success = cursor.execute("INSERT INTO reddit2.users VALUES(%s, %s, %s)", (username, 0, passwd))
        mysql.connection.commit()
    except Exception as it_is_what_it_is:
        print("excepion caught")
        pass
    
    if success == 1: #Successfully inserted
        print("Congratulations! Your account has been made")
        return True
    else:
        print("Error, the account already exists, please choose a different username")
        return False
    
def login(input_user, input_password):
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT username, password FROM reddit2.users WHERE username=%s AND password=%s", (input_user, input_password))
    
    if cursor.rowcount == 0:
        print("Incorrect username or password")
        return False
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE reddit2.active_users SET username = %s WHERE username = %s", (input_user, "guest"))
        mysql.connection.commit()
        
        return True



#Below, we have our routes

@app.route("/unsucessful.html", methods=['GET', 'POST'])
def unsuc():
    return render_template("unsucessful.html")


@app.route("/sucessful.html", methods=['GET', 'POST'])
def suc():
    return render_template("sucessful.html")


#These routes are for creating, joining, and leaving a subreddit
@app.route("/create-reddit.html", methods=["GET", "POST"])
def create():
    
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM reddit2.active_users")
        curr_user = cursor.fetchone()[0]
        
        if curr_user != "guest":
            subreddit_name = request.form.get("subreddit_name1")
            description = request.form.get("description1")
            #print("ae ki gal ae", subreddit_name)
            if(createSubreddit(subreddit_name, description)):
                return redirect("sucessful.html")
            else:
                return redirect("unsucessful.html")
        else:
            print("You must be logged in to create a subreddit")
            return redirect("login.html")
    return render_template("create-reddit.html")



@app.route("/join-reddit.html", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM reddit2.active_users")
        curr_user = cursor.fetchone()[0]
        
        if curr_user != "guest":
            subreddit_name = request.form.get("subreddit_name1")
           # print("lsakdjsalkjalkd", subreddit_name)
            if joinSubreddit(subreddit_name):
                return redirect("sucessful.html")
            else:
                return redirect("unsucessful.html")
        else:
            print("You must be logged in to join a subreddit")
            return redirect("login.html")
    return render_template("join-reddit.html")

@app.route("/delete-reddit.html", methods=["GET", "POST"])
def leave():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM reddit2.active_users")
        curr_user = cursor.fetchone()[0]
        if curr_user != "guest":
            subreddit_name = request.form.get("subreddit_name")
            if leaveSubredditCase(subreddit_name):
                return redirect("sucessful.html")
            else:
                return redirect("unsucessful.html")
        else:
            print("You must be logged in to leave a subreddit")
            return redirect("login.html")
    return render_template("delete-reddit.html")
    
    
    
'''This function is for the actions carried out on the dashboard '''
@app.route("/dashboard.html", methods=["GET", "POST"])
def dash():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username FROM reddit2.active_users")
    curr_user = cursor.fetchone()[0]
    if curr_user != "guest":
        return render_template("dashboard.html")
    else:
        print("You must be logged in to view the dashboard")
        return redirect("login.html")
    
'''This function is for the homepage of our application. By default, it opens the login page for the user'''
@app.route("/", methods = ["POST", "GET"])
def home(): 
    
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM active_users",)
    mysql.connection.commit()
    try:
        cursor.execute("INSERT INTO active_users VALUES (%s)", ("guest",))
        mysql.connection.commit()
    except:
        pass

    
    
    if request.method == 'POST':        
        username = request.form.get('username')
        password = request.form.get('password')
        if login(username, password): #This function automatically updates curr_user as well
            print("True")
            return redirect(url_for('dash'))
        else:
            print(False)
            return redirect("sucessful.html")
        
    return render_template("login.html")

'''This function is to handle the "sign up" use case, when a user wishes to create an account'''
@app.route("/signup.html", methods = ["POST", "GET"])
def signup(): 
    if request.method == 'POST':
        if curr_user == "guest":
            username = request.form.get('username')
            password = request.form.get('password1')
            print(username, password)
            
            val = signup_case(username, password)
            if(val):
                return redirect(url_for('home'))
            else:
                return redirect("/unsucessful.html")
        else:
            print("You are already logged in!")
            return redirect("/dashboard.html")
            
    #return render_template("signup.html")
    return render_template("signup.html")


    
if __name__ == "__main__":
    app.run(debug=True)
    