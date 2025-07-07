import requests
import os
from dotenv import load_dotenv

load_dotenv()

token_url = "http://127.0.0.1:8000/o/token/"

client_id = os.getenv("OAUTH_CLIENT_ID")
client_secret = os.getenv("OAUTH_CLIENT_SECRET")
username = os.getenv("OAUTH_USERNAME")
password = os.getenv("OAUTH_PASSWORD")

data = {
    "grant_type": "password",
    "username": username,
    "password": password,
    "client_id": client_id,
    "client_secret": client_secret,
}

response = requests.post(token_url, data=data)

if response.status_code == 200:
    token_data = response.json()
    print("✅ Access token retrieved successfully!")
    print("Access Token:", token_data["access_token"])
    print("Refresh Token:", token_data["refresh_token"])
    print("Expires In:", token_data["expires_in"], "seconds")
else:
    print("❌ Failed to get token")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
