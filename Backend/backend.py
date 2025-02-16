import asyncio
import json
import logging
import os
import time
import requests

from kick import getKick
from tiktok import getTiktok
from flask import Flask, jsonify
from twikit import Client

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

with open("config.json", "r") as f:
  config = json.load(f)
try:
  DATABASE = config["DATABASE"]
  CACHE_DURATION = config["CACHE_DURATION"]
  USERNAME = config["USERNAME"]
  PASSWORD = config["PASSWORD"]
  TWITCH_API_KEY = config["TWITCH_API_KEY"]
  TWITTER_API_KEY = config["TWITTER_API_KEY"]
except KeyError as e:
  print(open(".art", "r").read())
  print(f"Error occured with config. {e} is not set. which is required.")
  exit(0)


def load_data():
  if os.path.exists(DATABASE):
    with open(DATABASE, "r") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  else:
    return {}


def get_twitch_title(username):
  url = f"https://gwyo-twitch.p.rapidapi.com/title/{username}"
  headers = {
      "x-rapidapi-key": TWITCH_API_KEY,
      "x-rapidapi-host": "gwyo-twitch.p.rapidapi.com",
  }
  print(f"[Twitch] Getting title for {username}")
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    return response.json().get("title", "Unknown Title")
  return "Unknown Title"


def isLiveTwitch(username):
  current_time = time.time()
  data = load_data()
  print(f"[Twitch] Checking if {username} is live")
  TWITCH_CACHE = data["twitch"]
  if username in TWITCH_CACHE:
    print(f"[Twitch] Cached Data for {username} found!")
    cached_data = TWITCH_CACHE[username]
    if current_time - cached_data["timestamp"] < CACHE_DURATION:
      return cached_data
    else:
      print(f"[Twitch] Cached Data for {username} expired. Refreshing")
  print(f"[Twitch] No Cached Data for {username} found!")
  url = f"https://gwyo-twitch.p.rapidapi.com/viewers/{username}"
  headers = {
      "x-rapidapi-key": TWITCH_API_KEY,
      "x-rapidapi-host": "gwyo-twitch.p.rapidapi.com",
  }
  response = requests.get(url, headers=headers)
  url = f"https://gwyo-twitch.p.rapidapi.com/preview/{username}/350/200"

  headers = {"x-rapidapi-key":"75e6c0e1e2mshd90962ce1a87fcdp17225bjsndffdfda29565","x-rapidapi-host": "gwyo-twitch.p.rapidapi.com"}
  if response.status_code == 200 and response.json() != {}:
    data[username] = response.json()

    live_status = bool(data[username])
    print(response.json(), live_status)
    res = requests.get(url, headers=headers)
    preview = res.json()['preview_url']
    title = get_twitch_title(username) if live_status else None

    data["twitch"][username] = {
        "live": live_status,
        "title": title,
        "timestamp": current_time,
        "username": username,
        "preview": preview
    }
    save_data(data)
    data = {
        "live": live_status,
        "title": title,
        "timestamp": current_time,
        "username": username,
        "preview": preview
    }
    return data

  return {"live": {}}


def save_data(data):
  with open(DATABASE, "w") as f:
    json.dump(data, f, indent=4)


data = load_data()


@app.route("/twitch/<string:userId>")
async def twitch(userId):
  return jsonify({"live": isLiveTwitch(userId)})


@app.route("/kick/<string:userId>")
async def kick(userId):
  current_time = time.time()
  data = load_data()
  print(f"[Kick] Checking if {userId} is cached")
  KICK_CACHE = data.get("kick", {})  # Ensure "kick" key exists
  if userId in KICK_CACHE:
    print(f"[Kick] Cached Data for {userId} found!")
    cached_data = KICK_CACHE[userId]
    if current_time - cached_data["timestamp"] < CACHE_DURATION:
      return jsonify({"user": cached_data["user"], "live": cached_data["user"]['livestream']})
    else:
      print(f"[Kick] Cached Data for {userId} expired. Refreshing")

  print(f"[Kick] No Cached Data for {userId} found!")
  kickData = getKick(userId)

  # Ensure "kick" key exists before assigning to it
  if "kick" not in data:
    data["kick"] = {}

  data["kick"][userId] = {
      "user": kickData,
      "timestamp": current_time,
  }
  save_data(data)
  return jsonify({"user": kickData, "live": kickData['livestream']})


@app.route("/tiktok/<string:userId>")
async def tiktok(userId):
  current_time = time.time()
  data = load_data()
  print(f"[TikTok] Checking if {userId} is cached")
  TIKTOK_CACHE = data.get("tiktok", {})  # Ensure "tiktok" key exists
  if userId in TIKTOK_CACHE:
    print(f"[TikTok] Cached Data for {userId} found!")
    cached_data = TIKTOK_CACHE[userId]
    if current_time - cached_data["timestamp"] < CACHE_DURATION:
      return jsonify(cached_data["data"])
    else:
      print(f"[TikTok] Cached Data for {userId} expired. Refreshing")

  print(f"[TikTok] No Cached Data for {userId} found!")
  tiktok_data = getTiktok(userId)
  # Ensure "tiktok" key exists before assigning to it
  if "tiktok" not in data:
    data["tiktok"] = {}

  data["tiktok"][userId] = {
      "data": tiktok_data,
      "timestamp": current_time,
  }
  save_data(data)
  return jsonify(tiktok_data)


@app.route("/user/<string:userId>")
async def userapi(userId):
  return jsonify(await user(userId))


async def user(userId):
  print(f"[Twitter] Getting user with username {userId}")
  url = "https://twitter154.p.rapidapi.com/user/details"
  payload = {"username": userId}
  headers = {
      "x-rapidapi-key": TWITTER_API_KEY,
      "x-rapidapi-host": "twitter154.p.rapidapi.com",
      "Content-Type": "application/json",
  }

  response = requests.post(url, json=payload, headers=headers)

  return response.json()


async def get_tweets(user_id):
  try:
    print(f"[Twitter] Getting tweets for user {user_id}")
    client = Client("en-US")
    await client.login(
        auth_info_1=USERNAME, password=PASSWORD, cookies_file="cookies.json"
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
      },
      "media": media_data,
  }


def save_tweets(user_id, tweets):
  global data

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

  save_data(data)
  return jsonify({"new_tweets": new_tweets, "existing_tweets": existing_tweets})


@app.route("/")
async def home():
  return jsonify({
      "status": True,
      "message": "If you see this page. your Socialify backend is online!",
      "copyright": "2025 wlfyzz"
  })


@app.route("/twitter/<string:user_id>")
async def twitter_api(user_id):
  if not user_id.isdigit():
    info = await user(user_id)
    if info.get("detail", None) != None:
        return {}
    user_id = info["user_id"]
  tweets = await get_tweets(user_id)
  if tweets:
    new_tweets = save_tweets(user_id, tweets)
    return new_tweets
  else:
    return jsonify({"error": "Failed to retrieve tweets"}), 500


os.system("clear" if os.name == "posix" else "cls")
print(open(".art", "r").read())
print(
    "Welcome to Socialify. An Open source alternative of pingcord.gg for discord."
    " © wlfyzz.dev 2025"
)
if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)

