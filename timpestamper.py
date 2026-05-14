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

# Define the full question set 1-153
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
    # ... (Questions 11-44 would be populated here)
    "45": "Appetizers suggested during bar service.",
    
    # 46-87: Server Intro & Timing
    "46": "Server greeted table within 2 minutes.",
    "47": "Server was professionally groomed.",
    "48": "Server uniform was clean and pressed.",
    "49": "Server wore a visible name tag (if applicable).",
    "50": "Server introduced themselves by name.",
    "51": "Initial drink order taken immediately.",
    "52": "Drinks delivered within 5 minutes of order.",
    "53": "Server offered specific appetizers by name.",
    "54": "Server knowledgeable about the menu items.",
    "55": "Water served/offered immediately.",
    # ... (Questions 56-86)
    "87": "Bread/Butter service offered and delivered.",

    # 88-100: Service Quality
    "88": "Dessert served within 12 minutes of order.",
    "89": "Server checked on dessert quality.",
    "90": "Check presented within 2 minutes of request.",
    "91": "Server offered to wrap leftovers.",
    "92": "Thanked sincerely with eye contact.",
    "93": "Busser asked 'May I?' before clearing plates.",
    "94": "Server used a tray for all drink service.",
    "95": "Table remained crumb-free throughout the meal.",
    "96": "Refills offered before glass was empty.",
    "97": "Server handled glassware by the base/stem.",
    "98": "Server was available and readily accessible.",
    "99": "Server enhanced experience, anticipated needs.",
    "100": "Overall service was seamless.",

    # 101-116: Management
    "101": "Specific cocktails offered on first visit.",
    "102": "Menu was clean and in good condition.",
    "103": "Table was stable (not wobbling).",
    "104": "Silverware was polished; no water spots.",
    "105": "Plates were free of chips or cracks.",
    "106": "Glassware: Clean, free of blemishes.",
    "107": "Napkins were folded or placed properly.",
    "108": "Management interacted with bar guests.",
    "109": "Manager was visible on the floor.",
    "110": "Management made personal contact with table.",
    "111": "Manager handled any issues promptly.",
    "112": "Manager thanked guests for coming.",
    "113": "Management demeanor professional/upbeat.",
    "114": "Manager greeted staff members as well.",
    "115": "Manager was monitoring the host stand.",
    "116": "Manager dressed professionally.",

    # 117-134: Facility
    "117": "Sidewalk well-maintained.",
    "118": "Exterior windows were clean.",
    "119": "Entrance area free of debris.",
    "120": "Lighting at entrance was appropriate.",
    "121": "Background music at appropriate level.",
    "122": "Indoor temperature was comfortable.",
    "123": "Dining room lighting adjusted correctly.",
    "124": "Decor was clean and dust-free.",
    "125": "LINENS: Clean, no holes.",
    "126": "CARPETS/FLOORS/WALLS: Clean.",
    "127": "Ceiling tiles and vents were clean.",
    "128": "Restroom door was clean.",
    "129": "Restroom floor was dry and clean.",
    "130": "Restroom mirrors were streak-free.",
    "131": "Restroom sinks were clean.",
    "132": "Restroom fully supplied.",
    "133": "Restroom neat and odor free.",
    "134": "Waste receptacle not overflowing.",

    # 135-144: Kitchen
    "135": "Food was visually appealing.",
    "136": "Portion sizes were consistent.",
    "137": "Food served at correct temperature.",
    "138": "Garnish was fresh and appropriate.",
    "139": "Plates were wiped clean of spills/drips.",
    "140": "Food arrived as described on menu.",
    "141": "Ingredients fresh in taste/appearance.",
    "142": "Side dishes complemented the main course.",
    "143": "Would recommend restaurant based on food.",
    "144": "Food Narrative & Description",

    # 145-153: Loyalty
    "145": "NPS Recommendation Scale (0-10)",
    "146": "Emotional state upon departure",
    "147": "Staff energy and enthusiasm",
    "148": "Staff members exhibited teamwork.",
    "149": "No significant disappointment with experience.",
    "150": "Would return and spend own money.",
    "151": "Felt welcomed, cared for, and appreciated.",
    "152": "Would recommend based on service.",
    "153": "Ambiance Description"
}

# Add missing fillers for 11-44 and 56-86 to ensure a full 153 keys
for i in range(1, 154):
    if str(i) not in AUDIT_QUESTIONS:
        AUDIT_QUESTIONS[str(i)] = f"Standard Audit Requirement {i}"

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
        st.toast(f"✅ Q{q_id} Synced")
    except Exception as e:
        st.error(f"Sync failed for Q{q_id}. Check Sheet sharing. Error: {e}")

def q_ui(q_id):
    text = AUDIT_QUESTIONS.get(q_id)
    with st.container(border=True):
        st.markdown(f"**{q_id}. {text}**")
        
        # Custom logic for specific question types
        if q_id == "145":
            res = st.select_slider("Score", options=list(range(11)), key=f"r_{q_id}")
        elif q_id in ["144", "153"]:
            res = st.multiselect("Tags", ["Quality", "Speed", "Ambiance", "Value", "Service"], key=f"r_{q_id}")
        elif q_id == "147":
            res = st.radio("Level", ["All", "Most", "Some", "None"], key=f"r_{q_id}", horizontal=True)
        elif q_id == "149":
            res = st.select_slider("Agreement", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], key=f"r_{q_id}")
        else:
            res = st.radio("Status", ["Yes", "No", "N/A"], key=f"r_{q_id}", horizontal=True, label_visibility="collapsed")
            
        comm = st.text_input("Comment", key=f"c_{q_id}")
        if st.button(f"Log Question {q_id}", key=f"b_{q_id}", use_container_width=True):
            add_entry(q_id, text, res, comm)

# --- UI Layout ---
st.title("Service Evaluator 153")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["1-45", "46-87", "88-116", "117-144", "145-153"])

with tab1:
    for i in range(1, 46): q_ui(str(i))
with tab2:
    for i in range(46, 88): q_ui(str(i))
with tab3:
    for i in range(88, 117): q_ui(str(i))
with tab4:
    for i in range(117, 145): q_ui(str(i))
with tab5:
    for i in range(145, 154): q_ui(str(i))

st.divider()
if st.session_state.logs:
    st.subheader("Session Progress")
    st.dataframe(pd.DataFrame(st.session_state.logs), use_container_width=True)
