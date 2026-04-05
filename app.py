import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import json
import random
import pandas as pd
from datetime import datetime, timedelta

# =================================================================
# 1. ΠΡΟΗΓΜΕΝΗ ΑΡΧΙΤΕΚΤΟΝΙΚΗ UI & CSS (DUOLINGO 2.0)
# =================================================================
st.set_page_config(page_title="PedaGO Pro Ultra v1.3", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;700&family=Outfit:wght@300;600;900&display=swap');

    :root {
        --duo-green: #58cc02;
        --duo-blue: #1cb0f6;
        --duo-orange: #ff9600;
        --duo-red: #ff4b4b;
        --premium-gold: #ffc800;
    }

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; background-color: #ffffff; }

    /* Κάρτες Μαθημάτων στυλ Duolingo */
    .lesson-card {
        background: white;
        border: 2px solid #e5e5e5;
        border-bottom: 6px solid #e5e5e5;
        border-radius: 20px;
        padding: 20px;
        transition: all 0.2s;
        cursor: pointer;
        text-align: center;
    }
    .lesson-card:hover { transform: translateY(2px); border-bottom: 2px solid #e5e5e5; }

    /* Streak & Stats Bar */
    .stats-container {
        display: flex;
        justify-content: space-around;
        background: white;
        padding: 15px;
        border-bottom: 2px solid #f1f1f1;
        position: sticky;
        top: 0;
        z-index: 1000;
    }

    .stat-item { font-weight: 900; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }
    .fire { color: var(--duo-orange); }
    .gem { color: var(--duo-blue); }
    .heart { color: var(--duo-red); }

    /* Premium Chat Bubbles */
    .stChatMessage {
        border: 2px solid #e5e5e5 !important;
        border-radius: 20px !important;
        box-shadow: none !important;
        background: white !important;
        margin-bottom: 15px !important;
    }

    /* Floating Action Button (Mic) */
    .mic-fixed {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: var(--duo-blue);
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. ΣΥΣΤΗΜΑ ΔΙΑΧΕΙΡΙΣΗΣ ΔΕΔΟΜΕΝΩΝ (GAMIFICATION ENGINE)
# =================================================================
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "name": "Εξερευνητής",
        "gems": 500,
        "streak": 1,
        "hearts": 5,
        "xp": 0,
        "level": 1,
        "unlocked_topics": ["Χρώματα", "Ζώα"],
        "completed_lessons": 0
    }

if "app_state" not in st.session_state: st.session_state.app_state = "lobby"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "audio_to_play" not in st.session_state: st.session_state.audio_to_play = None

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# =================================================================
# 3. CORE FUNCTIONS (SENSORS & OUTPUT)
# =================================================================
def trigger_audio(text):
    try:
        tts = gTTS(text=text, lang='el')
        b = io.BytesIO()
        tts.write_to_fp(b)
        b.seek(0)
        b64 = base64.b64encode(b.read()).decode()
        return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except: return ""

def add_xp(amount):
    st.session_state.user_data["xp"] += amount
    if st.session_state.user_data["xp"] >= st.session_state.user_data["level"] * 100:
        st.session_state.user_data["level"] += 1
        st.toast(f"🎉 LEVEL UP! Έφτασες το επίπεδο {st.session_state.user_data['level']}!")

# =================================================================
# 4. ΟΘΟΝΗ LOBBY (DUOLINGO WORLD MAP)
# =================================================================
if st.session_state.app_state == "lobby":
    # Top Stats Bar
    st.markdown(f"""
        <div class="stats-container">
            <div class="stat-item fire">🔥 {st.session_state.user_data['streak']}</div>
            <div class="stat-item gem">💎 {st.session_state.user_data['gems']}</div>
            <div class="stat-item heart">❤️ {st.session_state.user_data['hearts']}</div>
            <div class="stat-item" style="color:#58cc02;">🏆 LVL {st.session_state.user_data['level']}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; font-family:Comfortaa; margin-top:30px;'>Πού θα πάμε σήμερα; 🗺️</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='lesson-card'><h3>🦁 Ζωολογικός Κήπος</h3><p>Μάθε τα ζώα!</p></div>", unsafe_allow_html=True)
        if st.button("Ξεκίνα 🐾", key="zoo"):
            st.session_state.current_topic = "Ζώα"
            st.session_state.app_state = "learning"
            st.rerun()

    with col2:
        st.markdown("<div class='lesson-card'><h3>🎨 Το Εργαστήρι</h3><p>Χρώματα & Σχήματα</p></div>", unsafe_allow_html=True)
        if st.button("Ξεκίνα 🎨", key="colors"):
            st.session_state.current_topic = "Χρώματα"
            st.session_state.app_state = "learning"
            st.rerun()

    with col3:
        st.markdown("<div class='lesson-card' style='opacity:0.5;'><h3>🚀 Διάστημα</h3><p>Locked</p></div>", unsafe_allow_html=True)
        st.button("Ξεκλείδωσε 💎200", key="space")

# =================================================================
# 5. ΟΘΟΝΗ LEARNING (ACTIVE INTERACTION)
# =================================================================
elif st.session_state.app_state == "learning":
    st.markdown(f"### 📍 Μαθαίνεις για: {st.session_state.current_topic}")
    
    if not st.session_state.chat_history:
        st.session_state.chat_history = [{
            "role": "system", 
            "content": f"Είσαι ο Φοίβος. Δίδαξε στο παιδί {st.session_state.current_topic}. Κάνε μικρές ερωτήσεις. Αν απαντήσει σωστά, δώσε XP. Μίλα με ενθουσιασμό!"
        }]

    # Chat Display
    for m in st.session_state.chat_history:
        if m["role"] != "system":
            avatar = "🧸" if m["role"] == "assistant" else "🧒"
            with st.chat_message(m["role"], avatar=avatar):
                st.write(m["content"])

    # Bottom Mic Zone
    st.write("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        voice_msg = speech_to_text(language='el', start_prompt="🎤 Μίλησε!", stop_prompt="✅ Τέλος", key='voice_pro')

    if voice_msg:
        if "last_v" not in st.session_state or st.session_state.last_v != voice_msg:
            st.session_state.last_v = voice_msg
            st.session_state.chat_history.append({"role": "user", "content": voice_msg})
            add_xp(20) # Πόντοι για κάθε απάντηση
            
            with st.chat_message("assistant", avatar="🧸"):
                with st.spinner("Ο Φοίβος ακούει..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=st.session_state.chat_history
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.session_state.audio_to_play = trigger_audio(reply)
                    st.rerun()

    if st.session_state.audio_to_play:
        st.markdown(st.session_state.audio_to_play, unsafe_allow_html=True)
        st.session_state.audio_to_play = None

    if st.button("⬅️ Πίσω στο Χάρτη"):
        st.session_state.app_state = "lobby"
        st.session_state.chat_history = []
        st.rerun()

# =================================================================
# 6. FOOTER & ANALYTICS
# =================================================================
st.markdown("<br><br><div style='text-align:center; color:#ccc;'>PedaGO Premium v1.3 | Powered by AI | 1000+ Lines Capability</div>", unsafe_allow_html=True)
