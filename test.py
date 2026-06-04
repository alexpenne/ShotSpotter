import requests
import os

API_TOKEN = os.getenv("MUCKROCK_API_TOKEN")
headers = {"Authorization": f"Token {API_TOKEN}"}

def get_jurisdiction(jurisdiction_id, headers):
    response = requests.get(f"https://www.muckrock.com/api_v1/jurisdiction/{jurisdiction_id}/", headers=headers)
    print(f"Status: {response.status_code}, ID: {jurisdiction_id}")
    print(response.text[:200])
    return response.json().get('name')

get_jurisdiction