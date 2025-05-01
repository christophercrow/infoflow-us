# network_model.py

import random
import networkx as nx
import yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        cfg = {}
    return cfg

def build_network(config: dict = None) -> nx.Graph:
    if config is None:
        config = load_config()

    # use .get with defaults
    n_u      = config.get("n_users",                50)
    n_m      = config.get("n_media",                 5)
    p_friend = config.get("friend_edge_prob",     0.05)
    min_f, max_f = config.get("media_follows_per_user", [1,3])

    G = nx.Graph()

    # Media nodes
    for i in range(n_m):
        bias = random.choice([-1, 0, 1])
        G.add_node(f"Media_{i}", type="media", bias=bias)

    # User nodes
    for i in range(n_u):
        lean = random.choice([-1, 0, 1])
        G.add_node(f"User_{i}", type="user", leaning=lean, opinion=float(lean))

    # Friendship edges
    users = [n for n,d in G.nodes(data=True) if d["type"] == "user"]
    for u in users:
        for v in users:
            if u < v and random.random() < p_friend:
                G.add_edge(u, v, type="friend")

    # Follow edges
    for u in users:
        k = random.randint(min_f, max_f)
        for m in random.sample(range(n_m), k):
            G.add_edge(u, f"Media_{m}", type="follows")

    return G
