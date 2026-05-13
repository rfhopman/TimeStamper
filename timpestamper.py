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

# Initialize session state
if 'logs' not in st.session_state:
    try:
        stored_data = local_storage.get("eval_logs")
        st.session_state.logs = stored_data if stored_data else []
    except Exception:
        st.session_state.logs = []

def add_entry(q_id, question, response, comment=""):
    local_tz = pytz.timezone('America/Aruba') 
    now_local = datetime.now(pytz.utc).astimezone(local_tz)
    
    entry = {
        "Timestamp": now_local.strftime("%I:%M:%S %p"),
        "Q_ID": q_id,
        "Question": question,
        "Response": str(response),
        "Comment": comment
    }
    
    st.session_state.logs.append(entry)
    try:
        # Dual-sync strategy
        local_storage.set("eval_logs", st.session_state.logs)
        new_row = pd.DataFrame([entry])
        conn.create(data=new_row)
        st.toast(f"Saved Q{q_id}")
    except Exception:
        st.error("Real-time sync delayed; data held in session.")

st.title("📋 Comprehensive Service Audit")

# --- UI Helper for Standard Questions ---
def standard_q(q_id, text):
    with st.container(border=True):
        st.markdown(f"**{q_id}. {text}**")
        res = st.radio("Response", ["Yes", "No", "N/A"], key=f"r_{q_id}", horizontal=True, label_visibility="collapsed")
        comm = st.text_input("Comment", key=f"c_{q_id}")
        if st.button(f"Log {q_id}", key=f"b_{q_id}", use_container_width=True):
            add_entry(q_id, text, res, comm)

# --- Sections 1-87 (Placeholder for brevity, add specific ones as needed) ---
with st.expander("📝 Initial Observations (1-87)", expanded=False):
    st.info("Insert specific questions for this range here.")

# --- Service Quality (88-100) ---
with st.expander("🤝 Service Quality (88-100)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.24 PM_2.png
    s_tasks = [
        ("88", "Dessert served within 12 minutes of order."),
        ("89", "Server checked on dessert."),
        ("90", "Check was presented within two minutes."),
        ("91", "Server offered to wrap leftovers."),
        ("92", "Thanked sincerely with eye contact."),
        ("93", "Busser asked 'May I?' before clearing."),
        ("99", "Server enhanced experience, anticipated needs.")
    ]
    for q, txt in s_tasks:
        standard_q(q, txt)

# --- Table & Management (101-116) ---
with st.expander("🍽️ Table & Management (101-116)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.32 PM_2.png and 7.07.42 PM_2.png
    m_tasks = [
        ("101", "Specific cocktails offered on first visit."),
        ("106", "Glassware: Clean, free of blemishes."),
        ("108", "Management interacted with bar guests."),
        ("113", "Management demeanor professional/upbeat."),
        ("116", "Manager dressed professionally.")
    ]
    for q, txt in m_tasks:
        standard_q(q, txt)

# --- Facility & Restroom (117-134) ---
with st.expander("🏢 Facility & Restroom (117-134)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.24 PM_2.png and 7.08.16 PM_2.png
    f_tasks = [
        ("117", "Sidewalk well-maintained."),
        ("125", "LINENS: Clean, no holes."),
        ("132", "Restroom fully supplied."),
        ("134", "Waste receptacle not overflowing.")
    ]
    for q, txt in f_tasks:
        standard_q(q, txt)

# --- Kitchen & Food (135-144) ---
with st.expander("🍳 Kitchen (135-144)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.09 PM_2.png and 7.08.00 PM_2.png
    k_tasks = [
        ("135", "Food was visually appealing."),
        ("137", "Food served at correct temperature."),
        ("143", "Would recommend restaurant based on food.")
    ]
    for q, txt in k_tasks:
        standard_q(q, txt)
    
    # Q144 Multi-select
    st.markdown("**144. Describe the food (mark all that apply):**")
    food_desc = st.multiselect("Select tags", ["Flavorful", "Fresh", "Innovative", "Unremarkable", "Exotic", "Bland", "Extraordinary"], key="q144")
    food_comm = st.text_area("Kitchen Narrative:", key="c144")
    if st.button("Log 144", use_container_width=True):
        add_entry("144", "Food Description", food_desc, food_comm)

# --- Loyalty & Final (145-153) ---
with st.expander("⭐ Loyalty & Final Impressions (145-153)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.36 PM_2.png and 7.08.42 PM_2.png
    
    # Q145 Scale
    st.markdown("**145. Recommendation Scale (0-10):**")
    score = st.select_slider("Score", options=list(range(11)), key="q145")
    score_comm = st.text_input("Why?", key="c145")
    if st.button("Log 145", use_container_width=True):
        add_entry("145", "NPS Score", score, score_comm)

    # Q147-152 Agreement
    agree_tasks = [
        ("148", "Staff members exhibited teamwork."),
        ("150", "You would return and spend your own money."),
        ("151", "You felt welcomed, cared for, and appreciated.")
    ]
    for q, txt in agree_tasks:
        with st.container(border=True):
            st.markdown(f"**{q}. {txt}**")
            res = st.select_slider("Agreement", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree", "N/A"], key=f"r_{q}")
            comm = st.text_input("Comment", key=f"c_{q}")
            if st.button(f"Log {q}", key=f"b_{q}", use_container_width=True):
                add_entry(q, txt, res, comm)

    # Q153 Ambiance
    st.markdown("**153. Describe the ambiance:**")
    ambiance = st.multiselect("Tags", ["Hectic", "Relaxing", "Lively", "Casual", "Cozy", "Elegant", "Romantic", "Noisy"], key="q153")
    amb_comm = st.text_area("Ambiance Comment:", key="c153")
    if st.button("Log 153", use_container_width=True):
        add_entry("153", "Ambiance", ambiance, amb_comm)

st.divider()

# --- Summary & Data Control ---
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    st.subheader("Logged Entries")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    if st.button("🚨 Clear Session", use_container_width=True):
        local_storage.delete("eval_logs")
        st.session_state.logs = []
        st.rerun()
        st.rerun()
