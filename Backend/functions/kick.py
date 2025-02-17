import requests
import json
import re
from flask import jsonify


def getKick(username):
  print(f"[Kick] Fetching info for {username}")
  url = "http://localhost:8191/v1"
  headers = {"Content-Type": "application/json"}
  data = {
      "cmd": "request.get",
      "url": f"https://kick.com/api/v2/channels/{username}",
      "maxTimeout": 60000,
  }
  try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    try:
      json_data = response.json()
      if json_data.get("status") == "ok":
        html_response = json_data["solution"]["response"]
        match = re.search(r"<body>(.*?)</body>", html_response)

        if match:
          json_string = match.group(1)
          try:
            extracted_data = json.loads(json_string)
            print("[Kick] Got data for user")
            return extracted_data
          except json.JSONDecodeError as e:
            print(f"[Kick] Error decoding extracted JSON: {e}")
        else:
          return {"error": "Invalid user or user does not exist on kick api."}
      else:
        return []
    except json.JSONDecodeError as e:
      return []

  except requests.exceptions.RequestException as e:
    return []


def get_kick_data(user_id, cache_duration, database):
  from socialify.utils.file import load_data, save_data

  current_time = time.time()
  data = load_data(database)
  print(f"[Kick] Checking if {user_id} is cached")
  kick_cache = data.get("kick", {})

  if user_id in kick_cache:
    print(f"[Kick] Cached Data for {user_id} found!")
    cached_data = kick_cache[user_id]
    if current_time - cached_data["timestamp"] < cache_duration:
      return {
          "user": cached_data["user"],
          "live": cached_data["user"]["livestream"],
      }
    else:
      print(f"[Kick] Cached Data for {user_id} expired. Refreshing")

  print(f"[Kick] No Cached Data for {user_id} found!")
  kick_data = getKick(user_id)

  if "kick" not in data:
    data["kick"] = {}

  data["kick"][user_id] = {
      "user": kick_data,
      "timestamp": current_time,
  }
  save_data(data, database)
  return {"user": kick_data, "live": kick_data["livestream"]}


if __name__ == "__main__":
  kick_username = "iceposeidon"
  cache_duration = 60
  database_file = "data.json"

  kick_data = get_kick_data(kick_username, cache_duration, database_file)
  print(kick_data)
