import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# =================================================================
# 1. ARCHITECTURAL UI ENGINE (NEOMORPHIC DESIGN)
# =================================================================
st.set_page_config(page_title="PedaGO Oracle v1.4", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Outfit:wght@300;400;700;900&display=swap');

    :root {
        --glass: rgba(255, 255, 255, 0.9);
        --neon-blue: #00d2ff;
        --neon-purple: #9d50bb;
    }

    html, body, [class*="css"] { 
        font-family: 'Outfit', sans-serif; 
        background: #0f172a; /* Dark Premium Theme */
        color: #f1f5f9;
    }

    /* Cinematic Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
    }

    /* Skill Cards */
    .skill-card {
        background: var(--glass);
        border-radius: 24px;
        padding: 25px;
        color: #1e293b;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .skill-card:hover { transform: scale(1.05) translateY(-10px); }

    /* XP Progress Bar Pro */
    .stProgress > div > div > div > div {
        background-image: linear-gradientTo(to right, #00d2ff, #3a7bd5);
        border-radius: 10px;
    }

    /* Chat Bubbles Oracle Style */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. ADVANCED DATA CORE (STATE & PERSISTENCE)
# =================================================================
if "vault" not in st.session_state:
    st.session_state.vault = {
        "xp": 0,
        "level": 1,
        "streak": 1,
        "energy": 100,
        "inventory": ["Φακός Γνώσης"],
        "achievements": [],
        "last_active": datetime.now().strftime("%Y-%m-%d")
    }

if "mode" not in st.session_state: st.session_state.mode = "world_map"
if "history" not in st.session_state: st.session_state.history = []
if "audio_trigger" not in st.session_state: st.session_state.audio_trigger = None

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def add_experience(pts):
    st.session_state.vault["xp"] += pts
    if st.session_state.vault["xp"] >= st.session_state.vault["level"] * 150:
        st.session_state.vault["level"] += 1
        st.balloons()
        return True
    return False

def get_audio_payload(text):
    tts = gTTS(text=text, lang='el')
    b = io.BytesIO()
    tts.write_to_fp(b)
    b.seek(0)
    b64 = base64.b64encode(b.read()).decode()
    return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# =================================================================
# 3. WORLD MAP SCREEN (QUEST SELECTION)
# =================================================================
if st.session_state.mode == "world_map":
    # Global HUD
    cols = st.columns([1,1,1,1])
    cols[0].markdown(f"🔥 **Streak:** {st.session_state.vault['streak']}")
    cols[1].markdown(f"💎 **XP:** {st.session_state.vault['xp']}")
    cols[2].markdown(f"🔋 **Ενέργεια:** {st.session_state.vault['energy']}%")
    cols[3].markdown(f"🏆 **Level:** {st.session_state.vault['level']}")
    
    st.markdown("<h1 style='text-align:center; font-family:Comfortaa; font-size:3rem;'>Επίλεξε την Αποστολή σου ⚔️</h1>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown("""<div class='skill-card'><h3>🌋 Το Ηφαίστειο των Λέξεων</h3><p>Δυσκολία: ⭐⭐</p></div>""", unsafe_allow_html=True)
        if st.button("Είσοδος ➔", key="mission_1"):
            st.session_state.quest = "Ηφαίστειο Λέξεων"
            st.session_state.mode = "quest_active"
            st.rerun()

    with m2:
        st.markdown("""<div class='skill-card'><h3>🌌 Ο Γαλαξίας των Σχημάτων</h3><p>Δυσκολία: ⭐⭐⭐</p></div>""", unsafe_allow_html=True)
        if st.button("Πτήση ➔", key="mission_2"):
            st.session_state.quest = "Γαλαξίας Σχημάτων"
            st.session_state.mode = "quest_active"
            st.rerun()
            
    with m3:
        st.markdown("""<div class='skill-card' style='opacity:0.6'><h3>🏰 Το Κάστρο των Μαθηματικών</h3><p>🔒 Κλειδωμένο (Level 5)</p></div>""", unsafe_allow_html=True)

# =================================================================
# 4. QUEST ENGINE (ACTIVE AI INTERACTION)
# =================================================================
elif st.session_state.mode == "quest_active":
    st.markdown(f"## 🛡️ Αποστολή: {st.session_state.quest}")
    st.progress(min(st.session_state.vault["xp"] % 150 / 150, 1.0))
    
    if not st.session_state.history:
        st.session_state.history = [{"role": "system", "content": f"Είσαι ο Φοίβος Oracle. Καθοδήγησε το παιδί στην αποστολή {st.session_state.quest}. Μίλα σαν επικός ήρωας, κάνε ερωτήσεις και δώσε πόντους για σωστές απαντήσεις."}]

    # Render History
    for m in st.session_state.history:
        if m["role"] != "system":
            with st.chat_message(m["role"], avatar="🧸" if m["role"]=="assistant" else "🧒"):
                st.write(m["content"])

    # Voice Input Layer
    st.write("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        voice_raw = speech_to_text(language='el', start_prompt="🎤 Μίλησε στον Oracle", stop_prompt="✅ Ανάλυση", key='oracle_mic')

    if voice_raw:
        if "last_v" not in st.session_state or st.session_state.last_v != voice_raw:
            st.session_state.last_v = voice_raw
            st.session_state.history.append({"role": "user", "content": voice_raw})
            add_experience(25)
            
            with st.chat_message("assistant", avatar="🧸"):
                with st.spinner("🔮 Ο Oracle οραματίζεται την απάντηση..."):
                    r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.history)
                    reply = r.choices[0].message.content
                    st.write(reply)
                    st.session_state.history.append({"role": "assistant", "content": reply})
                    st.session_state.audio_trigger = get_audio_payload(reply)
                    st.rerun()

    if st.session_state.audio_trigger:
        st.markdown(st.session_state.audio_trigger, unsafe_allow_html=True)
        st.session_state.audio_trigger = None

    if st.button("🏃 Φυγή στο Χάρτη"):
        st.session_state.mode = "world_map"
        st.session_state.history = []
        st.rerun()

# =================================================================
# 5. DATA ANALYTICS (TEACHER VIEW - HIDDEN IN SIDEBAR)
# =================================================================
with st.sidebar:
    st.title("🎛️ Oracle Console")
    if st.checkbox("Εμφάνιση Analytics"):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = st.session_state.vault["xp"],
            title = {'text': "Συνολική Γνώση (XP)"},
            gauge = {'axis': {'range': [None, 1000]}, 'bar': {'color': "#00d2ff"}}
        ))
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Συνολικά μηνύματα: {len(st.session_state.history)}")

st.markdown("<p style='text-align:center; opacity:0.3; margin-top:100px;'>Oracle v1.4 | PedaGO OS | 2026</p>", unsafe_allow_html=True)
