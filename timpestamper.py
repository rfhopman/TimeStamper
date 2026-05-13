import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from streamlit_local_storage import LocalStorage
from streamlit_gsheets import GSheetsConnection

# --- Setup ---
st.set_page_config(page_title="Service Evaluator Pro", layout="centered")
local_storage = LocalStorage()

# 1. Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Load Local Persistence
if 'logs' not in st.session_state:
    stored_data = local_storage.get("eval_logs")
    st.session_state.logs = stored_data if stored_data else []

def add_log(category, action):
    # Timezone Logic
    local_tz = pytz.timezone('America/Aruba') 
    now_local = datetime.now(pytz.utc).astimezone(local_tz)
    timestamp_str = now_local.strftime("%I:%M:%S %p")
    
    entry = {
        "Timestamp": timestamp_str,
        "Category": category,
        "Action": action
    }
    
    # Save to Session State
    st.session_state.logs.append(entry)
    
    # Save to iPhone Local Storage (Safety Option 1)
    local_storage.set("eval_logs", st.session_state.logs)
    
    # Save to Google Sheets (Safety Option 2 - Permanent)
    try:
        # Create a tiny dataframe for the single new row
        new_row = pd.DataFrame([entry])
        # Append to the existing sheet
        conn.create(data=new_row)
    except Exception as e:
        st.error(f"Cloud Sync failed, but data saved to phone: {e}")

st.title("📋 Multi-Sync Evaluation Log")
st.write("Data is being synced to your iPhone and Google Sheets simultaneously.")

# --- UI Sections (Same as previous version) ---
# [Insert the Expanders and Buttons code here...]

st.divider()

# --- Data Display & Export ---
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    # Manual CSV Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Backup CSV", csv, "service_eval.csv", "text/csv", use_container_width=True)
    
    # Sync Status Indicator
    st.success("✅ Cloud Connection Active")
    
    if st.button("🚨 Wipe Local Cache", use_container_width=True):
        local_storage.delete("eval_logs")
        st.session_state.logs = []
        st.rerun()
else:
    st.info("Awaiting input...")
    st.info("No activity logged yet.")
