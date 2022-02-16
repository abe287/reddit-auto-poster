## Description
This is a flask web app that lets you schedule posts for Reddit. You can schedule both text and media posts (images and videos). Media posts are uploaded to Imgur using their public API, these images and videos are not publicly visible on the Imgur website and are only visible to people on reddit or people with the media link. It uses MongoDB to store the post information and submits the posts using the official Reddit API. 

## Setup
#### Part 1
You will first need to get your reddit API keys, you will have to setup your very own reddit app to get these keys. Please go to the link down below and click on create app at the bottom of the page.
https://www.reddit.com/prefs/apps/
Fill in the fields like shown in the image below. The name and description can be whatever you want, but make sure to select web app and set the redirect uri to http://127.0.0.1:5000/reddit_response
![alt text](https://i.ibb.co/qYKvfCt/make-app.png)
Once you create your reddit app you should see the application on the same page along with your client id and client secret keys. Look at the image below for reference
![alt text](https://i.ibb.co/9g2ryDz/key-location.png)
Once you get your keys copy them into the KEYS.txt file.
#### Part 2
Install all the required packages by using the following command
```
pip install -r requirements.txt
```
This application uses MongoDB as it's database, so you will need to create one and save the connection string to the KEYS.txt file as well.

## Usage
To run the main flask application you will need to run app.py
```
python app.py
```
Navigate to http://127.0.0.1:5000/ Follow the on screen instructions to get started. You will have to link your reddit account(s) by going to http://127.0.0.1:5000/accounts After that you can schedule posts on the main page

You will also need to run the custom scheduler
```
python reddit_scheduler.py
```
This will check the database every 10 seconds to see if any posts need to be uploaded to reddit.
