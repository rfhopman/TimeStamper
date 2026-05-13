import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from streamlit_local_storage import LocalStorage
from streamlit_gsheets import GSheetsConnection

# --- Configuration ---
st.set_page_config(page_title="Service Evaluator Pro", layout="centered")
local_storage = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

if 'logs' not in st.session_state:
    try:
        stored_data = local_storage.get("eval_logs")
        st.session_state.logs = stored_data if stored_data else []
    except Exception:
        st.session_state.logs = []

def add_entry(q_num, task, status, comment):
    local_tz = pytz.timezone('America/Aruba') 
    now_local = datetime.now(pytz.utc).astimezone(local_tz)
    
    entry = {
        "Timestamp": now_local.strftime("%I:%M:%S %p"),
        "ID": q_num,
        "Task": task,
        "Status": status,
        "Comment": comment
    }
    
    st.session_state.logs.append(entry)
    try:
        local_storage.set("eval_logs", st.session_state.logs)
        new_row = pd.DataFrame([entry])
        conn.create(data=new_row)
        st.toast(f"Logged: {q_num}")
    except Exception:
        st.error("Storage sync failed, but entry kept in session.")

st.title("📋 Service Evaluation Form")

# Helper function to create the UI blocks seen in your screenshots
def question_block(q_num, text, category):
    with st.container(border=True):
        st.markdown(f"**{q_num}. {text}**")
        col1, col2 = st.columns([1, 1])
        status = st.radio("Status", ["Yes", "No", "N/A"], key=f"rad_{q_num}", horizontal=True, label_visibility="collapsed")
        comment = st.text_area("Comment:", key=f"comm_{q_num}", height=68)
        if st.button(f"Log {q_num}", key=f"btn_{q_num}", use_container_width=True):
            add_entry(q_num, text, status, comment)

# --- Sections based on Screenshots ---

with st.expander("👤 Management", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.42 PM.png
    mgt_tasks = [
        ("108", "Management interacted with bar guests who are dining."),
        ("109", "Management was engaged with staff at door and/or on the service floor."),
        ("110", "Management made personal contact with your table."),
        ("111", "Manager visited your table to ensure your satisfaction."),
        ("113", "Management demeanor was professional and upbeat; seen smiling."),
        ("116", "Manager dressed professionally.")
    ]
    for q, txt in mgt_tasks:
        question_block(q, txt, "Management")

with st.expander("🤝 Service Quality", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.24 PM.png
    srv_tasks = [
        ("88", "Dessert served within 12 minutes of order."),
        ("89", "Server checked on dessert."),
        ("90", "Check was presented to host within two minutes of request."),
        ("92", "You were thanked sincerely with eye contact."),
        ("93", "Busser made eye contact and specifically asked, 'May I?' before clearing items."),
        ("98", "Server was available and readily accessible.")
    ]
    for q, txt in srv_tasks:
        question_block(q, txt, "Service")

with st.expander("🍽️ Table & Glassware", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.32 PM.png
    tbl_tasks = [
        ("101", "Specific cocktails or beverage were offered on first visit."),
        ("102", "Coffee/tea, cappuccino, espresso and/or digestifs were offered."),
        ("103", "Coffee refills are automatic."),
        ("104", "Silverware was polished; no water spots or bent tines."),
        ("106", "Glassware: Clean, free of blemishes.")
    ]
    for q, txt in tbl_tasks:
        question_block(q, txt, "Table Setting")

with st.expander("🚽 Restroom", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.16 PM.png
    rst_tasks = [
        ("132", "Restroom was fully supplied."),
        ("133", "Restroom was neat and odor free."),
        ("134", "Waste receptacle not overflowing.")
    ]
    for q, txt in rst_tasks:
        question_block(q, txt, "Restroom")

st.divider()

# --- Data Management ---
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Final Report", csv, "evaluation.csv", "text/csv", use_container_width=True)
    
    if st.button("🚨 Clear All Progress", use_container_width=True):
        local_storage.delete("eval_logs")
        st.session_state.logs = []
        st.rerun()
