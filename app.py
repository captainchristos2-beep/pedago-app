import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# =================================================================
# 1. PREMIUM ENGINE CONFIGURATION & STYLING
# =================================================================
st.set_page_config(page_title="PedaGO Genesis Pro v1.7", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Outfit:wght@300;400;600;900&display=swap');

    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #0ea5e9, #6366f1);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Containers */
    .genesis-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(20px);
        border-radius: 35px;
        padding: 35px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        color: white;
        margin-bottom: 20px;
    }

    /* Pricing Tiers */
    .pricing-card {
        background: white;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        color: #1e293b;
        border: 4px solid transparent;
        transition: 0.3s;
    }
    .pricing-premium { border-color: #ffd700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.3); }

    /* HUD Stats */
    .hud-item { font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.1rem; color: #ffd700; }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
        color: white;
        font-weight: 700;
        border: none;
        padding: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.03); box-shadow: 0 0 15px rgba(14, 165, 233, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. CORE DATABASE & SESSION MANAGEMENT (SAAS LOGIC)
# =================================================================
if "user" not in st.session_state:
    st.session_state.user = {
        "is_auth": False,
        "plan": "Free", # Free / Premium
        "xp": 0,
        "energy": 100,
        "messages_today": 0,
        "name": "Εξερευνητής",
        "streak": 1
    }

if "scene" not in st.session_state: st.session_state.scene = "login"
if "history" not in st.session_state: st.session_state.history = []
if "audio_out" not in st.session_state: st.session_state.audio_out = None

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='el')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except: return ""

# =================================================================
# 3. SAAS AUTH & SUBSCRIPTION LAYER
# =================================================================
if st.session_state.scene == "login":
    st.markdown("<h1 style='text-align:center; color:white; font-family:Comfortaa; font-size:4rem;'>PedaGO Genesis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#cbd5e1;'>Η επόμενη γενιά στην AI εκπαίδευση</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""<div class='pricing-card'>
            <h2>Basic Plan</h2>
            <h1 style='color:#64748b;'>0€ <small>/μήνα</small></h1>
            <p>• 5 μηνύματα ανά ημέρα</p>
            <p>• 1 κόσμος μάθησης</p>
            <p>• Βασικό AI</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Επιλογή Basic"):
            st.session_state.user["is_auth"] = True
            st.session_state.user["plan"] = "Free"
            st.session_state.scene = "lobby"
            st.rerun()

    with col2:
        st.markdown("""<div class='pricing-card pricing-premium'>
            <h2 style='color:#ffd700;'>Premium Pro 💎</h2>
            <h1 style='color:#1e293b;'>9.99€ <small>/μήνα</small></h1>
            <p>• Απεριόριστα μηνύματα</p>
            <p>• Όλοι οι Genesis κόσμοι</p>
            <p>• Αναλυτικά Parent Reports</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Αγορά Premium 💳"):
            st.session_state.user["is_auth"] = True
            st.session_state.user["plan"] = "Premium"
            st.session_state.scene = "lobby"
            st.rerun()

# =================================================================
# 4. LOBBY: THE METASCHOOL HUB
# =================================================================
elif st.session_state.scene == "lobby":
    # HUD Bar
    hud1, hud2, hud3, hud4 = st.columns(4)
    hud1.markdown(f"<div class='hud-item'>👤 {st.session_state.user['name']}</div>", unsafe_allow_html=True)
    hud2.markdown(f"<div class='hud-item'>✨ XP: {st.session_state.user['xp']}</div>", unsafe_allow_html=True)
    hud3.markdown(f"<div class='hud-item'>🔋 Energy: {st.session_state.user['energy']}%</div>", unsafe_allow_html=True)
    hud4.markdown(f"<div class='hud-item'>🏆 Plan: {st.session_state.user['plan']}</div>", unsafe_allow_html=True)

    st.markdown("<br><h1 style='text-align:center; color:white;'>Πού θα ταξιδέψουμε;</h1>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown("<div class='genesis-card'><h3>🏝️ Νησί Γρίφων</h3><p>Ελεύθερη πρόσβαση</p></div>", unsafe_allow_html=True)
        if st.button("Εξερεύνηση ➔", key="island"):
            st.session_state.quest = "Νησί Γρίφων"
            st.session_state.scene = "adventure"
            st.rerun()

    with m2:
        is_locked = st.session_state.user["plan"] == "Free"
        st.markdown(f"<div class='genesis-card' style='opacity:{'0.5' if is_locked else '1'}'><h3>🪐 Πλανήτης Φαντασίας</h3><p>{'🔒 Μόνο Pro' if is_locked else 'Διαθέσιμο'}</p></div>", unsafe_allow_html=True)
        if st.button("Πτήση ➔", key="planet", disabled=is_locked):
            st.session_state.quest = "Πλανήτης Φαντασίας"
            st.session_state.scene = "adventure"
            st.rerun()

    with m3:
        st.markdown("<div class='genesis-card'><h3>📊 Parent Portal</h3><p>Αναλύσεις προόδου</p></div>", unsafe_allow_html=True)
        if st.button("Δες Αναφορές"):
            st.session_state.scene = "analytics"
            st.rerun()

# =================================================================
# 5. ADVENTURE ENGINE (AI NARRATIVE & QUOTA CONTROL)
# =================================================================
elif st.session_state.scene == "adventure":
    # Quota Control for SaaS
    if st.session_state.user["plan"] == "Free" and st.session_state.user["messages_today"] >= 5:
        st.error("🛑 Έφτασες το ημερήσιο όριο! Αναβάθμισε σε Premium για ασταμάτητο παιχνίδι.")
        if st.button("Επιστροφή"): st.session_state.scene = "lobby"; st.rerun()
    else:
        st.markdown(f"<h2 style='color:white; text-align:center;'>📍 Αποστολή: {st.session_state.quest}</h2>", unsafe_allow_html=True)
        
        if not st.session_state.history:
            st.session_state.history = [{"role": "system", "content": f"Είσαι ο Φοίβος Genesis. Οδηγείς το παιδί στην αποστολή {st.session_state.quest}. Κάνε μικρές ερωτήσεις, δώσε XP και μίλα με μαγικό τρόπο."}]

        # Render Chat
        for m in st.session_state.history:
            if m["role"] != "system":
                avatar = "🧸" if m["role"] == "assistant" else "🧒"
                with st.chat_message(m["role"], avatar=avatar):
                    st.write(m["content"])

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            input_text = speech_to_text(language='el', start_prompt="🎤 Μίλησε στον Φοίβο", stop_prompt="✅ Ανάλυση", key='genesis_mic')

        if input_text:
            if "last_v" not in st.session_state or st.session_state.last_v != input_text:
                st.session_state.last_v = input_text
                st.session_state.history.append({"role": "user", "content": input_text})
                st.session_state.user["messages_today"] += 1
                st.session_state.user["xp"] += 20
                
                with st.chat_message("assistant", avatar="🧸"):
                    with st.spinner("✨ Επεξεργασία μαγείας..."):
                        r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.history)
                        reply = r.choices[0].message.content
                        st.write(reply)
                        st.session_state.history.append({"role": "assistant", "content": reply})
                        st.session_state.audio_out = play_audio(reply)
                        st.rerun()

        if st.session_state.audio_out:
            st.markdown(st.session_state.audio_out, unsafe_allow_html=True)
            st.session_state.audio_out = None

    if st.button("⬅️ Έξοδος στο Lobby"):
        st.session_state.scene = "lobby"
        st.session_state.history = []
        st.rerun()

# =================================================================
# 6. ANALYTICS: THE PARENT DASHBOARD
# =================================================================
elif st.session_state.scene == "analytics":
    st.markdown("<h1 style='color:white; text-align:center;'>📊 Parent Analytics Portal</h1>", unsafe_allow_html=True)
    
    if st.session_state.user["plan"] == "Free":
        st.warning("⚠️ Οι αναλυτικές αναφορές είναι διαθέσιμες μόνο σε Premium χρήστες.")
        if st.button("Αναβάθμιση Τώρα"): st.session_state.scene = "login"; st.rerun()
    else:
        st.markdown("<div class='genesis-card'>", unsafe_allow_html=True)
        st.write(f"### Σύνοψη για τον {st.session_state.user['name']}")
        col1, col2 = st.columns(2)
        col1.metric("Συνολικά XP", st.session_state.user["xp"])
        col2.metric("Streak", f"{st.session_state.user['streak']} Ημέρες")
        
        # Mock Data Chart
        chart_data = pd.DataFrame({
            'Ημέρα': ['Δευτ', 'Τρ', 'Τετ', 'Πεμ', 'Παρ', 'Σαβ', 'Κυρ'],
            'Λέξεις': [50, 80, 45, 120, 90, 150, 200]
        })
        fig = px.line(chart_data, x='Ημέρα', y='Λέξεις', title='Λεκτική Ανάπτυξη ανά Ημέρα')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⬅️ Πίσω"): st.session_state.scene = "lobby"; st.rerun()

# Footer
st.markdown("<p style='text-align:center; color:white; opacity:0.3; margin-top:50px;'>PedaGO Genesis Pro v1.7 | SaaS Platform | 2026</p>", unsafe_allow_html=True)
