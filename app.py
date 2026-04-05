import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time

# 1. Configuration & Ultra Premium Theme
st.set_page_config(page_title="PedaGO Ultra v1.4", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;700&family=Outfit:wght@300;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%);
    }

    /* Glassmorphism Card για την Αρχική Οθόνη */
    .teacher-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
        text-align: center;
    }

    .main-title {
        font-family: 'Comfortaa', cursive;
        font-size: 4rem;
        background: linear-gradient(45deg, #0ea5e9, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* XP & Level Badges */
    .status-badge {
        background: white;
        padding: 8px 20px;
        border-radius: 50px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        font-weight: 600;
        color: #0369a1;
    }

    /* Custom Button */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background: linear-gradient(90deg, #0ea5e9, #2563eb);
        color: white;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(14, 165, 233, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. State Management
if "app_state" not in st.session_state:
    st.session_state.app_state = "teacher_gate" # Αρχική κατάσταση
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

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

# --- SCREEN 1: TEACHER GATE ---
if st.session_state.app_state == "teacher_gate":
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <div class='teacher-card'>
                <h1 class='main-title'>PedaGO</h1>
                <p style='color: #64748b; font-size: 1.2rem;'>Καλωσήρθατε στην ψηφιακή γωνιά μάθησης</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔐 Ρυθμίσεις Εκπαιδευτικού", expanded=True):
            goal = st.text_input("Στόχος Συζήτησης (π.χ. Τα ζώα της ζούγκλας)", "Γενική Μάθηση")
            tone = st.select_slider("Τόνος Φοίβου", options=["Πολύ Απλός", "Ενθουσιώδης", "Προκλητικός"])
            
            if st.button("✨ Έναρξη Μαγείας"):
                # Δημιουργία του System Prompt βάσει των ρυθμίσεων
                st.session_state.messages = [{
                    "role": "system", 
                    "content": f"""Είσαι ο Φοίβος, ο AI βοηθός. Στόχος: {goal}. 
                    Τόνος: {tone}. Μίλα απλά, κάνε 1 ερώτηση, χρησιμοποίησε emojis. 
                    Μην δίνεις έτοιμες απαντήσεις (τύπου MagicSchool)."""
                }]
                st.session_state.app_state = "interaction"
                st.rerun()

# --- SCREEN 2: INTERACTION MODE ---
else:
    # Sidebar Dashboard
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>📊 Πρόοδος</h2>", unsafe_allow_html=True)
        st.progress(min(st.session_state.xp / 100, 1.0))
        st.write(f"**XP Points:** {st.session_state.xp}")
        st.write("---")
        if st.button("🔒 Έξοδος & Αναφορά
