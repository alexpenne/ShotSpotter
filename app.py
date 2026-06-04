import streamlit as st
import requests
import pandas as pd 
from io import BytesIO
import time 
import plotly.graph_objects as go

headers = {"Authorization": f"Token {st.secrets['MUCKROCK_API_TOKEN']}"}

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

search_term = st.text_input("Search term", placeholder="e.g. Shotspotter, facial recognition")
if st.button("Search") and search_term:
    with st.spinner(f"Searching for '{search_term}'..."):
        results = fetch_requests(search_term)

    if not results:
        st.warning("No results found.")
    else:
        

        df = pd.DataFrame(results)
        
        df = df[['id', 'title', 'status', 'datetime_submitted', 'datetime_done', 'requested_docs']]

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
        st.subheader("All Requests")
        st.dataframe(df)

        # Excel download
        st.download_button(
            label="Download as Excel",
            data=to_excel(df),
            file_name=f"{search_term}_foia_requests.xlsx",
            mime="application/vnd.ms-excel"
        )
