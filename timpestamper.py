import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from streamlit_local_storage import LocalStorage
from streamlit_gsheets import GSheetsConnection

# --- Configuration ---
st.set_page_config(page_title="Service Evaluator Pro", layout="centered")

# Initialize LocalStorage with a specific key
local_storage = LocalStorage(key="service_eval_v1")

# Establish Google Sheets Connection
# Ensure you have set up your credentials in Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialize session state from local storage (iPhone memory)
if 'logs' not in st.session_state:
    try:
        stored_data = local_storage.get("eval_logs")
        st.session_state.logs = stored_data if stored_data is not None else []
    except Exception:
        st.session_state.logs = []

def add_log(category, action):
    # Timezone Logic (Fixed -4 offset for your location)
    local_tz = pytz.timezone('America/Aruba') 
    now_utc = datetime.now(pytz.utc)
    now_local = now_utc.astimezone(local_tz)
    timestamp_str = now_local.strftime("%I:%M:%S %p")
    
    entry = {
        "Timestamp": timestamp_str,
        "Category": category,
        "Action": action
    }
    
    # 1. Save to Session State
    st.session_state.logs.append(entry)
    
    # 2. Sync to iPhone Local Storage immediately
    local_storage.set("eval_logs", st.session_state.logs)
    
    # 3. Sync to Google Sheets Cloud
    try:
        new_row = pd.DataFrame([entry])
        conn.create(data=new_row)
    except Exception as e:
        st.warning(f"Cloud sync pending: {e}")

st.title("⏱️ Service Evaluation Tracker")
st.caption("Auto-syncing to iPhone and Google Sheets")

# --- UI Sections (Vertical for Mobile) ---

with st.expander("👤 Management", expanded=False):
    # From Screenshot 2026-05-13 at 7.07.42 PM.png
    mgt = ["Interacted with Bar", "Engaged at Door/Floor", "Table Contact", 
           "Satisfaction Check", "Follow-up on Complaints", "Professional Demeanor",
           "Food/Wine Knowledge", "Professional Dress"]
    for act in mgt:
        if st.button(act, key=f"mgt_{act}", use_container_width=True):
            add_log("Management", act)

with st.expander("🤝 Service Quality", expanded=False):
    # From Screenshot 2026-05-13 at 7.07.24 PM.png
    srv = ["Dessert within 12m", "Checked on Dessert", "Check within 2m", 
           "Leftover Wrap Offered", "Thanked w/ Eye Contact", "Busser 'May I?' Request",
           "Server Available/Accessible", "Anticipated Needs"]
    for act in srv:
        if st.button(act, key=f"srv_{act}", use_container_width=True):
            add_log("Service", act)

with st.expander("🍽️ Table & Glassware", expanded=False):
    # From Screenshot 2026-05-13 at 7.07.32 PM.png
    tbl = ["Cocktail Offered", "Coffee/Digestif Offered", "Automatic Refills", 
           "Silverware Polished", "Table Settings Neat", "Glassware Clean", "China No Defects"]
    for act in tbl:
        if st.button(act, key=f"tbl_{act}", use_container_width=True):
            add_log("Table Setting", act)

with st.expander("🍳 Kitchen & Food", expanded=False):
    # From Screenshot 2026-05-13 at 7.08.09 PM.png
    kit = ["Visually Appealing", "Beverage Proper", "Correct Temp", 
           "Prepared as Requested", "Exceptional Flavor", "Fresh Ingredients",
           "Diverse Offerings", "Recommend Based on Food"]
    for act in kit:
        if st.button(act, key=f"kit_{act}", use_container_width=True):
            add_log("Kitchen", act)

with st.expander("🏢 Facility", expanded=False):
    # From Screenshot 2026-05-13 at 7.08.24 PM.png
    fac = ["Sidewalk Maintained", "Entry Lit", "Windows Clean", "Door/Handle Good",
           "Podium Organized", "Foyer Clean", "Linens Clean", "Floor/Walls Clean",
           "Lighting Appropriate", "Tables/Chairs Sturdy", "Comfortable Temp"]
    for act in fac:
        if st.button(act, key=f"fac_{act}", use_container_width=True):
            add_log("Facility", act)

with st.expander("🚽 Restroom", expanded=False):
    # From Screenshot 2026-05-13 at 7.08.16 PM.png
    if st.button("Restroom Visit Start", use_container_width=True):
        add_log("Restroom", "Visit Start")
    rst = ["Fully Supplied", "Neat and Odor Free", "Waste Not Overflowing"]
    for act in rst:
        if st.button(act, key=f"rst_{act}", use_container_width=True):
            add_log("Restroom", act)

with st.expander("⭐ Final Impressions", expanded=False):
    # From Screenshot 2026-05-13 at 7.08.36 PM.png
    loy = ["Return/Spend Own Money", "Recommend Service", "Recommend Food", 
           "Staff Teamwork", "Welcomed/Cared For", "Staff Energy/Enthusiasm"]
    for act in loy:
        if st.button(act, key=f"loy_{act}", use_container_width=True):
            add_log("Loyalty", act)

st.divider()

# --- Data Review & Export ---
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    st.subheader("Current Log")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "eval_report.csv", "text/csv", use_container_width=True)
    
    if st.button("🚨 Clear All Progress", use_container_width=True):
        local_storage.delete("eval_logs")
        st.session_state.logs = []
        st.rerun()
else:
    st.info("No tasks logged yet. Tap a category above to begin.")
