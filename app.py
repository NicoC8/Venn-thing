import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import json
import os
import textwrap

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
selected_civs = st.multiselect("Select 2-3 civilizations:", list(civilizations.keys()), default=list(civilizations.keys())[:2])

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
