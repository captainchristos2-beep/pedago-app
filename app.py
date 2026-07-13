import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import time
import json
import sqlite3
from datetime import datetime, timedelta
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text

# =================================================================
# MODULE 1: GLOBAL CONFIGURATION, THEMES & DUOLINGO PREMIUM CSS
# =================================================================
class AppConfig:
    """Ρυθμίσεις Συστήματος & Οπτική Ταυτότητα (Duolingo Gamified Design)"""
    TITLE = "Φοίβος AI Μέντορας v10.0"
    VERSION = "Build 2026.OmnibusCore"
    
    THEMES = {
        "🌿 Πράσινη Εδέμ": {"color": "#58cc02", "icon": "🌿", "prompt": "Είσαι στον Παράδεισο της Εδέμ. Μίλα ήρεμα, στοργικά και ενθαρρυντικά με απλά λόγια σαν γλυκός παιδαγωγός.", "bg": "#eefced", "accent": "#58cc02"},
        "🏝️ Νησί Γρίφων": {"color": "#ff9600", "icon": "🏝️", "prompt": "Είσαι στο Νησί των Γρίφων. Μίλα με αινίγματα, έξυπνα παιχνίδια λέξεων και Σωκρατική μέθοδο κατάλληλη για παιδιά.", "bg": "#fef5e7", "accent": "#ff9600"},
        "🚀 Διάστημα": {"color": "#1cb0f6", "icon": "🚀", "prompt": "Είσαι στο Διάστημα. Μίλα για αστέρια, πλανήτες, πυραύλους και εξερεύνηση με μεγάλο ενθουσιασμό.", "bg": "#e8f7fe", "accent": "#1cb0f6"}
    }

    @staticmethod
    def inject_premium_styles():
        """Έγχυση CSS για το Duolingo Playful & Gamified Design System"""
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
            
            /* Καθολικό στυλ εφαρμογής (Φωτεινό, καθαρό, χαρούμενο) */
            .stApp { 
                background-color: #ffffff; 
                color: #3c3c3c; 
                font-family: 'Nunito', sans-serif; 
            }
            
            /* Duolingo Κάρτες με 3D border εφέ */
            .premium-card {
                background: #ffffff;
                border: 2px solid #e5e5e5;
                border-bottom: 4px solid #e5e5e5;
                padding: 24px;
                border-radius: 16px;
                margin-bottom: 20px;
                color: #3c3c3c;
            }
            
            /* Duolingo XP Μπάρα Προόδου (Κίτρινη/Χρυσή) */
            .duo-progress-container {
                width: 100%; 
                background-color: #e5e5e5; 
                border-radius: 16px; 
                padding: 4px; 
                margin: 10px 0px;
            }
            .duo-progress-bar {
                height: 16px; 
                background: #ffc800; 
                border-radius: 12px; 
                transition: width 0.5s ease-in-out;
            }
            
            /* Συννεφάκια Λόγου Φοίβου (Duolingo Style) */
            .phoebus-bubble {
                background: #ffffff; 
                border: 2px solid #e5e5e5; 
                border-bottom: 4px solid #e5e5e5;
                padding: 18px; 
                border-radius: 18px; 
                margin: 12px 0px; 
                color: #3c3c3c;
                font-size: 16px;
                font-weight: 700;
                width: 100%;
            }
            .phoebus-bubble-tired {
                background: #ffffff; 
                border: 2px solid #1cb0f6; 
                border-bottom: 4px solid #1cb0f6;
                padding: 18px; 
                border-radius: 18px; 
                margin: 12px 0px; 
                color: #3c3c3c;
                font-size: 16px;
                font-weight: 700;
                width: 100%;
            }
            
            /* Τίτλοι Ενοτήτων (Γαλάζιο Duolingo) */
            .smart-action-title {
                font-size: 16px; 
                font-weight: 900; 
                text-transform: uppercase; 
                letter-spacing: 1px; 
                color: #1cb0f6; 
                margin-bottom: 8px;
            }
            
            /* Tabs Styling */
            .stTabs [data-baseweb="tab"] {
                color: #777777 !important;
                font-weight: 700;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                color: #1cb0f6 !important;
            }
            </style>
        """, unsafe_allow_html=True)

# =================================================================
# MODULE 2: VOICE & AUDIO ENGINE (ELEVENLABS UPGRADE)
# =================================================================
class VoiceEngine:
    """Subsystem για Φωνητική Αλληλεπίδραση με ElevenLabs Streaming"""
    @staticmethod
    def speak(text):
        try:
            if "ELEVENLABS_API_KEY" in st.secrets:
                client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
            else:
                st.error("Παρακαλώ ρύθμισε το ELEVENLABS_API_KEY στα Streamlit Secrets.")
                return

            # Παραγωγή κορυφαίας, φυσικής φωνής στα Ελληνικά (Rachel/Multilingual)
            audio_stream = client.generate(
                text=text,
                voice="Rachel", 
                model="eleven_multilingual_v2", 
                stream=True
            )

            # Συλλογή των audio chunks και μετατροπή σε base64 για autoplay
            audio_bytes = b"".join(audio_stream)
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"ElevenLabs TTS Error: {e}")

    @staticmethod
    def listen():
        return speech_to_text(
            language='el', start_prompt="🎤 Μίλησε στον Φοίβο", stop_prompt="🛑 Σταμάτα", just_once=True, key='STT_Component'
        )

# =================================================================
# MODULE 3: AFFECTIVE & ADAPTIVE AI CORE (THE BRAIN)
# =================================================================
class PhoebusBrain:
    """Η Καρδιά του Φοίβου με Συναισθηματική & Ηλικιακή Νοημοσύνη"""
    def __init__(self):
        if "GROQ_API_KEY" in st.secrets:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        else:
            st.error("Παρακαλώ ρύθμισε το GROQ_API_KEY στα Streamlit Secrets.")

    def analyze_sentiment(self, text):
        try:
            prompt = f"Analyze child sentiment: '{text}'. Return STRICTLY a JSON object: {{'mood': 'χαρούμενος' or 'λυπημένος' or 'κουρασμένος', 'energy': 1-10}}"
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are a child psychologist. Respond ONLY with JSON."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"mood": "Ήρεμος", "energy": 5}

    def generate_response(self, history, mood_context, world_prompt, child_age):
        if child_age <= 4:
            age_instruction = "Το παιδί είναι προ-νήπιο (4 ετών). Χρησιμοποίησε πολύ απλές, μικρές προτάσεις έως 5-6 λέξεις."
        else:
            age_instruction = "Το παιδί είναι νήπιο/πρωτοσχολικό (5-6 ετών+). Ενθάρρυνε σύνθετες απαντήσεις και χτίσε γνωστική σκαλωσιά (scaffolding)."
            
        full_prompt = f"{world_prompt}\nΤο παιδί νιώθει {mood_context['mood']}. {age_instruction} Μίλα στα Ελληνικά με καθαρό, παιδικό και ζεστό ύφος."
        messages = [{"role": "system", "content": full_prompt}] + history
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages, temperature=0.7
        )
        return response.choices[0].message.content

# =================================================================
# MODULE 4: DATA MANAGER & MEMORY (SM-2 IMPLEMENTATION)
# =================================================================
class SessionManager:
    """Διαχείριση Χρηστών, Βάσης Δεδομένων & Αλγορίθμου Μνήμης SM-2"""
    
    @staticmethod
    def init_db():
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY, password TEXT, role TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY, name TEXT, xp INTEGER, level INTEGER, plan TEXT, age INTEGER, onboarded INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_memory (
                word TEXT PRIMARY KEY, interval INTEGER, ease_factor REAL, next_review TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def register_user(username, password, role):
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO accounts (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def authenticate_user(username, password):
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM accounts WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def save_to_db(user_data):
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_profile WHERE id = 1")
        cursor.execute("""
            INSERT INTO user_profile (id, name, xp, level, plan, age, onboarded)
            VALUES (1, ?, ?, ?, ?, ?, ?)
        """, (user_data["name"], user_data["xp"], user_data["level"], user_data["plan"], user_data["age"], 1 if user_data["onboarded"] else 0))
        conn.commit()
        conn.close()

    @staticmethod
    def load_from_db():
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, xp, level, plan, age, onboarded FROM user_profile WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "name": row[0], "xp": row[1], "level": row[2], "plan": row[3], "age": row[4],
                "onboarded": True if row[5] == 1 else False,
                "history": [], "mood": "Ήρεμος", "mood_history": ["Χαρούμενος", "Ήρεμος"], "xp_history": [10, row[1]],
                "usage_count": 0, "max_usage": 10, "vocab_bonus": False
            }
        return None

    @staticmethod
    def update_word_memory(word, quality):
        """Καθαρή υλοποίηση του αλγορίθμου SuperMemo-2 (SM-2)"""
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT interval, ease_factor FROM word_memory WHERE word = ?", (word,))
        row = cursor.fetchone()
        
        if row:
            interval, ef = row[0], row[1]
            if quality >= 3:
                if interval == 1: interval = 6
                elif interval == 6: interval = 12
                else: interval = int(interval * ef)
            else:
                interval = 1
        else:
            ef = 2.5
            interval = 1 if quality < 3 else 6

        # Προσαρμογή του Ease Factor
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ef < 1.3: ef = 1.3
        
        next_date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT OR REPLACE INTO word_memory (word, interval, ease_factor, next_review) VALUES (?, ?, ?, ?)", (word, interval, ef, next_date))
        conn.commit()
        conn.close()

    @staticmethod
    def initialize():
        SessionManager.init_db()
        if "user" not in st.session_state:
            db_user = SessionManager.load_from_db()
            if db_user: 
                st.session_state.user = db_user
            else:
                st.session_state.user = {
                    "name": "Ήρωας", "xp": 40, "level": 1, "plan": "Free", "history": [], "mood": "Ήρεμος", "age": 5,
                    "mood_history": ["Χαρούμενος", "Ήρεμος", "Ενθουσιώδης"], "xp_history": [10, 20, 40],
                    "onboarded": False, "usage_count": 0, "max_usage": 10, "vocab_bonus": False
                }
        if "page" not in st.session_state: st.session_state.page = "login"
        if "current_role" not in st.session_state: st.session_state.current_role = None

    @staticmethod
    def add_xp(points):
        st.session_state.user["xp"] += points
        st.session_state.user["xp_history"].append(st.session_state.user["xp"])
        st.session_state.user["level"] = (st.session_state.user["xp"] // 100) + 1
        SessionManager.save_to_db(st.session_state.user)

    @staticmethod
    def check_screen_time():
        if st.session_state.user["plan"] == "Free" and st.session_state.user["usage_count"] >= st.session_state.user["max_usage"]: return True
        return False

# =================================================================
# MODULE 5: UI COMPONENTS & RENDERING
# =================================================================
def render_hud():
    """Εμφάνιση HUD με Duolingo-Grade Σχεδιασμό"""
    remaining = max(0, st.session_state.user["max_usage"] - st.session_state.user["usage_count"]) if st.session_state.user["plan"] == "Free" else "∞"
    current_level_base = (st.session_state.user["level"] - 1) * 100
    xp_in_level = st.session_state.user["xp"] - current_level_base
    progress_percentage = min(100, max(5, xp_in_level))

    st.markdown(f"""
        <div class="premium-card" style="padding: 20px; border-left: 6px solid #58cc02;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size:16px; font-weight:900; color:#58cc02;">🏆 ΕΠΙΠΕΔΟ {st.session_state.user['level']}</span>
                <span style="font-size:14px; font-weight:bold; color:#777777;">✨ {st.session_state.user['xp']} / {st.session_state.user['level'] * 100} XP</span>
            </div>
            <div class="duo-progress-container">
                <div class="duo-progress-bar" style="width: {progress_percentage}%;"></div>
            </div>
            <div style="display: flex; gap: 15px; font-size:13px; color:#3c3c3c; margin-top: 12px; font-weight: bold;">
                <span>👤 <b>Παιδί:</b> {st.session_state.user['name']} ({st.session_state.user['age']} ετών)</span> | 
                <span>🎭 <b>Διάθεση:</b> {st.session_state.user['mood']}</span> | 
                <span>⏳ <b>Μηνύματα:</b> {remaining}</span> | 
                <span>💎 <b>Πλάνο:</b> <span style="color:#58cc02;">{st.session_state.user['plan']}</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    if st.session_state.page not in ["login", "onboarding"]:
        st.sidebar.title("📌 Φοίβος AI")
        st.sidebar.info(f"🔑 Ρόλος: **{st.session_state.current_role}**")
        
        if st.session_state.current_role == "Γονέας":
            if st.sidebar.button("🗺️ Κόσμοι Περιπέτειας", use_container_width=True): st.session_state.page = "hub"; st.rerun()
            if st.sidebar.button("🧠 Γλωσσική Μνήμη (SM-2)", use_container_width=True): st.session_state.page = "memory_core"; st.rerun()
            if st.sidebar.button("📊 Στατιστικά Γονέα", use_container_width=True): st.session_state.page = "parent_dashboard"; st.rerun()
            if st.sidebar.button("⚙️ Ρυθμίσεις Προφίλ", use_container_width=True): st.session_state.page = "profile_settings"; st.rerun()
        
        elif st.session_state.current_role == "Εκπαιδευτικός":
            if st.sidebar.button("🏫 Πύλη Εκπαιδευτικού", use_container_width=True): st.session_state.page = "educator_portal"; st.rerun()
            
        st.sidebar.write("---")
        if st.sidebar.button("🚪 Αποσύνδεση", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.current_role = None
            st.session_state.user["history"] = []
            st.rerun()

def main():
    AppConfig.inject_premium_styles()
    SessionManager.initialize()
    render_sidebar()
    brain = PhoebusBrain()

    # --- PAGE: LOGIN ---
    if st.session_state.page == "login":
        st.title("🚀 Φοίβος AI Μέντορας")
        st.subheader("Η έξυπνη, συναισθηματική πλατφόρμα ανάπτυξης λόγου.")
        
        auth_tab1, auth_tab2 = st.tabs(["🔑 Σύνδεση", "📝 Εγγραφή"])
        
        with auth_tab1:
            login_user = st.text_input("Όνομα Χρήστη / Email:", key="log_user")
            login_pass = st.text_input("Κωδικός Πρόσβασης:", type="password", key="log_pass")
            if st.button("🚀 Είσοδος", use_container_width=True):
                role = SessionManager.authenticate_user(login_user, login_pass)
                if role:
                    st.session_state.current_role = role
                    st.success(f"Καλώς ορίσατε!")
                    time.sleep(0.5)
                    st.session_state.page = "hub" if role == "Γονέας" and st.session_state.user["onboarded"] else ("onboarding" if role == "Γονέας" else "educator_portal")
                    st.rerun()
                else:
                    st.error("❌ Λανθασμένα στοιχεία σύνδεσης!")
                    
        with auth_tab2:
            reg_user = st.text_input("Όνομα Χρήστη:", key="reg_user")
            reg_pass = st.text_input("Κωδικός Πρόσβασης:", type="password", key="reg_pass")
            reg_role = st.selectbox("Ρόλος:", ["Γονέας", "Εκπαιδευτικός"])
            if st.button("📝 Ολοκλήρωση Εγγραφής", use_container_width=True):
                if reg_user.strip() and reg_pass.strip():
                    if SessionManager.register_user(reg_user, reg_pass, reg_role): 
                        st.success("🎉 Ο λογαριασμός δημιουργήθηκε!")
                    else: 
                        st.error("❌ Το όνομα χρήστη υπάρχει ήδη.")

    # --- PAGE: ONBOARDING ---
    elif st.session_state.page == "onboarding":
        st.title("👋 Προφίλ Μικρού Εξερευνητή")
        with st.form("onboarding_form"):
            onboard_name = st.text_input("Όνομα Παιού:")
            onboard_age = st.number_input("Ηλικία Παιδιού (3-12):", min_value=3, max_value=12, value=5)
            if st.form_submit_button("🚀 Έναρξη Περιπέτειας!", use_container_width=True):
                if onboard_name.strip():
                    st.session_state.user["name"] = onboard_name
                    st.session_state.user["age"] = onboard_age
                    st.session_state.user["onboarded"] = True
                    SessionManager.save_to_db(st.session_state.user)
                    st.session_state.page = "hub"
                    st.rerun()

    # --- PAGE: HUB ---
    elif st.session_state.page == "hub":
        render_hud()
        st.title("🗺️ Διάλεξε Κόσμο")
        if SessionManager.check_screen_time():
            st.error("⏰ **Screen Time Guard:** Συμπληρώθηκε το όριο χρήσης!")
            return
        
        cols = st.columns(3)
        for i, (name, data) in enumerate(AppConfig.THEMES.items()):
            with cols[i]:
                st.markdown(f"<div style='background: {data['bg']}; padding:25px; border-radius:20px; border: 2px solid {data['color']}; text-align:center;'><h2>{data['icon']}</h2><h4>{name}</h4></div>", unsafe_allow_html=True)
                if st.button(f"Είσοδος", key=name, use_container_width=True):
                    st.session_state.current_world = name
                    st.session_state.page = "adventure"
                    st.rerun()

    # --- PAGE: ADVENTURE ---
    elif st.session_state.page == "adventure":
        render_hud()
        if SessionManager.check_screen_time():
            st.error("⏰ **Screen Time Guard:** Το όριο χρήσης συμπληρώθηκε!")
            return

        world = st.session_state.current_world
        col_title, col_back = st.columns([4, 1])
        with col_title: st.header(f"{AppConfig.THEMES[world]['icon']} {world}")
        with col_back:
            if st.button("↩️ Πίσω", use_container_width=True): st.session_state.page = "hub"; st.rerun()

        current_mood = st.session_state.user["mood"].lower()
        avatar_icon, bubble_class = ("🧸✨", "phoebus-bubble")
        if "κουρασμένος" in current_mood or "λυπημένος" in current_mood:
            avatar_icon, bubble_class = ("🧸💤", "phoebus-bubble-tired")

        # Duolingo-style Character Header
        st.markdown(f"""
            <div style="padding: 20px; border-radius: 20px; border: 2px solid #e5e5e5; background: #f7f7f7; margin-bottom: 20px; display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 50px; background: white; padding: 10px; border-radius: 50%; border: 2px solid #e5e5e5;">{avatar_icon}</div>
                <div>
                    <b style="color: #3c3c3c; font-size: 18px;">Φοίβος</b><br>
                    <span style="color: #777777; font-size: 14px;">🌟 Μέντορας Λόγου • Κατάσταση: <b>{st.session_state.user['mood']}</b></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Διάλογος
        for msg in st.session_state.user["history"]:
            if msg["role"] == "assistant":
                st.markdown(f'<div style="display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px;"><div class="{bubble_class}"><b>Φοίβος:</b> {msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                with st.chat_message("user"): st.write(msg["content"])

        user_speech = VoiceEngine.listen()
        if user_speech:
            st.session_state.user["history"].append({"role": "user", "content": user_speech})
            st.session_state.user["usage_count"] += 1
            
            # Έλεγχος Λέξεων-Στόχων για το Spaced Repetition
            target_words = ["αστέρι", "πλανήτης", "γρίφος", "παράδεισος", "λουλούδι", "ουρανός", "δέντρο"]
            found_word = None
            for w in target_words:
                if w in user_speech.lower():
                    found_word = w
                    break
            
            if found_word:
                SessionManager.update_word_memory(found_word, 5) 
                st.toast(f"🎯 Η λέξη '{found_word}' καταγράφηκε στη Γλωσσική Μνήμη!", icon="🧠")
                SessionManager.add_xp(30)

            with st.spinner("Ο Φοίβος σε ακούει..."):
                mood_data = brain.analyze_sentiment(user_speech)
                st.session_state.user["mood"] = mood_data["mood"]
                st.session_state.user["mood_history"].append(mood_data["mood"])
                
                response = brain.generate_response(st.session_state.user["history"], mood_data, AppConfig.THEMES[world]["prompt"], st.session_state.user["age"])
                st.session_state.user["history"].append({"role": "assistant", "content": response})
                SessionManager.add_xp(20)
                VoiceEngine.speak(response)
                st.rerun()

    # --- PAGE: MEMORY CORE ---
    elif st.session_state.page == "memory_core":
        st.title("🧠 Σύστημα Γλωσσικής Μνήμης")
        st.subheader("Αλγόριθμος Spaced Repetition (SM-2)")
        
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT word, interval, ease_factor, next_review FROM word_memory")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            cards_data = pd.DataFrame(rows, columns=['Λέξη-Στόχος', 'Επόμενος Έλεγχος (Ημέρες)', 'Ease Factor (EF)', 'Ημερομηνία Επανάληψης'])
            st.dataframe(cards_data, use_container_width=True)
            
            fig_anki = go.Figure([go.Bar(x=cards_data['Λέξη-Στόχος'], y=cards_data['Επόμενος Έλεγχος (Ημέρες)'], marker_color='#58cc02')])
            fig_anki.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#3c3c3c'))
            st.plotly_chart(fig_anki, use_container_width=True)
        else: 
            st.warning("🔒 Καμία λέξη δεν έχει καταγραφεί ακόμα. Μίλησε στον Φοίβο χρησιμοποιώντας λέξεις όπως 'αστέρι' ή 'πλανήτης'.")

    # --- PAGE: PARENT DASHBOARD ---
    elif st.session_state.page == "parent_dashboard":
        st.title("📊 Αναφορές & Δεξιότητες Παιδιού")
        render_hud()
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.write("### 📊 Παιδαγωγικό Προφίλ")
            categories = ['Λεξιλόγιο', 'Κριτική Σκέψη', 'Συναισθηματική Αυτορύθμιση', 'Ταχύτητα Απόκρισης', 'Φαντασία']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[4, 3, 5, 4, 4], theta=categories, fill='toself', marker=dict(color='#1cb0f6'), fillcolor='rgba(28, 176, 246, 0.3)'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#3c3c3c'))
            st.plotly_chart(fig_radar, use_container_width=True)
        with col_chart2:
            st.write("### 📈 Εξέλιξη Μάθησης (XP)")
            fig_xp = go.Figure(data=go.Scatter(y=st.session_state.user["xp_history"], mode='lines+markers', line=dict(color='#58cc02', width=3)))
            fig_xp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#3c3c3c'))
            st.plotly_chart(fig_xp, use_container_width=True)

    # --- PAGE: EDUCATOR PORTAL ---
    elif st.session_state.page == "educator_portal":
        st.title("🏫 Educator Portal (Στατιστικά Τάξης)")
        class_data = pd.DataFrame({
            'Μαθητής': ['Νικόλας', 'Μαρία', 'Γιώργος', 'Ελένη', 'Δημήτρης'],
            'Εβδομαδιαία XP': [120, 240, 90, 310, 150],
            'Κυρίαρχο Συναίσθημα': ['Χαρούμενος', 'Ενθουσιώδης', 'Κουρασμένος', 'Χαρούμενος', 'Ήρεμος']
        })
        st.table(class_data)

    # --- PAGE: PROFILE SETTINGS ---
    elif st.session_state.page == "profile_settings":
        st.title("⚙️ Ρυθμίσεις Προφίλ")
        new_name = st.text_input("Όνομα Παιδιού:", value=st.session_state.user["name"])
        new_age = st.number_input("Ηλικία Παιδιού:", min_value=3, max_value=12, value=st.session_state.user["age"])
        if st.button("💾 Αποθήκευση", use_container_width=True):
            st.session_state.user["name"] = new_name
            st.session_state.user["age"] = new_age
            SessionManager.save_to_db(st.session_state.user)
            st.success("Οι αλλαγές αποθηκεύτηκαν!")
            st.rerun()

if __name__ == "__main__":
    main()
