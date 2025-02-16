import requests
import json
import re


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
