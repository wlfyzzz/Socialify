import requests
from flask import jsonify
from twikit import Client


async def get_user_details(username, twitter_api_key):
  print(f"[Twitter] Getting user with username {username}")
  url = "https://twitter154.p.rapidapi.com/user/details"
  payload = {"username": username}
  headers = {
      "x-rapidapi-key": twitter_api_key,
      "x-rapidapi-host": "twitter154.p.rapidapi.com",
      "Content-Type": "application/json",
  }

  response = requests.post(url, json=payload, headers=headers)

  return response.json()


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
      },
      "media": media_data,
  }


def save_tweets(user_id, tweets, database):
  from socialify.utils.file import load_data, save_data

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


if __name__ == "__main__":
  import asyncio

  async def main():
    twitter_username = "elonmusk"
    twitter_api_key = "YOUR_TWITTER_API_KEY"
    twitter_password = "YOUR_TWITTER_PASSWORD"
    database_file = "data.json"

    user_details = await get_user_details(twitter_username, twitter_api_key)
    if user_details and "user_id" in user_details:
      user_id = user_details["user_id"]
      tweets = await get_tweets(user_id, twitter_username, twitter_password)
      if tweets:
        saved_tweets = save_tweets(user_id, tweets, database_file)
        print(saved_tweets)
      else:
        print("Failed to retrieve tweets.")
    else:
      print("Failed to retrieve user details.")

  asyncio.run(main())
