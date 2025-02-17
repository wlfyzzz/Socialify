import requests
from flask import jsonify
from twikit import Client
import twikit


async def get_user_details(user, username, password):
  client = Client("en-US")
  await client.login(auth_info_1=username, password=password, cookies_file="cookies.json")
  try:
    user = await client.get_user_by_screen_name(user)
  except twikit.errors.UserUnavailable:
    return {"detail": "User suspended"}
  if user:
    return {"user_id": user.id}


async def get_tweets(user_id, username, password):
  try:
    print(f"[Twitter] Getting tweets for user {user_id}")
    client = Client("en-US")
    await client.login(
        auth_info_1=username, password=password, cookies_file="cookies.json"
    )
    tweets = await client.get_user_tweets(user_id, "Tweets")
    return tweets
  except Exception as e:
    print(f"Error fetching tweets: {e}")
    return None


def process_tweet(tweet):
  media_data = {}
  if tweet.media:
    for i, media in enumerate(tweet.media):
      media_data[i] = {
          "type": type(media).__name__,
          "id": media.id if hasattr(media, "id") else None,
          "url": media.url if hasattr(media, "url") else None,
      }

  return {
      "content": tweet.text,
      "id": tweet.id,
      "created-at": tweet.created_at,
      "url": f"https://x.com/{tweet.user.name}/status/{tweet.id}",
      "user": {
          "name": tweet.user.name,
          "url": tweet.user.url,
          "followers": tweet.user.followers_count,
          "avatar": tweet.user.profile_image_url
      },
      "media": media_data,
  }


def save_tweets(user_id, tweets, database):
  from utils.file import load_data, save_data

  data = load_data(database)

  if user_id not in data:
    data[user_id] = []

  new_tweets = []
  existing_tweets = data[user_id]
  existing_tweet_ids = {tweet["id"] for tweet in existing_tweets}

  for tweet in tweets:
    if tweet.id not in existing_tweet_ids:
      processed_tweet = process_tweet(tweet)
      data[user_id].append(processed_tweet)
      new_tweets.append(processed_tweet)

  save_data(data, database)
  return {"new_tweets": new_tweets, "existing_tweets": existing_tweets}


