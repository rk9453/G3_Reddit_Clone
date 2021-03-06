from typing import NewType
from app import *


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'us-cdbr-east-05.cleardb.net'
app.config['MYSQL_USER'] = 'bc581d899a9288'
app.config['MYSQL_PASSWORD'] = '019c7e40'
app.config['MYSQL_DB'] = 'heroku_0b525497a3fc037'

mysql = MySQL(app)

def joinSubreddit(subreddit_name):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM heroku_0b525497a3fc037.active_users")
        curr_user = cursor.fetchone()[0]
        inpUsername = curr_user
        
        #Check if the subreddit that the user wants to join exists or not
        cursor.execute("SELECT name FROM heroku_0b525497a3fc037.subreddits WHERE name=%s", (subreddit_name,))
        if(cursor.rowcount == 0):
            print("Subreddit does not exist")
            return False
        
        #Check if the user is already a member of the subreddit
        cursor.execute("SELECT roles FROM heroku_0b525497a3fc037.joined WHERE username=%s AND subreddit=%s", (inpUsername, subreddit_name))
        if(cursor.rowcount != 0):
            print("You are already a member of this subreddit")    
            return False
        
        try:
            cursor.execute("INSERT INTO heroku_0b525497a3fc037.joined VALUES(%s, %s, %s)", (inpUsername, subreddit_name, "Member"))    
            mysql.connection.commit()
        except Exception as rip:
            return False
            
    
        return True
    except Exception as rip:
        return False

def createSubreddit(subreddit_name, description):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM heroku_0b525497a3fc037.active_users")
        curr_user = cursor.fetchone()[0]
        
        inpUsername = curr_user
        
        cursor.execute("SELECT name FROM heroku_0b525497a3fc037.subreddits WHERE name=%s", (subreddit_name,))
        if(cursor.fetchone() != None):
            print("Subreddit with this name already exists")
            return False
        
        #Insert into the subreddit table
        cursor.execute("INSERT INTO heroku_0b525497a3fc037.subreddits VALUES(%s, %s)", (subreddit_name, description))
        mysql.connection.commit()

        #Insertion into the Joined table, to show that the user has created the subreddit
        cursor.execute("INSERT INTO heroku_0b525497a3fc037.joined VALUES(%s, %s, %s)", (inpUsername, subreddit_name, "Subreddit Owner"))
        mysql.connection.commit()
        
        return True    
    except Exception as a:
        return False
    
def leaveSubredditCase(subreddit_name):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM heroku_0b525497a3fc037.active_users")
        curr_user = cursor.fetchone()[0]
        
        username = curr_user
        print("subreddit ka naam is ", subreddit_name)
        
        cursor.execute("SELECT name FROM heroku_0b525497a3fc037.subreddits WHERE name= %s", (subreddit_name,))
        if(cursor.fetchone() == None):
            print("Subreddit does not exist")
            return False
        
        #Check if the user is the owner of the subreddit
        cursor.execute("SELECT roles FROM heroku_0b525497a3fc037.joined WHERE username=%s AND subreddit=%s", (username, subreddit_name))
        
        if(cursor.rowcount == 0): #The user is not a member of the subreddit
            #If thr user is not a member of the subreddit, they're made to join the subreddit
            print("you're not a member of the subreddit :p")
            return False
        if(cursor.fetchone()[0] == "Subreddit Owner"):
            print("You are the owner of this subreddit, you cannot leave :>")
            return False
        #Remove from the joined table
        print("username is ", username, "and subreddit name is", subreddit_name)
        cursor.execute("DELETE FROM heroku_0b525497a3fc037.joined WHERE username=%s AND subreddit=%s", (username, subreddit_name))
        mysql.connection.commit()
        return True
    except Exception as rip:
        return False

def signup_case(username, passwd):
    cursor = mysql.connect.cursor()
    success = 0

    try:
        success = cursor.execute("INSERT INTO heroku_0b525497a3fc037.users VALUES(%s, %s, %s)", (username, 0, passwd))
        # mysql.connection.commit()
        cursor.connection.commit()
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
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT username, password FROM heroku_0b525497a3fc037.users WHERE username=%s AND password=%s", (input_user, input_password))
        
        if cursor.rowcount == 0:
            print("Incorrect username or password")
            return False
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE heroku_0b525497a3fc037.active_users SET username = %s WHERE username = %s", (input_user, "guest"))
            mysql.connection.commit()
            
            return True
    except Exception as rip:
        return False

def viewSubreddit(subreddit_name):
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT name FROM heroku_0b525497a3fc037.subreddits WHERE name = %s", (subreddit_name))

        if cursor.rowcount == 0:
            return False
        else:
            return True
    except Exception as ded:
        return False

def PostInSubreddit(subreddit_name,inptitle, inptext):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username FROM heroku_0b525497a3fc037.active_users")
    curr_user = cursor.fetchone()[0]
    inpUsername = curr_user
    
    cursortemp = mysql.connection.cursor()
    cursortemp.execute("SELECT max(postid) FROM heroku_0b525497a3fc037.posts")
    #tempPostid = cursortemp.fetchall() 
    newPostid = cursortemp.fetchone()[0]+1
    #Check if the subreddit that the user wants to post in exists or not
    cursor.execute("SELECT name FROM heroku_0b525497a3fc037.subreddits WHERE name=%s", (subreddit_name,))
    if(cursor.rowcount == 0):
        print("Subreddit does not exist")
        return False
    
    #Check if the user is not a member of the subreddit
    cursor.execute("SELECT roles FROM heroku_0b525497a3fc037.joined WHERE username=%s AND subreddit=%s", (inpUsername, subreddit_name))
    if(cursor.rowcount == 0):
        print("You have not joined this subreddit subreddit")    
        return False
    
    # file_name = "SamplePicture.jpg"
    # with open(file_name, 'rb') as file:
    #     binary_data = file.read()
    binary_data = "nothinghere"
    # try:
    cursor.execute("INSERT INTO heroku_0b525497a3fc037.posts VALUES    (%s, %s, %s, %s, %s, %s, %s)", (newPostid, curr_user, inptitle, inptext, binary_data, 0, 0))    
    cursor.execute("INSERT INTO heroku_0b525497a3fc037.posted_in VALUES    (%s, %s)", (newPostid,subreddit_name))    
    cursor.execute("INSERT INTO heroku_0b525497a3fc037.posted_by VALUES    (%s, %s)", (curr_user, newPostid))    

    mysql.connection.commit()
    # except Exception as rip:
    #     print("exception here")
    #     return False
        
    return True


# @app.route('/post/', defaults = 'all')
# @app.route('/post/<postid>')
# def viewPost(postid):
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM heroku_0b525497a3fc037.posts WHERE  = %s", (postid,))
    
#     return render_template('post.html', post = cursor.fetchone()[0])
    
    
    

#Here, we implement the upvote/downvote features

def upvote(postid, upvoter):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM heroku_0b525497a3fc037.active_users")
        curr_user = cursor.fetchone()[0]
        if curr_user == "guest":
            print("You must be logged in to upvote")
            
            #print an alert message (front end)
            #return render_template(url_for('home'))
        else:
            
            cursor.execute("SELECT upvote FROM heroku_0b525497a3fc037.post_votes WHERE postid=%s AND username=%s", (postid, upvoter))
            if cursor.rowcount == 0:  #the user hasn't upvoted the post yet
                cursor.execute("INSERT INTO heroku_0b525497a3fc037.post_votes VALUES(%s, %s, %s)", (postid, upvoter, 1))
                mysql.connection.commit()
                
                #Increases the number of upvotes of the post
                cursor.execute("SELECT upvotes from heroku_0b525497a3fc037.posts WHERE postid=%s", (postid,))
                upV = cursor.fetchone()[0]
                upV += 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.posts SET upvotes=%s WHERE postid=%s", (upV, postid))
                mysql.connection.commit()
                
                #Increases the karma of the user who posted the post
                cursor.execute("SELECT karma from heroku_0b525497a3fc037.users WHERE username=%s", (curr_user,))
                k = cursor.fetchone()[0]
                k += 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.users SET karma=%s WHERE username=%s", (k, curr_user))
                mysql.connection.commit()
                
            else: #We must cancel the upvote for that post/person
                cursor.execute("DELETE FROM heroku_0b525497a3fc037.post_votes WHERE username=%s AND postid=%s", (upvoter, postid))

                #Decreases the number of upvotes of the post
                cursor.execute("SELECT upvotes from heroku_0b525497a3fc037.posts WHERE postid=%s", (postid,))
                upV = cursor.fetchone()[0]
                upV -= 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.posts SET upvotes=%s WHERE postid=%s", (upV, postid))
                mysql.connection.commit()
                
                
                #Decreases the karma of the user who posted the post
                cursor.execute("SELECT karma from heroku_0b525497a3fc037.users WHERE username=%s", (curr_user,))
                k = cursor.fetchone()[0]
                k -= 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.users SET karma=%s WHERE username=%s", (k, curr_user))
                mysql.connection.commit()      
            
            return True
    except Exception as rip:
        return False 
       
def downvote(postid, downvoter):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM heroku_0b525497a3fc037.active_users")
        curr_user = cursor.fetchone()[0]
        if curr_user == "guest":
            print("You must be logged in to upvote")
            return render_template(url_for('home'))
        else:
            
            cursor.execute("SELECT upvote FROM heroku_0b525497a3fc037.post_votes WHERE postid=%s AND username=%s", (postid, downvoter))
            if cursor.rowcount == 0:  #the user hasn't downvoted the post yet
                cursor.execute("INSERT INTO heroku_0b525497a3fc037.post_votes VALUES(%s, %s, %s)", (postid, downvoter, -1))
                mysql.connection.commit()
                
                #Increases the number of downvotes of the post
                cursor.execute("SELECT downvotes from heroku_0b525497a3fc037.posts WHERE postid=%s", (postid,))
                downV = cursor.fetchone()[0]
                downV += 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.posts SET downvotes=%s WHERE postid=%s", (downV, postid))
                mysql.connection.commit()
                
                #Decreases the karma of the user who posted the post
                cursor.execute("SELECT karma from heroku_0b525497a3fc037.users WHERE username=%s", (curr_user,))
                k = cursor.fetchone()[0]
                k -= 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.users SET karma=%s WHERE username=%s", (k, curr_user))
                mysql.connection.commit()
                
            else: #We must cancel the downvote for that post/person
                cursor.execute("DELETE FROM heroku_0b525497a3fc037.post_votes WHERE username=%s AND postid=%s", (downvoter, postid))

                #Decreases the number of downvotes of the post
                cursor.execute("SELECT downvotes from heroku_0b525497a3fc037.posts WHERE postid=%s", (postid,))
                downV = cursor.fetchone()[0]
                downV -= 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.posts SET downvotes=%s WHERE postid=%s", (downV, postid))
                mysql.connection.commit()
                
                
                #Decreases the karma of the user who posted the post
                cursor.execute("SELECT karma from heroku_0b525497a3fc037.users WHERE username=%s", (curr_user,))
                k = cursor.fetchone()[0]
                k += 1
                cursor.execute("UPDATE heroku_0b525497a3fc037.users SET karma=%s WHERE username=%s", (k, curr_user))
                mysql.connection.commit()      
            
            return True
    except Exception as rip:
        return False     
    