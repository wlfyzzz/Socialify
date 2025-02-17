import time
import requests
from flask import jsonify


def get_twitch_title(username, twitch_api_key):
  url = f"https://gwyo-twitch.p.rapidapi.com/title/{username}"
  headers = {
      "x-rapidapi-key": twitch_api_key,
      "x-rapidapi-host": "gwyo-twitch.p.rapidapi.com",
  }
  print(f"[Twitch] Getting title for {username}")
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    return response.json().get("title", "Unknown Title")
  return "Unknown Title"


def is_live_twitch(username, twitch_api_key, cache_duration, database):
  from socialify.utils.file import load_data, save_data

  current_time = time.time()
  data = load_data(database)
  print(f"[Twitch] Checking if {username} is live")
  twitch_cache = data.get("twitch", {})

  if username in twitch_cache:
    print(f"[Twitch] Cached Data for {username} found!")
    cached_data = twitch_cache[username]
    if current_time - cached_data["timestamp"] < cache_duration:
      return cached_data
    else:
      print(f"[Twitch] Cached Data for {username} expired. Refreshing")

  print(f"[Twitch] No Cached Data for {username} found!")
  url = f"https://gwyo-twitch.p.rapidapi.com/viewers/{username}"
  headers = {
      "x-rapidapi-key": twitch_api_key,
      "x-rapidapi-host": "gwyo-twitch.p.rapidapi.com",
  }
  response = requests.get(url, headers=headers)

  url = f"https://gwyo-twitch.p.rapidapi.com/preview/{username}/350/200"
  headers = {
      "x-rapidapi-key": twitch_api_key,
      "x-rapidapi-host": "gwyo-twitch.p.rapidapi.com",
  }
  res = requests.get(url, headers=headers)

  if response.status_code == 200 and response.json() != {}:
    live_status = bool(response.json())
    print(response.json(), live_status)
    preview = res.json()["preview_url"]
    title = get_twitch_title(username, twitch_api_key) if live_status else None

    if "twitch" not in data:
      data["twitch"] = {}

    data["twitch"][username] = {
        "live": live_status,
        "title": title,
        "timestamp": current_time,
        "username": username,
        "preview": preview,
    }
    save_data(data, database)
    data = {
        "live": live_status,
        "title": title,
        "timestamp": current_time,
        "username": username,
        "preview": preview,
    }
    return data

  return {"live": {}}


