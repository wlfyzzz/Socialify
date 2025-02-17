import asyncio
import json
import logging
import os

from flask import Flask, jsonify

from functions.kick import get_kick_data
from functions.tiktok import get_tiktok_data
from functions.twitch import is_live_twitch
from functions.twitter import get_tweets, get_user_details, save_tweets

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
  print(f"Error occurred with config. {e} is not set, which is required.")
  exit(0)


@app.route("/functions/twitch/<string:user_id>")
async def twitch(user_id):
  return jsonify({
      "live": is_live_twitch(
          user_id, TWITCH_API_KEY, CACHE_DURATION, DATABASE
      )
  })


@app.route("/functions/kick/<string:user_id>")
async def kick(user_id):
  return jsonify(get_kick_data(user_id, CACHE_DURATION, DATABASE))


@app.route("/functions/tiktok/<string:user_id>")
async def tiktok(user_id):
  return jsonify(get_tiktok_data(user_id, CACHE_DURATION, DATABASE))


@app.route("/functions/user/<string:user_id>")
async def user_api(user_id):
  return jsonify(await user(user_id))


async def user(user_id):
  return await get_user_details(user_id, TWITTER_API_KEY)


@app.route("/functions/twitter/<string:user_id>")
async def twitter_api(user_id):
  if not user_id.isdigit():
    info = await user(user_id)
    if info.get("detail", None) != None:
      return {}
    user_id = info["user_id"]
  tweets = await get_tweets(user_id, USERNAME, PASSWORD)
  if tweets:
    new_tweets = save_tweets(user_id, tweets, DATABASE)
    return jsonify(new_tweets)
  else:
    return jsonify({"error": "Failed to retrieve tweets"}), 500


@app.route("/")
async def home():
  return jsonify({
      "status": True,
      "message": "If you see this page, your Socialify backend is online!",
      "copyright": "2025 wlfyzz",
  })


os.system("clear" if os.name == "posix" else "cls")
print(open(".art", "r").read())
print(
    "Welcome to Socialify. An Open source alternative of pingcord.gg for discord."
    " © wlfyzz.dev 2025"
)
if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
