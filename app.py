import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import json
import os
import textwrap
import datetime
# --- Files ---
MESSAGES_FILE = "messages.json"
EVENTS_FILE = "events.json"

# --- Load messages (expire after 3 days) ---
if os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = []

def save_messages():
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

# Filter old messages
now = datetime.datetime.now()
messages = [
    m for m in messages
    if (now - datetime.datetime.strptime(m["time"], "%Y-%m-%d %H:%M:%S")).days < 3
]
save_messages()

# --- Load permanent event log ---
if os.path.exists(EVENTS_FILE):
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
else:
    events = []

def save_event(action: str):
    """Record a permanent event with timestamp."""
    events.append({
        "action": action,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)

# --- Sidebar Tabs ---
tab_choice = st.sidebar.radio("📂 Sidebar Options", ["💬 Chat", "📜 Event Log"])

# --- Chat Tab ---
if tab_choice == "💬 Chat":
    st.sidebar.subheader("💬 Shared Message Board")

    if messages:
        for msg in reversed(messages):
            st.sidebar.markdown(
                f"**{msg['user']}** [{msg['time']}]: {msg['text']}"
            )
    else:
        st.sidebar.info("No recent messages (messages auto-expire after 3 days).")

    # Chat form
    with st.sidebar.form("message_form", clear_on_submit=True):
        user = st.text_input("Your name")
        text = st.text_area("Your message")
        submitted = st.form_submit_button("Send")
        if submitted and user and text:
            msg = {
                "user": user.strip(),
                "text": text.strip(),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            messages.append(msg)
            save_messages()
            st.sidebar.success("Message posted!")

# --- Event Log Tab ---
elif tab_choice == "📜 Event Log":
    st.sidebar.subheader("📜 Permanent Event Log")
    if events:
        for ev in reversed(events):
            st.sidebar.markdown(f"- {ev['time']}: {ev['action']}")
    else:
        st.sidebar.info("No events logged yet.")

# --- Constants ---
JSON_FILE = "civilizations.json"
SUBCATEGORIES = ["Political", "Economic", "Religious", "Societal", "Intellectual", "Artistic", "Near"]

# --- Load or initialize data ---
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r") as f:
        civilizations = json.load(f)
else:
    civilizations = {}  # { "Qin": { "Political": [], ... } }

def save_data():
    with open(JSON_FILE, "w") as f:
        json.dump(civilizations, f, indent=2)

# --- Sidebar: Manage civilizations ---
st.sidebar.title("Civilizations Editor")

# Add new civilization
new_civ = st.sidebar.text_input("Add new civilization:")
if new_civ:
    if new_civ not in civilizations:
        civilizations[new_civ] = {sub: [] for sub in SUBCATEGORIES}
        save_data()
        st.sidebar.success(f"Added {new_civ}")

# Select civilization to edit
edit_civ = st.sidebar.selectbox("Select civilization to edit:", [""] + list(civilizations.keys()))
if edit_civ:
    for sub in SUBCATEGORIES:
        items = st.sidebar.text_area(f"{edit_civ} - {sub}", value=", ".join(civilizations[edit_civ][sub]))
        civilizations[edit_civ][sub] = [i.strip() for i in items.split(",") if i.strip()]
    save_data()

# Delete civilization
delete_civ = st.sidebar.selectbox("Delete civilization:", [""] + list(civilizations.keys()))
if delete_civ:
    if st.sidebar.button(f"Delete {delete_civ}"):
        civilizations.pop(delete_civ)
        save_data()
        st.sidebar.warning(f"{delete_civ} deleted.")

# --- JSON Export / Import ---
st.sidebar.markdown("---")
st.sidebar.subheader("Backup / Restore")

# Download button
if civilizations:
    st.sidebar.download_button(
        label="Download JSON",
        data=json.dumps(civilizations, indent=2),
        file_name="civilizations.json",
        mime="application/json"
    )

# Upload button
uploaded_file = st.sidebar.file_uploader("Upload JSON to restore", type=["json"])
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        if isinstance(data, dict):
            civilizations = data
            save_data()
            st.sidebar.success("Data restored from JSON!")
        else:
            st.sidebar.error("Invalid JSON format.")
    except Exception as e:
        st.sidebar.error(f"Error reading JSON: {e}")

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
