import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time

# 1. Configuration & Global Styling
st.set_page_config(page_title="PedaGO Ultra Pro v1.5", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Montserrat:wght@400;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #ffffff 0%, #f1f5f9 100%);
    }

    .premium-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 30px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
        text-align: center;
        max-width: 800px;
        margin: auto;
    }

    .main-header {
        font-family: 'Comfortaa', cursive;
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .achievement-badge {
        display: inline-block;
        padding: 8px 15px;
        background: #fef3c7;
        color: #92400e;
        border-radius: 12px;
        font-weight: 800;
        font-size: 0.8rem;
        margin: 5px;
        border: 1.5px solid #fcd34d;
    }

    .mic-wrap {
        display: flex;
        justify-content: center;
        padding: 15px;
        background: white;
        border-radius: 100px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State Initialization
if "app_state" not in st.session_state:
    st.session_state.app_state = "launcher"
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "achievements" not in st.session_state:
    st.session_state.achievements = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_goal" not in st.session_state:
    st.session_state.session_goal = ""

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='el')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except: pass

# --- SCREEN 1: THE LAUNCHER ---
if st.session_state.app_state == "launcher":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='premium-card'>
            <h1 class='main-header'>PedaGO</h1>
            <p style='color: #64748b; font-size: 1.2rem;'>Η απόλυτη AI εμπειρία μάθησης v1.5</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("teacher_settings"):
            st.markdown("### 🛠️ Ρυθμίσεις Εκπαιδευτικού")
            goal = st.text_input("Θέμα συζήτησης:", placeholder="π.χ. Τα ζώα της θάλασσας")
            difficulty = st.select_slider("Επίπεδο Καθοδήγησης:", options=["Απλό", "Μεσαίο", "Προχωρημένο"])
            
            submit = st.form_submit_button("🚀 ΕΝΑΡΞΗ ΜΑΘΗΜΑΤΟΣ")
            if submit:
                st.session_state.session_goal = goal
                system_instruction = f"Είσαι ο Φοίβος, AI παιδαγωγός. Θέμα: {goal}. Επίπεδο: {difficulty}. Μίλα απλά, κάνε ερωτήσεις, χρησιμοποίησε emojis και μην δίνεις έτοιμες απαντήσεις."
                st.session_state.
