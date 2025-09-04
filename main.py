import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import textwrap

# -------------------------
# Initialize session state
# -------------------------
if "civilizations" not in st.session_state:
    st.session_state.civilizations = {
        "Qin": {
            "Political": ["emperor", "Legalism", "centralized bureaucracy"],
            "Economic": ["standardized weights", "currency"],
            "Religious": ["Confucianism"],
            "Societal": ["forced labor"],
            "Intellectual": ["standardized script"],
            "Artistic": ["Terracotta Army"],
            "Near": ["influence on Han"]
        },
        "Han": {
            "Political": ["Confucian bureaucracy", "emperor"],
            "Economic": ["Silk Road trade"],
            "Religious": ["Confucianism", "Daoism"],
            "Societal": ["civil service exams"],
            "Intellectual": ["paper invention"],
            "Artistic": ["historical records"],
            "Near": ["contact with Rome via trade"]
        },
        "Rome": {
            "Political": ["Senate", "emperor"],
            "Economic": ["Mediterranean trade"],
            "Religious": ["polytheism", "Christianity"],
            "Societal": ["slavery"],
            "Intellectual": ["law codes"],
            "Artistic": ["Colosseum", "aqueducts"],
            "Near": ["contact with Han via Silk Road"]
        },
        "Greece": {
            "Political": ["city-states", "democracy (Athens)", "oligarchy (Sparta)"],
            "Economic": ["Mediterranean trade", "coinage"],
            "Religious": ["polytheism", "Olympian gods", "oracles"],
            "Societal": ["slavery", "citizenship limited to men"],
            "Intellectual": ["philosophy (Plato, Aristotle, Socrates)", "geometry", "medicine"],
            "Artistic": ["Parthenon", "drama", "sculpture"],
            "Near": ["influence on Rome"]
        },
        "Maurya": {
            "Political": ["centralized monarchy", "Ashoka’s rule", "bureaucracy"],
            "Economic": ["agriculture", "trade networks", "taxation"],
            "Religious": ["Buddhism", "Hinduism", "religious tolerance under Ashoka"],
            "Societal": ["caste system", "urban centers"],
            "Intellectual": ["Arthashastra (treatise on statecraft)"],
            "Artistic": ["stone pillars", "stupas"],
            "Near": ["contacts with Hellenistic kingdoms"]
        },
        "Gupta": {
            "Political": ["regional administration", "monarchy"],
            "Economic": ["Silk Road trade", "golden coins"],
            "Religious": ["Hinduism", "Buddhism", "revival of Hindu temples"],
            "Societal": ["caste system", "patriarchal society"],
            "Intellectual": ["decimal system", "concept of zero", "astronomy"],
            "Artistic": ["Ajanta caves", "classical Sanskrit literature"],
            "Near": ["trade with Rome and China"]
        },
        "Egypt": {
            "Political": ["pharaohs", "theocracy"],
            "Economic": ["Nile agriculture", "grain surplus", "trade with Nubia"],
            "Religious": ["polytheism", "pyramids as tombs", "afterlife belief"],
            "Societal": ["hierarchy with pharaoh at top", "slavery"],
            "Intellectual": ["hieroglyphics", "mathematics", "medicine"],
            "Artistic": ["pyramids", "temples", "sphinx"],
            "Near": ["interactions with Mesopotamia"]
        },
        "Babylon": {
            "Political": ["Hammurabi’s Code", "monarchy"],
            "Economic": ["Mesopotamian trade", "agriculture with irrigation"],
            "Religious": ["polytheism", "ziggurats"],
            "Societal": ["class divisions", "slavery"],
            "Intellectual": ["astronomy", "mathematics", "cuneiform writing"],
            "Artistic": ["Ishtar Gate", "hanging gardens (legendary)"],
            "Near": ["influence on Persia"]
        },
        "Persia": {
            "Political": ["monarchy", "satraps (regional governors)", "Royal Road administration"],
            "Economic": ["standardized coinage", "Royal Road trade", "agriculture"],
            "Religious": ["Zoroastrianism", "religious tolerance (Cyrus Cylinder)"],
            "Societal": ["multicultural empire", "slavery", "social hierarchy"],
            "Intellectual": ["engineering", "canals", "administrative records"],
            "Artistic": ["Persepolis palaces", "bas-reliefs"],
            "Near": ["conflicts with Greece", "influence on later empires"]
        }
    }

# -------------------------
# Subcategories
# -------------------------
subcats = ["Political", "Economic", "Religious", "Societal", "Intellectual", "Artistic", "Near"]

# -------------------------
# Sidebar: Civilization Editor
# -------------------------
st.sidebar.header("Edit Civilizations")

# Add new civilization
new_civ = st.sidebar.text_input("Add a new civilization:")
if st.sidebar.button("Add Civilization") and new_civ:
    if new_civ not in st.session_state.civilizations:
        st.session_state.civilizations[new_civ] = {sub: [] for sub in subcats}
        st.success(f"Added {new_civ}")
    else:
        st.warning(f"{new_civ} already exists")

# Select civilization to edit
selected_civ = st.sidebar.selectbox("Select Civilization to Edit", list(st.session_state.civilizations.keys()))
if st.sidebar.button("Delete Civilization"):
    st.session_state.civilizations.pop(selected_civ, None)
    st.sidebar.success(f"Deleted {selected_civ}")
    st.experimental_rerun()

# Editable subcategories
st.sidebar.subheader(f"Edit {selected_civ}")
for sub in subcats:
    items_str = ", ".join(st.session_state.civilizations[selected_civ][sub])
    updated = st.sidebar.text_area(sub, value=items_str, height=50)
    st.session_state.civilizations[selected_civ][sub] = [i.strip() for i in updated.split(",") if i.strip()]

# -------------------------
# Main Panel: Venn Diagram
# -------------------------
st.title("📘 Ancient Civilizations Venn Organizer")

# Subcategory to compare
subcategory = st.selectbox("Choose a subcategory to compare:", subcats)

# Select 2 or 3 civilizations
selected_civs = st.multiselect(
    "Select 2 or 3 civilizations for the Venn diagram:",
    list(st.session_state.civilizations.keys()),
    default=list(st.session_state.civilizations.keys())[:2]
)

if 2 <= len(selected_civs) <= 3:
    sets = [set(st.session_state.civilizations[c][subcategory]) for c in selected_civs]

    plt.figure(figsize=(10, 10))
    if len(sets) == 2:
        v = venn2(sets, set_labels=selected_civs)
        regions = {
            '10': sets[0] - sets[1],
            '01': sets[1] - sets[0],
            '11': sets[0] & sets[1]
        }
    else:
        v = venn3(sets, set_labels=selected_civs, alpha=0.8)
        regions = {
            '100': sets[0] - sets[1] - sets[2],
            '010': sets[1] - sets[0] - sets[2],
            '001': sets[2] - sets[0] - sets[1],
            '110': (sets[0] & sets[1]) - sets[2],
            '101': (sets[0] & sets[2]) - sets[1],
            '011': (sets[1] & sets[2]) - sets[0],
            '111': sets[0] & sets[1] & sets[2]
        }

    # Replace numbers with actual items
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