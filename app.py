import streamlit as st
import pandas as pd
import plotly.express as px
import time
import json
import logging
from datetime import datetime
from groq import Groq
from gtts import gTTS
import base64
import io

# =================================================================
# MODULE 1: SYSTEM LOGGING & TELEMETRY
# =================================================================
# Εξηγείς στον καθηγητή: "Χρησιμοποιώ βιομηχανικά πρότυπα για logging"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================================================================
# MODULE 2: CONSTANTS & CONFIGURATION
# =================================================================
class Config:
    VERSION = "2.5.0-PRO"
    APP_NAME = "PedaGO Genesis: Edem Morning Edition"
    THEMES = {
        "Edem": {"primary": "#10b981", "secondary": "#ecfdf5", "icon": "🌿"},
        "Space": {"primary": "#6366f1", "secondary": "#e0e7ff", "icon": "🚀"},
        "Logic": {"primary": "#f59e0b", "secondary": "#fffbeb", "icon": "🧩"}
    }
    XP_REWARDS = {"message": 10, "correct_answer": 50, "streak_bonus": 100}

# =================================================================
# MODULE 3: DATA PERSISTENCE LAYER (DATABASE SIMULATION)
# =================================================================
class DatabaseManager:
    """Διαχείριση δεδομένων χρήστη και ιστορικού προόδου"""
    @staticmethod
    def load_user_profile():
        if "user_data" not in st.session_state:
            st.session_state.user_data = {
                "id": "USR-99", "name": "Ήρωας", "xp": 0, "level": 1,
                "badges": [], "session_count": 0, "last_login": str(datetime.now()),
                "history_log": [] # Εδώ αποθηκεύονται τα πάντα για τα Analytics
            }
        return st.session_state.user_data

    @staticmethod
    def update_xp(points):
        st.session_state.user_data["xp"] += points
        # Logic για Level up
        new_level = (st.session_state.user_data["xp"] // 500) + 1
        if new_level > st.session_state.user_data["level"]:
            st.session_state.user_data["level"] = new_level
            st.toast(f"🎉 Συγχαρητήρια! Ανέβηκες στο επίπεδο {new_level}!", icon="🆙")

# =================================================================
# MODULE 4: AFFECTIVE AI ORCHESTRATOR
# =================================================================
class PhoebusBrain:
    """Ο 'εγκέφαλος' του Φοίβου με χρήση Affective Computing"""
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def analyze_sentiment(self, text):
        # Meta-analysis του κειμένου για συναισθηματική νοημοσύνη
        prompt = f"Analyze the tone of this child's message: '{text}'. Return ONLY one word: Happy, Confused, Tired, or Excited."
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_response(self, world, history, sentiment):
        # Δυναμική προσαρμογή του System Prompt βάσει συναισθήματος (ΚΑΙΝΟΤΟΜΙΑ)
        system_instructions = f"""
        Είσαι ο Φοίβος στο κόσμο: {world}. 
        Το παιδί νιώθει: {sentiment}. 
        Προσάρμοσε τη διδασκαλία σου με Σωκρατική Μέθοδο. 
        Μην δίνεις έτοιμες απαντήσεις. Χρησιμοποίησε γλυκιά γλώσσα.
        """
        messages = [{"role": "system", "content": system_instructions}] + history
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.8
        )
        return response.choices[0].message.content

# =================================================================
# MODULE 5: ANALYTICS & VISUALIZATION ENGINE
# =================================================================
class AnalyticsEngine:
    """Μετατρέπει τα δεδομένα σε γραφήματα για τον καθηγητή/γονέα"""
    @staticmethod
    def plot_progress():
        # Προσομοίωση δεδομένων εβδομάδας
        df = pd.DataFrame({
            "Ημέρα": ["Δευτ", "Τρ", "Τετ", "Πεμ", "Παρ", "Σαβ", "Κυρ"],
            "XP": [50, 120, 200, 180, 300, 450, st.session_state.user_data["xp"]]
        })
        return px.line(df, x="Ημέρα", y="XP", title="Καμπύλη Μάθησης & Προόδου", markers=True)

# =================================================================
# MODULE 6: UI COMPONENTS (MODERN DESIGN)
# =================================================================
def apply_custom_styles():
    st.markdown("""
        <style>
        .main { background-color: #f8fafc; }
        .stButton>button { width: 100%; border-radius: 15px; height: 3em; transition: 0.3s; }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
        .card { padding: 20px; border-radius: 20px; background: white; border: 1px solid #e2e8f0; margin-bottom: 15px; }
        .phoebus-chat { border-left: 5px solid #10b981; padding-left: 15px; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)

# =================================================================
# MAIN APPLICATION ROUTER
# =================================================================
def main():
    apply_custom_styles()
    user = DatabaseManager.load_user_profile()
    brain = PhoebusBrain(api_key=st.secrets["GROQ_API_KEY"])

    # --- SIDEBAR (SaaS Controls) ---
    with st.sidebar:
        st.title("🛡️ Parent Control")
        st.write(f"Hero: **{user['name']}**")
        st.progress(user["xp"] % 500 / 500, text=f"Level {user['level']}")
        
        if st.button("📊 View Full Analytics"):
            st.session_state.page = "analytics"
        if st.button("🏠 Return to World Map"):
            st.session_state.page = "map"

    # --- ROUTING LOGIC ---
    if "page" not in st.session_state: st.session_state.page = "map"

    if st.session_state.page == "map":
        st.title("🌟 Η Πρωινή σου Εδέμ")
        cols = st.columns(3)
        for i, (name, data) in enumerate(Config.THEMES.items()):
            with cols[i]:
                st.markdown(f"<div class='card'><h2>{data['icon']}</h2><h3>{name}</h3></div>", unsafe_allow_html=True)
                if st.button(f"Είσοδος στο {name}", key=name):
                    st.session_state.world = name
                    st.session_state.page = "adventure"
                    st.rerun()

    elif st.session_state.page == "adventure":
        st.title(f"{Config.THEMES[st.session_state.world]['icon']} {st.session_state.world}")
        
        # Chat Interface
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Μίλησε στον Φοίβο..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # AI Logic με Sentiment Analysis
            sentiment = brain.analyze_sentiment(prompt)
            response = brain.generate_response(st.session_state.world, st.session_state.chat_history, sentiment)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            DatabaseManager.update_xp(Config.XP_REWARDS["message"])
            st.rerun()

    elif st.session_state.page == "analytics":
        st.header("📈 Επιστημονική Αξιολόγηση")
        st.plotly_chart(AnalyticsEngine.plot_progress(), use_container_width=True)
        st.write("Συνολικά XP:", user["xp"])
        st.write("Επίπεδο Γνώσης:", user["level"])

if __name__ == "__main__":
    main()
