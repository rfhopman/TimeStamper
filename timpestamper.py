import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from streamlit_local_storage import LocalStorage
from streamlit_gsheets import GSheetsConnection

# --- Configuration ---
st.set_page_config(page_title="Full Service Audit", layout="centered")
local_storage = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

if 'logs' not in st.session_state:
    try:
        stored_data = local_storage.get("eval_logs")
        st.session_state.logs = stored_data if stored_data else []
    except Exception:
        st.session_state.logs = []

def add_entry(q_id, question, response, comment=""):
    # Timezone: Aruba (AST)
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
        local_storage.set("eval_logs", st.session_state.logs)
        new_row = pd.DataFrame([entry])
        conn.create(data=new_row)
        st.toast(f"✅ Q{q_id} Logged")
    except Exception:
        st.error("Real-time sync delayed; data held in session.")

# Helper for Standard Questions
def q_block(q_id, text):
    with st.container(border=True):
        st.markdown(f"**{q_id}. {text}**")
        res = st.radio("Status", ["Yes", "No", "N/A"], key=f"r_{q_id}", horizontal=True, label_visibility="collapsed")
        comm = st.text_input("Comment", key=f"c_{q_id}")
        if st.button(f"Log {q_id}", key=f"b_{q_id}", use_container_width=True):
            add_entry(q_id, text, res, comm)

st.title("📋 Full 153-Point Audit")

# --- SECTION 1: PRE-ENTRY & START (1-87) ---
with st.expander("📝 Initial Service Steps (1-87)", expanded=False):
    # Example block for 1-87 range
    q_block("1", "Reservation was handled professionally.")
    q_block("2", "Greeted within 30 seconds of entry.")
    # ... (Continue pattern for other 1-87 specific items)
    st.caption("Items 3-87 follow the standard Yes/No/NA format.")

# --- SECTION 2: SERVICE QUALITY (88-100) ---
with st.expander("🤝 Service Quality (88-100)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.24 PM_2.png
    sq_tasks = [
        ("88", "Dessert served within 12 minutes of order."),
        ("89", "Server checked on dessert."),
        ("90", "Check was presented within two minutes of request."),
        ("91", "Server offered to wrap leftovers."),
        ("92", "Thanked sincerely with eye contact."),
        ("98", "Server was available and readily accessible.")
    ]
    for q, txt in sq_tasks:
        q_block(q, txt)

# --- SECTION 3: TABLE & MANAGEMENT (101-116) ---
with st.expander("👤 Management & Setting (101-116)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.07.32 PM_2.png / 7.07.42 PM_2.png
    st.text_input("Manager name(s) or description(s):", key="mgt_desc")
    m_tasks = [
        ("101", "Specific cocktails offered on first visit."),
        ("104", "Silverware was polished; no water spots."),
        ("108", "Management interacted with bar guests."),
        ("110", "Management made personal contact with table."),
        ("116", "Manager dressed professionally.")
    ]
    for q, txt in m_tasks:
        q_block(q, txt)

# --- SECTION 4: FACILITY (117-134) ---
with st.expander("🏢 Facility & Restroom (117-134)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.24 PM_2.png / 7.08.16 PM_2.png
    f_tasks = [
        ("117", "Sidewalk well-maintained."),
        ("126", "CARPETS/FLOORS/WALLS: Clean."),
        ("132", "Restroom fully supplied."),
        ("134", "Waste receptacle not overflowing.")
    ]
    for q, txt in f_tasks:
        q_block(q, txt)

# --- SECTION 5: KITCHEN (135-144) ---
with st.expander("🍳 Kitchen & Food (135-144)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.09 PM_2.png / 7.08.00 PM_2.png
    k_tasks = [
        ("135", "Food was visually appealing."),
        ("137", "Food served at correct temperature."),
        ("141", "Ingredients fresh in taste/appearance.")
    ]
    for q, txt in k_tasks:
        q_block(q, txt)
    
    st.markdown("**144. Describe the food (mark all that apply):**")
    f_tags = st.multiselect("Tags", ["Flavorful", "Fresh", "Innovative", "Bland", "Well-executed"], key="mt_144")
    f_comm = st.text_area("Narrative (Include detailed paragraph):", key="narr_144")
    if st.button("Log 144", use_container_width=True):
        add_entry("144", "Food Description", f_tags, f_comm)

# --- SECTION 6: LOYALTY & AMBIANCE (145-153) ---
with st.expander("⭐ Final Impressions (145-153)", expanded=False):
    # Ref: Screenshot 2026-05-13 at 7.08.36 PM_2.png / 7.08.42 PM_2.png
    st.markdown("**145. Recommendation Scale (0-10):**")
    nps = st.select_slider("Select Score", options=list(range(11)), key="nps_145")
    nps_comm = st.text_input("Comment:", key="cnps_145")
    if st.button("Log 145", use_container_width=True):
        add_entry("145", "Recommendation Scale", nps, nps_comm)

    # Emotional State Radio
    st.markdown("**146. Emotional state upon departure:**")
    emotion = st.radio("State", ["Content", "Happy", "Excited", "Disappointed", "Angry"], key="emo_146", horizontal=True)
    if st.button("Log 146", use_container_width=True):
        add_entry("146", "Emotional State", emotion)

    # Likert Scales for 148-152
    l_tasks = [
        ("148", "Staff members exhibited teamwork."),
        ("150", "You would return and spend your own money."),
        ("152", "You would recommend the restaurant.")
    ]
    for q, txt in l_tasks:
        with st.container(border=True):
            st.markdown(f"**{q}. {txt}**")
            res = st.select_slider("Agreement", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree", "N/A"], key=f"lik_{q}")
            comm = st.text_input("Comment", key=f"likc_{q}")
            if st.button(f"Log {q}", key=f"likb_{q}", use_container_width=True):
                add_entry(q, txt, res, comm)

    # Ambiance Multi-select
    st.markdown("**153. Describe the ambiance:**")
    amb = st.multiselect("Tags", ["Hectic", "Relaxing", "Lively", "Casual", "Cozy", "Elegant"], key="mt_153")
    amb_comm = st.text_area("Final Summary Comment:", key="narr_153")
    if st.button("Log 153", use_container_width=True):
        add_entry("153", "Ambiance Description", amb, amb_comm)

st.divider()

# --- Data Display ---
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    st.subheader("Session Log")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    if st.button("🚨 Clear All", use_container_width=True):
        local_storage.delete("eval_logs")
        st.session_state.logs = []
        st.rerun()
