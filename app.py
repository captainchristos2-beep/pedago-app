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
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# =================================================================
# MODULE 1: GLOBAL CONFIGURATION, LOCALIZATION & PREMIUM STYLES
# =================================================================
class AppConfig:
    """System Architecture & International Dual-Core Localization"""
    TITLE = "PedaGO Sovereign v10.5"
    VERSION = "Build 2026.InternationalCore"

    # Localization Dictionary
    TRANSLATIONS = {
        "EL": {
            "title_sub": "Η δική σου Πρωινή Εδέμ περιμένει!",
            "banner_h": "✨ ΠΛΑΤΦΟΡΜΑ ΕΚΠΑΙΔΕΥΤΙΚΗΣ ΤΕΧΝΟΛΟΓΙΑΣ",
            "banner_p": "Ολοκληρωμένο περιβάλλον αλληλεπίδρασης και μάθησης.",
            "tab_login": "🔑 Σύνδεση Χρήστη",
            "tab_register": "📝 Δημιουργία Προφίλ",
            "username": "Όνομα Χρήστη (Email / Username):",
            "password": "Κωδικός Πρόσβασης:",
            "btn_login": "🚀 Είσοδος",
            "btn_register": "📝 Ολοκλήρωση Εγγραφής",
            "role_select": "Επιλέξτε τον Ρόλο σας:",
            "role_parent": "Γονέας",
            "role_teacher": "Εκπαιδευτικός",
            "login_success": "Επιτυχής σύνδεση ως",
            "login_fail": "❌ Λανθασμένα στοιχεία σύνδεσης!",
            "reg_success": "🎉 Ο λογαριασμός δημιουργήθηκε επιτυχώς!",
            "reg_fail": "❌ Το όνομα χρήστη χρησιμοποιείται ήδη.",
            "fill_fields": "💡 Παρακαλώ συμπληρώστε όλα τα πεδία!",
            "onboard_title": "👋 Δημιουργία Προφίλ Παιδιού",
            "onboard_sub": "Συνδέστε αυτόματα τον λογαριασμό γονέα με τον μικρό εξερευνητή.",
            "child_name": "Όνομα Παιδιού:",
            "child_age": "Ηλικία Παιδιού:",
            "btn_start": "🚀 Δημιουργία & Σύνδεση!",
            "level": "ΕΠΙΠΕΔΟ",
            "xp_label": "XP",
            "child_prof": "Προφίλ Παιδιού:",
            "mood_label": "Διάθεση:",
            "msgs_label": "Μηνύματα:",
            "plan_label": "Πλάνο:",
            "nav_title": "📌 PedaGO Dashboard",
            "active_role": "🔑 Ενεργός Ρόλος:",
            "btn_worlds": "🗺️ Κόσμοι & Περιπέτεια (Παιδί)",
            "btn_memory": "🧠 Γλωσσική Μνήμη",
            "btn_parent": "📊 Dashboard Γονέα & Analytics",
            "btn_settings": "⚙️ Ρυθμίσεις Προφίλ",
            "btn_portal": "🏫 Educator Portal (B2B)",
            "btn_logout": "🚪 Αποσύνδεση",
            "screen_guard": "⏰ Screen Time Guard: Συμπληρώθηκε το ημερήσιο όριο χρήσης!",
            "stripe_text": "💎 Pro Plan Upgrade: Ξεκλειδώστε απεριόριστο χρόνο ομιλίας και τα πλήρη Affective AI Analytics!",
            "stripe_btn": "Ενεργοποίηση Pro (9.99€/μήνα)",
            "vocab_challenge": "🎯 Vocabulary Challenge: Χρησιμοποίησε τη λέξη 'αστέρι' και κέρδισε +50 XP!",
            "change_world": "↩️ Αλλαγή Κόσμου",
            "listen_prompt": "🎤 Πάτα & Μίλησε στον Φοίβο",
            "stop_prompt": "🛑 Σταμάτα",
            "phoebus_listening": "Ο Φοίβος σε ακούει...",
            "target_word": "αστέρι",
            "stt_lang": "el",
            "tts_lang": "el",
            "beebot_caption": "🤖 Προαιρετική Σύνδεση με Εκπαιδευτική Ρομποτική (BeeBot Hybrid Mod Active)",
            "magic_tag": "🔮 MagicSchool Active Engine",
            "magic_desc": "Διαφοροποιημένη Διδασκαλία • Ηλικιακό Προφίλ: {age} ετών • Μέθοδος: Σωκρατική Γνωστική Σκαλωσιά"
        },
        "EN": {
            "title_sub": "Your personalized AI Learning Sanctuary awaits!",
            "banner_h": "✨ NEXT-GEN EDTECH PLATFORM",
            "banner_p": "Integrated affective computing and multimodal learning interface.",
            "tab_login": "🔑 User Login",
            "tab_register": "📝 Register Profile",
            "username": "Username / Email:",
            "password": "Password:",
            "btn_login": "🚀 Sign In",
            "btn_register": "📝 Complete Registration",
            "role_select": "Select Your Role:",
            "role_parent": "Parent",
            "role_teacher": "Educator",
            "login_success": "Successfully authenticated as",
            "login_fail": "❌ Invalid credentials!",
            "reg_success": "🎉 Account successfully created!",
            "reg_fail": "❌ Username already exists.",
            "fill_fields": "💡 Please fill in all fields!",
            "onboard_title": "👋 Student Profile Initialization",
            "onboard_sub": "Seamlessly link parent account to child's conversational agent.",
            "child_name": "Child's Name:",
            "child_age": "Child's Age:",
            "btn_start": "🚀 Initialize & Launch!",
            "level": "LEVEL",
            "xp_label": "XP",
            "child_prof": "Student:",
            "mood_label": "Mood:",
            "msgs_label": "Messages:",
            "plan_label": "Tier:",
            "nav_title": "📌 Navigation Suite",
            "active_role": "🔑 Active Role:",
            "btn_worlds": "🗺️ Worlds & Adventure (Child)",
            "btn_memory": "🧠 Language Memory Engine",
            "btn_parent": "📊 Parent Analytics Dashboard",
            "btn_settings": "⚙️ Profile Settings",
            "btn_portal": "🏫 Educator Portal (B2B)",
            "btn_logout": "🚪 Sign Out",
            "screen_guard": "⏰ Screen Time Guard: Daily usage limit reached!",
            "stripe_text": "💎 Pro Plan Upgrade: Unlock unlimited voice runtime and complete Affective AI Analytics!",
            "stripe_btn": "Activate Pro (€9.99/mo)",
            "vocab_challenge": "🎯 Vocabulary Challenge: Use the word 'star' to gain +50 XP Bonus!",
            "change_world": "↩️ Change World",
            "listen_prompt": "🎤 Press & Speak to Phoebus",
            "stop_prompt": "🛑 Stop",
            "phoebus_listening": "Phoebus is listening carefully...",
            "target_word": "star",
            "stt_lang": "en",
            "tts_lang": "en",
            "beebot_caption": "🤖 Optional Educational Robotics Bridge (BeeBot Hybrid Mod Active)",
            "magic_tag": "🔮 MagicSchool Engine Active",
            "magic_desc": "Differentiated Instruction • Age Cohort: {age} yo • Method: Socratic Cognitive Scaffolding"
        }
    }

    THEMES = {
        "Εδέμ Πρωί": {
            "name_en": "Morning Eden", "color": "#10b981", "icon": "🌿",
            "prompt_el": "Είσαι στον Παράδεισο της Εδέμ. Μίλα ήρεμα και ενθαρρυντικά με απλά λόγια.",
            "prompt_en": "You are in the Paradise of Eden. Speak gently and encouragingly using simple, nurturing words.",
            "bg": "linear-gradient(135deg, #064e3b, #022c22)"
        },
        "Νησί Γρίφων": {
            "name_en": "Riddle Island", "color": "#f59e0b", "icon": "🏝️",
            "prompt_el": "Είσαι στο Νησί των Γρίφων. Μίλα με αινίγματα και Σωκρατική μέθοδο.",
            "prompt_en": "You are on Riddle Island. Challenge the child with curious questions, playful riddles, and Socratic guidance.",
            "bg": "linear-gradient(135deg, #78350f, #451a03)"
        },
        "Διάστημα": {
            "name_en": "Deep Space", "color": "#6366f1", "icon": "🚀",
            "prompt_el": "Είσαι στο Διάστημα. Μίλα για αστέρια, πλανήτες και εξερεύνηση.",
            "prompt_en": "You are in Deep Space. Talk about stars, planets, and cosmic exploration with infectious excitement.",
            "bg": "linear-gradient(135deg, #1e1b4b, #0f172a)"
        }
    }

    @staticmethod
    def inject_premium_styles():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
            .stApp { background-color: #0b0f19; color: #f1f5f9; font-family: 'Nunito', sans-serif; }
            .premium-card {
                background: rgba(30, 41, 59, 0.45);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                padding: 24px;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
                margin-bottom: 20px;
            }
            .duo-progress-container {
                width: 100%; background-color: #1e293b; border-radius: 12px; padding: 3px; border: 1px solid #334155; margin: 10px 0px;
            }
            .duo-progress-bar {
                height: 16px; background: linear-gradient(90deg, #10b981, #34d399); border-radius: 9px; transition: width 0.5s ease-in-out;
            }
            .phoebus-bubble {
                background: rgba(30, 41, 59, 0.7); border-left: 5px solid #10b981; padding: 18px; border-radius: 4px 20px 20px 20px; margin: 12px 0px; color: #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .phoebus-bubble-tired {
                background: rgba(30, 41, 59, 0.7); border-left: 5px solid #3b82f6; padding: 18px; border-radius: 4px 20px 20px 20px; margin: 12px 0px; color: #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .smart-action-title {
                font-size: 14px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; color: #6366f1; margin-bottom: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

# =================================================================
# MODULE 2: ADAPTIVE VOICE & AUDIO ENGINE
# =================================================================
class VoiceEngine:
    """Subsystem for Dynamic STT / TTS Locale Adaptation"""
    @staticmethod
    def speak(text, lang='el'):
        try:
            tts = gTTS(text=text, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"TTS Engine Error: {e}")

    @staticmethod
    def listen(t):
        return speech_to_text(
            language=t["stt_lang"],
            start_prompt=t["listen_prompt"],
            stop_prompt=t["stop_prompt"],
            just_once=True,
            key='STT_Component'
        )

# =================================================================
# MODULE 3: AFFECTIVE & MULTILINGUAL AI CORE
# =================================================================
class PhoebusBrain:
    """Emotionally Intelligent & Multilingual Groq Core"""
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    def analyze_sentiment(self, text, lang="EL"):
        prompt = f"Analyze child sentiment in this utterance: '{text}'. Language is {lang}. Return valid JSON: {{\"mood\": \"happy/sad/tired/calm\", \"energy\": 1-10}}"
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are an expert pediatric psychologist."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_response(self, history, mood_context, world_key, child_age, lang="EL"):
        theme_info = AppConfig.THEMES[world_key]
        world_prompt = theme_info["prompt_en"] if lang == "EN" else theme_info["prompt_el"]
        
        if lang == "EN":
            age_instruction = "The child is in preschool (4yo), use simple sentences up to 5 words." if child_age <= 4 else "The child is 5-6yo, foster expressive responses and Socratic inquiry."
            full_prompt = f"{world_prompt} The child currently seems {mood_context.get('mood', 'calm')}. {age_instruction} Maintain an encouraging, warm pedagogical tone in fluent English."
        else:
            age_instruction = "Το παιδί είναι προ-νήπιο (4 ετών), χρησιμοποίησε πολύ απλές, μικρές προτάσεις έως 5 λέξεις." if child_age <= 4 else "Το παιδί είναι νήπιο (5-6 ετών), ενθάρρυνε σύνθετες απαντήσεις και κριτική σκέψη."
            full_prompt = f"{world_prompt} Το παιδί νιώθει {mood_context.get('mood', 'ήρεμο')}. {age_instruction} Προσάρμοσε τον τόνο σου ακαδημαϊκά και παιδαγωγικά στα Ελληνικά."
            
        messages = [{"role": "system", "content": full_prompt}] + history
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages, temperature=0.7
        )
        return response.choices[0].message.content

# =================================================================
# MODULE 4: SAAS, AUTH & DATA MANAGER
# =================================================================
class SessionManager:
    """Relational SQL Database Engine, Accounts, and Spaced Repetition (SM-2)"""
    @staticmethod
    def init_db():
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS user_profile (id INTEGER PRIMARY KEY, name TEXT, xp INTEGER, level INTEGER, plan TEXT, age INTEGER, onboarded INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS word_memory (word TEXT PRIMARY KEY, interval INTEGER, ease_factor REAL, next_review TEXT)")
        conn.commit()
        conn.close()

    @staticmethod
    def register_user(username, password, role):
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO accounts (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

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
                "history": [], "mood": "Calm / Ήρεμος", "mood_history": ["Calm / Ήρεμος"], "xp_history": [10, row[1]],
                "usage_count": 0, "max_usage": 3, "vocab_bonus": False
            }
        return None

    @staticmethod
    def update_word_memory(word, quality):
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT interval, ease_factor FROM word_memory WHERE word = ?", (word,))
        row = cursor.fetchone()
        if row: interval, ef = row[0], row[1]
        else: interval, ef = 1, 2.5
        if quality >= 3:
            if interval == 1: interval = 2
            elif interval == 2: interval = 4
            else: interval = int(interval * ef)
        else: interval = 1
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ef < 1.3: ef = 1.3
        next_date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT OR REPLACE INTO word_memory (word, interval, ease_factor, next_review) VALUES (?, ?, ?, ?)", (word, interval, ef, next_date))
        conn.commit()
        conn.close()

    @staticmethod
    def initialize():
        SessionManager.init_db()
        if "lang" not in st.session_state:
            st.session_state.lang = "EL"
        if "user" not in st.session_state:
            db_user = SessionManager.load_from_db()
            if db_user: st.session_state.user = db_user
            else:
                st.session_state.user = {
                    "name": "Alex", "xp": 40, "level": 1, "plan": "Free", "history": [], "mood": "Calm / Ήρεμος", "age": 5,
                    "mood_history": ["Calm / Ήρεμος"], "xp_history": [10, 20, 40],
                    "onboarded": False, "usage_count": 0, "max_usage": 3, "vocab_bonus": False
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
# MODULE 5: PRESENTATION LAYER & INTERFACE
# =================================================================
def render_hud(t):
    remaining = max(0, st.session_state.user["max_usage"] - st.session_state.user["usage_count"]) if st.session_state.user["plan"] == "Free" else "∞"
    current_level_base = (st.session_state.user["level"] - 1) * 100
    xp_in_level = st.session_state.user["xp"] - current_level_base
    progress_percentage = min(100, max(5, xp_in_level))

    st.markdown(f"""
        <div class="premium-card" style="padding: 20px; border-left: 6px solid #6366f1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size:16px; font-weight:900; color:#818cf8;">🏆 {t['level']} {st.session_state.user['level']}</span>
                <span style="font-size:14px; font-weight:bold; color:#94a3b8;">✨ {st.session_state.user['xp']} / {st.session_state.user['level'] * 100} {t['xp_label']}</span>
            </div>
            <div class="duo-progress-container">
                <div class="duo-progress-bar" style="width: {progress_percentage}%;"></div>
            </div>
            <div style="display: flex; gap: 15px; font-size:13px; color:#cbd5e1; margin-top: 12px; font-weight: bold;">
                <span>👤 <b>{t['child_prof']}</b> {st.session_state.user['name']}</span> | 
                <span>🎭 <b>{t['mood_label']}</b> {st.session_state.user['mood']}</span> | 
                <span>⏳ <b>{t['msgs_label']}</b> {remaining}</span> | 
                <span>💎 <b>{t['plan_label']}</b> <span style="color:#10b981;">{st.session_state.user['plan']}</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar(t):
    st.sidebar.markdown("### 🌐 Language / Γλώσσα")
    selected_lang = st.sidebar.selectbox(
        "Choose interface language:",
        options=["EL", "EN"],
        index=0 if st.session_state.lang == "EL" else 1,
        format_func=lambda x: "🇬🇷 Ελληνικά" if x == "EL" else "🇬🇧 English"
    )
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

    if st.session_state.page not in ["login", "onboarding"]:
        st.sidebar.title(t["nav_title"])
        st.sidebar.info(f"{t['active_role']} **{st.session_state.current_role}**")
        
        if st.session_state.current_role in ["Γονέας", "Parent"]:
            if st.sidebar.button(t["btn_worlds"], use_container_width=True): st.session_state.page = "hub"; st.rerun()
            if st.sidebar.button(t["btn_memory"], use_container_width=True): st.session_state.page = "memory_core"; st.rerun()
            if st.sidebar.button(t["btn_parent"], use_container_width=True): st.session_state.page = "parent_dashboard"; st.rerun()
            if st.sidebar.button(t["btn_settings"], use_container_width=True): st.session_state.page = "profile_settings"; st.rerun()
        
        elif st.session_state.current_role in ["Εκπαιδευτικός", "Educator"]:
            if st.sidebar.button(t["btn_portal"], use_container_width=True): st.session_state.page = "educator_portal"; st.rerun()
            
        st.sidebar.write("---")
        if st.sidebar.button(t["btn_logout"], use_container_width=True):
            st.session_state.page = "login"
            st.session_state.current_role = None
            st.session_state.user["history"] = []
            st.rerun()

def main():
    AppConfig.inject_premium_styles()
    SessionManager.initialize()
    t = AppConfig.TRANSLATIONS[st.session_state.lang]
    render_sidebar(t)
    brain = PhoebusBrain()

    # --- PAGE: UNIFIED AUTHENTICATION ---
    if st.session_state.page == "login":
        st.title(AppConfig.TITLE)
        st.subheader(t["title_sub"])
        
        st.markdown(f"""
            <div class="premium-card" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); text-align: center; border: none;">
                <h2 style="color: white; font-weight: 900; margin: 0;">{t['banner_h']}</h2>
                <p style="color: #bfdbfe; margin-top: 8px; font-size: 16px;">{t['banner_p']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs([t["tab_login"], t["tab_register"]])
        
        with tab_login:
            login_user = st.text_input(t["username"], key="log_u")
            login_pass = st.text_input(t["password"], type="password", key="log_p")
            if st.button(t["btn_login"], use_container_width=True):
                role = SessionManager.authenticate_user(login_user, login_pass)
                if role:
                    st.session_state.current_role = role
                    st.success(f"{t['login_success']} {role}!")
                    time.sleep(1)
                    if role in ["Γονέας", "Parent"]:
                        st.session_state.page = "hub" if st.session_state.user["onboarded"] else "onboarding"
                    else:
                        st.session_state.page = "educator_portal"
                    st.rerun()
                else:
                    st.error(t["login_fail"])
                    
        with tab_reg:
            reg_user = st.text_input(t["username"], key="reg_u")
            reg_pass = st.text_input(t["password"], type="password", key="reg_p")
            role_options = [t["role_parent"], t["role_teacher"]]
            reg_role = st.selectbox(t["role_select"], role_options)
            
            if st.button(t["btn_register"], use_container_width=True):
                if not reg_user.strip() or not reg_pass.strip():
                    st.error(t["fill_fields"])
                else:
                    success = SessionManager.register_user(reg_user, reg_pass, reg_role)
                    if success: st.success(t["reg_success"])
                    else: st.error(t["reg_fail"])

    # --- PAGE: ONBOARDING ---
    elif st.session_state.page == "onboarding":
        st.title(t["onboard_title"])
        st.subheader(t["onboard_sub"])
        with st.form("onboarding_form"):
            onboard_name = st.text_input(t["child_name"], placeholder="e.g. Alex / Νικόλας")
            onboard_age = st.number_input(t["child_age"], min_value=3, max_value=12, value=5)
            if st.form_submit_button(t["btn_start"], use_container_width=True):
                if not onboard_name.strip():
                    st.error(t["fill_fields"])
                else:
                    st.session_state.user["name"] = onboard_name
                    st.session_state.user["age"] = onboard_age
                    st.session_state.user["onboarded"] = True
                    SessionManager.save_to_db(st.session_state.user)
                    st.success("🎉 Initialized!")
                    time.sleep(1)
                    st.session_state.page = "hub"
                    st.rerun()

    # --- PAGE: WORLD SELECTION HUB ---
    elif st.session_state.page == "hub":
        render_hud(t)
        st.title("🗺️ Worlds / Κόσμοι")
        if SessionManager.check_screen_time():
            st.error(t["screen_guard"])
            return

        st.markdown(f"""
            <div class="premium-card" style="border-left: 5px solid #10b981; display:flex; justify-content:space-between; align-items:center;">
                <div>{t['stripe_text']}</div>
                <a href="https://buy.stripe.com/5kA6oE736g1Y5JCdQQ" target="_blank" style="text-decoration:none; background:#10b981; color:white; padding:8px 16px; border-radius:8px; font-weight:bold;">{t['stripe_btn']}</a>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (key, data) in enumerate(AppConfig.THEMES.items()):
            display_title = data["name_en"] if st.session_state.lang == "EN" else key
            with cols[i]:
                st.markdown(f"<div style='background: {data['bg']}; padding:30px; border-radius:20px; border: 2px solid {data['color']}; text-align:center;'><h2>{data['icon']} {display_title}</h2></div>", unsafe_allow_html=True)
                if st.button(f"Enter: {display_title}", key=key, use_container_width=True):
                    st.session_state.current_world = key
                    st.session_state.page = "adventure"
                    st.rerun()

    # --- PAGE: INTERACTIVE ADVENTURE ---
    elif st.session_state.page == "adventure":
        render_hud(t)
        if SessionManager.check_screen_time():
            st.error(t["screen_guard"])
            return

        world_key = st.session_state.current_world
        world_data = AppConfig.THEMES[world_key]
        display_world = world_data["name_en"] if st.session_state.lang == "EN" else world_key

        col_title, col_back = st.columns([4, 1])
        with col_title: st.header(f"{world_data['icon']} {display_world}")
        with col_back:
            if st.button(t["change_world"], use_container_width=True): st.session_state.page = "hub"; st.rerun()

        st.markdown(f"""
            <div class="premium-card" style="padding:15px; border-left: 4px solid {world_data['color']}; margin-bottom:15px;">
                <div class="smart-action-title">{t['magic_tag']}</div>
                <span style="font-size:13px; color:#94a3b8;">{t['magic_desc'].format(age=st.session_state.user['age'])}</span>
            </div>
        """, unsafe_allow_html=True)

        st.caption(t["beebot_caption"])

        # Chat Bubble Stream
        for msg in st.session_state.user["history"]:
            if msg["role"] == "assistant":
                st.markdown(f'<div style="display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px;"><div style="font-size: 24px;">🧸</div><div class="phoebus-bubble" style="border-left-color: {world_data["color"]};"><b>Phoebus:</b> {msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                with st.chat_message("user"): st.write(msg["content"])

        user_speech = VoiceEngine.listen(t)
        if user_speech:
            st.session_state.user["history"].append({"role": "user", "content": user_speech})
            st.session_state.user["usage_count"] += 1
            
            # Repetition tracking
            if t["target_word"] in user_speech.lower():
                SessionManager.update_word_memory(t["target_word"], 5)
                if not st.session_state.user["vocab_bonus"]:
                    st.session_state.user["vocab_bonus"] = True
                    SessionManager.add_xp(50)
                    st.toast("🎯 Vocabulary Bonus Triggered!", icon="✨")

            with st.spinner(t["phoebus_listening"]):
                mood_data = brain.analyze_sentiment(user_speech, st.session_state.lang)
                st.session_state.user["mood"] = mood_data.get("mood", "Calm")
                st.session_state.user["mood_history"].append(st.session_state.user["mood"])
                
                response = brain.generate_response(
                    st.session_state.user["history"], mood_data, world_key, st.session_state.user["age"], st.session_state.lang
                )
                st.session_state.user["history"].append({"role": "assistant", "content": response})
                SessionManager.add_xp(20)
                VoiceEngine.speak(response, lang=t["tts_lang"])
                st.rerun()

    # --- PAGE: LANGUAGE MEMORY CORE ---
    elif st.session_state.page == "memory_core":
        st.title(t["btn_memory"])
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT word, interval, ease_factor, next_review FROM word_memory")
        rows = cursor.fetchall()
        conn.close()
        if rows:
            cols_names = ['Word / Lexeme', 'Interval (Days)', 'Ease Factor', 'Next Review'] if st.session_state.lang == "EN" else ['Λέξη / Έννοια', 'Μεσοδιάστημα (Ημέρες)', 'Συντελεστής Ευκολίας', 'Επόμενος Έλεγχος']
            cards_data = pd.DataFrame(rows, columns=cols_names)
            st.dataframe(cards_data, use_container_width=True)
            fig_anki = go.Figure([go.Bar(x=cards_data[cols_names[0]], y=cards_data[cols_names[1]], marker_color='#10b981')])
            fig_anki.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_anki, use_container_width=True)
        else:
            st.warning("🔒 No active vocabulary entries recorded yet.")

    # --- PAGE: PARENT ANALYTICS ---
    elif st.session_state.page == "parent_dashboard":
        st.title(t["btn_parent"])
        render_hud(t)
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📊 Cognitive Competency Radar")
            cats = ['Vocabulary', 'Critical Thinking', 'Self-Regulation', 'Speech Latency', 'Empathy'] if st.session_state.lang == "EN" else ['Λεξιλόγιο', 'Κριτική Σκέψη', 'Αυτορύθμιση', 'Ταχύτητα Απόκρισης', 'Ενσυναίσθηση']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[4, 3, 5, 4, 4], theta=cats, fill='toself', marker=dict(color='#6366f1'), fillcolor='rgba(99, 102, 241, 0.3)'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_radar, use_container_width=True)
        with col2:
            st.write("### 📈 Learning Trajectory (XP)")
            fig_xp = go.Figure(data=go.Scatter(y=st.session_state.user["xp_history"], mode='lines+markers', line=dict(color='#10b981', width=3)))
            fig_xp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_xp, use_container_width=True)

    # --- PAGE: EDUCATOR PORTAL ---
    elif st.session_state.page == "educator_portal":
        st.title(t["btn_portal"])
        st.info("💡 e-me / Open eClass API Gateway Interface: Active & Synchronized.")
        class_data = pd.DataFrame({
            'Student': ['Nicolas', 'Maria', 'George', 'Elena', 'Dimitris'],
            'Weekly XP': [120, 240, 90, 310, 150],
            'Dominant Affect': ['Happy', 'Enthusiastic', 'Fatigued', 'Happy', 'Calm']
        })
        st.table(class_data)

    # --- PAGE: PROFILE SETTINGS ---
    elif st.session_state.page == "profile_settings":
        st.title(t["btn_settings"])
        new_name = st.text_input(t["child_name"], value=st.session_state.user["name"])
        new_age = st.number_input(t["child_age"], min_value=3, max_value=12, value=st.session_state.user["age"])
        if st.button("💾 Save Changes", use_container_width=True):
            st.session_state.user["name"] = new_name
            st.session_state.user["age"] = new_age
            SessionManager.save_to_db(st.session_state.user)
            st.success("Updated successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
