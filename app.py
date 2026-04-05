import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import pandas as pd
import plotly.express as px

# =================================================================
# MODULE 1: UI & DESIGN SYSTEM (THE LOOK)
# =================================================================
class UI:
    @staticmethod
    def apply_styles():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Outfit:wght@300;600;900&display=swap');
            
            /* Genesis Gradient Background */
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

            /* Glassmorphism Components */
            .card {
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(25px);
                border-radius: 30px;
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 20px 40px rgba(0,0,0,0.4);
                color: white;
                margin-bottom: 20px;
            }

            .pricing-card {
                background: white;
                border-radius: 25px;
                padding: 40px;
                text-align: center;
                color: #1e293b;
                border: 2px solid #e2e8f0;
                transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            .pricing-card:hover { border-color: #0ea5e9; transform: translateY(-10px); }
            
            .premium-border { border: 4px solid #ffd700 !important; }

            /* Professional HUD */
            .hud-label { font-family: 'Outfit', sans-serif; font-weight: 800; color: #ffd700; font-size: 1rem; }
            
            /* Buttons */
            .stButton>button {
                border-radius: 15px;
                background: linear-gradient(90deg, #0ea5e9, #6366f1);
                color: white;
                font-weight: 700;
                border: none;
                height: 3.5rem;
                transition: 0.3s ease;
            }
            </style>
        """, unsafe_allow_html=True)

# =================================================================
# MODULE 2: SAAS & USER CORE (THE RULES)
# =================================================================
class SessionManager:
    @staticmethod
    def initialize():
        if "user" not in st.session_state:
            st.session_state.user = {
                "auth": False,
                "plan": "Free",
                "name": "Εξερευνητής",
                "xp": 0,
                "energy": 100,
                "daily_limit": 5,
                "usage": 0
            }
        if "scene" not in st.session_state: st.session_state.scene = "login"
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        if "audio_buffer" not in st.session_state: st.session_state.audio_buffer = None

    @staticmethod
    def check_quota():
        if st.session_state.user["plan"] == "Free" and st.session_state.user["usage"] >= st.session_state.user["daily_limit"]:
            return False
        return True

# =================================================================
# MODULE 3: AI ORCHESTRATOR (THE BRAIN)
# =================================================================
class AICore:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    def generate_response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ωχ! Κάτι κούρασε τη σκέψη μου: {str(e)}"

    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='el')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        except: return ""

# =================================================================
# MODULE 4: SCENE CONTROLLER (THE JOURNEY)
# =================================================================
def main():
    UI.apply_styles()
    SessionManager.initialize()
    ai = AICore()

    # --- SCENE: LOGIN / PRICING ---
    if st.session_state.scene == "login":
        st.markdown("<h1 style='text-align:center; color:white; font-family:Comfortaa;'>PedaGO Genesis Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#cbd5e1;'>Επίλεξε το επίπεδο της περιπέτειάς σου</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div class='pricing-card'>
                <h3>🌱 Basic</h3>
                <h2>0€</h2>
                <p>5 μηνύματα / ημέρα<br>1 Κόσμος μάθησης</p>
            </div>""", unsafe_allow_html=True)
            if st.button("Ξεκίνα Δωρεάν"):
                st.session_state.user["auth"] = True
                st.session_state.user["plan"] = "Free"
                st.session_state.scene = "lobby"
                st.rerun()
        
        with c2:
            st.markdown("""<div class='pricing-card premium-border'>
                <h3>💎 Premium Pro</h3>
                <h2>9.99€</h2>
                <p>Απεριόριστη μάθηση<br>Όλοι οι Genesis κόσμοι<br>Parent Analytics</p>
            </div>""", unsafe_allow_html=True)
            if st.button("Γίνε Pro 💳"):
                st.session_state.user["auth"] = True
                st.session_state.user["plan"] = "Premium"
                st.session_state.scene = "lobby"
                st.rerun()

    # --- SCENE: LOBBY (WORLD HUB) ---
    elif st.session_state.scene == "lobby":
        # HUD Status Bar
        h1, h2, h3, h4 = st.columns(4)
        h1.markdown(f"<div class='hud-label'>👤 {st.session_state.user['name']}</div>", unsafe_allow_html=True)
        h2.markdown(f"<div class='hud-label'>✨ XP: {st.session_state.user['xp']}</div>", unsafe_allow_html=True)
        h3.markdown(f"<div class='hud-label'>🏆 Plan: {st.session_state.user['plan']}</div>", unsafe_allow_html=True)
        h4.markdown(f"<div class='hud-label'>🔋 {st.session_state.user['energy']}%</div>", unsafe_allow_html=True)

        st.markdown("<br><h2 style='text-align:center; color:white;'>Επίλεξε Προορισμό</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='card'><h3>🏝️ Νησί των Γρίφων</h3><p>Μάθε παίζοντας!</p></div>", unsafe_allow_html=True)
            if st.button("Ταξίδι ➔", key="btn_island"):
                st.session_state.quest = "Νησί Γρίφων"
                st.session_state.scene = "adventure"
                st.rerun()
        
        with col2:
            is_pro = st.session_state.user["plan"] == "Premium"
            st.markdown(f"<div class='card' style='opacity:{1 if is_pro else 0.5}'><h3>🪐 Πλανήτης Φαντασίας</h3><p>{'Διαθέσιμο' if is_pro else '🔒 Μόνο Pro'}</p></div>", unsafe_allow_html=True)
            if st.button("Πτήση ➔", key="btn_planet", disabled=not is_pro):
                st.session_state.quest = "Πλανήτης Φαντασίας"
                st.session_state.scene = "adventure"
                st.rerun()

    # --- SCENE: ADVENTURE (ACTIVE LEARNING) ---
    elif st.session_state.scene == "adventure":
        if not SessionManager.check_quota():
            st.error("🛑 Το ημερήσιο όριο εξαντλήθηκε! Γίνε Pro για απεριόριστη χρήση.")
            if st.button("⬅️ Πίσω"): st.session_state.scene = "lobby"; st.rerun()
        else:
            st.markdown(f"<h2 style='color:white; text-align:center;'>📍 {st.session_state.quest}</h2>", unsafe_allow_html=True)
            
            if not st.session_state.chat_history:
                st.session_state.chat_history = [{"role": "system", "content": f"Είσαι ο Φοίβος. Δίδαξε στο παιδί για {st.session_state.quest} με μαγικό τρόπο και ερωτήσεις."}]

            # Chat Display
            for msg in st.session_state.chat_history:
                if msg["role"] != "system":
                    avatar = "🧸" if msg["role"] == "assistant" else "🧒"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.write(msg["content"])

            # Voice Input
            st.markdown("---")
            mic_col1, mic_col2, mic_col3 = st.columns([1, 2, 1])
            with mic_col2:
                voice = speech_to_text(language='el', start_prompt="🎤 Πες κάτι στον Φοίβο", stop_prompt="✅ Ανάλυση", key='v_mic')

            if voice:
                if "last_v" not in st.session_state or st.session_state.last_v != voice:
                    st.session_state.last_v = voice
                    st.session_state.chat_history.append({"role": "user", "content": voice})
                    st.session_state.user["usage"] += 1
                    st.session_state.user["xp"] += 25
                    
                    with st.chat_message("assistant", avatar="🧸"):
                        with st.spinner("✨ Επεξεργασία..."):
                            reply = ai.generate_response(st.session_state.chat_history)
                            st.write(reply)
                            st.session_state.chat_history.append({"role": "assistant", "content": reply})
                            st.session_state.audio_buffer = ai.text_to_speech(reply)
                            st.rerun()

            if st.session_state.audio_buffer:
                st.markdown(st.session_state.audio_buffer, unsafe_allow_html=True)
                st.session_state.audio_buffer = None

            if st.button("🏃 Επιστροφή στο Lobby"):
                st.session_state.scene = "lobby"
                st.session_state.chat_history = []
                st.rerun()

if __name__ == "__main__":
    main()
