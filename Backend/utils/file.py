import json
import os


def load_data(database):
  if os.path.exists(database):
    with open(database, "r") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  else:
    return {}


def save_data(data, database):
  with open(database, "w") as f:
    json.dump(data, f, indent=4)
