import streamlit as st
import pandas as pd
import pytz
from datetime import datetime

# --- Setup ---
st.set_page_config(page_title="Audit Notes Pro", layout="centered")

# --- Initialize Local Session Memory ---
if 'logs' not in st.session_state:
    st.session_state.logs = []

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
    "16": "Host attentive to all entering/exiting guests.",
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
    "66": "Server greeted guest at table within two minutes.",
  "67": "Server smiled, made eye contact with everyone in party.",
  "68": "You were greeted/welcomed (before being asked to order).",
  "69": "Server is extremely well spoken, polite and clear, avoiding slang and phrase-fragments.",
  "70": "Menus were handed to each guest once all were seated.",
  "71": "Beverages served within five minutes of ordering them.",
  "72": "Server offered or provided a glass for bottled beer.",
  "73": "Glassware was handled appropriately.",
  "74": "Server automatically explained specials, any unavailable items and concept.",
  "75": "Server suggested wine/presented wine list; beverage knowledgeable.",
  "76": "Server repeated back order, including meat color/temperatures.",
  "77": "Wine/cocktails/beer served at correct temperature.",
  "78": "Server forthcoming with menu details; developed rapport.",
  "79": "Utensils are properly positioned.",
  "80": "Share plates provided for shared foods (if applicable).",
  "81": "First course served within 12 minutes of order.",
  "82": "Food was announced by each item.",
  "83": "First course cleared within five minutes of all guests being done.",
  "84": "Server ascertained satisfaction of main course.",
  "85": "Amount of time between first and main course was five-ten minutes.",
  "86": "Wine and water were continually topped up.",
  "87": "Condiments/salt and pepper removed when entrees were cleared.",

    # 88-116: Service Quality & Management
     "88": "Dessert served within 12 minutes of order.",
  "89": "Server checked on dessert.",
  "90": "Check was presented to host within two minutes of request.",
  "91": "Server offered to wrap leftovers.",
  "92": "You were thanked sincerely with eye contact.",
  "93": "Busser made eye contact and specifically asked, \"May I?\" before clearing items.",
  "94": "Busser uniforms were pressed and clean; neatly groomed.",
  "95": "Server was well groomed.",
  "96": "Side stands and service stations were organized and clean.",
  "97": "Napkins were refolded when guests left table.",
  "98": "Server was available and readily accessible.",
  "99": "Server enhanced dining experience, anticipated needs.",
  "100": "None of the items that you ordered were 86’ed.",
  "101": "Specific cocktails or beverage were offered on first visit.",
  "102": "Coffee/tea, cappuccino, espresso and/or digestifs were offered.",
  "103": "Coffee refills are automatic.",
  "104": "Silverware was polished; no water spots or bent tines.",
  "105": "Table settings were neat, straight and complete.",
  "106": "Glassware: Clean, free of blemishes.",
  "107": "China: No chips or defects.",
  "108": "Management interacted with bar guests who are dining.",
  "109": "Management was engaged with staff at door and/or on the service floor.",
  "110": "Management made personal contact with your table.",
  "111": "Manager visited your table to ensure your satisfaction.",
  "112": "If applicable, management followed through with complaints/defects.",
  "113": "Management demeanor was professional and upbeat; seen smiling.",
  "114": "When asked, manager demonstrated knowledge of food and wine.",
  "115": "The outcome of any interaction with management was positive.",
  "116": "Manager dressed professionally.",

    # 117-134: Facility & Restroom
    "117": "Sidewalk was well-maintained; no cigarette butts.",
  "118": "Outside entry was well lit.",
  "119": "Windows are clean and free of streaks, spots, and cracks.",
  "120": "Door was in good condition; handle not worn, no fingerprints, scuffs.",
  "121": "Podium was clean and organized; no back-of-the house items visible to guest.",
  "122": "Foyer area clean, no visible trash or debris.",
  "123": "Condiments; sugar caddy PC container clean (tongs provided where applicable).",
  "124": "Menu was clean, pages crisp.",
  "125": "LINENS: Napkins/tablecloths clean, no holes or frayed seams.",
  "126": "CARPETS/FLOORS/WALLS: Clean, no debris, cracks or stains.",
  "127": "LIGHTING: appropriate, no burned out bulbs.",
  "128": "TABLES/CHAIRS: sturdy, no scratches or debris.",
  "129": "Temperature of restaurant was comfortable.",
  "130": "Music/lighting appropriate and comfortable.",
  "131": "Check presenter was clean; good condition.",
  "132": "Restroom was fully supplied.",
  "133": "Restroom was neat and odor free.",
  "134": "Waste receptacle not overflowing.",

    # 135-144: Kitchen & Food Quality
     "135": "Food was visually appealing.",
  "136": "There were no disappointments with any of the beverages served (coffee, wine, etc.).",
  "137": "Food was served at correct temperature.",
  "138": "Order was prepared properly (as requested).",
  "139": "Flavors were exceptional and memorable (clearly detail in narrative).",
  "140": "Food quality and presentation is exceptional.",
  "141": "Ingredients fresh in taste and appearance.",
  "142": "Menu offerings are diverse; include a range of dishes for a variety of palates.",
  "143": "You could recommend restaurant based upon food.",
  "144": "You would describe the food as (mark all that apply).",

    # 145-153: Loyalty & Summary
    "145": "On a scale of 0–10, how likely are you to recommend this location to friends/family/colleagues? Why?",
  "146": "Upon departure, choose the word that BEST described your emotional state.",
  "147": "Staff exhibited energy and enthusiasm; smiles were prevalent.",
  "148": "Staff members exhibited teamwork.",
  "149": "There was no significant disappointment with your dining experience.",
  "150": "You would return to the restaurant and spend your own money.",
  "151": "Based on your experience, you felt welcomed, cared for and appreciated by the service staff.",
  "152": "You would recommend the restaurant based upon the service and hospitality.",
  "153": "You would describe the ambiance as (mark all that apply)."
    
}
def add_entry(q_id, question, response, comment=""):
    local_tz = pytz.timezone('America/Aruba') 
    now_local = datetime.now(pytz.utc).astimezone(local_tz)
    
    entry = {
        "Time": now_local.strftime("%I:%M %p"),
        "Q": f"Q{q_id}",
        "Result": response,
        "Note": comment if comment else "-"
    }
    st.session_state.logs.append(entry)
    st.toast(f"Logged Q{q_id}")

# --- Question Rendering Logic ---
def render_q(q_id):
    # (Assuming AUDIT_QUESTIONS dictionary is defined here as before)
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
    "16": "Host attentive to all entering/exiting guests.",
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
    "66": "Server greeted guest at table within two minutes.",
  "67": "Server smiled, made eye contact with everyone in party.",
  "68": "You were greeted/welcomed (before being asked to order).",
  "69": "Server is extremely well spoken, polite and clear, avoiding slang and phrase-fragments.",
  "70": "Menus were handed to each guest once all were seated.",
  "71": "Beverages served within five minutes of ordering them.",
  "72": "Server offered or provided a glass for bottled beer.",
  "73": "Glassware was handled appropriately.",
  "74": "Server automatically explained specials, any unavailable items and concept.",
  "75": "Server suggested wine/presented wine list; beverage knowledgeable.",
  "76": "Server repeated back order, including meat color/temperatures.",
  "77": "Wine/cocktails/beer served at correct temperature.",
  "78": "Server forthcoming with menu details; developed rapport.",
  "79": "Utensils are properly positioned.",
  "80": "Share plates provided for shared foods (if applicable).",
  "81": "First course served within 12 minutes of order.",
  "82": "Food was announced by each item.",
  "83": "First course cleared within five minutes of all guests being done.",
  "84": "Server ascertained satisfaction of main course.",
  "85": "Amount of time between first and main course was five-ten minutes.",
  "86": "Wine and water were continually topped up.",
  "87": "Condiments/salt and pepper removed when entrees were cleared.",

    # 88-116: Service Quality & Management
     "88": "Dessert served within 12 minutes of order.",
  "89": "Server checked on dessert.",
  "90": "Check was presented to host within two minutes of request.",
  "91": "Server offered to wrap leftovers.",
  "92": "You were thanked sincerely with eye contact.",
  "93": "Busser made eye contact and specifically asked, \"May I?\" before clearing items.",
  "94": "Busser uniforms were pressed and clean; neatly groomed.",
  "95": "Server was well groomed.",
  "96": "Side stands and service stations were organized and clean.",
  "97": "Napkins were refolded when guests left table.",
  "98": "Server was available and readily accessible.",
  "99": "Server enhanced dining experience, anticipated needs.",
  "100": "None of the items that you ordered were 86’ed.",
  "101": "Specific cocktails or beverage were offered on first visit.",
  "102": "Coffee/tea, cappuccino, espresso and/or digestifs were offered.",
  "103": "Coffee refills are automatic.",
  "104": "Silverware was polished; no water spots or bent tines.",
  "105": "Table settings were neat, straight and complete.",
  "106": "Glassware: Clean, free of blemishes.",
  "107": "China: No chips or defects.",
  "108": "Management interacted with bar guests who are dining.",
  "109": "Management was engaged with staff at door and/or on the service floor.",
  "110": "Management made personal contact with your table.",
  "111": "Manager visited your table to ensure your satisfaction.",
  "112": "If applicable, management followed through with complaints/defects.",
  "113": "Management demeanor was professional and upbeat; seen smiling.",
  "114": "When asked, manager demonstrated knowledge of food and wine.",
  "115": "The outcome of any interaction with management was positive.",
  "116": "Manager dressed professionally.",

    # 117-134: Facility & Restroom
    "117": "Sidewalk was well-maintained; no cigarette butts.",
  "118": "Outside entry was well lit.",
  "119": "Windows are clean and free of streaks, spots, and cracks.",
  "120": "Door was in good condition; handle not worn, no fingerprints, scuffs.",
  "121": "Podium was clean and organized; no back-of-the house items visible to guest.",
  "122": "Foyer area clean, no visible trash or debris.",
  "123": "Condiments; sugar caddy PC container clean (tongs provided where applicable).",
  "124": "Menu was clean, pages crisp.",
  "125": "LINENS: Napkins/tablecloths clean, no holes or frayed seams.",
  "126": "CARPETS/FLOORS/WALLS: Clean, no debris, cracks or stains.",
  "127": "LIGHTING: appropriate, no burned out bulbs.",
  "128": "TABLES/CHAIRS: sturdy, no scratches or debris.",
  "129": "Temperature of restaurant was comfortable.",
  "130": "Music/lighting appropriate and comfortable.",
  "131": "Check presenter was clean; good condition.",
  "132": "Restroom was fully supplied.",
  "133": "Restroom was neat and odor free.",
  "134": "Waste receptacle not overflowing.",

    # 135-144: Kitchen & Food Quality
     "135": "Food was visually appealing.",
  "136": "There were no disappointments with any of the beverages served (coffee, wine, etc.).",
  "137": "Food was served at correct temperature.",
  "138": "Order was prepared properly (as requested).",
  "139": "Flavors were exceptional and memorable (clearly detail in narrative).",
  "140": "Food quality and presentation is exceptional.",
  "141": "Ingredients fresh in taste and appearance.",
  "142": "Menu offerings are diverse; include a range of dishes for a variety of palates.",
  "143": "You could recommend restaurant based upon food.",
  "144": "You would describe the food as (mark all that apply).",

    # 145-153: Loyalty & Summary
    "145": "On a scale of 0–10, how likely are you to recommend this location to friends/family/colleagues? Why?",
  "146": "Upon departure, choose the word that BEST described your emotional state.",
  "147": "Staff exhibited energy and enthusiasm; smiles were prevalent.",
  "148": "Staff members exhibited teamwork.",
  "149": "There was no significant disappointment with your dining experience.",
  "150": "You would return to the restaurant and spend your own money.",
  "151": "Based on your experience, you felt welcomed, cared for and appreciated by the service staff.",
  "152": "You would recommend the restaurant based upon the service and hospitality.",
  "153": "You would describe the ambiance as (mark all that apply)."
    text = f"Question Text for {q_id}" 
    with st.container(border=True):
        st.markdown(f"**{q_id}. {text}**")
        res = st.radio("Selection", ["Yes", "No", "N/A"], key=f"r_{q_id}", horizontal=True)
        comm = st.text_input("Comment", key=f"c_{q_id}", placeholder="Add detail...")
        if st.button(f"Add to Note", key=f"b_{q_id}", use_container_width=True):
            add_entry(q_id, text, res, comm)

st.title("📝 Audit Note Generator")

# --- Tabs for 153 Questions ---
tabs = st.tabs(["1-30", "31-60", "61-90", "91-120", "121-153"])
for idx, t in enumerate(tabs):
    with t:
        start = (idx * 30) + 1
        end = min(start + 30, 154)
        for i in range(start, end):
            render_q(i)

# --- THE "NOTES" AREA ---
st.sidebar.header("Audit Summary")

if st.session_state.logs:
    # Existing text note logic...
    note_text = "SERVICE AUDIT LOG\n" + "="*20 + "\n"
    for l in st.session_state.logs:
        note_text += f"[{l['Time']}] {l['Q']}: {l['Result']} | Note: {l['Note']}\n"
    
    # NEW: CSV Conversion
    df_logs = pd.DataFrame(st.session_state.logs)
    csv_data = df_logs.to_csv(index=False).encode('utf-8')

    # Sidebar Buttons
    st.sidebar.download_button(
        label="💾 Save as Text (Notes)",
        data=note_text,
        file_name=f"Audit_{datetime.now().strftime('%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.sidebar.download_button(
        label="📊 Save as CSV (Excel)",
        data=csv_data,
        file_name=f"Audit_{datetime.now().strftime('%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

if st.session_state.logs:
    # Format the logs as a single text block (like a Note)
    note_text = "SERVICE AUDIT LOG\n" + "="*20 + "\n"
    for l in st.session_state.logs:
        note_text += f"[{l['Time']}] {l['Q']}: {l['Result']} | Note: {l['Note']}\n"
    
    st.sidebar.text_area("Live Note Preview", value=note_text, height=400)
    
    # 1. DOWNLOAD AS TXT (To save to iPhone Files)
    st.sidebar.download_button(
        label="💾 Save Note to Phone",
        data=note_text,
        file_name=f"Audit_Note_{datetime.now().strftime('%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    # 2. CLEAR BUTTON
    if st.sidebar.button("🗑️ Start New Audit", use_container_width=True):
        st.session_state.logs = []
        st.rerun()
else:
    st.sidebar.info("No items logged yet.")


    st.info("No items logged yet. Use the buttons above to start.")
