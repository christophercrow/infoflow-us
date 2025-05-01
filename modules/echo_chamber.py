# modules/echo_chamber.py

import streamlit as st
import networkx as nx
import plotly.graph_objs as go
import altair as alt
from network_model import build_network
from simulator import run_simulation, load_config
from pyvis.network import Network
import streamlit.components.v1 as components
from utils import init_quiz_state

def run():
    st.title("🔊 Echo Chamber Dynamics")

    # --- Relevant Readings for Module 5: Knowledge & Bubbles ---
    with st.expander("📚 Readings for Module 5: Truth, Understanding, Knowledge", expanded=True):
        st.markdown("""
**Week 11: Misinformation & Bubbles**  
- **Mon Mar 17** | *“Searching for People and Communities,”* Noble  
- **Wed Mar 19** | *“Two: Looking Down”* & *“Three: Mirror Image,”* Rabbit Hole Series  
- **Fri Mar 21** | *“Escape the Echo Chamber,”* Nguyen  

**Week 12: Heuristics & Superheroism**  
- **Mon Mar 24** | Review Nguyen  
- **Wed Mar 26** | *“Doing Your Own Research and Other Impossible Acts of Epistemic Superheroism,”* Buzzell & Rini  
- **Fri Mar 28** | *“Blame and Praise,”* Buzzell & Rini; Critical Analysis Part 2  
        """)

    # --- Definition ---
    with st.expander("❓ What Is an Echo Chamber?"):
        st.markdown("""
An **echo chamber** is a network in which people mostly encounter viewpoints similar to their own,  
amplifying existing beliefs and excluding opposing perspectives.  

Algorithms and social connections both contribute to creating these closed loops.
        """)
        st.info(
            "*Example:* If your social feed only shows friends and sources who agree with you, your beliefs get reinforced."
        )

    # --- Step 1: Simulation Parameters ---
    cfg = load_config() or {}
    st.header("1️⃣ Configure Simulation Settings")
    col1, col2 = st.columns(2)
    with col1:
        n_users = st.slider(
            "Number of Users", 10, 200,
            int(cfg.get("n_users", 50)),
            step=10
        )
        filter_strength = st.slider(
            "Filter Strength",
            0.0, 1.0, float(cfg.get("filter_strength", 0.5)), 0.01,
            help="How strongly users ignore opposing views"
        )
        steps = st.slider(
            "Simulation Steps", 5, 100,
            int(cfg.get("steps", 20)), 1
        )
    with col2:
        n_media = st.slider(
            "Number of Media Outlets", 1, 20,
            int(cfg.get("n_media", 5)), 1
        )
        new_info_rate = st.slider(
            "New-Info Rate",
            0.0, 1.0, float(cfg.get("new_info_rate", 0.3)), 0.01,
            help="Probability users see fresh, neutral content"
        )

    # --- Reset on Input Change ---
    sig = (n_users, n_media, filter_strength, new_info_rate, steps)
    if st.session_state.get("ec_sig") != sig:
        st.session_state["ec_sig"] = sig
        st.session_state["ec_run"] = False

    # --- Session-State Keys ---
    run_key  = "ec_run"
    hist_key = "ec_history"
    ops_key  = "ec_opinions"
    net_key  = "ec_network"
    if run_key not in st.session_state:
        st.session_state[run_key]  = False
        st.session_state[hist_key] = None
        st.session_state[ops_key]  = None
        st.session_state[net_key]  = None

    # --- Step 2: Run Simulation ---
    if st.button("Run Simulation"):
        sim_config = {
            "n_users": n_users,
            "n_media": n_media,
            "friend_edge_prob": cfg.get("friend_edge_prob", 0.05),
            "media_follows_per_user": cfg.get("media_follows_per_user", [1, 3])
        }
        G = build_network(sim_config)
        history, opinions = run_simulation(G, steps, filter_strength, new_info_rate)

        st.session_state[hist_key] = history
        st.session_state[ops_key]  = opinions
        st.session_state[net_key]  = G
        st.session_state[run_key]  = True

        init_quiz_state(
            "echo",
            correct_answer="High filter strength + low new-info rate → strong echo chamber"
        )

    # Prompt to run if not yet
    if not st.session_state[run_key]:
        st.info("Set parameters above and click **Run Simulation** to see results.")
        return

    # --- Step 3: Visualize Time Series ---
    st.header("2️⃣ Opinion & Polarization Over Time")
    history = st.session_state[hist_key]
    steps_idx = list(range(1, len(history) + 1))
    avg_opinions = [h[0] for h in history]
    polarization = [h[1] for h in history]

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=steps_idx, y=avg_opinions,
        mode="lines+markers", name="Average Opinion",
        line=dict(color="#636EFA")
    ))
    fig_ts.add_trace(go.Scatter(
        x=steps_idx, y=polarization,
        mode="lines+markers", name="Polarization",
        line=dict(color="#EF553B")
    ))
    fig_ts.update_layout(
        xaxis_title="Step",
        yaxis_title="Value",
        template="plotly_white",
        height=350
    )
    st.plotly_chart(fig_ts, use_container_width=True)
    st.caption("Average Opinion (closer to ±1 = consensus) and Polarization over simulation steps.")

    # --- Step 4: Interactive Network ---
    st.header("3️⃣ Final Network Structure")
    G_final = st.session_state[net_key]
    ops_final = st.session_state[ops_key][-1]

    net = Network(
        height="600px", width="100%",
        notebook=False, cdn_resources="in_line"
    )
    net.force_atlas_2based()

    # Add nodes with colors by type/opinion
    for node, attrs in G_final.nodes(data=True):
        if attrs["type"] == "media":
            net.add_node(node, label=node, color="black",
                         title=f"Media Outlet (bias={attrs['bias']})")
        else:
            op = ops_final.get(node, 0.0)
            if op > 0.5:
                color = "red"
            elif op < -0.5:
                color = "blue"
            else:
                color = "gray"
            net.add_node(node, label=node, color=color,
                         title=f"User (opinion={op:.2f})")

    for u, v in G_final.edges():
        net.add_edge(u, v)

    html = net.generate_html()
    components.html(html, height=650)

    # Legend
    st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-top:8px;">
  <div style="width:16px; height:16px; background:black;"></div><span>Media Outlet</span>
  <div style="width:16px; height:16px; background:red;"></div><span>User (opinion &gt; 0.5)</span>
  <div style="width:16px; height:16px; background:gray;"></div><span>User (–0.5 ≤ opinion ≤ 0.5)</span>
  <div style="width:16px; height:16px; background:blue;"></div><span>User (opinion &lt; –0.5)</span>
</div>
""", unsafe_allow_html=True)

    # --- Step 5: Insights ---
    st.markdown("""
**Key Takeaways**  
- **High filter strength** + **low new-info rate** → rapid echo chamber formation (high polarization).  
- **Lower filter strength** or **higher new-info rate** → more diverse information flow (lower polarization).
    """)

    # --- Step 6: Quiz & Reveal ---
    st.header("❓ Quiz: Check Your Understanding")
    question = "Which settings produce the strongest echo chamber?"
    options = [
        "High filter + low new-info → strong echo chamber",
        "Low filter + low new-info → strong echo chamber",
        "High filter + high new-info → strong echo chamber"
    ]
    correct = options[0]
    qs = st.session_state["echo_quiz"]
    idx = options.index(qs["choice"]) if qs["choice"] in options else 0
    choice = st.radio(question, options, index=idx, key="echo_choice")
    if st.button("Submit Answer", key="echo_submit"):
        qs["submitted"] = True
        qs["correct"]   = (choice == correct)
        qs["choice"]    = choice
    if qs["submitted"]:
        if qs["correct"]:
            st.success("✅ Correct! Echo chambers thrive under high filter and little new info.")
        else:
            st.error("❌ Not quite—consider how filtering and info inflow interact.")
        if st.button("Reveal Answer", key="echo_reveal"):
            qs["revealed"] = True
    if qs["revealed"]:
        st.info(f"Answer: **{correct}**")

    # --- Step 7: Reflection ---
    with st.expander("🖋️ Reflection (optional)"):
        note = st.text_area(
            "How might you introduce more new information to break an echo chamber?",
            key="echo_reflect"
        )
        if st.button("Save Reflection", key="echo_save"):
            st.success("Your reflection has been saved.")
