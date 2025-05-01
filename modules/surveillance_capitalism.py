# modules/surveillance_capitalism.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objs as go
from utils import init_quiz_state

def run():
    st.title("💰 Surveillance Capitalism Simulator")

    # --- Relevant Readings for Module 6: Privacy & Surveillance ---
    with st.expander("📚 Readings for Module 6: Privacy & Surveillance", expanded=True):
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
    with st.expander("❓ What Is Surveillance Capitalism?"):
        st.markdown("""
Surveillance capitalism refers to business models where companies **collect**, **analyze**, and **sell** personal data  
to **predict** and **influence** user behavior for profit.  

- **Data Collection**: e.g., location, browsing history, contacts, app usage, device sensors.  
- **Ad Personalization**: Tailoring ads based on your profile.  
- **User Autonomy**: Your freedom to browse without algorithmic steering.  
- **Revenue Potential**: Estimated profit from data-driven ads and services.
        """)

    st.header("1️⃣ Configure Data Permissions")
    data_types = {
        "Location":        {"weight": 1.2, "desc": "GPS, cell-tower, Wi-Fi data"},
        "Contacts":        {"weight": 1.5, "desc": "Address book & social graph"},
        "Browsing History":{"weight": 1.0, "desc": "Websites & clicks"},
        "App Usage":       {"weight": 1.1, "desc": "Which apps you open & when"},
        "Device Sensors":  {"weight": 1.3, "desc": "Microphone, camera, accelerometer"}
    }
    permissions = {}
    cols = st.columns(2)
    for i, (dtype, info) in enumerate(data_types.items()):
        with cols[i % 2]:
            permissions[dtype] = st.checkbox(
                f"{dtype} ({info['desc']})",
                value=False
            )

    st.header("2️⃣ Set Personalization Level")
    personalization = st.slider(
        "Ad Personalization Strength",
        0.0, 1.0, 0.5, 0.01,
        help="0 = generic ads; 1 = fully tailored"
    )

    # Reset on input change
    sig = (tuple(permissions.values()), personalization)
    if st.session_state.get("sc_sig") != sig:
        st.session_state["sc_sig"] = sig
        st.session_state["sc_run"] = False

    # Session-state initialization
    run_key = "sc_run"
    metrics_key = "sc_metrics"
    ads_key = "sc_ads"
    if run_key not in st.session_state:
        st.session_state[run_key] = False
        st.session_state[metrics_key] = None
        st.session_state[ads_key] = None

    # --- Run Simulation ---
    if st.button("Run Simulation"):
        # Compute autonomy and revenue
        total_w = sum(info["weight"] for info in data_types.values())
        collected = sum(data_types[d]["weight"] for d, ok in permissions.items() if ok)
        autonomy = max(0.0, (total_w - collected) / total_w)
        revenue = collected * personalization * 100  # in $k

        # Save metrics
        st.session_state[metrics_key] = {"autonomy": autonomy, "revenue": revenue}

        # Generate ad feed
        generic = [
            {"Ad": "Summer Sale – 20% Off!", "Type": "Generic"},
            {"Ad": "Subscribe to Newsletter", "Type": "Generic"},
            {"Ad": "Join Our Loyalty Program", "Type": "Generic"},
            {"Ad": "Today’s Weather Forecast", "Type": "Generic"},
            {"Ad": "Download Our Free App", "Type": "Generic"}
        ]
        personalized = []
        if permissions["Location"]:
            personalized.append({"Ad": "Nearby Restaurant Discounts", "Type": "Location-Based"})
        if permissions["Browsing History"]:
            personalized.append({"Ad": "New Tech Gadgets for You", "Type": "Interest-Based"})
        if permissions["Contacts"]:
            personalized.append({"Ad": "What Your Friends Are Buying", "Type": "Social-Graph"})
        if permissions["App Usage"]:
            personalized.append({"Ad": "Premium Upgrade in Your Favorited App", "Type": "Usage-Based"})
        if permissions["Device Sensors"]:
            personalized.append({"Ad": "Night-Mode Glasses", "Type": "Sensor-Inferred"})

        st.session_state[ads_key] = pd.DataFrame(generic + personalized)
        st.session_state[run_key] = True

        # Initialize quiz
        init_quiz_state(
            "surveillance",
            correct_answer="User autonomy decreases as data collection increases"
        )

    # --- Display Results ---
    if st.session_state[run_key]:
        metrics = st.session_state[metrics_key]
        df_ads = st.session_state[ads_key]

        # a) Autonomy gauge
        st.subheader("📊 User Autonomy")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics["autonomy"] * 100,
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2CA02C"},
                'steps': [
                    {'range': [0, 50], 'color': "#FFC0C0"},
                    {'range': [50, 100], 'color': "#C0FFC0"}
                ]
            },
            title={'text': "Autonomy"}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # b) Revenue metric
        st.subheader("💵 Revenue Potential")
        st.metric(label="Estimated Revenue (k$)", value=f"{metrics['revenue']:.1f}")

        # c) Ad Feed Breakdown
        st.subheader("📰 Ad Feed Breakdown")
        df_count = df_ads["Type"].value_counts().reset_index()
        df_count.columns = ["Type", "Count"]
        chart = alt.Chart(df_count).mark_bar().encode(
            x='Type',
            y='Count',
            color=alt.Color('Type', legend=None)
        ).properties(width=600, height=300)
        st.altair_chart(chart, use_container_width=True)
        st.table(df_ads.rename(columns={"Ad": "Ad Content", "Type": "Ad Type"}))

        # d) Insights
        st.markdown("""
**Insights:**  
- Granting more permissions **increases revenue** but **decreases your autonomy**.  
- Even “harmless” data (e.g., app usage) can reduce your ability to see unbiased content.
        """)

        # e) Quiz
        st.subheader("❓ Quiz: Check Your Understanding")
        question = "Which statement is correct?"
        options = {
            "User autonomy decreases as data collection increases": True,
            "User autonomy increases as data collection increases": False,
            "Revenue decreases as personalization increases": False
        }
        choice = st.radio(question, list(options.keys()), key="sc_choice")
        if st.button("Submit Answer", key="sc_submit"):
            qs = st.session_state["surveillance_quiz"]
            qs["submitted"] = True
            qs["correct"] = options[choice]
            qs["choice"] = choice
        if st.session_state["surveillance_quiz"]["submitted"]:
            if st.session_state["surveillance_quiz"]["correct"]:
                st.success("✅ Correct! More data → less autonomy.")
            else:
                st.error("❌ Not quite—remember how data collection affects control.")
            if st.button("Reveal Answer", key="sc_reveal"):
                st.info(f"Answer: **{st.session_state['surveillance_quiz']['correct_answer']}**")

        # f) Reflection
        with st.expander("🖋️ Reflection (optional)"):
            text = st.text_area(
                "What permissions would you limit to protect your autonomy?",
                key="sc_reflect"
            )
            if st.button("Save Reflection", key="sc_save"):
                st.success("Your reflection has been saved.")
    else:
        st.info("Configure permissions and click **Run Simulation** to begin.")
