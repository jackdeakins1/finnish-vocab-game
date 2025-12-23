import streamlit as st
import random
import os
from collections import deque

# --- 1. Load Data ---
def load_words(filename):
    word_list = []
    # Try loading 'words' or 'words.txt' to be safe
    if os.path.exists(filename):
        target = filename
    elif os.path.exists(filename + ".txt"):
        target = filename + ".txt"
    else:
        return []
    
    with open(target, 'r', encoding='utf-8') as f:
        for line in f:
            if ';' in line:
                parts = line.strip().split(';')
                if len(parts) >= 2:
                    word_list.append({'en': parts[0].strip(), 'fi': parts[1].strip()})
    return word_list

# --- 2. Session State Initialization ---
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_words("words")
if 'buffer' not in st.session_state:
    st.session_state.buffer = deque(maxlen=5)
if 'error_stats' not in st.session_state:
    st.session_state.error_stats = {}
if 'current_pair' not in st.session_state:
    st.session_state.current_pair = None
if 'game_active' not in st.session_state:
    st.session_state.game_active = True
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'reveal_text' not in st.session_state:
    st.session_state.reveal_text = ""

# --- 3. Game Logic ---
def get_new_word():
    vocab = st.session_state.vocab
    buffer = st.session_state.buffer
    
    if not vocab:
        return

    available_pool = vocab
    if len(vocab) > 5:
        available_pool = [w for w in vocab if w['en'] not in buffer]
    
    pair = random.choice(available_pool)
    st.session_state.buffer.append(pair['en'])
    st.session_state.current_pair = pair
    st.session_state.feedback = ""
    st.session_state.reveal_text = ""

def submit_answer():
    user_input = st.session_state.user_answer.strip().lower()
    
    if user_input == "stop":
        st.session_state.game_active = False
        st.session_state.feedback = "Game stopped."
        return

    pair = st.session_state.current_pair
    mode = st.session_state.mode_selection
    
    correct = pair['fi'] if mode == "English -> Finnish" else pair['en']

    if user_input == correct.lower():
        st.session_state.feedback = "✅ Correct!"
        get_new_word()
        st.session_state.user_answer = "" 
    else:
        en_key = pair['en']
        st.session_state.error_stats[en_key] = st.session_state.error_stats.get(en_key, 0) + 1
        st.session_state.feedback = "❌ Wrong answer."

def skip_word():
    st.session_state.feedback = "Skipped."
    get_new_word()

def reveal_word():
    pair = st.session_state.current_pair
    mode = st.session_state.mode_selection
    answer = pair['fi'] if mode == "English -> Finnish" else pair['en']
    st.session_state.reveal_text = f"The correct answer was: **{answer}**"

# --- 4. UI Layout ---
st.title("🇫🇮 Finnish Vocabulary Trainer")

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Select Mode:", ["English -> Finnish", "Finnish -> English"], key="mode_selection")
    
    st.markdown("---")
    st.header("Stats")
    if st.session_state.error_stats:
        sorted_stats = sorted(st.session_state.error_stats.items(), key=lambda x: x[1], reverse=True)
        for w, c in sorted_stats:
            st.write(f"**{w}**: {c} errors")
    else:
        st.write("No errors yet.")

if not st.session_state.vocab:
    st.error("Could not find 'words' file. Please upload a file named 'words' or 'words.txt' to GitHub.")
elif not st.session_state.game_active:
    st.info("Game Stopped. Reload page to restart.")
else:
    if st.session_state.current_pair is None:
        get_new_word()

    pair = st.session_state.current_pair
    question_word = pair['en'] if st.session_state.mode_selection == "English -> Finnish" else pair['fi']

    st.subheader(f"Translate: **{question_word}**")

    with st.form(key='answer_form', clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Your Answer:", key="user_answer")
        with col2:
            st.write("") 
            st.write("") 
            st.form_submit_button("Submit", on_click=submit_answer)

    if st.session_state.feedback:
        if "Correct" in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)

    if st.session_state.reveal_text:
        st.warning(st.session_state.reveal_text)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("Skip Word", on_click=skip_word)
    with c2:
        st.button("Reveal Word", on_click=reveal_word)
    with c3:
        if st.button("Stop Game"):
            st.session_state.game_active = False
            st.rerun()
