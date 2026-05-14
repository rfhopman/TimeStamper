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

# --- THE COMPLETE 1-153 QUESTION DATABASE ---
AUDIT_QUESTIONS = {
    # 1-15: Hostess & Initial Bar
    "1": "Reservation handled professionally.",
    "2": "Greeted within 30 seconds of entry.",
    "3": "Hostess made eye contact and smiled.",
    "4": "Table was ready at reservation time.",
    "5": "Hostess walked at a comfortable pace.",
    "6": "Hostess seated guests and provided menus.",
    "7": "Table was clean and properly set.",
    "8": "Hostess mentioned the server's name.",
    "9": "Chair was assisted for at least one guest.",
    "10": "Bar staff acknowledged presence within 1 minute.",
    "11": "Bar staff offered a specific cocktail/beverage.",
    "12": "Drinks delivered to bar guest within 3 minutes.",
    "13": "Napkin/Coaster placed before drink service.",
    "14": "Bar snacks offered or provided.",
    "15": "Bar menu offered for food.",

    # 16-45: Bar Service & Table Transition
    "16": "Bartender knowledgeable about the menu/spirits.",
    "17": "Glassware at bar was spotless.",
    "18": "Bar surface was clean and dry.",
    "19": "Drink refills offered at bar promptly.",
    "20": "Bartender used professional language/posture.",
    "21": "Bartender suggested a specific appetizer.",
    "22": "Appetizer order taken within 5 mins of seating.",
    "23": "Silverware provided before food arrival.",
    "24": "Food delivered to bar within 15 minutes.",
    "25": "Bartender checked back after two bites.",
    "26": "Bar tab transferred to table seamlessly.",
    "27": "Hostess informed server of guest preferences.",
    "28": "Drink consistency and presentation was excellent.",
    "29": "Bar music and lighting were appropriate.",
    "30": "Bar trash/empty bottles removed quickly.",
    "31": "Bartender thanked guest upon departure/transfer.",
    "32": "Staff groomed according to professional standards.",
    "33": "Uniforms clean and free of stains.",
    "34": "Name tags visible and straight.",
    "35": "Staff posture and body language professional.",
    "36": "Staff avoided congregating in view of guests.",
    "37": "Table settings aligned and complete.",
    "38": "Salt/Pepper shakers clean and full.",
    "39": "Menu condition was pristine.",
    "40": "Wine list offered and explained.",
    "41": "Draft beer/beverage availability confirmed.",
    "42": "Staff smiled during all interactions.",
    "43": "Service was focused entirely on the guest.",
    "44": "Wait times (if any) accurately quoted.",
    "45": "Appetizers suggested during bar service.",

    # 46-87: Server Introduction & Dining Flow
    "46": "Server greeted table within 2 minutes.",
    "47": "Server provided their name clearly.",
    "48": "Server offered specific bottled water options.",
    "49": "First drink order taken promptly.",
    "50": "Server introduced themselves by name.",
    "51": "Server repeated order back for accuracy.",
    "52": "Drinks delivered within 5 minutes of order.",
    "53": "Server utilized a tray for all drink service.",
    "54": "Server placed drinks without reaching across.",
    "55": "Water served/offered immediately.",
    "56": "Daily specials explained with detail/enthusiasm.",
    "57": "Server made specific entree recommendations.",
    "58": "Server asked about allergies/dietary needs.",
    "59": "Order taken efficiently without disruption.",
    "60": "Specials explained clearly/enthusiastically.",
    "61": "Proper silverware set for the specific order.",
    "62": "Wine bottle presented correctly before opening.",
    "63": "Wine cork placed on table after opening.",
    "64": "Guest given the first taste of wine.",
    "65": "Wine poured without dripping; label facing guest.",
    "66": "Appetizers served within 12 minutes.",
    "67": "Used plates removed within 2 mins of finishing.",
    "68": "New silverware provided for every course.",
    "69": "Entrees served within 20 minutes of order.",
    "70": "Plates delivered to correct guest (no auctioning).",
    "71": "Plates placed gently with minimal noise.",
    "72": "Food items explained as they were placed.",
    "73": "Meat temperatures checked immediately.",
    "74": "Side dishes served with entrees.",
    "75": "Server checked back after two bites of entree.",
    "76": "Extra sauces/condiments offered proactively.",
    "77": "Server refilled wine/water without being asked.",
    "78": "Empty glassware removed promptly.",
    "79": "Napkin refolded if guest left the table.",
    "80": "Refills offered before glass was 1/4 full.",
    "81": "Server maintained a pleasant, unhurried pace.",
    "82": "Server aware of table needs without hovering.",
    "83": "Any service issues handled with empathy/speed.",
    "84": "Table crumbed before dessert service.",
    "85": "Dessert menu presented or described.",
    "86": "Specific dessert/coffee suggested by name.",
    "87": "Bread/Butter service offered and delivered.",

    # 88-116: Service Quality & Management
    "88": "Dessert served within 12 minutes of order.",
    "89": "Server checked on dessert.",
    "90": "Check was presented within two minutes of request.",
    "91": "Server offered to wrap leftovers.",
    "92": "Thanked sincerely with eye contact.",
    "93": "Busser asked 'May I?' before clearing.",
    "94": "Server used a tray for all drink transport.",
    "95": "Table remained crumb-free throughout.",
    "96": "Server handled glassware by the base/stem.",
    "97": "Service was timed perfectly between courses.",
    "98": "Server was available and readily accessible.",
    "99": "Server enhanced experience, anticipated needs.",
    "100": "Overall service was seamless.",
    "101": "Specific cocktails offered on first visit.",
    "102": "Menu was clean and in good condition.",
    "103": "Table was stable (no wobbling).",
    "104": "Silverware was polished; no water spots.",
    "105": "Plates were free of chips or cracks.",
    "106": "Glassware: Clean, free of blemishes.",
    "107": "Napkins were folded/placed properly.",
    "108": "Management interacted with bar guests.",
    "109": "Manager was visible on the floor.",
    "110": "Management made personal contact with table.",
    "111": "Manager handled issues promptly/professionally.",
    "112": "Manager thanked guests for coming.",
    "113": "Management demeanor professional/upbeat.",
    "114": "Manager greeted staff members as well.",
    "115": "Manager monitored the host stand.",
    "116": "Manager dressed professionally.",

    # 117-134: Facility & Restroom
    "117": "Sidewalk well-maintained.",
    "118": "Exterior windows were clean.",
    "119": "Entrance area free of debris.",
    "120": "Entrance lighting was appropriate.",
    "121": "Background music at correct level.",
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

    # 135-144: Kitchen & Food Quality
    "135": "Food was visually appealing.",
    "136": "Portion sizes were consistent.",
    "137": "Food served at correct temperature.",
    "138": "Garnish was fresh and appropriate.",
    "139": "Plates wiped clean of spills/drips.",
    "140": "Food arrived as described on menu.",
    "141": "Ingredients fresh in taste/appearance.",
    "142": "Side dishes complemented main course.",
    "143": "Would recommend restaurant based on food.",
    "144": "Describe the food (Multi-select Narrative).",

    # 145-153: Loyalty & Summary
    "145": "NPS Recommendation Scale (0-10).",
    "146": "Emotional state upon departure.",
    "147": "Staff exhibited energy and enthusiasm; smiles prevalent.",
    "148": "Staff members exhibited teamwork.",
    "149": "No significant disappointment with dining experience.",
    "150": "You would return and spend your own money.",
    "151": "You felt welcomed, cared for, and appreciated.",
    "152": "You would recommend based on service.",
    "153": "Describe the ambiance (Multi-select Narrative)."
}

# --- Standard Logic ---
if 'logs' not in st.session_state:
    try: st.session_state.logs = local_storage.get("eval_logs") or []
    except: st.session_state.logs = []

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
        conn.create(data=pd.DataFrame([entry]))
        st.toast(f"✅ Q{q_id} Logged")
    except Exception:
        st.error(f"Sync Issue. Check Sheet sharing settings.")

def render_q(q_id):
    text = AUDIT_QUESTIONS.get(str(q_id))
    with st.container(border=True):
        st.markdown(f"**{q_id}. {text}**")
        if q_id == 145:
            res = st.select_slider("Score", options=list(range(11)), key=f"r_{q_id}")
        elif q_id in [144, 153]:
            res = st.multiselect("Tags", ["Flavorful", "Fresh", "Ambiance", "Music"], key=f"r_{q_id}")
        elif q_id == 147:
            res = st.radio("Presence", ["All", "Most", "Some", "None"], key=f"r_{q_id}", horizontal=True)
        elif q_id == 149:
            res = st.select_slider("Agreement", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], key=f"r_{q_id}")
        else:
            res = st.radio("Selection", ["Yes", "No", "N/A"], key=f"r_{q_id}", horizontal=True, label_visibility="collapsed")
        
        comm = st.text_input("Comment", key=f"c_{q_id}")
        if st.button(f"Log {q_id}", key=f"b_{q_id}", use_container_width=True):
            add_entry(q_id, text, res, comm)

st.title("Full 153-Question Service Audit")
tabs = st.tabs(["1-30", "31-60", "61-90", "91-120", "121-153"])
with tabs[0]:
    for i in range(1, 31): render_q(i)
with tabs[1]:
    for i in range(31, 61): render_q(i)
with tabs[2]:
    for i in range(61, 91): render_q(i)
with tabs[3]:
    for i in range(91, 121): render_q(i)
with tabs[4]:
    for i in range(121, 154): render_q(i)

# --- ADD THIS TO THE BOTTOM OF YOUR FILE TO SEE LOGS ON YOUR PHONE ---
st.divider()
st.subheader("Current Session Logs")

if st.session_state.logs:
    # Convert logs to a dataframe to show as a table
    df = pd.DataFrame(st.session_state.logs)
    st.dataframe(df, use_container_width=True)
    
    if st.button("Clear Local Logs"):
        st.session_state.logs = []
        local_storage.set("eval_logs", [])
        st.rerun()
else:
    st.info("No items logged in this session yet.")
