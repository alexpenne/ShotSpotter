import requests
import json
import time
import streamlit as st

headers = {"Authorization": f"Token {st.secrets['MUCKROCK_API_TOKEN']}"}
agency_cache_file = "agency_cache.json"

def fetch_all_agencies():
    
    i = 1
    
    agencies = {}

    while i < 284:
        url = f"https://www.muckrock.com/api_v2/agencies/?page={str(i)}&page_size=100"
        print(url)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error {response.status_code}, retrying in 1 minute...")
            time.sleep(60)
            continue
        
        data = response.json()

        for a in data["results"]:
            agencies[a["id"]] = {
                "name": a["name"],
                "jurisdiction_id": a["jurisdiction"],
                "slug": a["slug"]
            }
        
        print(f"Fetched {len(agencies)} agencies")

        
        time.sleep(5)

        if len(agencies) % 1000 == 0:
            with open(agency_cache_file, "w") as f:
                json.dump(agencies, f, indent=2)

        i = i + 1
    
    return agencies

def save_cache():
    agencies = fetch_all_agencies()
    with open(agency_cache_file, "w") as f:
        json.dump(agencies, f, indent=2)

    print("Agency cache saved")

if __name__ == "__main__":
    save_cache()