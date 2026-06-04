import requests
import json
import time
import streamlit as st

headers = {"Authorization": f"Token {st.secrets['MUCKROCK_API_TOKEN']}"}
cache_file = "jurisdictions_cache3.json"



def fetch_all_jurisdictions():
    url = "https://www.muckrock.com/api_v1/jurisdiction/?page=121&page_size=100"
    jurisdictions = {}

    while url:
        response = safe_request(url, headers)
        data = response.json()

        for j in data["results"]:
            jurisdictions[j["id"]] = j["name"]

        print(f"Fetched {len(jurisdictions)} so far...")
        url = data["next"]

        if len(jurisdictions) % 1000 == 0:
            with open(cache_file, "w") as f:
                json.dump(jurisdictions, f, indent=2)

        time.sleep(5)

    return jurisdictions

def safe_request(url, headers):
    while True:
        response = requests.get(url, headers)

        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited. Sleeping {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            print(f"Error {response.status_code}. Retrying in 5 seconds...")
            time.sleep(5)

def save_cache():
    jurisdictions = fetch_all_jurisdictions()
    with open(cache_file, "w") as f:
        json.dump(jurisdictions, f, indent=2)

    print(f"Saved {len(jurisdictions)} jurisdictions to {cache_file}")

if __name__ == "__main__":
    save_cache()

