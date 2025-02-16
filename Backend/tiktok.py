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


    return video_info_list
def getTiktok(username):
  print(f"[Tiktok] Getting Posts by {username}")
  url = "https://tiktok-scraper7.p.rapidapi.com/user/posts"
  querystring = {"unique_id":f"{username}","count":"25","cursor":"0"}
  headers = {"x-rapidapi-key": "75e6c0e1e2mshd90962ce1a87fcdp17225bjsndffdfda29565","x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"}
  response = requests.get(url, headers=headers, params=querystring)
  print(f"[Tiktok] Posts found and returned.")
  open("temp.json","w").write(json.dumps(VideoInfo(response.json())))