import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import time
import json
import requests
from datetime import datetime
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie

# =================================================================
# MODULE 1: GLOBAL CONFIGURATION & ANIMATIONS
# =================================================================
class AppConfig:
    """Ρυθμίσεις Συστήματος & Οπτική Ταυτότητα"""
    TITLE = "PedaGO Genesis Pro v3.5"
    VERSION = "Build 2026.Premium"
    THEMES = {
        "Εδέμ Πρωί": {"color": "#10b981", "icon": "🌿", "prompt": "Είσαι στον Παράδεισο της Εδέμ. Μίλα ήρεμα και ενθαρρυντικά με απλά λόγια."},
        "Νησί Γρίφων": {"color": "#f59e0b", "icon": "🏝️", "prompt": "Είσαι στο Νησί των Γρίφων. Μίλα με αινίγματα και Σωκρατική μέθοδο."},
        "Διάστημα": {"color": "#6366f1", "icon": "🚀", "prompt": "Είσαι στο Διάστημα. Μίλα για αστέρια, πλανήτες και εξερεύνηση."}
    }

    @staticmethod
    def load_lottie_url(url: str):
        """Φόρτωση Lottie Animations από το web"""
        try:
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()
        except:
            return None

# =================================================================
# MODULE 2: VOICE & AUDIO ENGINE (STT / TTS)
# =================================================================
class VoiceEngine:
    """Subsystem για Φωνητική Αλληλεπίδραση"""
    @staticmethod
    def speak(text):
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
        prompt = f"Analyze child sentiment: '{text}'. Return JSON: {{'mood': 'χαρούμενος/λυπημένος/κουρασμένος', 'energy': 1-10}}"
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a child psychologist."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_response(self, history, mood_context, world_prompt):
        full_prompt = f"{world_prompt}. Το παιδί νιώθει {mood_context['mood']}. Προσάρμοσε τον τόνο σου ακαδημαϊκά και παιδαγωγικά."
        messages = [{"role": "system", "content": full_prompt}] + history
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

# =================================================================
# MODULE 4: SAAS & DATA MANAGER
# =================================================================
class SessionManager:
    """Διαχείριση Χρήστη, XP και Ιστορικού"""
    @staticmethod
    def initialize():
        if "user" not in st.session_state:
            st.session_state.user = {
                "name": "Φίλιππος", 
                "xp": 40, 
                "level": 1, 
                "plan": "Free",
                "history": [], 
                "mood": "Ήρεμος",
                "age": 6,
                "mood_history": ["Χαρούμενος", "Ήρεμος", "Ενθουσιώδης"],
                "xp_history": [10, 20, 40]
            }
        if "page" not in st.session_state: 
            st.session_state.page = "login"

    @staticmethod
    def add_xp(points):
        st.session_state.user["xp"] += points
        st.session_state.user["xp_history"].append(st.session_state.user["xp"])
        st.session_state.user["level"] = (st.session_state.user["xp"] // 100) + 1

# =================================================================
# MODULE 5: UI COMPONENTS & PAGES
# =================================================================
def render_hud():
    """Εμφάνιση HUD (Heads-Up Display) με Premium Σχεδιασμό"""
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding:18px; border-radius:15px; margin-bottom:25px; border: 1px solid #334155; color: white;">
            <span style="font-size:16px; margin-right:15px;">✨ <b>XP:</b> {st.session_state.user['xp']}</span> | 
            <span style="font-size:16px; margin-left:15px; margin-right:15px;">🏆 <b>Επίπεδο:</b> {st.session_state.user['level']}</span> | 
            <span style="font-size:16px; margin-left:15px; margin-right:15px;">🎭 <b>Διάθεση:</b> {st.session_state.user['mood']}</span> | 
            <span style="font-size:16px; margin-left:15px;">💎 <b>Πλάνο:</b> <span style="color:#10b981; font-weight:bold;">{st.session_state.user['plan']}</span></span>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Επαγγελματικό Μενού Πλοήγησης (Back & Forward)"""
    if st.session_state.page != "login":
        st.sidebar.title("📌 Πλοήγηση")
        st.sidebar.write(f"Γεια σου, **{st.session_state.user['name']}**!")
        
        if st.sidebar.button("🗺️ Κόσμοι (Hub)", use_container_width=True):
            st.session_state.page = "hub"
            st.rerun()
            
        if st.sidebar.button("📊 Dashboard Γονέα", use_container_width=True):
            st.session_state.page = "parent_dashboard"
            st.rerun()
            
        if st.sidebar.button("⚙️ Ρυθμίσεις Προφίλ", use_container_width=True):
            st.session_state.page = "profile_settings"
            st.rerun()
            
        st.sidebar.write("---")
        if st.sidebar.button("🚪 Αποσύνδεση", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.user["history"] = []
            st.rerun()

def main():
    st.set_page_config(page_title=AppConfig.TITLE, page_icon="🚀", layout="wide")
    SessionManager.initialize()
    render_sidebar()
    brain = PhoebusBrain()

    # Φόρτωση Παιδικού Animation για τη μουντάδα
    child_anim = AppConfig.load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_ch84wup9.json")
    
    # --- PAGE: LOGIN / SAAS TIERS ---
    if st.session_state.page == "login":
        st.title("🚀 PedaGO Genesis Pro")
        st.subheader("Η δική σου Πρωινή Εδέμ περιμένει!")
        
        if child_anim:
            st_lottie(child_anim, height=200, key="login_anim")
            
        col1, col2 = st.columns(2)
        with col1:
            st.info("### Basic Plan\n- 5 Μηνύματα/μέρα\n- Standard AI")
            if st.button("Επιλογή Basic", use_container_width=True):
                st.session_state.user["plan"] = "Free"
                st.session_state.page = "hub"
                st.rerun()
        with col2:
            st.success("### Pro Plan\n- Απεριόριστη Φωνή\n- Affective AI Analytics")
            stripe_link = "https://buy.stripe.com/σου_εδώ" 
            st.markdown(f'<a href="{stripe_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#10b981;color:white;padding:12px;text-align:center;border-radius:10px;font-weight:bold;font-size:16px;">💎 Ενεργοποίηση Pro (9.99€/μήνα)</div></a>', unsafe_allow_html=True)
            
            if st.button("Σύνδεση ως Pro (Demo Mode)", use_container_width=True):
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
                st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border-top: 5px solid {data['color']}; text-align:center;'><h3>{data['icon']} {name}</h3></div>", unsafe_allow_html=True)
                if st.button(f"Ταξίδι στο {name}", key=name, use_container_width=True):
                    st.session_state.current_world = name
                    st.session_state.page = "adventure"
                    st.rerun()

    # --- PAGE: ADVENTURE (THE HEART) ---
    elif st.session_state.page == "adventure":
        render_hud()
        world = st.session_state.current_world
        
        col_title, col_back = st.columns([4, 1])
        with col_title:
            st.header(f"{AppConfig.THEMES[world]['icon']} {world}")
        with col_back:
            if st.button("↩️ Αλλαγή Κόσμου", use_container_width=True):
                st.session_state.page = "hub"
                st.rerun()
        
        # Display Chat History
        for msg in st.session_state.user["history"]:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        # Voice Interaction
        user_speech = VoiceEngine.listen()
        if user_speech:
            st.session_state.user["history"].append({"role": "user", "content": user_speech})
            with st.spinner("Ο Φοίβος σε ακούει με προσοχή..."):
                mood_data = brain.analyze_sentiment(user_speech)
                st.session_state.user["mood"] = mood_data["mood"]
                st.session_state.user["mood_history"].append(mood_data["mood"])
                
                response = brain.generate_response(
                    st.session_state.user["history"], 
                    mood_data, 
                    AppConfig.THEMES[world]["prompt"]
                )
                st.session_state.user["history"].append({"role": "assistant", "content": response})
                SessionManager.add_xp(20)
                VoiceEngine.speak(response)
                st.rerun()

    # --- PAGE: PARENT DASHBOARD ---
    elif st.session_state.page == "parent_dashboard":
        st.title("📊 Dashboard Γονέα & Analytics")
        st.subheader(f"Συμπεράσματα και Πρόοδος για τον/την: {st.session_state.user['name']}")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Συνολικά XP", f"{st.session_state.user['xp']} XP", "20 XP σήμερα")
        with col_m2:
            st.metric("Τρέχον Επίπεδο", f"Level {st.session_state.user['level']}")
            
        st.write("### 📈 Καμπύλη Μάθησης (XP Progression)")
        fig_xp = go.Figure(data=go.Scatter(y=st.session_state.user["xp_history"], mode='lines+markers', line=dict(color='#10b981', width=3)))
        fig_xp.update_layout(title="Εξέλιξη Πόντων Εμπειρίας", xaxis_title="Αλληλεπιδράσεις", yaxis_title="XP")
        st.plotly_chart(fig_xp, use_container_width=True)
        
        st.write("### 🎭 Συναισθηματικό Ιστορικό (Mood Tracker)")
        st.info(f"Η τελευταία καταγεγραμμένη διάθεση του παιδιού είναι: **{st.session_state.user['mood']}**")

    # --- PAGE: PROFILE SETTINGS ---
    elif st.session_state.page == "profile_settings":
        st.title("⚙️ Ρυθμίσεις Προφίλ")
        st.write("Διαχείριση στοιχείων του μικρού μαθητή.")
        
        new_name = st.text_input("Όνομα Παιδιού:", value=st.session_state.user["name"])
        new_age = st.number_input("Ηλικία Παιδιού:", min_value=3, max_value=12, value=st.session_state.user["age"])
        
        if st.button("💾 Αποθήκευση Αλλαγών", use_container_width=True):
            st.session_state.user["name"] = new_name
            st.session_state.user["age"] = new_age
            st.success("Το προφίλ ενημερώθηκε επιτυχώς!")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()
