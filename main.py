# main.py

import streamlit as st
from modules import (
    filter_bubbles,
    epistemic_injustice,
    surveillance_capitalism,
    algorithmic_autonomy,
    privacy_consent,
    echo_chamber
)

# --- Page config ---
st.set_page_config(
    page_title="InfoFlow US Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Available pages ---
PAGES = {
    "🏠 Home": None,
    "🗞️ Filter Bubbles": filter_bubbles.run,
    "⚖️ Epistemic Injustice": epistemic_injustice.run,
    "💰 Surveillance Capitalism": surveillance_capitalism.run,
    "⚙️ Algorithmic Autonomy": algorithmic_autonomy.run,
    "🔒 Privacy & Consent": privacy_consent.run,
    "🔊 Echo Chamber Dynamics": echo_chamber.run,
}

# --- Initialize session state ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# --- Sidebar navigation ---
with st.sidebar:
    st.title("InfoFlow US")
    selection = st.radio(
        "Navigate to",
        options=list(PAGES.keys()),
        index=list(PAGES.keys()).index(st.session_state.current_page),
        format_func=lambda x: x
    )
    st.session_state.current_page = selection
    st.markdown("---")
    st.caption("© 2025 InfoFlow US Project")

# --- Home screen with module cards ---
def show_home():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
      <h1 style="font-size: 3rem; margin-bottom: 0.25rem;">🌐 InfoFlow US</h1>
      <p style="font-size: 1.2rem; color: #555;">
        Interactive simulations to explore how algorithms shape information flow,
        filter bubbles, echo chambers, and digital privacy.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🚀 Launch a Module")
    st.write("Click **Launch** on any module below to begin.")

    descriptions = {
        "🗞️ Filter Bubbles":           "See how personalization narrows your news feed and reduces diversity.",
        "⚖️ Epistemic Injustice":      "Explore who gets heard—and who remains unheard—in a data-driven model.",
        "💰 Surveillance Capitalism":   "Visualize the trade-off between data collection, personalization, and autonomy.",
        "⚙️ Algorithmic Autonomy":     "Experiment with recommendation settings to understand content diversity.",
        "🔒 Privacy & Consent":        "Decide which permissions to grant and see the impact on privacy.",
        "🔊 Echo Chamber Dynamics":    "Simulate network effects that amplify like-minded views.",
    }

    # render cards in rows of three
    keys = list(descriptions.keys())
    for i in range(0, len(keys), 3):
        cols = st.columns(3, gap="medium")
        for col, key in zip(cols, keys[i:i+3]):
            with col:
                st.markdown(f"### {key}")
                st.write(descriptions[key])
                if st.button("Launch", key=f"launch_{key}"):
                    st.session_state.current_page = key

# --- Main ---
st.markdown("<div style='padding:1rem'>", unsafe_allow_html=True)

page = st.session_state.current_page
if page == "🏠 Home":
    show_home()
else:
    # call the module’s run() function
    PAGES[page]()

st.markdown("</div>", unsafe_allow_html=True)
