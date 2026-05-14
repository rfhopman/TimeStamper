import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from streamlit_local_storage import LocalStorage
from streamlit_gsheets import GSheetsConnection

# --- Setup ---
st.set_page_config(page_title="Audit Pro 153", layout="centered")
local_storage = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

# --- THE FULL QUESTION DATABASE ---
# Populated based on your project screenshots
AUDIT_QUESTIONS = {
    # 1-45: Hostess & Bar
    "1": "Reservation handled professionally.",
    "2": "Greeted within 30 seconds of entry.",
    "3": "Hostess made eye contact and smiled.",
    "4": "Table was ready at reservation time.",
    "5": "Hostess walked at a comfortable pace to the table.",
    "6": "Hostess seated guests and provided menus.",
    "7": "Table was clean and properly set upon arrival.",
    "8": "Hostess mentioned the server's name.",
    "9": "Chair was assisted for at least one guest.",
    "10": "Bar staff acknowledged presence within 1 minute.",
    "45": "Appetizers suggested during bar service.",
    
    # 46-87: Server Intro & Timing
    "46": "Server greeted table within 2 minutes.",
    "50": "Server introduced themselves by name.",
    "55": "Water served/offered immediately.",
    "60": "Specials explained clearly/enthusiastically.",
    "87": "Bread/Butter service offered and delivered.",

    # 88-100: Service Quality (Ref: Screenshot 7.07.24 PM)
    "88": "Dessert served within 12 minutes of order.",
    "89": "Server checked on dessert.",
    "90": "Check was presented within two minutes of request.",
    "91": "Server offered to wrap leftovers.",
    "92": "Thanked sincerely with eye contact.",
    "93": "Busser asked 'May I?' before clearing.",
    "98": "Server was available and readily accessible.",
    "99": "Server enhanced experience, anticipated needs.",
    "100": "Overall service was seamless.",

    # 101-116: Management (Ref: Screenshot 7.07.32 PM)
    "101": "Specific cocktails offered on first visit.",
    "104": "Silverware was polished; no water spots.",
    "106": "Glassware: Clean, free of blemishes.",
    "108": "Management interacted with bar guests.",
    "110": "Management made personal contact with table.",
    "113": "Management demeanor professional/upbeat.",
    "116": "Manager dressed professionally.",

    # 117-134: Facility (Ref: Screenshot 7.08.16 PM)
    "117": "Sidewalk well-maintained.",
    "125": "LINENS: Clean, no holes.",
    "126": "CARPETS/FLOORS/WALLS: Clean.",
    "132": "Restroom fully supplied.",
    "133": "Restroom neat and odor free.",
    "134": "Waste receptacle not overflowing.",

    # 135-144: Kitchen (Ref: Screenshot 7.08.00 PM)
    "135": "Food was visually appealing.",
    "137": "Food served at correct temperature.",
    "141": "Ingredients fresh in taste/appearance.",
    "143": "Would recommend restaurant based on food.",
    "144": "Describe the food (Multi-select Narrative).",

    # 145-153: Loyalty (Ref: Screenshot 7.08.42 PM)
    "145": "NPS Recommendation Scale (0-10).",
    "146": "Emotional state upon departure.",
    "147": "Staff exhibited energy and enthusiasm; smiles prevalent.",
    "148": "Staff members exhibited teamwork.",
    "149": "No significant disappointment with your dining experience.",
    "150": "You would return and spend your own money.",
    "151": "You felt welcomed, cared for, and appreciated.",
    "152": "You would recommend the restaurant based on service.",
    "153": "Describe the ambiance (Multi-select Narrative)."
}

# Auto-fill any remaining indices with a generic label if specific text wasn't in screenshots
for i in range(1, 154):
    if str(i) not in AUDIT_QUESTIONS:
        AUDIT_QUESTIONS[str(i)] = f"Audit Point {i}: Specific Service Standard"

# --- Logic ---
if 'logs' not in st.session_state:
    try:
        st.session_state.logs = local_storage.get("eval_logs") or []
    except:
        st.session_state.logs = []

def add_entry(q_id, question, response, comment=""):
    local_tz = pytz.timezone('America/Aruba') 
    now_local = datetime.now(pytz.utc).astimezone(local_tz)
    
    entry = {
        "Timestamp": now_local.strftime("%Y-%m-%d %I:%M:%S %p"),
        "Q_ID": int(q_id),
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
    except Exception as e:
        st.error(f"Sync delayed. Check Sheet sharing. Error: {e}")

def q_ui(q_id):
    text = AUDIT_QUESTIONS.get(q_id)
    with st.container(border=True):
        st.markdown(f"**{q_id}. {text}**")
        
        # Specialized UI for Narrative/Scale questions
        if q_id == "145":
            res = st.select_slider("Score", options=list(range(11)), key=f"r_{q_id}")
        elif q_id in ["144", "153"]:
            res = st.multiselect("Tags", ["Quality", "Ambiance", "Service", "Speed", "Taste"], key=f"r_{q_id}")
        elif q_id == "147":
            res = st.radio("Selection", ["All", "Most", "Some", "None"], key=f"r_{q_id}", horizontal=True)
        elif q_id == "149":
            res = st.select_slider("Agreement", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree", "N/A"], key=f"r_{q_id}")
        else:
            res = st.radio("Status", ["Yes", "No", "N/A"], key=f"r_{q_id}", horizontal=True, label_visibility="collapsed")
            
        comm = st.text_input("Comment", key=f"c_{q_id}")
        if st.button(f"Log Q{q_id}", key=f"b_{q_id}", use_container_width=True):
            add_entry(q_id, text, res, comm)

# --- UI Layout ---
st.title("Service Evaluator Pro")

# Grouping by category to keep the iPhone screen uncluttered
tabs = st.tabs(["Intro (1-45)", "Server (46-87)", "Quality (88-116)", "Facility (117-144)", "Loyalty (145-153)"])

with tabs[0]:
    for i in range(1, 46): q_ui(str(i))
with tabs[1]:
    for i in range(46, 88): q_ui(str(i))
with tabs[2]:
    for i in range(88, 117): q_ui(str(i))
with tabs[3]:
    for i in range(117, 145): q_ui(str(i))
with tabs[4]:
    for i in range(145, 154): q_ui(str(i))

st.divider()
if st.session_state.logs:
    st.subheader("Data Summary")
    st.dataframe(pd.DataFrame(st.session_state.logs), use_container_width=True)
