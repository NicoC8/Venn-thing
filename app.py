import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import json
import os
import textwrap
import datetime

import os
import json
import datetime
import streamlit as st

# Define subcategories globally
SUBCATEGORIES = ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"]

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
if os.path.exists(CIV_FILE):
    with open(CIV_FILE, "r") as f:
        civilizations = json.load(f)
else:
    civilizations = {}  # { civ_name: { subcategory: [items] } }

if os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = []

if os.path.exists(EVENTS_FILE):
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
else:
    events = []

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# -----------------------------
# Helper functions
# -----------------------------

def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            events = json.load(f)
        # Ensure all events have a "user" field
        for ev in events:
            if "user" not in ev:
                ev["user"] = "Unknown"
        return events
    return []

def save_event(action, user=None):
    events = load_events()
    events.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "user": user if user else "Unknown"
    })
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)
        
def save_data():
    with open(CIV_FILE, "w") as f:
        json.dump(civilizations, f, indent=2)

def save_messages():
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def save_event(action, user=None):
    events = load_events()
    events.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "user": user if user else "Unknown"
    })
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# -----------------------------
# Session state for email
# -----------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

st.sidebar.text_input("Enter your email (sign in):", key="user_email")

nickname = None
if st.session_state["user_email"]:
    email = st.session_state["user_email"].strip()
    if email in users:
        nickname = users[email]
    else:
        with st.sidebar.form("nickname_form"):
            new_nick = st.text_input("Choose a nickname")
            submitted = st.form_submit_button("Save Nickname")
            if submitted and new_nick.strip():
                users[email] = new_nick.strip()
                save_users()
                nickname = users[email]
                st.sidebar.success(f"Nickname '{nickname}' saved!")

# -----------------------------
# Sidebar tabs
# -----------------------------
tab_choice = st.sidebar.radio("Sidebar Options", ["Civilizations", "Chat", "Event Log"])

# -----------------------------
# Civilization Editor Tab
# -----------------------------
if tab_choice == "Civilizations":
    st.sidebar.subheader("Add Civilization")
    new_civ = st.text_input("Civilization Name", key="add_civ")
    if st.sidebar.button("Add Civilization"):
        if new_civ and new_civ not in civilizations:
            civilizations[new_civ] = {sub: [] for sub in ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"]}
            save_data()
            user = st.session_state.get("nickname") or st.session_state.get("user_email", "Unknown")
            save_event(f"Edited subcategory '{edit_sub}' in '{edit_civ}'", user=user)
            st.sidebar.success(f"Civilization '{new_civ}' added!")

    st.sidebar.subheader("Delete Civilization")
    if civilizations:
        delete_civ = st.sidebar.selectbox("Choose Civilization", list(civilizations.keys()), key="delete_civ")
        if st.sidebar.button("Delete Civilization"):
            del civilizations[delete_civ]
            save_data()
            user = st.session_state.get("nickname") or st.session_state.get("user_email", "Unknown")
            save_event(f"Edited subcategory '{edit_sub}' in '{edit_civ}'", user=user)
            st.sidebar.success(f"Civilization '{delete_civ}' deleted!")

    st.sidebar.subheader("Edit Civilization")
    if civilizations:
        edit_civ = st.sidebar.selectbox("Choose Civilization to Edit", list(civilizations.keys()), key="edit_civ")
        edit_sub = st.sidebar.selectbox("Choose Subcategory", ["Political","Economic","Religious","Societal","Intellectual","Artistic","Near"], key="edit_sub")
        current_items = civilizations[edit_civ][edit_sub]
        new_items = st.sidebar.text_area("Enter items (comma-separated)", ", ".join(current_items), key="edit_items")
        if st.sidebar.button("Save Changes"):
            civilizations[edit_civ][edit_sub] = [i.strip() for i in new_items.split(",") if i.strip()]
            save_data()
            user = st.session_state.get("nickname") or st.session_state.get("user_email", "Unknown")
            save_event(f"Edited subcategory '{edit_sub}' in '{edit_civ}'", user=user)
            st.toast(f"Updated {edit_sub} for {edit_civ}")

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
                st.sidebar.success("Data restored from JSON!")
                save_event("Civilizations restored from uploaded JSON")
            else:
                st.sidebar.error("Invalid JSON format.")
        except Exception as e:
            st.sidebar.error(f"Error reading JSON: {e}")

# -----------------------------
# Chat Tab
# -----------------------------
elif tab_choice == "Chat":
    st.sidebar.subheader("Shared Message Board")

    # Remove messages older than 3 days
    now = datetime.datetime.now()
    messages[:] = [
        m for m in messages
        if (now - datetime.datetime.strptime(m["time"], "%Y-%m-%d %H:%M:%S")).days < 3
    ]
    save_messages()

    if messages:
        for msg in reversed(messages):
            st.sidebar.markdown(f"**{msg['user']}** [{msg['time']}]: {msg['text']}")
    else:
        st.sidebar.info("No recent messages (messages auto-expire after 3 days).")

    if nickname:
        with st.sidebar.form("message_form", clear_on_submit=True):
            text = st.text_area("Your message", key="chat_text")
            submitted = st.form_submit_button("Send")
            if submitted and text:
                msg = {
                    "user": nickname,
                    "text": text.strip(),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                messages.append(msg)
                save_messages()
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
    
    # --- Admin Clear Button ---
    ADMIN_EMAIL = "ncobb@cusd.me"  # change to your email
    if st.session_state.get("user_email") == ADMIN_EMAIL:
        st.sidebar.markdown("---")
        st.sidebar.write("Admin Controls")
        confirm_clear = st.sidebar.checkbox("Confirm clearing the event log", key="confirm_clear")
        if confirm_clear and st.sidebar.button("Clear Event Log"):
            events.clear()
            with open(EVENTS_FILE, "w") as f:
                json.dump(events, f, indent=2)
            st.sidebar.success("Event log cleared!")


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
