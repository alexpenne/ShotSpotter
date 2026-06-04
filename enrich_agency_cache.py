import json

with open("agency_cache.json", "r") as f:
    agencies = json.load(f)

with open("jurisdiction_cache.json") as f:
    jurisdictions = json.load(f)

jurisdiction_lookup = {
    int(k): {
        "name": v["name"],
        "slug": v.get("slug")
    }
    for k, v in jurisdictions.items()
}

print(jurisdiction_lookup)

merged = {}

for agency_id_str, agency_data in agencies.items():

    agency_id = int(agency_id_str)
    j_id = agency_data.get("jurisdiction_id", "Unknown")
    if j_id is not None:
        j_id = int(j_id)
    
    j_info = jurisdiction_lookup.get(j_id, {})
    j_name = j_info.get("name", "Unknown")
    j_slug = j_info.get("slug", None)
    
    merged[agency_id_str] = {
        "name": agency_data.get("name"),
        "jurisdiction_id": j_id,
        "jurisdiction_name": j_name,
        "agency_slug": agency_data.get("slug"),
        "jurisdiction_slug": j_slug
    }

with open("agency_enriched.json", "w") as f:
    json.dump(merged, f, indent=2)

print("agency_enriched.json created successfully.")