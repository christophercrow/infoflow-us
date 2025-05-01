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

# --- Page Configuration (only here) ---
st.set_page_config(
    page_title="InfoFlow US Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Define Welcome Screen ---
def show_welcome():
    st.markdown("""
    <div style="text-align:center; padding:2rem 0;">
      <h1 style="font-size:3rem; margin-bottom:0.5rem;">🌐 InfoFlow US</h1>
      <p style="font-size:1.25rem; color:gray;">
        Explore how information spreads, how filter bubbles form, and what shapes our digital lives.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 Get Started")
    st.write(
        "Use the **sidebar** on the left to choose a simulation module and begin your interactive journey."
    )
    st.write(
        "Each module includes:\n"
        "- Clear definitions & examples\n"
        "- Interactive sliders and visualizations\n"
        "- A quick quiz with feedback\n"
        "- An optional reflection prompt\n"
    )

# --- Sidebar with Home + Modules ---
with st.sidebar:
    st.markdown("## 📑 Menu")
    # Create an ordered list, first 'Home'
    pages = {
        "🏠 Home": show_welcome,
        "🗞️ Filter Bubbles": filter_bubbles.run,
        "⚖️ Epistemic Injustice": epistemic_injustice.run,
        "💰 Surveillance Capitalism": surveillance_capitalism.run,
        "⚙️ Algorithmic Autonomy": algorithmic_autonomy.run,
        "🔒 Privacy & Consent": privacy_consent.run,
        "🔊 Echo Chamber Dynamics": echo_chamber.run
    }

    # Let the user pick
    page_titles = list(pages.keys())
    selection = st.radio(
        label="",
        options=page_titles,
        index=0,
        format_func=lambda t: t  # icons already included
    )

    st.markdown("---")
    st.caption("© 2025 InfoFlow US Project")

# --- Main Content ---
st.markdown("<div style='padding:1rem'>", unsafe_allow_html=True)
pages[selection]()
st.markdown("</div>", unsafe_allow_html=True)
