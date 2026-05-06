import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import time
import json
from datetime import datetime
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# =================================================================
# MODULE 1: GLOBAL CONFIGURATION & THEMES
# =================================================================
class AppConfig:
    """Ρυθμίσεις Συστήματος & Οπτική Ταυτότητα"""
    TITLE = "PedaGO Genesis Pro v3.0"
    VERSION = "Build 2026.Innovation"
    THEMES = {
        "Εδέμ Πρωί": {"color": "#10b981", "icon": "🌿", "prompt": "Είσαι στον Παράδεισο της Εδέμ. Μίλα ήρεμα και ενθαρρυντικά."},
        "Νησί Γρίφων": {"color": "#f59e0b", "icon": "🏝️", "prompt": "Είσαι στο Νησί των Γρίφων. Μίλα με αινίγματα και Σωκρατική μέθοδο."},
        "Διάστημα": {"color": "#6366f1", "icon": "🚀", "prompt": "Είσαι στο Διάστημα. Μίλα για αστέρια και εξερεύνηση."}
    }

# =================================================================
# MODULE 2: VOICE & AUDIO ENGINE (STT / TTS)
# =================================================================
class VoiceEngine:
    """Subsystem για Φωνητική Αλληλεπίδραση"""
    @staticmethod
    def speak(text):
        """Μετατροπή κειμένου σε ήχο με αυτόματη αναπαραγωγή"""
        try:
            tts = gTTS(text=text, lang='el')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"TTS Error: {e}")

    @staticmethod
    def listen():
        """Λήψη φωνής και μετατροπή σε κείμενο (STT)"""
        return speech_to_text(
            language='el',
            start_prompt="🎤 Πάτα & Μίλησε στον Φοίβο",
            stop_prompt="🛑 Σταμάτα",
            just_once=True,
            key='STT_Component'
        )

# =================================================================
# MODULE 3: AFFECTIVE AI CORE (THE BRAIN)
# =================================================================
class PhoebusBrain:
    """Η Καρδιά του Φοίβου με Συναισθηματική Νοημοσύνη"""
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    def analyze_sentiment(self, text):
        """Καινοτομία: Ανάλυση συναισθήματος πριν την απάντηση"""
        prompt = f"Analyze child sentiment: '{text}'. Return JSON: {{'mood': 'happy/sad/tired', 'energy': 1-10}}"
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a child psychologist."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_response(self, history, mood_context, world_prompt):
        """Παραγωγή απάντησης με βάση το συναίσθημα και τον κόσμο"""
        full_prompt = f"{world_prompt}. Το παιδί νιώθει {mood_context['mood']}. Προσάρμοσε τον τόνο σου."
        messages = [{"role": "system", "content": full_prompt}] + history
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

# =================================================================
# MODULE 4: SAAS & GAMIFICATION MANAGER
# =================================================================
class SessionManager:
    """Διαχείριση Χρήστη, XP και Συνδρομών"""
    @staticmethod
    def initialize():
        if "user" not in st.session_state:
            st.session_state.user = {
                "name": "Ήρωας", "xp": 0, "level": 1, "plan": "Free",
                "usage": 0, "history": [], "mood": "Ήρεμος"
            }
        if "page" not in st.session_state: st.session_state.page = "login"

    @staticmethod
    def add_xp(points):
        st.session_state.user["xp"] += points
        st.session_state.user["level"] = (st.session_state.user["xp"] // 100) + 1

# =================================================================
# MODULE 5: UI & PAGES
# =================================================================
def render_hud():
    """Εμφάνιση HUD (Heads-Up Display) με XP και Mood"""
    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); padding:15px; border-radius:15px; margin-bottom:20px;">
            ✨ XP: {st.session_state.user['xp']} | 🏆 Level: {st.session_state.user['level']} | 
            🎭 Mood: {st.session_state.user['mood']} | 💎 Plan: {st.session_state.user['plan']}
        </div>
    """, unsafe_allow_html=True)

def main():
    SessionManager.initialize()
    brain = PhoebusBrain()
    
    # --- PAGE: LOGIN / SAAS TIERS ---
    if st.session_state.page == "login":
        st.title("🚀 PedaGO Genesis Pro")
        st.subheader("Η δική σου Πρωινή Εδέμ περιμένει!")
        col1, col2 = st.columns(2)
        with col1:
            st.info("### Basic Plan\n- 5 Μηνύματα/μέρα\n- Standard AI")
            if st.button("Επιλογή Basic"):
                st.session_state.user["plan"] = "Free"
                st.session_state.page = "hub"
                st.rerun()
        with col2:
            st.success("### Pro Plan\n- Απεριόριστη Φωνή\n- Affective AI Analytics")
            if st.button("Ενεργοποίηση Pro 💎"):
                st.session_state.user["plan"] = "Pro"
                st.session_state.page = "hub"
                st.rerun()

    # --- PAGE: WORLD HUB ---
    elif st.session_state.page == "hub":
        render_hud()
        st.title("🗺️ Διάλεξε τον Κόσμο σου")
        cols = st.columns(3)
        for i, (name, data) in enumerate(AppConfig.THEMES.items()):
            with cols[i]:
                st.markdown(f"### {data['icon']} {name}")
                if st.button(f"Ταξίδι στο {name}"):
                    st.session_state.current_world = name
                    st.session_state.page = "adventure"
                    st.rerun()

    # --- PAGE: ADVENTURE (THE HEART) ---
    elif st.session_state.page == "adventure":
        render_hud()
        world = st.session_state.current_world
        st.header(f"{AppConfig.THEMES[world]['icon']} {world}")
        
        # Display Chat History
        for msg in st.session_state.user["history"]:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        # Voice Interaction
        user_speech = VoiceEngine.listen()
        
        if user_speech:
            st.session_state.user["history"].append({"role": "user", "content": user_speech})
            
            # Innovation: Analyze Mood & Generate Response
            with st.spinner("Ο Φοίβος σε αισθάνεται..."):
                mood_data = brain.analyze_sentiment(user_speech)
                st.session_state.user["mood"] = mood_data["mood"]
                
                response = brain.generate_response(
                    st.session_state.user["history"], 
                    mood_data, 
                    AppConfig.THEMES[world]["prompt"]
                )
                
                st.session_state.user["history"].append({"role": "assistant", "content": response})
                SessionManager.add_xp(20)
                
                # Output Voice
                VoiceEngine.speak(response)
                st.rerun()

        if st.button("🏠 Επιστροφή στο Hub"):
            st.session_state.user["history"] = []
            st.session_state.page = "hub"
            st.rerun()

if __name__ == "__main__":
    main()
