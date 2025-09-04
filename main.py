import os
import json
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import textwrap

# -------------------------
# Constants
# -------------------------
DATA_FILE = "civilizations.json"
subcats = ["Political", "Economic", "Religious", "Societal", "Intellectual", "Artistic", "Near"]

# -------------------------
# Helper: load/save data
# -------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        # Default civilizations if no file exists
        return {
            "Qin": {"Political": ["emperor", "Legalism"], "Economic": ["currency"], "Religious": ["Confucianism"],
                    "Societal": ["forced labor"], "Intellectual": ["script"], "Artistic": ["Terracotta Army"], "Near": ["Han"]},
            "Han": {"Political": ["Confucian bureaucracy"], "Economic": ["Silk Road"], "Religious": ["Confucianism"],
                    "Societal": ["civil exams"], "Intellectual": ["paper"], "Artistic": ["records"], "Near": ["Rome"]},
            "Rome": {"Political": ["Senate", "emperor"], "Economic": ["Mediterranean trade"], "Religious": ["polytheism"],
                     "Societal": ["slavery"], "Intellectual": ["law codes"], "Artistic": ["Colosseum"], "Near": ["Han"]},
            "Greece": {"Political": ["city-states"], "Economic": ["coinage"], "Religious": ["polytheism"],
                       "Societal": ["slavery"], "Intellectual": ["philosophy"], "Artistic": ["Parthenon"], "Near": ["Rome"]},
            "Maurya": {"Political": ["centralized monarchy"], "Economic": ["trade"], "Religious": ["Buddhism"],
                       "Societal": ["caste system"], "Intellectual": ["Arthashastra"], "Artistic": ["stupas"], "Near": ["Hellenistic"]},
            "Gupta": {"Political": ["monarchy"], "Economic": ["Silk Road"], "Religious": ["Hinduism"],
                      "Societal": ["caste system"], "Intellectual": ["decimal system"], "Artistic": ["Ajanta caves"], "Near": ["Rome"]},
            "Egypt": {"Political": ["pharaohs"], "Economic": ["Nile agriculture"], "Religious": ["polytheism"],
                      "Societal": ["hierarchy"], "Intellectual": ["hieroglyphics"], "Artistic": ["pyramids"], "Near": ["Mesopotamia"]},
            "Babylon": {"Political": ["monarchy"], "Economic": ["trade"], "Religious": ["polytheism"],
                        "Societal": ["class divisions"], "Intellectual": ["astronomy"], "Artistic": ["Ishtar Gate"], "Near": ["Persia"]},
            "Persia": {"Political": ["monarchy"], "Economic": ["coinage"], "Religious": ["Zoroastrianism"],
                       "Societal": ["multicultural empire"], "Intellectual": ["engineering"], "Artistic": ["Persepolis"], "Near": ["Greece"]}
        }

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.civilizations, f, indent=4)

# -------------------------
# Load civilizations
# -------------------------
if "civilizations" not in st.session_state:
    st.session_state.civilizations = load_data()

# -------------------------
# Sidebar Editor
# -------------------------
st.sidebar.header("Edit Civilizations")

# Add new civilization
new_civ = st.sidebar.text_input("Add a new civilization:")
if st.sidebar.button("Add Civilization") and new_civ:
    if new_civ not in st.session_state.civilizations:
        st.session_state.civilizations[new_civ] = {sub: [] for sub in subcats}
        save_data()
        st.success(f"Added {new_civ}")
    else:
        st.warning(f"{new_civ} already exists")

# Select civilization to edit
selected_civ = st.sidebar.selectbox("Select Civilization to Edit", list(st.session_state.civilizations.keys()))
if st.sidebar.button("Delete Civilization"):
    st.session_state.civilizations.pop(selected_civ, None)
    save_data()
    st.sidebar.success(f"Deleted {selected_civ}")
    st.experimental_rerun()

# Editable subcategories
st.sidebar.subheader(f"Edit {selected_civ}")
for sub in subcats:
    items_str = ", ".join(st.session_state.civilizations[selected_civ][sub])
    updated = st.sidebar.text_area(sub, value=items_str, height=50)
    st.session_state.civilizations[selected_civ][sub] = [i.strip() for i in updated.split(",") if i.strip()]
save_data()

# -------------------------
# Main Panel: Venn Diagram
# -------------------------
st.title("📘 Ancient Civilizations Venn Organizer")

# Subcategory to compare
subcategory = st.selectbox("Choose a subcategory to compare:", subcats)

# Select 2 or 3 civilizations
selected_civs = st.multiselect("Select 2 or 3 civilizations:", list(st.session_state.civilizations.keys()), default=["Qin", "Han"])

if 2 <= len(selected_civs) <= 3:
    sets = [set(st.session_state.civilizations[c][subcategory]) for c in selected_civs]

    plt.figure(figsize=(10, 10))
    if len(sets) == 2:
        v = venn2(sets, set_labels=selected_civs)
        regions = {'10': sets[0]-sets[1], '01': sets[1]-sets[0], '11': sets[0]&sets[1]}
    else:
        v = venn3(sets, set_labels=selected_civs, alpha=0.8)
        regions = {
            '100': sets[0]-sets[1]-sets[2],
            '010': sets[1]-sets[0]-sets[2],
            '001': sets[2]-sets[0]-sets[1],
            '110': (sets[0]&sets[1])-sets[2],
            '101': (sets[0]&sets[2])-sets[1],
            '011': (sets[1]&sets[2])-sets[0],
            '111': sets[0]&sets[1]&sets[2]
        }

    for region_code, elements in regions.items():
        label = v.get_label_by_id(region_code)
        if label:
            if elements:
                wrapped = "\n".join(textwrap.wrap(", ".join(elements), width=25))
                label.set_text(wrapped)
            else:
                label.set_text("")

    st.pyplot(plt)

elif len(selected_civs) > 3:
    st.error("Please select no more than 3 civilizations.")
else:
    st.info("Please select at least 2 civilizations.")
