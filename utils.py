import streamlit as st

def init_quiz_state(module: str, correct_answer: str, default_choice=None):
    """Initialize quiz state for module if not already present."""
    key = f"{module}_quiz"
    if key not in st.session_state:
        st.session_state[key] = {
            "submitted": False,
            "correct": False,
            "revealed": False,
            "choice": default_choice,
            "correct_answer": correct_answer
        }
