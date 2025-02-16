import requests
import json
import re  # Import the regular expression module


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
                # Extract the JSON string from the HTML response
                html_response = json_data["solution"]["response"]

                # Use a regular expression to find the JSON string within the HTML
                match = re.search(r"<body>(.*?)</body>", html_response)  # Corrected regex

                if match:
                    json_string = match.group(1)  # Extract the captured group (the JSON)
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
