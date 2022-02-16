from flask import Flask, render_template, redirect, url_for, request
from mongoengine import *
from mongoengine.queryset.visitor import Q
from classes import Account, Post
import time
import requests
import string, json, random
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    current_timestamp = time.time()
    posts = Post.objects(timestamp__gte = current_timestamp).order_by('date_time')
    accounts = Account.objects()

    return render_template('index.html', posts = posts, accounts = accounts)

@app.route('/accounts')
def accounts():
    accounts = Account.objects()
    
    return render_template('accounts.html', accounts = accounts)

@app.route("/remove_account", methods=['POST'])
def remove_account():
    account_id = request.form['account_id']

    #Delete account
    Account.objects(id = account_id).delete()

    return {"success": True, "message": "Successfully removed account."}

@app.route("/reddit_auth")
def reddit():
    CLIENT_ID = [line.rstrip('\n') for line in open('KEYS.txt')][1].split("=")[1].strip()

    random_string = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(100))
    redirect_uri = "http://127.0.0.1:5000/reddit_response"
    
    reddit_uri = f"https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={random_string}&redirect_uri={redirect_uri}&duration=permanent&scope=submit%20identity"

    return redirect(reddit_uri)

@app.route("/reddit_response")
def reddit_response():
    error = request.args.get('error')
    code = request.args.get('code')

    if error == None:
        CLIENT_ID = [line.rstrip('\n') for line in open('KEYS.txt')][1].split("=")[1].strip()
        CLIENT_SECRET = [line.rstrip('\n') for line in open('KEYS.txt')][2].split("=")[1].strip()

        redirect_uri = "http://127.0.0.1:5000/reddit_response"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        }
        client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        epoch = time.time()
        auth_response = requests.post("https://www.reddit.com/api/v1/access_token", data = data, headers=headers, auth = client_auth).json()
        token_expiration = epoch + auth_response['expires_in']

        headers['Authorization'] = f"bearer {auth_response['access_token']}"
        user_details = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers).json()

        if Account.objects(username = user_details['name']).count() == 0:
            Account(
                access_token = auth_response['access_token'],
                refresh_token = auth_response['refresh_token'],
                token_expiration = token_expiration,
                username = user_details['name']
            ).save()
        return redirect(url_for('accounts'))
        
    return error

@app.route('/schedule_post', methods=['POST'])
def schedule_post():
    #read in data from ajax call
    data = json.loads(request.form['data'])
    data = { k: (None if v == '' else v) for k, v in data.items() }
    
    #Get exact time and minute from scheduled post time
    post_time = data['text_time'] if 'text_time' in data else data['media_time']
    if post_time.split(" ")[1] == "PM":
        hour = int(post_time.split(":")[0])
        post_hour = 12 if hour == 12 else 12 + hour
        post_minute = int(post_time.replace(" PM", "").split(":")[1])
    elif post_time.split(" ")[1] == "AM":
        hour = int(post_time.split(":")[0])
        post_hour = 0 if hour == 12 else hour
        post_minute = int(post_time.replace(" AM", "").split(":")[1])
    
    #Get exact month, day, year from scheduled post date
    post_date = data['text_date'] if 'text_date' in data else data['media_date']
    post_month, post_day, post_year = int(post_date.split("/")[0]), int(post_date.split("/")[1]), int(post_date.split("/")[2])

    #Get timestamp, datetime and format string date
    date_time = datetime(year = post_year, month = post_month, day = post_day, hour=post_hour, minute=post_minute)
    timestamp = datetime.timestamp(date_time)
    months = ['Jan.','Feb.','Mar.','Apr.','May','June','July','Aug.','Sept.','Oct.','Nov.','Dec.']
    string_timestamp = f"{post_day} {months[post_month-1]} - {post_time}"

    #Check if user is trying to schedule for before current time (in the past and not future)
    current_timestamp = time.time()
    if current_timestamp > timestamp:
        return {"success": False, "message": "You cannot schedule a post in the past, please select a time in the future."}

    #check if there is a post scheduled for 10 minutes before this post (600 seconds)
    high_range = timestamp + 599
    low_range = timestamp - 599
    posts = Post.objects(Q(timestamp__gte = low_range) & Q(timestamp__lt = high_range) & Q(status = "scheduled")).count()
    if posts > 0:
        return {"success": False, "message": "Please schedule posts 10 minutes apart."}


    #if text post
    if data['post_type'] == "text":
        if data['text_account'] == None or data['text_title'] == None or data['text_body'] == None or data['text_date'] == None or data['text_time'] == None or data['text_subreddit'] == None:
            return {"success": False, "message": "All fields must be filled."}

        account = Account.objects(id = data['text_account'])
        if account.count() == 0:
            return {"success": False, "message": "Invalid reddit account."}
        account = account.get()

        text_post_body = ""
        paragraphs = data['text_body'].split("\n")
        for paragraph in paragraphs:
            text_post_body = text_post_body +"<p>"+ paragraph + "</p>"

        post = Post(
            account_id = str(account['id']),
            account_username = account['username'],
            subreddit = data['text_subreddit'],
            post_type = data['post_type'],
            title = data['text_title'],
            body = text_post_body,
            raw_body = data['text_body'],
            timestamp = timestamp,
            string_timestamp = string_timestamp,
            date_time = date_time,
            raw_time = data['text_time'],
            raw_date = data['text_date']
        ).save()

        post = json.loads(post.to_json())
        return {"success": True, "message": "Successfully scheduled post.", "post_details": post}

    #if media post
    elif data['post_type'] == "media":
        #Check required fields
        if data['media_account'] == None or data['media_title'] == None or data['media_date'] == None or data['media_time'] == None or data['media_subreddit'] == None:
            return {"success": False, "message": "All fields must be filled."}
        
        account = Account.objects(id = data['media_account'])
        if account.count() == 0:
            return {"success": False, "message": "Invalid reddit channel."}
        account = account.get()

        #If there is media attached to request upload
        if request.files:
            media_file = request.files['file']
            content_type = media_file.content_type

            #Upload file to imgur
            media_type = "image" if content_type == "image/png" or content_type == "image/jpeg" else "video"
            url = "https://api.imgur.com/3/upload"
            files = [(media_type, media_file)]

            try:
                response = requests.post(url, files = files).json()
            except:
                return {"success": False, "message": "Failed to connect to imgur, try again in a few minutes."}
            if response['success'] == True:
                media_url = response['data']['link']
                if content_type == "video/mp4":
                    time.sleep(5) #sleep for a few seconds (wait for video to process before displaying)
            else:
                if response['data']['error'] == "Internal expectation failed":
                    return {"success": False, "message": "Failed to upload image, try again"}
                else:
                    return {"success": False, "message": response['data']['error']}
        else:
            return {"success": False, "message": "No file was selected."}

        post = Post(
            media_url = media_url,
            account_id = str(account['id']),
            account_username = account['username'],
            subreddit = data['media_subreddit'],
            post_type = data['post_type'],
            title = data['media_title'],
            timestamp = timestamp,
            string_timestamp = string_timestamp,
            date_time = date_time,
            content_type = content_type,
            raw_time = data['media_time'],
            raw_date = data['media_date']
        ).save()

        post = Post.objects(id = post['id']).get()
        post = json.loads(post.to_json())

        return {"success": True, "message": "Successfully scheduled post.", "post_details": post}

@app.route('/remove_post', methods=['POST'])
def remove_post():
    #get post object
    post = Post.objects(id = request.form['post_id']).get()

    #delete from database
    post.delete()

    return {"success": True, "message": "Successfully removed scheduled post."}

@app.route('/edit_post', methods=['POST'])
def edit_post():
    post = Post.objects(id = request.form['post_id']).get()
    post = json.loads(post.to_json())

    accounts = Account.objects()
    accounts = json.loads(accounts.to_json())

    data = {"success": True, "post": post, "accounts": accounts}
    return data

@app.route('/update_post', methods=['POST'])
def update_post():
    #Get data from ajax call
    data = json.loads(request.form['data'])
    data = { k: (None if v == '' else v) for k, v in data.items() }

    #check required fields and return error if any
    if data['post_id'] == None or data['update_title'] == None or data['update_time'] == None or data['update_date'] == None or data['update_subreddit'] == None or data['update_account'] == None:
        return {"success": False, "message": "Please fill in all fields."}

    #Get scheduled post object
    post = Post.objects(id = data['post_id']).get()

    #If time or date are different, generate new date time, timestamp, etc.
    if data['update_date'] != post['raw_date'] or data['update_time'] != post['raw_time']:
        post_time = data['update_time']
        if post_time.split(" ")[1] == "PM":
            hour = int(post_time.split(":")[0])
            post_hour = 12 if hour == 12 else 12 + hour
            post_minute = int(post_time.replace(" PM", "").split(":")[1])
        elif post_time.split(" ")[1] == "AM":
            hour = int(post_time.split(":")[0])
            post_hour = 0 if hour == 12 else hour
            post_minute = int(post_time.replace(" AM", "").split(":")[1])

        post_date = data['update_date']
        post_month, post_day, post_year = int(post_date.split("/")[0]), int(post_date.split("/")[1]), int(post_date.split("/")[2])
        date_time = datetime(year = post_year, month = post_month, day = post_day, hour=post_hour, minute=post_minute)
        timestamp = datetime.timestamp(date_time)
        months = ['Jan.','Feb.','Mar.','Apr.','May','June','July','Aug.','Sept.','Oct.','Nov.','Dec.']
        string_timestamp = f"{post_day} {months[post_month-1]} - {data['update_time']}"

        #check if there is a post scheduled for 10 minutes before this post (600 seconds)
        high_range = timestamp + 599
        low_range = timestamp - 599
        posts = Post.objects(Q(timestamp__gte = low_range) & Q(timestamp__lt = high_range) & Q(status = "scheduled") & Q(id__ne = post['id'])).count()
        if posts > 0:
            return {"success": False, "message": "Please schedule posts 10 minutes apart."}  

        #Check if user is trying to schedule for before current time (in the past and not future)
        current_timestamp = time.time()
        if current_timestamp > timestamp:
            return {"success": False, "message": "You cannot schedule a post in the past, please select a time in the future."}

        #update database with new time
        post.update(timestamp = timestamp, string_timestamp = string_timestamp, date_time = date_time, raw_time = data['update_time'], raw_date = data['update_date'])

    #update title, subreddit, and reddit account
    account_username = Account.objects(id = data['update_account']).get()['username']
    post.update(title = data['update_title'], subreddit = data['update_subreddit'], account_id = data['update_account'], account_username = account_username)

    #if media post check for new media and update media_url
    if post['post_type'] == "media":
        #if there are any media files in request, process and update media_url
        if request.files:
            media_file = request.files['file']
            content_type = media_file.content_type

            #Upload file to imgur
            media_type = "image" if content_type == "image/png" or content_type == "image/jpeg" else "video"
            url = "https://api.imgur.com/3/upload"
            files = [(media_type, media_file)]

            try:
                response = requests.post(url, files = files).json()
            except:
                return {"success": False, "message": "Failed to connect to imgur, try again in a few minutes."}
            if response['success'] == True:
                media_url = response['data']['link']
                if content_type == "video/mp4":
                    time.sleep(5) #sleep for a few seconds (wait for video to process before displaying)
            else:
                if response['data']['error'] == "Internal expectation failed":
                    return {"success": False, "message": "Failed to upload image, try again"}
                else:
                    return {"success": False, "message": response['data']['error']}
        
        #add new media url to database 
        post.update(media_url = media_url, content_type = content_type)

    #else if post type is text render post body and update
    elif post['post_type'] == "text":
        text_post_body = ""
        paragraphs = data['text_post_body'].split("\n")
        for paragraph in paragraphs:
            text_post_body = text_post_body +"<p>"+ paragraph + "</p>"
        post.update(body = text_post_body, raw_body = data['text_post_body'])
    

    #Get post details, return to client
    post = Post.objects(id = data['post_id']).get()
    post = json.loads(post.to_json())
    return {"success": True, "message": "Successfully updated post.", "post_details": post}


if __name__ == "__main__":
    #Set flask secret key
    app.secret_key = 'B[@;\+6>+(BjufcV!c&[yp\]/KzqMcZS^qb6_3D:8yaa+{5,FS'

    #Connect to MongoDB
    DB_URI = [line.rstrip('\n') for line in open('KEYS.txt')][0].split("=")[1].strip()
    connect(db="reddit", host=DB_URI)

    #Start flask app
    app.run(debug=True)