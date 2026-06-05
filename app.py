import streamlit as st
import requests
import pandas as pd 
from io import BytesIO
import time 
import plotly.graph_objects as go
import json

headers = {"Authorization": f"Token {st.secrets['MUCKROCK_API_TOKEN']}"}

def load_agency_lookup():
    with open("agency_enriched.json", "r") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}

def fetch_requests(search_time):
    all_requests = []
    url = f"https://www.muckrock.com/api_v2/requests/?search={search_term}&page_size=100"

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200 or not response.text.strip():
            time.sleep(5)
            continue
        data = response.json()
        all_requests.extend(data['results'])
        url = data['next']

    return all_requests


def to_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()

st.title("FOIA Request Explorer")
st.write("Search MuckRock's database of public records requests.")
st.write("Made for Chicago Justice Project. Questions or suggestions? Email alex.penne@us.dlapiper.com.")

search_term = st.text_input("Search term", placeholder="e.g. Shotspotter, facial recognition")
if st.button("Search") and search_term:
    with st.spinner(f"Searching for '{search_term}'..."):
        results = fetch_requests(search_term)

    if not results:
        st.warning("No results found.")
    else:
        

        df = pd.DataFrame(results)
        
        
        
        agency_lookup = load_agency_lookup()
        
        df["agency_name"] = df["agency"].map(
            lambda x: agency_lookup.get(x, {}).get("name", "Unknown")
        )

        df["jurisdiction"] = df["agency"].map(
            lambda x: agency_lookup.get(x, {}).get("jurisdiction_name", "Unknown")
        )

        

        

        st.subheader(f"Found {len(results)} requests")

        # Status breakdown
        st.subheader("Status Breakdown")

        status_groups = {
            "Completed": df['status'].isin(['done', 'partial']).sum(),
            "Rejected": df['status'].isin(['rejected']).sum(),
            "Awaiting Response": df['status'].isin(['ack', 'processed']).sum(),
            "No Documents Found": df['status'].isin(['no_docs']).sum()
        }

        colors = {
            "Completed": "#2ecc71",       # green
            "Rejected": "#e74c3c",        # red
            "Awaiting Response": "#f1c40f", # yellow
            "No Documents Found": "#95a5a6" # gray
        }

        fig = go.Figure([go.Bar(
            x=list(status_groups.keys()),
            y=list(status_groups.values()),
            marker_color=[colors[k] for k in status_groups.keys()]
        )])

        fig.update_layout(yaxis_title="Number of Requests")
        st.plotly_chart(fig)

        # Success rate
        success = df['status'].isin(['done', 'partial']).sum()
        rate = round((success / len(df)) * 100, 1)
        st.metric("Success Rate (docs received)", f"{rate}%")



        # Results table

        # Rename Statuses

        status_map = {
            "done": "Completed",
            "partial": "Partially Completed",
            "rejected": "Rejected",
            "ack": "Awaiting Acknowledgment",
            "processed": "Awaiting Response",
            "no_docs": "No Documents Found"
        }

        df["status"] = df["status"].map(status_map)

        # Change Times
        df["datetime_submitted"] = pd.to_datetime(df["datetime_submitted"], format="ISO8601", errors="coerce", utc=True)
        df["datetime_done"] = pd.to_datetime(df["datetime_done"], format="ISO8601", errors="coerce", utc=True)

        df["days_to_completion"] = (df["datetime_done"] - df["datetime_submitted"]).dt.days
        df["days_to_completion"] = df["days_to_completion"].fillna("Pending")
        df["days_to_completion"] = df["days_to_completion"].apply(
            lambda x: int(x) if pd.notnull(x) and x != "Pending" else x
        )

        
        df["datetime_submitted"] = df["datetime_submitted"].dt.strftime("%m/%d/%Y")
        df["datetime_done"] = df["datetime_done"].dt.strftime("%m/%d/%Y")
        df["datetime_done"] = df["datetime_done"].fillna("Pending")

        df["agency_path"] = df["agency"].map(
            lambda x: f"{agency_lookup.get(int(x), {}).get('jurisdiction_slug')}-{agency_lookup.get(int(x), {}).get('jurisdiction_id')}"
        )

        df["request_path"] = df["slug"] + "-" + df["id"].astype(str)

        df["request_URL"] = df.apply(
            lambda row: f"https://www.muckrock.com/foi/{row['agency_path']}/{row['request_path']}/",
            axis=1
        )

        df = df[['id', 'title', 'jurisdiction', 'agency_name', 'status', 'datetime_submitted', 'datetime_done', 'days_to_completion', 'requested_docs', 'request_URL']]

        # Rename Columns
        df = df.rename(columns={
            "id":"ID",
            "title": "Title",
            "agency_name": "Agency Name",
            "jurisdiction": "Jurisdiction",
            "status": "Status",
            "datetime_submitted": "Date Submitted",
            "datetime_done": "Date Completed",
            "requested_docs": "Documents Requested",
            "days_to_completion": "Days to Completion",
            "request_URL": "Link to Request"

        })
        st.subheader("All Requests")

        st.download_button(
            label="Download as Excel",
            data=to_excel(df),
            file_name=f"{search_term}_foia_requests.xlsx",
            mime="application/vnd.ms-excel"
        )

        
        
        st.dataframe(
            df,
            column_config={
                "Link to Request": st.column_config.LinkColumn(
                    label="View Request",
                    display_text="View Request"
                )
            },
            hide_index=True
        )


        # Excel download
        
