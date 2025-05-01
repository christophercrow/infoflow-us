# modules/algorithmic_autonomy.py

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import plotly.graph_objs as go
from utils import init_quiz_state

def run():
    st.title("⚙️ Algorithmic Autonomy & Recommendation Diversity")

    # --- Relevant Readings for Module 4: Algorithmic Bias & Injustice ---
    with st.expander("📚 Readings for Module 4: Algorithmic Bias & Injustice", expanded=True):
        st.markdown("""
**Week 9: Algorithmic Bias & Injustice**  
- **Mon Mar 3** | “Algorithmic bias: Senses, sources, solutions,” *Fazelpour & Danks*  
- **Mon Mar 3** | “How We Analyzed the COMPAS Recidivism Algorithm,” *Larson et al.*  
- **Wed Mar 5** | “Algorithmic Injustice: A Relational Ethics Approach,” *Birhane*  
- **Fri Mar 7** | Review Birhane  
        """)

    # --- Definitions & Context ---
    with st.expander("❓ What Is Algorithmic Autonomy?"):
        st.markdown("""
Algorithms learn from your past behavior to suggest content you’re likely to engage with.  
**Algorithmic Autonomy** is your freedom to explore diverse content without strong algorithmic steering.  

- **High Autonomy** → you see varied recommendations.  
- **Low Autonomy** → your feed narrows to familiar items.
        """)
        st.info(
            "*Example:* A music app that only plays songs you’ve already liked may prevent you from discovering new genres."
        )

    # --- Step 1: Set Your Preference ---
    st.header("1️⃣ Choose Your Preferred Category")
    categories = ["Books", "Electronics", "Clothing", "Toys", "Home", "Sports"]
    pref = st.selectbox("Preferred Category:", categories)

    # --- Step 2: Configure Algorithm Parameters ---
    st.header("2️⃣ Configure Algorithm Parameters")
    col1, col2 = st.columns(2)
    with col1:
        algo_inf = st.slider(
            "Algorithm Influence",
            0.0, 1.0, 0.5, 0.01,
            help="Probability the algorithm suggests your preferred category"
        )
        st.caption("Higher → more of your chosen category.")
    with col2:
        novelty = st.slider(
            "Novelty Rate",
            0.0, 1.0, 0.1, 0.01,
            help="Probability the algorithm injects a random, non-preferred item"
        )
        st.caption("Higher → more unexpected suggestions.")

    picks = st.slider(
        "Number of Recommendations",
        5, 50, 20, 1,
        help="How many items the algorithm suggests"
    )

    # --- Reset on Input Change ---
    sig = (pref, algo_inf, novelty, picks)
    if st.session_state.get("aa_sig") != sig:
        st.session_state["aa_sig"] = sig
        st.session_state["aa_run"] = False

    # --- Session-State Keys ---
    run_key    = "aa_run"
    counts_key = "aa_counts"
    div_key    = "aa_diversity"
    picks_key  = "aa_list"
    if run_key not in st.session_state:
        st.session_state[run_key]     = False
        st.session_state[counts_key]  = None
        st.session_state[div_key]     = None
        st.session_state[picks_key]   = None

    # --- Run Simulation ---
    if st.button("Run Recommendation Simulation"):
        rng = np.random.default_rng()
        picks_list = []
        for _ in range(picks):
            r = rng.random()
            if r < novelty:
                choices = [c for c in categories if c != pref]
            elif r < (novelty + algo_inf):
                choices = [pref]
            else:
                choices = categories
            picks_list.append(rng.choice(choices))

        # Build DataFrame of counts reliably
        counts_dict = {c: 0 for c in categories}
        for choice in picks_list:
            counts_dict[choice] += 1
        df_counts = pd.DataFrame({
            "Category": list(counts_dict.keys()),
            "Count":    list(counts_dict.values())
        })

        # Compute Shannon entropy
        freqs = np.array(list(counts_dict.values())) / picks
        freqs_nz = freqs[freqs > 0]
        diversity = -np.sum(freqs_nz * np.log2(freqs_nz))

        # Save to session
        st.session_state[counts_key]  = df_counts
        st.session_state[div_key]     = diversity
        st.session_state[picks_key]   = picks_list
        st.session_state[run_key]     = True

        # Initialize quiz
        init_quiz_state("algo", correct_answer="Increase Novelty Rate")

    # --- Display Results ---
    if st.session_state[run_key]:
        df_counts  = st.session_state[counts_key]
        diversity  = st.session_state[div_key]
        picks_list = st.session_state[picks_key]

        # a) Recommendation distribution bar chart
        st.subheader("📊 Recommendation Distribution")
        bar_chart = alt.Chart(df_counts).mark_bar().encode(
            x=alt.X("Category", sort=categories),
            y="Count",
            color=alt.Color("Category", legend=None)
        ).properties(width=600, height=300)
        st.altair_chart(bar_chart, use_container_width=True)
        st.caption("Frequency of each category in the generated recommendations.")

        # b) Diversity gauge
        st.subheader("🔄 Recommendation Diversity (Shannon Entropy)")
        max_entropy = np.log2(len(categories))
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=diversity,
            number={"suffix": " bits"},
            gauge={
                "axis": {"range": [0, max_entropy]},
                "bar": {"color": "#17BECF"},
                "steps": [
                    {"range": [0, max_entropy/2], "color": "#FFC0C0"},
                    {"range": [max_entropy/2, max_entropy], "color": "#C0FFC0"}
                ]
            },
            title={"text": "Entropy"}
        ))
        gauge.update_layout(height=300, margin={"t":40})
        st.plotly_chart(gauge, use_container_width=True)
        st.caption("Higher entropy indicates a more diverse set of recommendations.")

        # c) Sample recommendations table
        st.subheader("📝 Sample Recommendations")
        st.table(pd.DataFrame(picks_list, columns=["Category"]))

        # d) Insights
        st.markdown("""
**Insights:**  
- **↑ Algorithm Influence** → more of your preferred category → **↓ diversity**.  
- **↑ Novelty Rate** → more random picks → **↑ diversity**.
        """)

        # e) Quiz & reveal
        st.subheader("❓ Quiz: Check Your Understanding")
        question = "To maximize recommendation diversity, which parameter should you increase?"
        options = [
            "Increase Algorithm Influence",
            "Increase Novelty Rate",
            "Increase Number of Recommendations"
        ]
        correct = "Increase Novelty Rate"
        qs = st.session_state["algo_quiz"]
        idx = options.index(qs["choice"]) if qs["choice"] in options else 1
        choice = st.radio(question, options, index=idx, key="aa_choice")
        if st.button("Submit Answer", key="aa_submit"):
            qs["submitted"] = True
            qs["correct"]   = (choice == correct)
            qs["choice"]    = choice
        if qs["submitted"]:
            if qs["correct"]:
                st.success("✅ Correct—novelty introduces fresh content!")
            else:
                st.error("❌ Not quite—consider which adds truly new items.")
            if st.button("Reveal Answer", key="aa_reveal"):
                qs["revealed"] = True
        if qs["revealed"]:
            st.info(f"Answer: **{correct}**")

        # f) Reflection
        with st.expander("🖋️ Reflection (optional)"):
            text = st.text_area(
                "How would you balance algorithmic guidance and discovery on a real platform?",
                key="aa_reflect"
            )
            if st.button("Save Reflection", key="aa_save"):
                st.success("Your reflection has been saved.")
    else:
        st.info("Adjust parameters above and click **Run Recommendation Simulation** to begin.")
