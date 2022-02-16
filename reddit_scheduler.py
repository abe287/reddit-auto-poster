from turtle import pos
import requests
import time
from mongoengine import *
from classes import Account, Post
import datetime as dt
import calendar

#Custom console print
def console_log(message):
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')

    print(f"[{currentDT}] [{message}]")

def check_token(account_id, attempts):
    if attempts == 3:
        console_log("Could not refresh token!")
        return None

    try:
        account = Account.objects(id = account_id).get()
        expiration_ts, ts = account['token_expiration'], time.time()
        if expiration_ts < ts:
            console_log("Token expired, requesting new token")

            request_data = {
                "grant_type": "refresh_token",
                "refresh_token": account['refresh_token']
            }
            
            client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
            response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data = request_data, headers = headers).json()
            epoch = time.time()
            token_expiration = epoch + response['expires_in']

            if response['access_token'] == None:
                console_log("Failed to get token, retrying...")
                time.sleep(5)
                return check_token(account_id, attempts + 1)
            account.update(
                access_token = response['access_token'],
                refresh_token = response['refresh_token'],
                token_expiration = token_expiration
            )
            account = Account.objects(id = account_id).get()
    except:
        console_log("Failed to get token, retrying...")
        time.sleep(5)
        return check_token(account_id, attempts + 1)

    return account['access_token']

def get_posts():
    #Get posts that need to be posted
    current_timestamp = time.time()
    posts = Post.objects(Q(timestamp__lte = current_timestamp) & Q(status = "scheduled"))

    return posts

def submit_media(access_token, media_url, title, subreddit, content_type, attempts):
    if attempts == 4:
        console_log("Could not submit media post!")
        return None

    headers = {'Authorization': f'bearer {access_token}', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

    request_data = {
        "title": title,
        "sr": subreddit,
        "resubmit": True,
        "sendreplies": True
    }

    if content_type == "image/png" or content_type == "image/jpeg":
        request_data["kind"] = "link"
        request_data["url"] = media_url
    elif content_type == "video/mp4":
        request_data["kind"] = "link"
        media_url = media_url[:-3] + "gifv"
        request_data["url"] = media_url
    
    try:
        submit = requests.post("https://oauth.reddit.com/api/submit", headers=headers, data = request_data).json()
    except Exception as e:
        console_log("Failed to send post request, retrying...")
        print(e)
        return submit_media(access_token, media_url, title, subreddit, content_type, attempts + 1)
    
    if "success" in submit:
        return {"success": submit['success']}
    else:
        console_log("Unsuccessful post, retrying...")
        return submit_media(access_token, media_url, title, subreddit, content_type, attempts + 1)


def submit_text(access_token, raw_body, title, subreddit, attempts):
    if attempts == 4:
        console_log("Could not submit text post!")
        return None

    headers = {'Authorization': f'bearer {access_token}', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

    body = raw_body.replace("\n","\n\n")
    
    request_data = {
        "title": title,
        "kind": "self",
        "text": body,
        "sr": subreddit,
        "resubmit": True,
        "sendreplies": True
    }

    try:
        submit = requests.post("https://oauth.reddit.com/api/submit", headers=headers, data = request_data).json()
    except Exception as e:
        console_log("Failed to send post request, retrying...")
        print(e)
        return submit_text(access_token, raw_body, title, subreddit, attempts + 1)

    if submit['success'] == True:
        return {"success": True}
    elif submit['success'] == False:
        console_log("Unsucessful post, retrying...")
        return submit_text(access_token, raw_body, title, subreddit, attempts + 1)
    else:
        console_log("Unsucessful post, retrying...")
        return submit_text(access_token, raw_body, title, subreddit, attempts + 1)


if __name__ == "__main__":
    #Connect to MongoDB
    DB_URI = [line.rstrip('\n') for line in open('KEYS.txt')][0].split("=")[1].strip()
    connect(db="reddit", host=DB_URI)

    #Read Reddit API keys
    CLIENT_ID = [line.rstrip('\n') for line in open('KEYS.txt')][1].split("=")[1].strip()
    CLIENT_SECRET = [line.rstrip('\n') for line in open('KEYS.txt')][2].split("=")[1].strip()

    while True:
        console_log("Checking for posts...")
        posts = get_posts()

        if posts.count() == 0:
            console_log("No posts found")

        for post in posts:
            console_log(f"Attempting to post | POST_ID: {post['id']}")
            access_token = check_token(post['account_id'], 1)
            if access_token != None:
                if post['post_type'] == "media":
                    response = submit_media(access_token, post['media_url'], post['title'], post['subreddit'], post['content_type'], 1)
                else:
                    response = submit_text(access_token, post['raw_body'], post['title'], post['subreddit'], 1)
                
                if response == None:
                    post.update(status = "failed")
        
                elif response['success'] == True:
                    console_log("Successfully submitted post.")
                    post.update(status = "posted")
                    
            else:
                post.update(status = "failed")
        
        #Check again in 10 seconds
        delay = 10
        console_log(f"Checking again in {delay} seconds")
        print()
        time.sleep(delay)