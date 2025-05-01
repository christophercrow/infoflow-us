# modules/filter_bubbles.py

import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objs as go
from utils import init_quiz_state

def run():
    st.title("🗞️ Filter Bubbles & Echo Chambers")

    # --- Course Context & Readings ---
    with st.expander("📚 Week 11–12 Course Schedule & Readings", expanded=True):
        st.markdown("""
- **Week 11**  
  - **Mon Mar 17** | Misinformation: “Searching for People and Communities,” *Noble*  
  - **Wed Mar 19** | Echo Chambers & Epistemic Bubbles: “Two: Looking Down” & “Three: Mirror Image,” *The Daily’s Rabbit Hole Series*  
  - **Fri Mar 21** | Echo Chambers & Epistemic Bubbles: “Escape the Echo Chamber,” *Nguyen*  

- **Week 12**  
  - **Mon Mar 24** | Heuristics of Belief Formation – Review “Escape the Echo Chamber,” *Nguyen*  
  - **Wed Mar 26** | Epistemic Superheroism: “Doing Your Own Research and Other Impossible Acts of Epistemic Superheroism,” *Buzzell & Rini*  
  - **Fri Mar 28** | Blame and Praise & Critical Analysis: *Buzzell & Rini* (cont.), plus Critical Analysis Part 2
        """)

    # --- Key Concepts ---
    with st.expander("❓ What are Filter Bubbles & Echo Chambers?"):
        st.markdown("""
A **filter bubble** arises when personalization algorithms show you content similar to your past behavior, narrowing the information you see.  
An **echo chamber** amplifies those same views by repeated exposure, excluding opposing perspectives.

**Readings & Insights**  
- Noble (Mar 17): How search filters invisibilize marginalized communities.  
- Rabbit Hole (Mar 19): “Looking Down” and “Mirror Image” reinforcement cycles.  
- Nguyen (Mar 21): Strategies to “Escape the Echo Chamber.”  
- Heuristics (Mar 24): Serendipity injections to break filter bubbles.  
        """)

    # --- Simulation Controls ---
    st.header("🛠️ Simulation Parameters")
    topics = ["Politics", "Health", "Technology", "Sports", "Arts", "Local"]
    prefs = {}
    cols = st.columns(3)
    for i, topic in enumerate(topics):
        prefs[topic] = cols[i % 3].slider(
            f"Interest in {topic}", 0.0, 1.0, 0.5, 0.05,
            help=f"Your baseline interest in {topic.lower()}"
        )

    personalization = st.slider(
        "Personalization Strength",
        0.0, 1.0, 0.6, 0.01,
        help="0 = random; 1 = strictly your top interests"
    )
    serendipity = st.slider(
        "Serendipity Rate",
        0.0, 0.5, 0.1, 0.01,
        help="Chance to inject random/unrelated content"
    )
    feed_size = st.number_input(
        "Feed Size (articles/day)", 5, 100, 20, 5
    )
    days = st.slider(
        "Days to Simulate", 1, 14, 7, 1
    )

    # --- Prepare Sample Headlines ---
    sample_headlines = []
    for t in topics:
        for i in range(4):
            sample_headlines.append({
                "topic": t,
                "headline": f"{t} News Item #{i+1}"
            })

    # --- Session State Init ---
    run_key     = "fb_run"
    counts_key  = "fb_counts"
    shannon_key = "fb_shannon"
    simpson_key = "fb_simpson"
    feeds_key   = "fb_feeds"
    if run_key not in st.session_state:
        st.session_state[run_key]     = False
        st.session_state[counts_key]  = None
        st.session_state[shannon_key] = None
        st.session_state[simpson_key] = None
        st.session_state[feeds_key]   = None

    # --- Run Simulation ---
    if st.button("Run Simulation"):
        counts, shannon, simpson, feeds = [], [], [], {}
        pref_vals = np.array([prefs[t] for t in topics])
        base = (pref_vals + 0.1)
        base = base / base.sum()

        for day in range(1, days+1):
            day_feed = []
            for _ in range(feed_size):
                r = random.random()
                if r < serendipity:
                    choice = random.choice(sample_headlines)
                else:
                    weights = base + personalization * pref_vals
                    weights = weights / weights.sum()
                    topic_choice = np.random.choice(topics, p=weights)
                    candidates = [h for h in sample_headlines if h["topic"] == topic_choice]
                    choice = random.choice(candidates)
                day_feed.append(choice)

            # Tally counts
            topic_list = [h["topic"] for h in day_feed]
            cnt = {t: topic_list.count(t) for t in topics}
            cnt_record = {"Day": day, **cnt}
            counts.append(cnt_record)

            # Shannon entropy
            freqs = np.array(list(cnt.values())) / feed_size
            freqs_nz = freqs[freqs > 0]
            H = -np.sum(freqs_nz * np.log2(freqs_nz))
            shannon.append({"Day": day, "Shannon Entropy": H})

            # Simpson index
            D = 1 - np.sum(freqs**2)
            simpson.append({"Day": day, "Simpson Index": D})

            feeds[day] = day_feed

        st.session_state[counts_key]  = pd.DataFrame(counts)
        st.session_state[shannon_key] = pd.DataFrame(shannon)
        st.session_state[simpson_key] = pd.DataFrame(simpson)
        st.session_state[feeds_key]   = feeds
        st.session_state[run_key]     = True

        init_quiz_state("fb", correct_answer="“Searching for People and Communities,” Noble")

    # --- Display Results ---
    if st.session_state[run_key]:
        df_counts  = st.session_state[counts_key]
        df_shannon = st.session_state[shannon_key]
        df_simpson = st.session_state[simpson_key]
        feeds      = st.session_state[feeds_key]

        # Topic composition
        st.subheader("📊 Topic Composition Over Time")
        fig = go.Figure()
        colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b"]
        for t, c in zip(topics, colors):
            fig.add_trace(go.Bar(x=df_counts["Day"], y=df_counts[t], name=t, marker_color=c))
        fig.update_layout(barmode="stack", xaxis_title="Day", yaxis_title="Articles", template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

        # Diversity metrics
        st.subheader("🔄 Feed Diversity Over Time")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_shannon["Day"], y=df_shannon["Shannon Entropy"], mode="lines+markers", name="Shannon"))
        fig2.add_trace(go.Scatter(x=df_simpson["Day"], y=df_simpson["Simpson Index"], mode="lines+markers", name="Simpson"))
        fig2.update_layout(xaxis_title="Day", yaxis_title="Diversity", template="plotly_white", height=350)
        st.plotly_chart(fig2, use_container_width=True)

        # Sample feed table
        st.subheader("📰 Sample Headlines for a Selected Day")
        sel = st.slider("Select Day", 1, days, days)
        st.table(pd.DataFrame(feeds[sel]))

        # Insights & readings
        st.markdown("""
**Insights & Course Connections**  
- **Search Bias (Noble, Mar 17)**: invisibilization in your personalized feed.  
- **Recommendation Loops (Rabbit Hole, Mar 19)**: “Looking Down” & “Mirror Image.”  
- **Escaping Bubbles (Nguyen, Mar 21)**: serendipity injection helps.  
- **Heuristics (Mar 24)**: small random injections boost Simpson diversity.
        """)

        # Quiz
        st.subheader("❓ Quick Quiz")
        q = "Which reading discusses algorithmic invisibility of marginalized communities?"
        opts = [
            "“Searching for People and Communities,” Noble",
            "“Escape the Echo Chamber,” Nguyen",
            "“Two: Looking Down,” Rabbit Hole",
            "“Doing Your Own Research,” Buzzell & Rini"
        ]
        correct = opts[0]
        qs = st.session_state["fb_quiz"]
        idx = opts.index(qs["choice"]) if qs["choice"] in opts else 0
        choice = st.radio(q, opts, index=idx, key="fb_choice")
        if st.button("Submit Answer", key="fb_submit"):
            qs["submitted"] = True
            qs["correct"]   = (choice == correct)
            qs["choice"]    = choice
        if qs["submitted"]:
            if qs["correct"]:
                st.success("✅ Correct! Noble addresses search invisibility.")
            else:
                st.error("❌ Not quite—think of search engine bias.")
            if st.button("Reveal Answer", key="fb_reveal"):
                qs["revealed"] = True
        if qs["revealed"]:
            st.info(f"Answer: **{correct}**")

        # Reflection
        with st.expander("🖋️ Reflection (optional)"):
            txt = st.text_area(
                "How would you add serendipity to your own information diet?"
            )
            if st.button("Save Reflection", key="fb_reflect"):
                st.success("Reflection saved!")
    else:
        st.info("Adjust parameters above and click **Run Simulation** to begin.")
