# simulator.py

import random
import numpy as np
import yaml
import networkx as nx
from typing import List, Tuple, Dict

def load_config(path: str = "config.yaml") -> Dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        cfg = {}
    return cfg

def run_simulation(
    G: nx.Graph,
    steps: int,
    filter_strength: float,
    new_info_rate: float
) -> Tuple[List[Tuple[float, float]], List[Dict[str, float]]]:
    """
    Simulate echo‐chamber dynamics on graph G.

    Parameters:
    - G: networkx.Graph with 'type' ('user' or 'media') and
         for users: 'leaning' and 'opinion' floats; for media: 'bias'.
    - steps: number of time steps to run.
    - filter_strength: [0,1], how strongly users ignore opposing info.
    - new_info_rate: [0,1], probability a user sees neutral info each step.

    Returns:
    - history: list of (avg_opinion, polarization) tuples per step.
    - opinions_hist: list of { user_node: opinion } snapshots per step.
    """
    # Identify user nodes
    users = [n for n, data in G.nodes(data=True) if data.get("type") == "user"]
    history: List[Tuple[float, float]] = []
    opinions_hist: List[Dict[str, float]] = []

    for _ in range(steps):
        current_opinions = []
        for u in users:
            data = G.nodes[u]
            # decide source of information
            if random.random() < new_info_rate:
                info_bias = 0.0
            else:
                neighbor = random.choice(list(G.neighbors(u)))
                # media have 'bias', users have current 'opinion'
                info_bias = G.nodes[neighbor].get("bias",
                             G.nodes[neighbor].get("opinion", 0.0))
            # compute influence factor
            if np.sign(data["leaning"]) == np.sign(info_bias):
                influence = 1.0
            else:
                influence = 1.0 - filter_strength
            # update user opinion
            new_op = data["opinion"] + 0.5 * influence * (info_bias - data["opinion"])
            G.nodes[u]["opinion"] = new_op
            current_opinions.append(new_op)

        # record metrics
        avg_op = float(np.mean(current_opinions))
        pol    = float(np.mean(np.abs(current_opinions)))
        history.append((avg_op, pol))
        # snapshot all user opinions
        opinions_hist.append({u: G.nodes[u]["opinion"] for u in users})

    return history, opinions_hist
