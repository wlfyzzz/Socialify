import requests, json


def VideoInfo(data):
  video_info_list = []

  if "data" in data and "videos" in data["data"]:
    for video in data["data"]["videos"]:
      thumbnail = video.get("cover")
      username = video["author"]["nickname"]
      title = video.get("title")
      play_url = video.get("play")

      video_info = {
          "thumbnail": thumbnail,
          "username": username,
          "title": title,
          "play_url": play_url,
      }
      video_info_list.append(video_info)

  return video_info_list


def getTiktok(username):
  print(f"[Tiktok] Getting Posts by {username}")
  url = "https://tiktok-scraper7.p.rapidapi.com/user/posts"
  querystring = {"unique_id": f"{username}", "count": "25", "cursor": "0"}
  headers = {
      "x-rapidapi-key": "75e6c0e1e2mshd90962ce1a87fcdp17225bjsndffdfda29565",
      "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com",
  }
  response = requests.get(url, headers=headers, params=querystring)
  print(f"[Tiktok] Posts found and returned.")
  open("temp.json", "w").write(json.dumps(VideoInfo(response.json())))


def get_tiktok_data(user_id, cache_duration, database):
  from socialify.utils.file import load_data, save_data

  current_time = time.time()
  data = load_data(database)
  print(f"[TikTok] Checking if {user_id} is cached")
  tiktok_cache = data.get("tiktok", {})

  if user_id in tiktok_cache:
    print(f"[TikTok] Cached Data for {user_id} found!")
    cached_data = tiktok_cache[user_id]
    if current_time - cached_data["timestamp"] < cache_duration:
      return cached_data["data"]
    else:
      print(f"[TikTok] Cached Data for {user_id} expired. Refreshing")

  print(f"[TikTok] No Cached Data for {user_id} found!")
  tiktok_data = getTiktok(user_id)
  if "tiktok" not in data:
    data["tiktok"] = {}

  data["tiktok"][user_id] = {
      "data": tiktok_data,
      "timestamp": current_time,
  }
  save_data(data, database)
  return tiktok_data

