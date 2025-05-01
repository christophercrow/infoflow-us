# modules/epistemic_injustice.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from sklearn.feature_extraction.text import CountVectorizer
from utils import init_quiz_state

def run():
    st.title("⚖️ Epistemic Injustice: A Data-Driven Exploration")

    # --- Module 5 Readings & Context ---
    with st.expander("📚 Relevant Readings for This Module", expanded=True):
        st.markdown("""
**Week 11: Truth, Understanding, Knowledge**  
- **Mon Mar 17** | Misinformation: “Searching for People and Communities,” *Noble*  
- **Wed Mar 19** | Echo Chambers & Epistemic Bubbles: “Two: Looking Down” & “Three: Mirror Image,” *The Daily’s Rabbit Hole Series*  
- **Fri Mar 21** | Echo Chambers & Epistemic Bubbles: “Escape the Echo Chamber,” *Nguyen*  

**Week 12: Heuristics & Epistemic Superheroism**  
- **Mon Mar 24** | Review “Escape the Echo Chamber,” *Nguyen*  
- **Wed Mar 26** | Epistemic Superheroism: “Doing Your Own Research and Other Impossible Acts of Epistemic Superheroism,” *Buzzell & Rini*  
- **Fri Mar 28** | Blame and Praise & Critical Analysis Part 2 (selections from Buzzell & Rini)  
        """)

    # --- What is Epistemic Injustice? ---
    with st.expander("❓ Defining Epistemic Injustice"):
        st.markdown("""
**Epistemic injustice** happens when people’s capacity as knowers is unfairly undermined.
- **Testimonial injustice**: A speaker’s word is given less credibility due to prejudice.
- **Hermeneutical injustice**: A group’s experiences are misunderstood or ignored because society lacks the concepts to interpret them.
        """)

    # --- Step 1: Load Quotes ---
    st.header("1️⃣ Supply or Explore Quotes")
    uploaded = st.file_uploader(
        "Upload a CSV with columns `speaker,group,text` (optional)",
        type="csv",
        help="If none is uploaded, we’ll use a built-in sample."
    )
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success(f"Loaded {len(df)} quotes.")
    else:
        sample = [
            {"speaker":"Anna","group":"Locals","text":"Traffic noise has doubled in our neighborhood."},
            {"speaker":"Ben","group":"Newcomers","text":"I started an urban farm in the vacant lot."},
            {"speaker":"Carla","group":"Locals","text":"Our school funding was cut again."},
            {"speaker":"Diego","group":"Newcomers","text":"I organized a street art festival downtown."},
            {"speaker":"Elaine","group":"Locals","text":"We need more benches in the park."},
            {"speaker":"Farah","group":"Newcomers","text":"We speak multiple languages in my community."},
            {"speaker":"George","group":"Locals","text":"The local bus service has improved."},
            {"speaker":"Hannah","group":"Newcomers","text":"There's a new coworking space opening soon."},
            {"speaker":"Ian","group":"Locals","text":"Potholes on Elm Street are getting worse."},
            {"speaker":"Jade","group":"Newcomers","text":"I started volunteering at the community center."},
        ]
        df = pd.DataFrame(sample)
        st.info(f"Using built-in sample ({len(df)} quotes).")

    if not {"speaker","group","text"} <= set(df.columns):
        st.error("CSV must include `speaker`, `group`, and `text` columns.")
        return

    # --- Step 2: Concept Extraction ---
    st.header("2️⃣ Pick Recognized Concepts")
    vectorizer = CountVectorizer(stop_words="english", max_features=20, ngram_range=(1,2))
    X = vectorizer.fit_transform(df["text"])
    candidate_concepts = vectorizer.get_feature_names_out().tolist()
    recognized = st.multiselect(
        "Which keywords does your system recognize?",
        candidate_concepts,
        default=candidate_concepts[:8],
        help="Quotes lacking all recognized terms will be 'unheard.'"
    )

    # --- Step 3: Trust Levels ---
    st.header("3️⃣ Assign Trust Levels (Testimonial Injustice)")
    groups = sorted(df["group"].unique())
    trust = {}
    cols = st.columns(len(groups))
    for i, g in enumerate(groups):
        trust[g] = cols[i].slider(
            f"Trust for {g}",
            0.0, 1.0, 0.5, 0.01,
            help=f"0 = never believe, 1 = fully believe {g}"
        )

    # Reset simulation when inputs change
    sig = (tuple(recognized), tuple(trust.values()))
    if st.session_state.get("ej_sig") != sig:
        st.session_state["ej_sig"] = sig
        st.session_state["ej_run"] = False

    # Session-state keys
    run_key = "ej_run"
    tdf_key = "ej_test_df"
    hdf_key = "ej_herm_df"
    udf_key = "ej_uncls_df"
    if run_key not in st.session_state:
        st.session_state[run_key] = False
        st.session_state[tdf_key] = None
        st.session_state[hdf_key] = None
        st.session_state[udf_key] = None

    # --- Run Analysis ---
    if st.button("Run Epistemic Analysis"):
        # Testimonial: weighted credibility per group
        counts = df["group"].value_counts().to_dict()
        weighted = {g: trust[g] * counts.get(g, 0) for g in groups}
        df_test = pd.DataFrame({
            "Group": groups,
            "Credibility Score": [weighted[g] for g in groups]
        })

        # Hermeneutical: coverage & unheard quotes
        total = df["group"].value_counts().to_dict()
        unheard = {g: [] for g in groups}
        for _, row in df.iterrows():
            txt = row["text"].lower()
            if not any(kw in txt for kw in recognized):
                unheard[row["group"]].append(row)

        coverage = {g: 1 - len(unheard[g]) / total.get(g,1) for g in groups}
        df_herm = pd.DataFrame({
            "Group": groups,
            "Coverage Rate": [coverage[g] for g in groups],
            "Unheard Count": [len(unheard[g]) for g in groups],
            "Total Quotes": [total.get(g,0) for g in groups]
        })

        records = []
        for g, rows in unheard.items():
            for r in rows:
                records.append({
                    "Group": g,
                    "Speaker": r["speaker"],
                    "Quote": r["text"]
                })
        df_uncls = pd.DataFrame(records)

        # Save to session
        st.session_state[tdf_key] = df_test
        st.session_state[hdf_key] = df_herm
        st.session_state[udf_key] = df_uncls
        st.session_state[run_key] = True

        # Init quiz
        init_quiz_state("epistemic", correct_answer="Hermeneutical Injustice")

    # --- Display Results ---
    if st.session_state[run_key]:
        # a) Testimonial chart
        df_test = st.session_state[tdf_key]
        st.subheader("📊 Credibility by Group (Testimonial Injustice)")
        fig1 = go.Figure(go.Bar(
            x=df_test["Group"], y=df_test["Credibility Score"],
            marker_color=["#636EFA"]*len(df_test)
        ))
        fig1.update_layout(template="plotly_white", yaxis_title="Score")
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("Groups with lower scores suffer testimonial injustice.")

        # b) Hermeneutical coverage
        df_herm = st.session_state[hdf_key]
        st.subheader("🔍 Concept Coverage (Hermeneutical Injustice)")
        df_herm["Pct"] = df_herm["Coverage Rate"]
        fig2 = go.Figure(go.Bar(
            x=df_herm["Pct"], y=df_herm["Group"], orientation="h",
            marker_color=["#00CC96","#AB63FA"][:len(groups)],
            hovertemplate="%{y}: %{x:.0%}"
        ))
        fig2.update_layout(
            xaxis_title="Coverage (%)",
            xaxis_tickformat=".0%",
            template="plotly_white",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

        # pie breakdown
        cols = st.columns(len(groups))
        for i, g in enumerate(groups):
            total_q = df_herm.loc[df_herm["Group"]==g, "Total Quotes"].iat[0]
            unheard_q = df_herm.loc[df_herm["Group"]==g, "Unheard Count"].iat[0]
            heard_q = total_q - unheard_q
            figp = go.Figure(go.Pie(
                labels=["Understood","Unheard"],
                values=[heard_q, unheard_q],
                hole=0.4,
                marker_colors=["#00CC96","#FF6361"],
                hovertemplate="%{label}: %{value} (%{percent})"
            ))
            figp.update_layout(title_text=f"{g} Coverage", template="plotly_white", height=240)
            cols[i].plotly_chart(figp, use_container_width=True)

        # c) Keyword table
        st.subheader("🔑 Keyword Recognition Summary")
        keyword_stats = []
        for kw in candidate_concepts:
            occ = (df["text"].str.lower().str.contains(kw)).sum()
            keyword_stats.append({
                "Keyword": kw,
                "Occurrences": int(occ),
                "Recognized?": "✅" if kw in recognized else "❌"
            })
        df_kw = pd.DataFrame(keyword_stats).sort_values("Occurrences", ascending=False)
        st.dataframe(df_kw, use_container_width=True)
        st.caption("✅ terms the system understands; ❌ lead to unheard quotes.")

        # d) Unheard quotes table
        st.subheader("🗂️ Unheard Quotes (Hermeneutical Gap)")
        df_uncls = st.session_state[udf_key]
        if not df_uncls.empty:
            st.table(df_uncls)
        else:
            st.success("All quotes understood—no hermeneutical gap!")

        # e) Key takeaways
        st.markdown("""
**Key Takeaways**  
- **Testimonial injustice**: Groups you trust less have lower credibility scores.  
- **Hermeneutical injustice**: Missing recognized concepts leads to unheard experiences.
        """)

        # f) Quiz
        st.subheader("❓ Quiz: Check Your Understanding")
        q = "Which injustice arises when experiences are unheard due to lack of interpretive resources?"
        opts = ["Testimonial Injustice", "Hermeneutical Injustice", "Neither"]
        correct = "Hermeneutical Injustice"
        qs = st.session_state["epistemic_quiz"]
        idx = opts.index(qs["choice"]) if qs["choice"] in opts else 1
        choice = st.radio(q, opts, index=idx, key="epi_choice")
        if st.button("Submit Answer", key="epi_submit"):
            qs["submitted"] = True
            qs["correct"]   = (choice == correct)
            qs["choice"]    = choice
        if qs["submitted"]:
            if qs["correct"]:
                st.success("✅ Correct—this is hermeneutical injustice.")
            else:
                st.error("❌ Not quite—this refers to missing interpretive resources.")
            if st.button("Reveal Answer", key="epi_reveal"):
                qs["revealed"] = True
        if qs["revealed"]:
            st.info(f"Answer: **{correct}**")

        # g) Reflection
        with st.expander("🖋️ Reflection (optional)"):
            text = st.text_area(
                "How might you redesign a platform to prevent these injustices?",
                key="epi_reflect"
            )
            if st.button("Save Reflection", key="epi_save"):
                st.success("Your reflection has been saved.")
    else:
        st.info("Adjust inputs above and click **Run Epistemic Analysis** to begin.")
