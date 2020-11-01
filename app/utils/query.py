import tweepy
from dotenv import load_dotenv
import os

load_dotenv()

auth = tweepy.OAuthHandler(os.environ.get("consumer_key"), os.environ.get("consumer_secret"))
auth.set_access_token(os.environ.get("access_token"), os.environ.get("access_token_secret"))

api = tweepy.API(auth)

"""
Uses tweepy to get information about the twitter user
"""

def getTwitterInfo(username):
    return api.get_user(screen_name=username)

def getTwitterTimeline(username):
    return api.user_timeline(screen_name=username)