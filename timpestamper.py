import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from streamlit_local_storage import LocalStorage

# --- Configuration & Persistence ---
st.set_page_config(page_title="Service Evaluator", layout="centered")
local_storage = LocalStorage()

# Load data from iPhone's browser cache if session was interrupted
if 'logs' not in st.session_state:
    stored_data = local_storage.get("eval_logs")
    st.session_state.logs = stored_data if stored_data else []

def add_log(category, action):
    # Local Time Adjustment (-4 UTC)
    local_tz = pytz.timezone('America/Aruba') 
    now_local = datetime.now(pytz.utc).astimezone(local_tz)
    timestamp_str = now_local.strftime("%I:%M:%S %p")
    
    entry = {
        "Timestamp": timestamp_str,
        "Category": category,
        "Action": action
    }
    
    st.session_state.logs.append(entry)
    # Save to local storage immediately so data isn't lost on sleep/refresh
    local_storage.set("eval_logs", st.session_state.logs)

st.title("📋 Service Evaluation Log")

# --- Categories from Screenshots ---

# Management (Ref: Screenshot 2026-05-13 at 7.07.42 PM.png)
with st.expander("👤 Management", expanded=False):
    mgt_actions = ["Interacted with Bar", "Engaged at Door/Floor", "Table Contact", "Satisfaction Check", "Complaint Follow-up"]
    for act in mgt_actions:
        if st.button(act, use_container_width=True):
            add_log("Management", act)

# Service Quality (Ref: Screenshot 2026-05-13 at 7.07.24 PM.png)
with st.expander("🤝 Service Details", expanded=False):
    srv_actions = ["Dessert within 12m", "Check on Dessert", "Check within 2m", "Leftover Wrap Offered", "Thanked w/ Eye Contact", "Busser 'May I?' Request"]
    for act in srv_actions:
        if st.button(act, use_container_width=True):
            add_log("Service", act)

# Table Setting (Ref: Screenshot 2026-05-13 at 7.07.32 PM.png)
with st.expander("🍽️ Table & Glassware", expanded=False):
    tbl_actions = ["Cocktail Offered", "Coffee/Digestif Offered", "Automatic Refill", "Silverware Polished", "Settings Neat", "Glassware Clean"]
    for act in tbl_actions:
        if st.button(act, use_container_width=True):
            add_log("Table Setting", act)

# Kitchen & Food (Ref: Screenshot 2026-05-13 at 7.08.09 PM.png)
with st.expander("🍳 Kitchen & Food", expanded=False):
    kit_actions = ["Visually Appealing", "Beverage Proper", "Correct Temp", "Prepared as Requested", "Exceptional Flavor", "Fresh Ingredients"]
    for act in kit_actions:
        if st.button(act, use_container_width=True):
            add_log("Kitchen", act)

# Facility (Ref: Screenshot 2026-05-13 at 7.08.24 PM.png)
with st.expander("🏢 Facility Condition", expanded=False):
    fac_actions = ["Sidewalk Maintained", "Entry Lit", "Windows Clean", "Podium Organized", "Linens Clean", "Lighting Appropriate"]
    for act in fac_actions:
        if st.button(act, use_container_width=True):
            add_log("Facility", act)

# Restroom (Ref: Screenshot 2026-05-13 at 7.08.16 PM.png)
with st.expander("🚽 Restroom", expanded=False):
    if st.button("Restroom Visit Start", use_container_width=True):
        add_log("Restroom", "Visit Start")
    rest_actions = ["Fully Supplied", "Neat/Odor Free", "Waste Not Overflowing"]
    for act in rest_actions:
        if st.button(act, use_container_width=True):
            add_log("Restroom", act)

# Final Sentiment (Ref: Screenshot 2026-05-13 at 7.08.36 PM.png)
with st.expander("⭐ Final Impressions", expanded=False):
    sent_actions = ["Return/Spend Own Money", "Recommend (Service)", "Recommend (Food)", "Staff Teamwork", "Welcomed/Cared For"]
    for act in sent_actions:
        if st.button(act, use_container_width=True):
            add_log("Loyalty", act)

st.divider()

# --- Data Display & Export ---
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Final Report", csv, "service_eval.csv", "text/csv", use_container_width=True)
    
    if st.button("🚨 Clear App Cache", use_container_width=True):
        local_storage.delete("eval_logs")
        st.session_state.logs = []
        st.rerun()
else:
    st.info("Start tapping buttons to log service events.")
    st.info("No activity logged yet.")
