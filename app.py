import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3 
import json
import os
import textwrap
import datetime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # built-in in Python 3.9+
import base64
import requests

#import gspread
# Define subcategories globally
SUBCATEGORIES = ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"]
TIMEZONE = ZoneInfo("America/Los_Angeles")  # change to your desired timezone

# -----------------------------
# File paths
# -----------------------------
CIV_FILE = "civilizations.json"
MESSAGES_FILE = "messages.json"
EVENTS_FILE = "events.json"
USERS_FILE = "users.json"

# -----------------------------
# Load or initialize data
# -----------------------------
if not os.path.exists(CIV_FILE):
    SUBCATEGORIES = ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"]
    default_civilizations = {
    "Qin": {
        "Political": ["emperor", "Legalism", "centralized"],
        "Economic": ["currency"],
        "Religious": ["Confucianism"],
        "Societal": ["forced labor", "warriors valued"],
        "Intellectual": ["script"],
        "Artistic": ["Terracotta Army"],
        "Near": ["India"]
    },
    "Han": {
        "Political": ["Confucian bureaucracy", "centralized", "emperor"],
        "Economic": ["Silk Road"],
        "Religious": ["Confucianism"],
        "Societal": ["civil exams", "warriors valued"],
        "Intellectual": ["paper"],
        "Artistic": ["records"],
        "Near": ["Rome", "India"]
    },
    "Rome": {
        "Political": ["Senate", "emperor", "regional", "centralized"],
        "Economic": ["Mediterranean trade", "agriculture"],
        "Religious": ["polytheism"],
        "Societal": ["slavery", "warriors valued"],
        "Intellectual": ["law codes"],
        "Artistic": ["Colosseum"],
        "Near": ["Han"]
    },
    "Greece": {
        "Political": ["city-states", "democracy (Athens)", "regional"],
        "Economic": ["Mediterranean trade", "agriculture"],
        "Religious": ["polytheism"],
        "Societal": ["slavery", "intellectuals valued", "warriors valued"],
        "Intellectual": ["philosophy", "math", "geometry", "architecture"],
        "Artistic": ["Parthenon", "religious"],
        "Near": ["Rome"]
    },
    "Maurya": {
        "Political": ["centralized", "monarchy"],
        "Economic": ["trade"],
        "Religious": ["Buddhism"],
        "Societal": ["caste system"],
        "Intellectual": ["Arthashastra", "math"],
        "Artistic": ["stupas"],
        "Near": ["Hellenistic"]
    },
    "Gupta": {
        "Political": ["monarchy", "regional"],
        "Economic": ["Silk Road"],
        "Religious": ["Hinduism"],
        "Societal": ["caste system"],
        "Intellectual": ["math"],
        "Artistic": ["Ajanta caves"],
        "Near": ["Rome"]
    },
    "Egypt": {
        "Political": ["pharaohs"],
        "Economic": ["Nile agriculture"],
        "Religious": ["polytheism"],
        "Societal": ["hierarchy"],
        "Intellectual": ["hieroglyphics", "architecture"],
        "Artistic": ["pyramids"],
        "Near": ["Mesopotamia"]
    },
    "Babylon": {
        "Political": ["monarchy", "centralized"],
        "Economic": ["trade"],
        "Religious": ["polytheism"],
        "Societal": ["class divisions"],
        "Intellectual": ["astronomy"],
        "Artistic": ["Ishtar Gate"],
        "Near": ["India"]
    },
    "Persia": {
        "Political": ["monarchy", "centralized"],
        "Economic": ["coinage"],
        "Religious": ["Zoroastrianism"],
        "Societal": ["multicultural empire"],
        "Intellectual": ["engineering"],
        "Artistic": ["Persepolis"],
        "Near": ["Greece", "India"]
    },
    "Umayya": {
        "Political": ["centralized", "caliphate"],
        "Economic": ["agriculture", "Indian Ocean trade"],
        "Religious": ["Islam", "tolerant"],
        "Societal": ["gender equality", "warriors valued", "merchants valued"],
        "Intellectual": ["borrowed", "architecture"],
        "Artistic": ["religious", "colorful", "mosaics"],
        "Near": ["Indonesia", "India", "Persia", "Byzantines"]
    }
}


    with open(CIV_FILE, "w") as f:
        json.dump(default_civilizations, f, indent=2)

# Load the current data
with open(CIV_FILE, "r") as f:
    civilizations = json.load(f)

if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
    with open(MESSAGES_FILE, "w") as f:
        json.dump([], f)  # initialize as empty list
    messages = []
else:
    with open(MESSAGES_FILE, "r") as f:
        try:
            messages = json.load(f)
            if not isinstance(messages, list):
                messages = []  # ensure it’s a list
        except json.JSONDecodeError:
            messages = []

if not os.path.exists(EVENTS_FILE) or os.path.getsize(EVENTS_FILE) == 0:
    with open(EVENTS_FILE, "w") as f:
        json.dump([], f)   # initialize as empty list
    events = []
else:
    with open(EVENTS_FILE, "r") as f:
        try:
            events = json.load(f)
            if not isinstance(events, list):
                events = []  # ensure it's always a list
        except json.JSONDecodeError:
            events = []

if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)
    users = {}
else:
    with open(USERS_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}

# -----------------------------
# Helper functions
# -----------------------------
import pandas as pd

SHEET_URL = "https://docs.google.com/spreadsheets/d/1kPbvMwDIqnbk-uN3PmXx-NOWqafVvX-VSUZlUPBBoFY/pub?output=csv"

def push_to_github(file_path=CIV_FILE, message="Update civilizations.json"):
    """Push updated JSON to GitHub repo."""
    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]
    branch = st.secrets["github"].get("branch", "main")

    # Read file
    with open(file_path, "rb") as f:
        content = f.read()
    b64_content = base64.b64encode(content).decode("utf-8")

    # GitHub API URL
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

    # Get current file SHA (needed for update)
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers, params={"ref": branch})
    sha = r.json().get("sha") if r.status_code == 200 else None

    # Prepare payload
    data = {
        "message": message,
        "content": b64_content,
        "branch": branch,
    }
    if sha:
        data["sha"] = sha

    # Commit to GitHub
    r = requests.put(url, headers=headers, json=data)
    try:
        resp_json = r.json()
    except Exception:
        resp_json = {"text": r.text}

    if r.status_code in (200, 201):
        st.sidebar.success("Changes pushed to GitHub! (Saved forever!)")
    else:
        st.sidebar.error(f"GitHub push failed ({r.status_code}): {resp_json}")
        
def push_users(file_path=USERS_FILE, message="Update users.json"):
    """Push updated JSON to GitHub repo."""
    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]
    branch = st.secrets["github"].get("branch", "main")

    # Read file
    with open(file_path, "rb") as f:
        content = f.read()
    b64_content = base64.b64encode(content).decode("utf-8")

    # GitHub API URL
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

    # Get current file SHA (needed for update)
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers, params={"ref": branch})
    sha = r.json().get("sha") if r.status_code == 200 else None

    # Prepare payload
    data = {
        "message": message,
        "content": b64_content,
        "branch": branch,
    }
    if sha:
        data["sha"] = sha

    # Commit to GitHub
    r = requests.put(url, headers=headers, json=data)
    try:
        resp_json = r.json()
    except Exception:
        resp_json = {"text": r.text}

def push_messages(file_path=MESSAGES_FILE, message="Update messages.json"):
    """Push messages.json to GitHub."""
    try:
        # Read GitHub secrets
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"].get("branch", "main")

        # Ensure messages.json exists
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, "w") as f:
                json.dump([], f)

        # Read file content and encode
        with open(file_path, "rb") as f:
            content = f.read()
        b64_content = base64.b64encode(content).decode("utf-8")

        # GitHub API URL
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

        # Get current SHA (needed for update)
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers, params={"ref": branch})
        sha = r.json().get("sha") if r.status_code == 200 else None

        # Prepare payload
        data = {"message": message, "content": b64_content, "branch": branch}
        if sha:
            data["sha"] = sha

        # Commit to GitHub
        r = requests.put(url, headers=headers, json=data)
        r.raise_for_status()  # Raise error if status is not 200/201

        st.sidebar.success("messages.json pushed successfully!")

    except Exception as e:
        st.sidebar.error(f"GitHub push failed: {e}")

def push_events(file_path=EVENTS_FILE, message="Update events.json"):
    """Push events.json to GitHub."""
    try:
        # Read GitHub secrets
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"].get("branch", "main")

        # Ensure events.json exists and is valid
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, "w") as f:
                json.dump([], f)

        # Read file content and encode
        with open(file_path, "rb") as f:
            content = f.read()
        b64_content = base64.b64encode(content).decode("utf-8")

        # GitHub API URL
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

        # Get current SHA (needed for update)
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers, params={"ref": branch})
        sha = r.json().get("sha") if r.status_code == 200 else None

        # Prepare payload
        data = {"message": message, "content": b64_content, "branch": branch}
        if sha:
            data["sha"] = sha

        # Commit to GitHub
        r = requests.put(url, headers=headers, json=data)
        r.raise_for_status()  # Raise error if status is not 200/201

        st.sidebar.success("events.json pushed successfully!")

    except Exception as e:
        st.sidebar.error(f"GitHub push failed: {e}")
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        civilizations = {}
        for _, row in df.iterrows():
            civ = row["Civilization"]
            sub = row["Subcategory"]
            items = [i.strip() for i in str(row["Items"]).split(",") if i.strip()]
            civilizations.setdefault(civ, {})[sub] = items
        return civilizations
    except Exception:
        return {}  # empty if sheet is blank
        
def load_events():
    """Safely load events.json and always return a list."""
    if not os.path.exists(EVENTS_FILE) or os.path.getsize(EVENTS_FILE) == 0:
        with open(EVENTS_FILE, "w") as f:
            json.dump([], f)
        return []
    else:
        with open(EVENTS_FILE, "r") as f:
            try:
                events = json.load(f)
                if not isinstance(events, list):
                    return []
                return events
            except json.JSONDecodeError:
                return []

def save_event(action, user=None):
    events = load_events()
    # Get current time in desired timezone
    now = datetime.now(TIMEZONE)
    timestamp = now.strftime("%m-%d %H:%M")  # month-day hour:minute
    events.append({
        "time": timestamp,
        "action": action,
        "user": user if user else "Unknown"
    })
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)
        import gspread

# authenticate once with your credentials.json
#gc = gspread.service_account(filename="credentials.json")
#sh = gc.open("CivilizationsDB")   # Sheet name
#worksheet = sh.sheet1

def save_data():
    # Flatten dict into rows
    #rows = []
    #for civ, subs in civilizations.items():
    #    for sub, items in subs.items():
    #        rows.append([civ, sub, ", ".join(items)])

    # Rewrite the sheet
    #worksheet.clear()
    #worksheet.append_row(["Civilization", "Subcategory", "Items"])  # header
    #worksheet.append_rows(rows)
    with open(CIV_FILE, "w") as f:
        json.dump(civilizations, f, indent=2)

def save_messages():
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def save_event(action, user=None):
    events = load_events()
    events.append({
        "time": datetime.now().strftime("%m-%d %H:%M"),
        "action": action,
        "user": user if user else "Unknown"
    })
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)
        
def save_categories():
    with open(CIV_FILE, "w") as f:
        json.dump(categories, f, indent=2)
# -----------------------------
# Session state for email
# -----------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

st.sidebar.text_input("Enter your email (sign in):", key="user_email")

if st.session_state["user_email"]:
    email = st.session_state["user_email"].strip()
    if email in users:
        # Load existing nickname into session_state
        st.session_state["nickname"] = users[email]
    else:
        with st.sidebar.form("nickname_form"):
            new_nick = st.text_input("Choose a nickname")
            submitted = st.form_submit_button("Save Nickname")
            if submitted and new_nick.strip():
                users[email] = new_nick.strip()
                save_users()
                push_users()
                st.session_state["nickname"] = new_nick.strip()  # <-- store in session_state
                st.sidebar.success(f"Nickname '{st.session_state['nickname']}' saved!")


# -----------------------------
# Sidebar tabs
# -----------------------------
tab_choice = st.sidebar.radio("Sidebar Options", ["Civilizations", "Chat", "Event Log"])

# -----------------------------
# Civilization Editor Tab
# -----------------------------
if tab_choice == "Civilizations":
    st.sidebar.subheader("Add Civilization")
    new_civ = st.sidebar.text_input("Civilization Name", key="add_civ")
    if st.sidebar.button("Add Civilization"):
        if new_civ and new_civ not in civilizations:
            civilizations[new_civ] = {sub: [] for sub in ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"]}
            save_data()
            push_to_github()
            user = st.session_state.get("nickname", "Unknown")
            save_event(f"Added the '{new_civ}' civilization", user=user)
            push_events()
            st.sidebar.success(f"Civilization '{new_civ}' added!")

    st.sidebar.subheader("Delete Civilization")
    if civilizations:
        delete_civ = st.sidebar.selectbox("Choose Civilization", list(civilizations.keys()), key="delete_civ")
        if st.sidebar.button("Delete Civilization"):
            del civilizations[delete_civ]
            save_data()
            push_to_github()
            user = st.session_state.get("nickname", "Unknown")
            save_event(f"Deleted the '{delete_civ}' civilization", user=user)
            push_events()
            st.sidebar.success(f"Civilization '{delete_civ}' deleted!")

    st.sidebar.subheader("Edit Civilization")
    if civilizations:
        edit_civ = st.sidebar.selectbox(
            "Choose Civilization to Edit", 
            list(civilizations.keys()), 
            key="edit_civ"
        )
        edit_sub = st.sidebar.selectbox(
            "Choose Subcategory", 
            ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"], 
            key="edit_sub"
        )
        current_items = civilizations[edit_civ][edit_sub]
        new_items = st.sidebar.text_area(
            "Enter items (comma-separated)", 
            ", ".join(current_items), 
            key="edit_items"
        )
    
        # Custom HTML button (green)
        save_button = st.sidebar.markdown(
            """
            <style>
            .green-btn {
                background-color: #28a745;
                color: white;
                border: white;
                border-radius: 8px;
                padding: 0.6em 1em;
                font-weight: thin;
                cursor: grab;
                text-align: center;
                display: inline-block;
            }
            .green-btn:hover {
                background-color: #218838;
                border: white;
                curson: grabbing;
            }
            </style>
            <form action="" method="get">
                <button class="green-btn" type="submit" name="save" value="1">Save Changes (NECESSARY)</button>
            </form>
            """,
            unsafe_allow_html=True
        )
    
        # Detect click by query param
        if st.query_params.get("save") == "1":
            civilizations[edit_civ][edit_sub] = [i.strip() for i in new_items.split(",") if i.strip()]
            save_data()
            push_to_github(message=f"Updated {edit_sub} for {edit_civ}")
            user = st.session_state.get("nickname", "Unknown")
            save_event(f"Edited subcategory '{edit_sub}' in '{edit_civ}'", user=user)
            push_events()
            st.toast(f"Updated {edit_sub} for {edit_civ}")
            # clear query param so it doesn't re-trigger
            st.query_params["save"] = None






    
    
        
    
    st.sidebar.subheader("Backup / Restore")
    st.sidebar.download_button(
        label="Download JSON",
        data=json.dumps(civilizations, indent=2),
        file_name="civilizations.json",
        mime="application/json"
    )
    uploaded_file = st.sidebar.file_uploader("Upload JSON to restore", type=["json"])
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            if isinstance(data, dict):
                civilizations = data
                save_data()
                push_to_github()
                st.sidebar.success("Data restored from JSON!")
                save_event("Civilizations restored from uploaded JSON")
                push_events()
            else:
                st.sidebar.error("Invalid JSON format.")
        except Exception as e:
            st.sidebar.error(f"Error reading JSON: {e}")

# -----------------------------
# Chat Tab
# -----------------------------
elif tab_choice == "Chat":
    st.sidebar.subheader("Shared Message Board")

    # --- Load messages safely ---
    if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
        with open(MESSAGES_FILE, "w") as f:
            json.dump([], f)
        messages = []
    else:
        with open(MESSAGES_FILE, "r") as f:
            try:
                messages = json.load(f)
                if not isinstance(messages, list):
                    messages = []
            except json.JSONDecodeError:
                messages = []

    # --- Current time ---
    now = datetime.now(TIMEZONE)
    three_days_ago = now - timedelta(days=3)

    # --- Filter messages from the last 3 days ---
    recent_messages = []
    for m in messages:
        ts_str = m.get("time", "").strip()
        ts = None
        for fmt in ("%m-%d %H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                if fmt == "%m-%d %H:%M":
                    ts_naive = datetime.strptime(f"{now.year}-{ts_str}", "%Y-%m-%d %H:%M")
                else:
                    ts_naive = datetime.strptime(ts_str, fmt)
                ts = ts_naive.replace(tzinfo=TIMEZONE)
                break
            except ValueError:
                continue
        if ts and ts >= three_days_ago:
            recent_messages.append(m)

    # Overwrite messages with only recent ones
    messages = recent_messages
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

    # --- Display recent messages ---
    if recent_messages:
        for msg in reversed(recent_messages):
            st.sidebar.markdown(f"**{msg['user']}** [{msg['time']}]: {msg['text']}")
    else:
        st.sidebar.info("No recent messages (messages auto-expire after 3 days).")

    # --- Chat input form ---
    if "nickname" in st.session_state and st.session_state["nickname"]:
        with st.sidebar.form("message_form", clear_on_submit=True):
            text = st.text_area("Your message", key="chat_text")
            submitted = st.form_submit_button("Send")
            if submitted and text:
                ts = datetime.now(TIMEZONE).strftime("%m-%d %H:%M")
                msg = {
                    "user": st.session_state["nickname"],
                    "text": text.strip(),
                    "time": ts
                }
                messages.append(msg)

                # --- Save locally ---
                with open(MESSAGES_FILE, "w") as f:
                    json.dump(messages, f, indent=2)

                # --- Push to GitHub ---
                push_messages(message=f"{st.session_state['nickname']} sent a message")

                st.sidebar.success("Message posted!")
    else:
        st.sidebar.info("Enter your email and choose a nickname to chat.")
# -----------------------------
# Event Log Tab
# -----------------------------
elif tab_choice == "Event Log":
    st.sidebar.subheader("Permanent Event Log")
    
    # Show events
    if events:
        for ev in reversed(events):
            user = ev.get("user", "Unknown")
            st.sidebar.markdown(f"- {ev['time']} — **{user}**: {ev['action']}")
    else:
        st.sidebar.info("No events logged yet.")
    
    # --- Admin ctrls ---
    ADMIN_EMAIL = "ncobb@cusd.me"  
    if st.session_state.get("user_email") == ADMIN_EMAIL:
        st.sidebar.markdown("---")
        st.sidebar.write("Admin Controls")
        confirm_clear = st.sidebar.checkbox("Confirm clearing the event log", key="confirm_clear")
        if confirm_clear and st.sidebar.button("Clear Event Log"):
            events.clear()
            with open(EVENTS_FILE, "w") as f:
                json.dump(events, f, indent=2)
            st.sidebar.success("Event log cleared!")
        custom_event = st.sidebar.text_input("Custom Event", key="cust-evnt")
        if st.sidebar.button("Create custom event"):
            save_event(custom_event, "Nico")
            push_events()


# --- Main panel: Venn diagram ---
st.title("Ancient Civilizations Venn Diagram")

# Subcategory selection
subcat = st.selectbox("Select subcategory to compare:", SUBCATEGORIES)

# Civilization selection
selected_civs = st.multiselect("Select 2-3 civilizations:", list(civilizations.keys()))

def plot_venn(selected_civs, subcat):
    sets = [set(civilizations[c][subcat]) for c in selected_civs]
    plt.figure(figsize=(8, 8))
    
    if len(sets) == 2:
        v = venn2(sets, set_labels=selected_civs)
        regions = {
            "10": sets[0] - sets[1],
            "01": sets[1] - sets[0],
            "11": sets[0] & sets[1],
        }
    elif len(sets) == 3:
        v = venn3(sets, set_labels=selected_civs)
        regions = {
            "100": sets[0] - sets[1] - sets[2],
            "010": sets[1] - sets[0] - sets[2],
            "001": sets[2] - sets[0] - sets[1],
            "110": (sets[0] & sets[1]) - sets[2],
            "101": (sets[0] & sets[2]) - sets[1],
            "011": (sets[1] & sets[2]) - sets[0],
            "111": sets[0] & sets[1] & sets[2],
        }
    else:
        st.warning("Select 2 or 3 civilizations to compare.")
        return

    # Update labels with items
    for region_code, elements in regions.items():
        label = v.get_label_by_id(region_code)
        if label:
            if elements:
                label.set_text("\n".join(textwrap.wrap(", ".join(elements), width=30)))
            else:
                label.set_text("")
    
    st.pyplot(plt)

if len(selected_civs) >= 2:
    plot_venn(selected_civs, subcat)
else:
    st.info("Select at least 2 civilizations to generate a Venn diagram.")
