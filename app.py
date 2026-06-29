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
# MODULE 1: GLOBAL CONFIGURATION, THEMES & HYPER-GAMIFIED CSS
# =================================================================
class AppConfig:
    """Ρυθμίσεις Συστήματος & Οπτική Ταυτότητα (Duolingo + MagicSchool Grade)"""
    TITLE = "PedaGO Sovereign v8.0"
    VERSION = "Build 2026.HyperSaaS"
    THEMES = {
        "Εδέμ Πρωί": {"color": "#10b981", "icon": "🌿", "prompt": "Είσαι στον Παράδεισο της Εδέμ. Μίλα ήρεμα και ενθαρρυντικά με απλά λόγια.", "bg": "linear-gradient(135deg, #064e3b, #022c22)", "accent": "#34d399"},
        "Νησί Γρίφων": {"color": "#f59e0b", "icon": "🏝️", "prompt": "Είσαι στο Νησί των Γρίφων. Μίλα με αινίγματα και Σωκρατική μέθοδο.", "bg": "linear-gradient(135deg, #78350f, #451a03)", "accent": "#fbbf24"},
        "Διάστημα": {"color": "#6366f1", "icon": "🚀", "prompt": "Είσαι στο Διάστημα. Μίλα για αστέρια, πλανήτες και εξερεύνηση.", "bg": "linear-gradient(135deg, #1e1b4b, #0f172a)", "accent": "#818cf8"}
    }

    @staticmethod
    def inject_premium_styles():
        """Έγχυση CSS για Glassmorphism, Neon Elements & Duolingo Bars"""
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
            
            /* Global Reset & Typography */
            .stApp { background-color: #0b0f19; color: #f1f5f9; font-family: 'Nunito', sans-serif; }
            
            /* Glassmorphism Premium Cards */
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
            
            /* Duolingo Style Progress Bar Container */
            .duo-progress-container {
                width: 100%;
                background-color: #1e293b;
                border-radius: 12px;
                padding: 3px;
                border: 1px solid #334155;
                margin: 10px 0px;
            }
            .duo-progress-bar {
                height: 16px;
                background: linear-gradient(90deg, #10b981, #34d399);
                border-radius: 9px;
                transition: width 0.5s ease-in-out;
            }
            
            /* Speech Bubbles */
            .phoebus-bubble {
                background: rgba(30, 41, 59, 0.7);
                border-left: 5px solid #10b981;
                padding: 18px;
                border-radius: 4px 20px 20px 20px;
                margin: 12px 0px;
                color: #e2e8f0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            
            /* MagicSchool Controls Heading */
            .smart-action-title {
                font-size: 14px;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #6366f1;
                margin-bottom: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

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
# MODULE 3: AFFECTIVE & ADAPTIVE AI CORE (THE BRAIN)
# =================================================================
class PhoebusBrain:
    """Η Καρδιά του Φοίβου με Συναισθηματική & Ηλικιακή Νοημοσύνη"""
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

    def generate_response(self, history, mood_context, world_prompt, child_age):
        age_instruction = "Το παιδί είναι προ-νήπιο (4 ετών), χρησιμοποίησε πολύ απλές, μικρές προτάσεις έως 5 λέξεις." if child_age <= 4 else "Το παιδί είναι νήπιο (5-6 ετών), ενθάρρυνε σύνθετες απαντήσεις και κριτική σκέψη."
        
        full_prompt = f"{world_prompt}. Το παιδί νιώθει {mood_context['mood']}. {age_instruction} Προσάρμοσε τον τόνο σου ακαδημαϊκά και παιδαγωγικά."
        messages = [{"role": "system", "content": full_prompt}] + history
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

# =================================================================
# MODULE 4: SAAS & DATA MANAGER (WITH PERSISTENCE)
# =================================================================
class SessionManager:
    """Διαχείριση Χρήστη, SQLite Βάσης, XP, Onboarding, Χρονοδιακόπτη & Καμπύλης Μνήμης"""
    
    @staticmethod
    def init_db():
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
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
                "usage_count": 0, "max_usage": 3, "vocab_bonus": False
            }
        return None

    @staticmethod
    def update_word_memory(word, quality):
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT interval, ease_factor FROM word_memory WHERE word = ?", (word,))
        row = cursor.fetchone()
        
        if row:
            interval, ef = row[0], row[1]
        else:
            interval, ef = 1, 2.5
            
        if quality >= 3:
            if interval == 1: interval = 2
            elif interval == 2: interval = 4
            else: interval = int(interval * ef)
        else:
            interval = 1
            
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ef < 1.3: ef = 1.3
        
        next_date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d %H:%M")
        
        cursor.execute("""
            INSERT OR REPLACE INTO word_memory (word, interval, ease_factor, next_review)
            VALUES (?, ?, ?, ?)
        """, (word, interval, ef, next_date))
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
                    "onboarded": False, "usage_count": 0, "max_usage": 3, "vocab_bonus": False
                }
        if "page" not in st.session_state: 
            st.session_state.page = "login"

    @staticmethod
    def add_xp(points):
        st.session_state.user["xp"] += points
        st.session_state.user["xp_history"].append(st.session_state.user["xp"])
        st.session_state.user["level"] = (st.session_state.user["xp"] // 100) + 1
        SessionManager.save_to_db(st.session_state.user)

    @staticmethod
    def check_screen_time():
        if st.session_state.user["plan"] == "Free" and st.session_state.user["usage_count"] >= st.session_state.user["max_usage"]:
            return True
        return False

# =================================================================
# MODULE 5: UI COMPONENTS & PAGES
# =================================================================
def render_hud():
    """Εμφάνιση HUD (Heads-Up Display) με Duolingo-Grade Σχεδιασμό"""
    remaining = max(0, st.session_state.user["max_usage"] - st.session_state.user["usage_count"]) if st.session_state.user["plan"] == "Free" else "∞"
    
    # Υπολογισμός ποσοστού προόδου για την Duolingo μπάρα
    current_level_base = (st.session_state.user["level"] - 1) * 100
    xp_in_level = st.session_state.user["xp"] - current_level_base
    progress_percentage = min(100, max(5, xp_in_level))

    st.markdown(f"""
        <div class="premium-card" style="padding: 20px; border-left: 6px solid #6366f1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size:16px; font-weight:900; color:#818cf8;">🏆 ΕΠΙΠΕΔΟ {st.session_state.user['level']}</span>
                <span style="font-size:14px; font-weight:bold; color:#94a3b8;">✨ {st.session_state.user['xp']} / {st.session_state.user['level'] * 100} XP</span>
            </div>
            <div class="duo-progress-container">
                <div class="duo-progress-bar" style="width: {progress_percentage}%;"></div>
            </div>
            <div style="display: flex; gap: 15px; font-size:13px; color:#cbd5e1; margin-top: 12px; font-weight: bold;">
                <span>🎭 <b>Διάθεση:</b> {st.session_state.user['mood']}</span> | 
                <span>⏳ <b>Μηνύματα:</b> {remaining}</span> | 
                <span>👶 <b>Ηλικία:</b> {st.session_state.user['age']} ετών</span> |
                <span>💎 <b>Πλάνο:</b> <span style="color:#10b981;">{st.session_state.user['plan']}</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Επαγγελματικό Μενού Πλοήγησης (Back & Forward)"""
    if st.session_state.page != "login" and st.session_state.page != "onboarding":
        st.sidebar.title("📌 PedaGO Hub")
        st.sidebar.write(f"Γεια σου, **{st.session_state.user['name']}**!")
        
        if st.sidebar.button("🗺️ Κόσμοι (Hub)", use_container_width=True):
            st.session_state.page = "hub"
            st.rerun()

        if st.sidebar.button("🧠 Γλωσσική Μνήμη", use_container_width=True):
            st.session_state.page = "memory_core"
            st.rerun()
            
        if st.sidebar.button("📊 Dashboard Γονέα", use_container_width=True):
            st.session_state.page = "parent_dashboard"
            st.rerun()

        if st.sidebar.button("🏫 Educator Portal (B2B)", use_container_width=True):
            st.session_state.page = "educator_portal"
            st.rerun()
            
        if st.sidebar.button("⚙️ Ρυθμίσεις Προφίλ", use_container_width=True):
            st.session_state.page = "profile_settings"
            st.rerun()
            
        st.sidebar.write("---")
        if st.sidebar.button("🚪 Αποσύνδεση", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.user["history"] = []
            st.session_state.user["onboarded"] = False
            st.session_state.user["usage_count"] = 0
            st.rerun()

def main():
    AppConfig.inject_premium_styles()
    SessionManager.initialize()
    render_sidebar()
    brain = PhoebusBrain()

    # --- PAGE: LOGIN / SAAS TIERS ---
    if st.session_state.page == "login":
        st.title("🚀 PedaGO Sovereign v8.0")
        st.subheader("Η δική σου Πρωινή Εδέμ περιμένει!")
        
        st.markdown("""
            <div class="premium-card" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); text-align: center; border: none;">
                <h2 style="color: white; font-weight: 900; margin: 0;">✨ THE NEW EDTECH STANDARD</h2>
                <p style="color: #bfdbfe; margin-top: 8px; font-size: 16px;">100x Πιο Διαδραστικό από το Duolingo & το MagicSchool μαζί.</p>
            </div>
        """, unsafe_allow_html=True)
            
        col1, col2 = st.columns(2)
        with col1:
            st.info("### Basic Plan\n- 5 Μηνύματα/μέρα\n- Standard AI")
            if st.button("Επιλογή Basic", use_container_width=True):
                st.session_state.user["plan"] = "Free"
                st.session_state.page = "hub" if st.session_state.user["onboarded"] else "onboarding"
                st.rerun()
        with col2:
            st.success("### Pro Plan\n- Απεριόριστη Φωνή\n- Affective AI Analytics")
            
            stripe_link = "https://buy.stripe.com/5kA6oE736g1Y5JCdQQ"
            
            st.markdown(f"""
                <a href="{stripe_link}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #10b981; color: white; padding: 14px 20px; text-align: center; border-radius: 12px; font-weight: bold; font-size: 16px; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.15); cursor: pointer; display: block; border: 1px solid #059669;">
                        💎 Ενεργοποίηση Pro (9.99€/μήνα)
                    </div>
                </a>
            """, unsafe_allow_html=True)
            
            if st.button("Σύνδεση ως Pro (Demo Mode)", use_container_width=True):
                st.session_state.user["plan"] = "Pro"
                st.session_state.page = "hub" if st.session_state.user["onboarded"] else "onboarding"
                st.rerun()

    # --- PAGE: FIRST TIME USER ONBOARDING ---
    elif st.session_state.page == "onboarding":
        st.title("👋 Καλώς ήρθες στο PedaGO!")
        st.subheader("Ας δημιουργήσουμε το προφίλ του μικρού μας εξερευνητή για πρώτη φορά.")
        
        with st.form("onboarding_form"):
            st.markdown("#### 📝 Στοιχεία Μαθητή")
            onboard_name = st.text_input("Πώς σε φωνάζουν; (Όνομα Παιδιού):", placeholder="π.χ. Νικόλας")
            onboard_age = st.number_input("Πόσων χρονών είσαι; (Ηλικία):", min_value=3, max_value=12, value=5)
            
            submit_onboarding = st.form_submit_button("🚀 Ξεκινάμε το Ταξίδι!", use_container_width=True)
            
            if submit_onboarding:
                if not onboard_name.strip():
                    st.error("💡 Σε παρακαλώ, συμπλήρωσε το όνομα του παιδιού για να μπορεί ο Φοίβος να του απευθύνεται σωστά!")
                else:
                    st.session_state.user["name"] = onboard_name
                    st.session_state.user["age"] = onboard_age
                    st.session_state.user["onboarded"] = True
                    SessionManager.save_to_db(st.session_state.user) 
                    st.success(f"🎉 Πανέτοιμα! Το προφίλ του/της {onboard_name} δημιουργήθηκε!")
                    time.sleep(1.5)
                    st.session_state.page = "hub"
                    st.rerun()

    # --- PAGE: WORLD HUB ---
    elif st.session_state.page == "hub":
        render_hud()
        st.title("🗺️ Διάλεξε τον Κόσμο σου")
        
        if SessionManager.check_screen_time():
            st.error("⏰ **Screen Time Guard:** Συμπληρώθηκε το ημερήσιο όριο χρήσης!")
            return

        st.markdown("""
            <div class="premium-card" style="border-left: 5px solid #6366f1; padding: 15px;">
                🎯 <b>Vocabulary Challenge:</b> Χρησιμοποίησε τη λέξη <b>"αστέρι"</b> στη συζήτηση με τον Φοίβο και κέρδισε <b>+50 XP Bonus!</b>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (name, data) in enumerate(AppConfig.THEMES.items()):
            with cols[i]:
                st.markdown(f"""
                    <div style='background: {data["bg"]}; padding:30px; border-radius:20px; border: 2px solid {data["color"]}; text-align:center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);'>
                        <h2 style='color: white; margin-bottom:15px;'>{data['icon']} {name}</h2>
                        <p style='color: #cbd5e1; font-size:14px; min-height:40px;'>Έτοιμος για περιπέτεια;</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Είσοδος: {name}", key=name, use_container_width=True):
                    st.session_state.current_world = name
                    st.session_state.page = "adventure"
                    st.rerun()

    # --- PAGE: ADVENTURE (WITH DUOLINGO ACCENT BUBBLES) ---
    elif st.session_state.page == "adventure":
        render_hud()
        
        if SessionManager.check_screen_time():
            st.error("⏰ **Screen Time Guard:** Το όριο χρήσης συμπληρώθηκε! Ώρα για διάλειμμα.")
            if st.button("🏠 Επιστροφή στο Hub"):
                st.session_state.page = "hub"
                st.rerun()
            return

        world = st.session_state.current_world
        col_title, col_back = st.columns([4, 1])
        with col_title:
            st.header(f"{AppConfig.THEMES[world]['icon']} {world}")
        with col_back:
            if st.button("↩️ Αλλαγή Κόσμου", use_container_width=True):
                st.session_state.page = "hub"
                st.rerun()
        
        # MagicSchool Style Context Panel
        st.markdown(f"""
            <div class="premium-card" style="padding:15px; border-left: 4px solid {AppConfig.THEMES[world]['color']}; margin-bottom:15px;">
                <div class="smart-action-title">🔮 MagicSchool Active Engine</div>
                <span style="font-size:13px; color:#94a3b8;">Διαφοροποιημένη Διδασκαλία Ενεργή • Ηλικιακό Προφίλ: {st.session_state.user['age']} ετών • Μέθοδος: Σωκρατική Γνωστική Σκαλωσιά</span>
            </div>
        """, unsafe_allow_html=True)

        # Εμφάνιση Διαλόγου
        for msg in st.session_state.user["history"]:
            if msg["role"] == "assistant":
                st.markdown(f"""
                    <div style="display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px;">
                        <div style="font-size: 28px;">🧸</div>
                        <div class="phoebus-bubble" style="border-left-color: {AppConfig.THEMES[world]['color']};">
                            <b>Φοίβος:</b> {msg['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                with st.chat_message("user"): st.write(msg["content"])

        user_speech = VoiceEngine.listen()
        if user_speech:
            st.session_state.user["history"].append({"role": "user", "content": user_speech})
            st.session_state.user["usage_count"] += 1 
            
            if "αστέρι" in user_speech.lower():
                SessionManager.update_word_memory("αστέρι", 5) 
                if not st.session_state.user["vocab_bonus"]:
                    st.session_state.user["vocab_bonus"] = True
                    SessionManager.add_xp(50)
                    st.toast("🎯 Γλωσσική Μνήμη Καταγράφηκε!", icon="✨")

            with st.spinner("Ο Φοίβος σε ακούει με προσοχή..."):
                mood_data = brain.analyze_sentiment(user_speech)
                st.session_state.user["mood"] = mood_data["mood"]
                st.session_state.user["mood_history"].append(mood_data["mood"])
                
                response = brain.generate_response(
                    st.session_state.user["history"], 
                    mood_data, 
                    AppConfig.THEMES[world]["prompt"],
                    st.session_state.user["age"]
                )
                st.session_state.user["history"].append({"role": "assistant", "content": response})
                SessionManager.add_xp(20)
                VoiceEngine.speak(response)
                st.rerun()

    # --- PAGE: LANGUAGE MEMORY CORE ---
    elif st.session_state.page == "memory_core":
        st.title("🧠 Σύστημα Γλωσσικής Μνήμης")
        st.subheader("Παρακολούθηση Καμπύλης Λήθης & Διαστημικής Επανάληψης (Spaced Repetition)")
        
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT word, interval, ease_factor, next_review FROM word_memory")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            cards_data = pd.DataFrame(rows, columns=['Λέξη / Έννοια', 'Μεσοδιάστημα (Ημέρες)', 'Συντελεστής Ευκολίας (Ease Factor)', 'Επόμενος Έλεγχος Αναφοράς'])
            st.write("### 🗂️ Ενεργές Έννοιες στο SQL Brain")
            st.dataframe(cards_data, use_container_width=True)
            
            st.write("### 📉 Live Στατιστικά Μνήμης")
            fig_anki = go.Figure([go.Bar(x=cards_data['Λέξη / Έννοια'], y=cards_data['Μεσοδιάστημα (Ημέρες)'], marker_color='#10b981')])
            fig_anki.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_anki, use_container_width=True)
        else:
            st.warning("🔒 Καμία έννοια δεν έχει καταγραφεί ακόμα! Μπείτε σε έναν Κόσμο και χρησιμοποιήστε τη λέξη 'αστέρι' για να ενεργοποιηθεί live η καταγραφή.")

    # --- PAGE: PARENT DASHBOARD ---
    elif st.session_state.page == "parent_dashboard":
        st.title("📊 Dashboard Γονέα & Analytics")
        render_hud()
        
        st.write("### 🏅 Ψηφιακά Παράσημα (Achievements)")
        badges_col = st.columns(3)
        with badges_col[0]: st.success("🌱 **Πρώτο Βήμα**\n(Ξεκλείδωσε με την εγγραφή)")
        with badges_col[1]:
            if st.session_state.user["xp"] >= 60: st.success("🏝️ **Εξερευνητής**\n(Ξεκλείδωσε με 60+ XP)")
            else: st.code("🔒 Κλειδωμένο (60 XP)")
        with badges_col[2]:
            if st.session_state.user["level"] >= 2: st.success("👑 **Master του Λόγου**\n(Ξεκλείδωσε στο Level 2)")
            else: st.code("🔒 Κλειδωμένο (Level 2)")

        st.write("---")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.write("### 📊 Παιδαγωγικό Προφίλ Δεξιοτήτων")
            categories = ['Λεξιλόγιο', 'Κριτική Σκέψη', 'Συναισθηματική Αυτορύθμιση', 'Ταχύτητα Απόκρισης', 'Κοινωνική Ενσυναίσθηση']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[4, 3, 5, 4, 4], theta=categories, fill='toself', marker=dict(color='#6366f1'), fillcolor='rgba(99, 102, 241, 0.3)'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_chart2:
            st.write("### 📈 Καμπύλη Μάθησης (XP Progression)")
            fig_xp = go.Figure(data=go.Scatter(y=st.session_state.user["xp_history"], mode='lines+markers', line=dict(color='#10b981', width=3)))
            fig_xp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_xp, use_container_width=True)

    # --- PAGE: EDUCATOR PORTAL ---
    elif st.session_state.page == "educator_portal":
        st.title("🏫 Educator Portal (Στατιστικά Τάξης)")
        st.subheader("Συγκεντρωτική εικόνα για τους συνεργαζόμενους Παιδικούς Σταθμούς / Νηπιαγωγεία")
        
        st.info("💡 Συμβατότητα με e-me API & Ψηφιακό Σχολείο Ενεργή.")
        
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
        
        if st.button("💾 Αποθήκευση Αλλαγών", use_container_width=True):
            st.session_state.user["name"] = new_name
            st.session_state.user["age"] = new_age
            SessionManager.save_to_db(st.session_state.user) 
            st.success("Το προφίλ ενημερώθηκε επιτυχώς στη μόνιμη βάση!")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()
