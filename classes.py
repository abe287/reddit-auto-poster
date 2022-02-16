from mongoengine import *

class Account(Document):
    username = StringField()
    access_token = StringField()
    refresh_token = StringField()
    token_expiration = FloatField()

    meta = {
        "indexes": ["username"]
    }

class Post(Document):
    account_id = StringField()
    account_username = StringField()
    subreddit = StringField()
    post_type = StringField()
    title = StringField()
    raw_body = StringField()
    body = StringField()
    timestamp = FloatField()
    string_timestamp = StringField()
    date_time = DateTimeField()
    media_url = StringField(default = None)
    content_type = StringField(default = None)
    raw_date = StringField(default = None)
    raw_time = StringField(default = None)
    status = StringField(default = "scheduled")

    meta = {
        "indexes": ["timestamp", "account_id", "status"]
    }