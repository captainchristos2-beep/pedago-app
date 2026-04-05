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

# =================================================================
# MODULE 1: THE INFINITE DESIGN SYSTEM
# =================================================================
class DesignSystem:
    @staticmethod
    def inject_assets():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Outfit:wght@300;600;900&display=swap');
            
            /* Genesis Pro Background */
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

            /* Pro Containers */
            .genesis-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border-radius: 40px;
                padding: 40px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 30px 60px rgba(0,0,0,0.4);
                color: white;
                margin-bottom: 25px;
            }

            /* Subscription Tiers */
            .tier-card {
                background: white;
                border-radius: 30px;
                padding: 45px;
                text-align: center;
                color: #1e293b;
                border: 3px solid transparent;
                transition: all 0.4s ease;
            }
            .tier-card:hover { transform: translateY(-15px); border-color: #0ea5e9; }
            .premium-gold { border: 4px solid #ffd700 !important; box-shadow: 0 0 30px rgba(255, 215, 0, 0.2); }

            /* HUD Metrics */
            .hud-value { font-family: 'Outfit', sans-serif; font-weight: 900; color: #ffd700; font-size: 1.2rem; }
            
            /* Professional Chat */
            .stChatMessage {
                background: rgba(255, 255, 255, 0.05) !important;
                border-radius: 25px !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
            }
            </style>
        """, unsafe_allow_html=True)

# =================================================================
# MODULE 2: DATA & SAAS ORCHESTRATION
# =================================================================
class DataCore:
    @staticmethod
    def sync():
        if "meta" not in st.session_state:
            st.session_state.meta = {
                "auth": False,
                "plan": "Free",
                "name": "Εξερευνητής",
                "xp": 0,
                "streak": 1,
                "quota": 5,
                "used": 0,
                "mood": "Neutral"
            }
        if "scene" not in st.session_state: st.session_state.scene = "gateway"
        if "log" not in st.session_state: st.session_state.log = []
        if "stream" not in st.session_state: st.session_state.stream = None

# =================================================================
# MODULE 3: INTELLIGENT AI ENGINE
# =================================================================
class OracleAI:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    def process(self, history):
        try:
            # Ενισχυμένο Prompting για EQ
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                temperature=0.8,
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Σφάλμα σύνδεσης: {str(e)}"

    def voice_synth(self, text):
        tts = gTTS(text=text, lang='el')
        b = io.BytesIO()
        tts.write_to_fp(b)
        b.seek(0)
        b64 = base64.b64encode(b.read()).decode()
        return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# =================================================================
# MODULE 4: INFINITE SCENE CONTROLLER
# =================================================================
def app_controller():
    DesignSystem.inject_assets()
    DataCore.sync()
    ai = OracleAI()

    # --- SCENE 1: GATEWAY (PRICING) ---
    if st.session_state.scene == "gateway":
        st.markdown("<h1 style='text-align:center; color:white;'>PedaGO Infinite</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#cbd5e1;'>Η απόλυτη εμπειρία AI μάθησης</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='tier-card'><h2>Basic</h2><h1>0€</h1><p>5 Αποστολές/Ημέρα<br>Βασικό AI</p></div>", unsafe_allow_html=True)
            if st.button("Επιλογή Basic"):
                st.session_state.meta["auth"] = True
                st.session_state.meta["plan"] = "Free"
                st.session_state.scene = "hub"
                st.rerun()

        with c2:
            st.markdown("<div class='tier-card premium-gold'><h2>Infinity Pro</h2><h1>9.99€</h1><p>Απεριόριστες Αποστολές<br>Full Parent Insights<br>Voice Synthesis Pro</p></div>", unsafe_allow_html=True)
            if st.button("Γίνε Pro 💳"):
                st.session_state.meta["auth"] = True
                st.session_state.meta["plan"] = "Pro"
                st.session_state.scene = "hub"
                st.rerun()

    # --- SCENE 2: HUB (CENTRAL MAP) ---
    elif st.session_state.scene == "hub":
        # Global HUD Bar
        hud = st.columns(4)
        hud[0].markdown(f"<div class='hud-value'>👤 {st.session_state.meta['name']}</div>", unsafe_allow_html=True)
        hud[1].markdown(f"<div class='hud-value'>✨ XP: {st.session_state.meta['xp']}</div>", unsafe_allow_html=True)
        hud[2].markdown(f"<div class='hud-value'>🔥 Streak: {st.session_state.meta['streak']}</div>", unsafe_allow_html=True)
        hud[3].markdown(f"<div class='hud-value'>💎 Plan: {st.session_state.meta['plan']}</div>", unsafe_allow_html=True)

        st.markdown("<br><h2 style='text-align:center; color:white;'>Πού θα ταξιδέψουμε;</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='genesis-card'><h3>🏝️ Νησί των Γρίφων</h3><p>Μάθε τα μυστικά της φύσης!</p></div>", unsafe_allow_html=True)
            if st.button("Έναρξη ➔", key="q1"):
                st.session_state.quest = "Νησί Γρίφων"
                st.session_state.scene = "active_quest"
                st.rerun()
        
        with col2:
            is_pro = st.session_state.meta["plan"] == "Pro"
            st.markdown(f"<div class='genesis-card' style='opacity:{1 if is_pro else 0.4}'><h3>🌌 Πλανήτης Φαντασίας</h3><p>{'Ανοιχτό' if is_pro else '🔒 Μόνο Pro'}</p></div>", unsafe_allow_html=True)
            if st.button("Πτήση ➔", key="q2", disabled=not is_pro):
                st.session_state.quest = "Πλανήτης Φαντασίας"
                st.session_state.scene = "active_quest"
                st.rerun()

    # --- SCENE 3: ACTIVE QUEST (LEARNING) ---
    elif st.session_state.scene == "active_quest":
        # Quota Logic
        if st.session_state.meta["plan"] == "Free" and st.session_state.meta["used"] >= st.session_state.meta["quota"]:
            st.error("🛑 Το ημερήσιο όριο εξαντλήθηκε! Γίνε Pro για να συνεχίσεις.")
            if st.button("Πίσω στο Hub"): st.session_state.scene = "hub"; st.rerun()
        else:
            st.markdown(f"<h2 style='color:white; text-align:center;'>📍 {st.session_state.quest}</h2>", unsafe_allow_html=True)
            
            if not st.session_state.log:
                st.session_state.log = [{"role": "system", "content": f"Είσαι ο Φοίβος. Δίδαξε τον {st.session_state.meta['name']} για {st.session_state.quest}. Κάνε ερωτήσεις και δίνε XP!"}]

            # Chat Display
            for m in st.session_state.log:
                if m["role"] != "system":
                    avatar = "🧸" if m["role"] == "assistant" else "🧒"
                    with st.chat_message(m["role"], avatar=avatar):
                        st.write(m["content"])

            # Interaction
            st.markdown("---")
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                voice = speech_to_text(language='el', start_prompt="🎤 Μίλησε στον Φοίβο", stop_prompt="✅ Τέλος", key='voice_infinite')

            if voice:
                if "last_processed" not in st.session_state or st.session_state.last_processed != voice:
                    st.session_state.last_processed = voice
                    st.session_state.log.append({"role": "user", "content": voice})
                    st.session_state.meta["used"] += 1
                    st.session_state.meta["xp"] += 30
                    
                    with st.chat_message("assistant", avatar="🧸"):
                        with st.spinner("✨ Επεξεργασία Γνώσης..."):
                            reply = ai.process(st.session_state.log)
                            st.write(reply)
                            st.session_state.log.append({"role": "assistant", "content": reply})
                            st.session_state.stream = ai.voice_synth(reply)
                            st.rerun()

            if st.session_state.stream:
                st.markdown(st.session_state.stream, unsafe_allow_html=True)
                st.session_state.stream = None

            if st.button("🏃 Επιστροφή"):
                st.session_state.scene = "hub"
                st.session_state.log = []
                st.rerun()

if __name__ == "__main__":
    app_controller()
