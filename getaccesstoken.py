import requests
import json

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def update_tokens(file_path, access_token, refresh_token):
    with open(file_path, 'r') as f:
        config = json.load(f)
    # Update access_token and refreshToken
    config["access_token"] = access_token
    config["refreshToken"] = refresh_token
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

config_file_path = 'config.json'
config = load_config(config_file_path)

url = "https://services.leadconnectorhq.com/oauth/token"

payload = {
    "client_id": config["clientId"],
    "client_secret": config["clientSecret"],
    "grant_type": "refresh_token",
    "refresh_token": config["refreshToken"],
    "user_type": config["userType"],
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "Authorization": "Bearer 123"
}

response = requests.post(url, data=payload, headers=headers)

if response.status_code == 200:
    json_data = response.json()
    new_access_token = json_data.get("access_token")
    new_refresh_token = json_data.get("refresh_token")
    update_tokens(config_file_path, new_access_token, new_refresh_token)
else:
    print(f"Request failed with status code {response.status_code}")
