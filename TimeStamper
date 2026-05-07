import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration for mobile
st.set_page_config(page_title="Task Logger", layout="centered")

# Initialize session state for data storage
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(category, action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append({
        "Timestamp": now,
        "Category": category,
        "Action": action
    })

st.title("⏱️ Activity Tracker")

# --- UI Layout ---
# Using expanders to keep the mobile interface clean
with st.expander("🛎️ Front Desk", expanded=True):
    for action in ["Arrival", "Wait", "Departure"]:
        if st.button(f"FD: {action}", use_container_width=True):
            add_log("Front Desk", action)

with st.expander("🍸 Bar / Restaurant", expanded=False):
    actions = ["Seated", "Greeted", "Orders", "Served", "Payment", "Departure"]
    for action in actions:
        if st.button(f"Bar: {action}", use_container_width=True):
            add_log("Bar/Restaurant", action)

with st.expander("🍽️ Table Service", expanded=False):
    ts_actions = [
        "Drinks Ordered", "Drinks Delivered", 
        "Appetizer Ordered", "Appetizer Served",
        "Entrée Ordered", "Entrée Served",
        "Dessert Ordered", "Dessert Served",
        "Check Back", "Check Requested", 
        "Check Provided", "Payment Taken", 
        "Check Settled", "Departure"
    ]
    for action in ts_actions:
        if st.button(f"TS: {action}", use_container_width=True):
            add_log("Table Service", action)

with st.expander("🚽 Facilities", expanded=False):
    if st.button("Restroom Visit", use_container_width=True):
        add_log("Facilities", "Restroom Visit")

---

### Data Log
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    # Display newest first for easy viewing on phone
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    # Download Section
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"activity_log_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )
    
    if st.button("🗑️ Clear All Logs", use_container_width=True):
        st.session_state.logs = []
        st.rerun()
else:
    st.info("No activity logged yet.")
