import requests
import json
import time
import streamlit as st

headers = {"Authorization": f"Token {st.secrets['MUCKROCK_API_TOKEN']}"}
jurisdiction_cache_file = "jurisdiction_cache.json"

def fetch_all_jurisdictions():
    
    i = 1
    
    jurisdictions = {}

    while i < 321:
        url = f"https://www.muckrock.com/api_v2/jurisdictions/?page={str(i)}&page_size=100"
        print(url)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error {response.status_code}, retrying in 1 minute...")
            time.sleep(60)
            continue
        
        data = response.json()

        for a in data["results"]:
            jurisdictions[a["id"]] = {
                "name": a["name"],
                "slug": a["slug"]
            }
        
        print(f"Fetched {len(jurisdictions)} jurisdictions")

        
        time.sleep(5)

        if len(jurisdictions) % 1000 == 0:
            with open(jurisdiction_cache_file, "w") as f:
                json.dump(jurisdictions, f, indent=2)

        i = i + 1
    
    return jurisdictions

def save_cache():
    jurisdictions = fetch_all_jurisdictions()
    with open(jurisdiction_cache_file, "w") as f:
        json.dump(jurisdictions, f, indent=2)

    print("Jurisdictions cache saved")

if __name__ == "__main__":
    save_cache()