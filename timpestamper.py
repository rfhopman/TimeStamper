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
    # 1-23: Hostess & Initial Bar
    "1": "Guest greeted at podium with a smile and welcome.",
    "2": "Host initiated greeting.",
    "3": "Guest acknowledged with smile/gesture if you were in line.",
    "4": "If applicable,you were proactively offered coat check assistance.",
    "5": "Once learned,host used guest name.",
    "6": "Tone,demeanor was welcoming,not businesslike or harried.",
    "7": "Host maintained eye contact while speaking with guest.",
    "8": "If there was a delay,the manager updates the guest.",
    "9": "Cocktails/drinks carried by restaurant employee to the table.",
    "10": "Host made pleasant conversation on the way to the table (min. 10 pace distance).",
    "11": "Host pulled out chair or positioned table for the guest (N/A for booths).",
    "12": "All guests were seated before host departed.",
    "13": "Menus were handed to each guest once all were seated.",
    "14": "Host wished a you a pleasant dinner/meal.",
    "15": "You were advised of the presence of stairs or other obstacles before approaching them.",
    "16": "BHost attentive to all entering/exiting guests.",
    "17": "You received a sincere farewell upon departure.",
    "18": "Shirt/Slacks/Dresses; pressed,hair was neat.",
    "19": "Host had pleasant physical appearance.",
    "20": "Special reservation requests were acknowledged/honored.",
    "21": "Host staff was dressed appropriately and well groomed.",
    "22": "Outside entry was clean.",
    "23": "Lobby/entry area was well lit and clean.",

    # 24-65: Bar Service & Table Transition
    "24": "Bartender smiled and maintained eye contact.",
    "25": "Bartender was helpful and knowledgeable about coctails and wines.",
    "26": "Bartender greeted you within one minute of your arrival at the bar.",
    "27": "Upsold liquor, beer and wine.",
    "28": "Pour sizes were consistent.",
    "29": "Drink was properly prepared: chilled glass, ice level, etc. .",
    "30": "Ice scoop was employed.",
    "31": "Glasses not handled near rim.",
    "32": "Garnishes fresh and appropriate.",
    "33": "UAnother round was suggested when drinks were nearly empty.",
    "34": "Transaction ws rung immediately.",
    "35": "NO intoxicated patrons were being served alcohol.",
    "36": "Check(s) was produced after each order *hard copy).",
    "37": "TItemized recepts were given with cash change.",
    "38": "POS drawer closed between transacitons.",
    "39": "You were thanked with eye contact when you paid.",
    "40": "Asked if guests would be eating at the ar/offered menu *iuf applicable).",
    "41": "Demonstrates knowledge of food menu *detailed when answereing questions).",
    "42": "Glassware was clean..",
    "43": "Beverage menu/wine list was clean, no misspellings.",
    "44": "Bartop wiped and clean; no crumbs, no sticky or wet spots.",
    "45": "Dirty glassware was promptly bussed from bar tp.",
    "46": "SBartender mis en place was neat.",
    "47": "Shaker was washed between uses.",
    "48": "Back bar was maintined neatly.",
    "49": "Bartender was available to all guests, made eye contact; courteous.",
    "50": "SPatrons of questionable age were asked for identification.",
    "51": "Uniform pressed; hair neat, shoes shined; no sneakers.",
    "52": "Bartender was friendly and enhanced experience, interacted with guests, especially single guests.",
    "53": "Misappropriation of funds was not observed or suspected.",
    "54": "Free drinks were not served.",
    "55": "Drinks prepared for servers were accompanied by tickets.",
    "56": "You were billed for all items consumed (unless noted by staff).",
    "57": "Special requests were accommodated happily.",
    "58": "timing flowed smoothly.",
    "59": "Drink refillswere timely; consumption moved along.",
    "60": "Table was maintined; crumbs and dishes/glassware cleared.",
    "61": "You would describe service as freindly and warm.",
    "62": "Once payment was tendered, check was settled within three minutes.",
    "63": "Staff member does not ask if cash change is needed but automatically brings change to guest.",
    "64": "Did not touch face or hari (or washes hands immediately after); hygienic.",
    "65": "Staff not eating or drinking in public view.",

    # 66-87: Server Introduction & Dining Flow
    "46": "SBartender mis en place was neat.",
    "47": "Shaker was washed between uses.",
    "48": "Back bar was maintined neatly.",
    "49": "Bartender was available to all guests, made eye contact; courteous.",
    "50": "SPatrons of questionable age were asked for identification.",
    "51": "Uniform pressed; hair neat, shoes shined; no sneakers.",
    "52": "Bartender was friendly and enhanced experience, interacted with guests, especially single guests.",
    "53": "Misappropriation of funds was not observed or suspected.",
    "54": "Free drinks were not served.",
    "55": "Drinks prepared for servers were accompanied by tickets.",
    "56": "You were billed for all items consumed (unless noted by staff).",
    "57": "Special requests were accommodated happily.",
    "58": "timing flowed smoothly.",
    "59": "Drink refillswere timely; consumption moved along.",
    "60": "Table was maintined; crumbs and dishes/glassware cleared.",
    "61": "You would describe service as freindly and warm.",
    "62": "Once payment was tendered, check was settled within three minutes.",
    "63": "Staff member does not ask if cash change is needed but automatically brings change to guest.",
    "64": "Did not touch face or hari (or washes hands immediately after); hygienic.",
    "65": "Staff not eating or drinking in public view.",
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
