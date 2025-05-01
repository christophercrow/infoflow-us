# modules/privacy_consent.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objs as go
from utils import init_quiz_state

def run():
    st.title("🔒 Privacy & Consent Simulator")

    # --- Relevant Readings for Module 6: Privacy ---
    with st.expander("📚 Readings for Module 6: Privacy", expanded=True):
        st.markdown("""
**Week 13: What Is the Problem?**  
- **Mon Mar 31** | “Update: Eye in the Sky,” *Radiolab*  
- **Mon Mar 31** | “A Modern Pascal’s Wager for Mass Electronic Surveillance,” *Danks*  
- **Wed Apr 2** | “The Surveillance Society: Information Technology and Bureaucratic Social Control,” *Gandy*  
- **Fri Apr 4** | Review Gandy  

**Week 14: Privacy Revisited**  
- **Mon Apr 7** | “Legitimacy and Automated Decisions: The Moral Limits of Algocracy,” *Chomanski*  
- **Wed Apr 9** | Review Chomanski  
- **Fri Apr 11** | “Protecting Data Privacy is Key to a Smart Energy Future,” *Véliz & Grunewald*  
        """)

    # --- Definitions & Context ---
    with st.expander("❓ What Are Privacy & Consent?"):
        st.markdown("""
**Privacy**: Your control over personal data—who collects it and how it's used.  
**Consent**: Your informed agreement to grant apps or services access to that data.

Good consent is **informed**, **specific**, and **revocable**.  
Poor consent requests often bundle unnecessary permissions, eroding privacy.
        """)
        st.info(
            "*Example:* A flashlight app that requests location and contacts in addition to camera access."
        )

    # --- Step 1: Select Permissions ---
    st.header("1️⃣ Select Permissions to Grant")
    permissions = {
        "Location":        {"weight": 1.5, "desc": "GPS, Wi-Fi, cell-tower data"},
        "Contacts":        {"weight": 2.0, "desc": "Address book & social connections"},
        "Camera":          {"weight": 1.8, "desc": "Photo & video access"},
        "Microphone":      {"weight": 1.8, "desc": "Audio recordings"},
        "App Usage Data":  {"weight": 1.0, "desc": "Which apps you use and when"},
        "Browsing History":{"weight": 1.2, "desc": "Websites & searches"}
    }
    granted = {}
    cols = st.columns(2)
    for i, (perm, info) in enumerate(permissions.items()):
        with cols[i % 2]:
            granted[perm] = st.checkbox(
                f"{perm} ({info['desc']})",
                value=False
            )

    # --- Reset on input change ---
    sig = (tuple(granted.values()),)
    if st.session_state.get("pc_sig") != sig:
        st.session_state["pc_sig"] = sig
        st.session_state["pc_run"] = False

    # --- Session-state initialization ---
    run_key     = "pc_run"
    metrics_key = "pc_metrics"
    perm_key    = "pc_perm_df"
    if run_key not in st.session_state:
        st.session_state[run_key]     = False
        st.session_state[metrics_key] = None
        st.session_state[perm_key]    = None

    # --- Step 2: Run Assessment ---
    if st.button("Assess Consent"):
        # Compute data footprint (%)
        total_w       = sum(info["weight"] for info in permissions.values())
        granted_w     = sum(permissions[p]["weight"] for p, ok in granted.items() if ok)
        footprint_pct = granted_w / total_w
        # Estimate personalized ads/day
        ads_per_day   = int(footprint_pct * np.random.uniform(20, 100))

        # Save metrics
        st.session_state[metrics_key] = {
            "footprint": footprint_pct,
            "ads": ads_per_day
        }

        # Build permission DataFrame
        df_perms = pd.DataFrame([
            {
                "Permission": perm,
                "Granted":    "✅" if ok else "❌"
            }
            for perm, ok in granted.items()
        ])
        st.session_state[perm_key] = df_perms
        st.session_state[run_key] = True

        # Initialize quiz
        init_quiz_state("privacy", correct_answer="Deny non-essential permissions")

    # --- Display Results ---
    if st.session_state[run_key]:
        metrics = st.session_state[metrics_key]
        df_perms = st.session_state[perm_key]

        # a) Data Footprint Gauge
        st.subheader("📊 Data Footprint")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics["footprint"] * 100,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1f77b4"},
                "steps": [
                    {"range": [0, 50], "color": "#E0F2FF"},
                    {"range": [50, 100], "color": "#A3D3FF"}
                ]
            },
            title={"text": "Personal Data Footprint"}
        ))
        fig_gauge.update_layout(height=300, margin={"t":50})
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("Higher percentage → more of your data is collected.")

        # b) Personalized Ads Metric
        st.subheader("💬 Personalized Ads per Day")
        st.metric(label="Ads / Day", value=metrics["ads"])

        # c) Permission Overview Table
        st.subheader("🔐 Permission Overview")
        st.table(df_perms)

        # d) Permission Distribution Pie
        st.subheader("🗂️ Granted vs. Denied Permissions")
        df_dist = df_perms["Granted"].value_counts().reset_index()
        df_dist.columns = ["Granted", "Count"]
        pie = alt.Chart(df_dist).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("Count", type="quantitative"),
            color=alt.Color("Granted", legend=None),
            tooltip=["Granted", "Count"]
        ).properties(width=300, height=300)
        st.altair_chart(pie, use_container_width=False)

        # e) Insights
        st.markdown("""
**Insights:**  
- Granting more permissions ↑ your data footprint and ↑ personalized ads.  
- Denying non-essential permissions helps protect your privacy and autonomy.
        """)

        # f) Quiz: Check Understanding
        st.subheader("❓ Quiz")
        question = "Which practice best protects your privacy?"
        options = {
            "Deny non-essential permissions": True,
            "Allow all permissions": False,
            "Permissions don't matter": False
        }
        choice = st.radio(question, list(options.keys()), key="pc_choice")
        if st.button("Submit Answer", key="pc_submit"):
            qs = st.session_state["privacy_quiz"]
            qs["submitted"] = True
            qs["correct"]   = options[choice]
            qs["choice"]    = choice
        if st.session_state["privacy_quiz"]["submitted"]:
            if st.session_state["privacy_quiz"]["correct"]:
                st.success("✅ Correct—only grant essential permissions to maintain privacy.")
            else:
                st.error("❌ Not quite—consider the impact of unnecessary data collection.")
            if st.button("Reveal Answer", key="pc_reveal"):
                st.info(f"Answer: **{st.session_state['privacy_quiz']['correct_answer']}**")

        # g) Reflection
        with st.expander("🖋️ Reflection (optional)"):
            text = st.text_area(
                "How will you decide which permissions to grant in the future?",
                key="pc_reflect"
            )
            if st.button("Save Reflection", key="pc_save"):
                st.success("Your reflection has been saved.")
    else:
        st.info("Select permissions above and click **Assess Consent** to begin.")
