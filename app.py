import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import time
import json
import sqlite3
from datetime import datetime
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# =================================================================
# MODULE 1: GLOBAL CONFIGURATION & THEMES
# =================================================================
class AppConfig:
    """Ρυθμίσεις Συστήματος & Οπτική Ταυτότητα"""
    TITLE = "PedaGO Genesis Pro v5.0"
    VERSION = "Build 2026.Infinite"
    THEMES = {
        "Εδέμ Πρωί": {"color": "#10b981", "icon": "🌿", "prompt": "Είσαι στον Παράδεισο της Εδέμ. Μίλα ήρεμα και ενθαρρυντικά με απλά λόγια.", "bg": "linear-gradient(135deg, #064e3b, #022c22)"},
        "Νησί Γρίφων": {"color": "#f59e0b", "icon": "🏝️", "prompt": "Είσαι στο Νησί των Γρίφων. Μίλα με αινίγματα και Σωκρατική μέθοδο.", "bg": "linear-gradient(135deg, #78350f, #451a03)"},
        "Διάστημα": {"color": "#6366f1", "icon": "🚀", "prompt": "Είσαι στο Διάστημα. Μίλα για αστέρια, πλανήτες και εξερεύνηση.", "bg": "linear-gradient(135deg, #1e1b4b, #0f172a)"}
    }

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
# MODULE 4: SAAS & DATA MANAGER (WITH SQL PERSISTENCE)
# =================================================================
class SessionManager:
    """Διαχείριση Χρήστη, SQLite Βάσης, XP, Ιστορικού, Onboarding & Χρονοδιακόπτη"""
    
    @staticmethod
    def init_db():
        """Αρχικοποίηση Τοπικής Βάσης Δεδομένων SQLite"""
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                name TEXT,
                xp INTEGER,
                level INTEGER,
                plan TEXT,
                age INTEGER,
                onboarded INTEGER
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def save_to_db(user_data):
        """Αποθήκευση στοιχείων στη SQLite"""
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
        """Φόρτωση στοιχείων από τη SQLite"""
        conn = sqlite3.connect("pedago.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, xp, level, plan, age, onboarded FROM user_profile WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "name": row[0],
                "xp": row[1],
                "level": row[2],
                "plan": row[3],
                "age": row[4],
                "onboarded": True if row[5] == 1 else False,
                "history": [], 
                "mood": "Ήρεμος",
                "mood_history": ["Χαρούμενος", "Ήρεμος"],
                "xp_history": [10, row[1]],
                "usage_count": 0,       
                "max_usage": 3,
                "vocab_bonus": False
            }
        return None

    @staticmethod
    def initialize():
        SessionManager.init_db()
        if "user" not in st.session_state:
            db_user = SessionManager.load_from_db()
            if db_user:
                st.session_state.user = db_user
            else:
                st.session_state.user = {
                    "name": "Ήρωας",
                    "xp": 40, 
                    "level": 1, 
                    "plan": "Free",
                    "history": [], 
                    "mood": "Ήρεμος",
                    "age": 5,
                    "mood_history": ["Χαρούμενος", "Ήρεμος", "Ενθουσιώδης"],
                    "xp_history": [10, 20, 40],
                    "onboarded": False,
                    "usage_count": 0,       
                    "max_usage": 3,
                    "vocab_bonus": False
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
    """Εμφάνιση HUD (Heads-Up Display) με Premium Σχεδιασμό"""
    remaining = max(0, st.session_state.user["max_usage"] - st.session_state.user["usage_count"]) if st.session_state.user["plan"] == "Free" else "∞"
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding:18px; border-radius:15px; margin-bottom:25px; border: 1px solid #334155; color: white;">
            <span style="font-size:14px; margin-right:12px;">✨ <b>XP:</b> {st.session_state.user['xp']}</span> | 
            <span style="font-size:14px; margin-left:12px; margin-right:12px;">🏆 <b>Επίπεδο:</b> {st.session_state.user['level']}</span> | 
            <span style="font-size:14px; margin-left:12px; margin-right:12px;">🎭 <b>Διάθεση:</b> {st.session_state.user['mood']}</span> | 
            <span style="font-size:14px; margin-left:12px; margin-right:12px;">⏳ <b>Μηνύματα:</b> {remaining}</span> |
            <span style="font-size:14px; margin-left:12px;">💎 <b>Πλάνο:</b> <span style="color:#10b981; font-weight:bold;">{st.session_state.user['plan']}</span></span>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Επαγγελματικό Μενού Πλοήγησης (Back & Forward)"""
    if st.session_state.page != "login" and st.session_state.page != "onboarding":
        st.sidebar.title("📌 Πλοήγηση")
        st.sidebar.write(f"Γεια σου, **{st.session_state.user['name']}**!")
        
        if st.sidebar.button("🗺️ Κόσμοι (Hub)", use_container_width=True):
            st.session_state.page = "hub"
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
    st.set_page_config(page_title=AppConfig.TITLE, page_icon="🚀", layout="wide")
    SessionManager.initialize()
    render_sidebar()
    brain = PhoebusBrain()

    # --- PAGE: LOGIN / SAAS TIERS ---
    if st.session_state.page == "login":
        st.title("🚀 PedaGO Genesis Pro")
        st.subheader("Η δική σου Πρωινή Εδέμ περιμένει!")
        
        st.markdown("""
            <style>
            @keyframes pulse {
                0% { transform: scale(0.98); opacity: 0.9; }
                50% { transform: scale(1.01); opacity: 1; }
                100% { transform: scale(0.98); opacity: 0.9; }
            }
            .animated-banner {
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 30px;
                animation: pulse 4s infinite ease-in-out;
                box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
            }
            </style>
            <div class="animated-banner">
                ✨ Καλώς ήρθες στον Κόσμο του Φοίβου! Ολοκληρωμένη Πλατφόρμα Εκπαιδευτικής Τεχνολογίας
            </div>
        """, unsafe_allow_html=True)
            
        col1, col2 = st.columns(2)
        with col1:
            st.info("### Basic Plan\n- 3 Μηνύματα/μέρα\n- Standard AI")
            if st.button("Επιλογή Basic", use_container_width=True):
                st.session_state.user["plan"] = "Free"
                st.session_state.page = "hub" if st.session_state.user["onboarded"] else "onboarding"
                st.rerun()
        with col2:
            st.success("### Pro Plan\n- Απεριόριστη Φωνή\n- Affective AI Analytics")
            
            stripe_link = "https://buy.stripe.com/test_9B6eVc3Jcb0DgBrdal9Ve00"
            
            st.markdown(f"""
                <a href="{stripe_link}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background-color: #10b981;
                        color: white;
                        padding: 14px 20px;
                        text-align: center;
                        border-radius: 12px;
                        font-weight: bold;
                        font-size: 16px;
                        margin-top: 10px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
                        cursor: pointer;
                        display: block;
                        transition: 0.3s;
                        border: 1px solid #059669;">
                        💎 Ενεργοποίηση Pro (9.99€/μήνα)
                    </div>
                </a>
                <p style="text-align:center; font-size:12px; color:gray; margin-top:6px;">Ασφαλής πληρωμή μέσω Stripe Checkout</p>
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
                if onboard_name.strip() == "":
                    st.error("💡 Σε παρακαλώ, συμπλήρωσε το όνομα του παιδιού για να μπορεί ο Φοίβος να του απευθύνεται σωστά!")
                else:
                    st.session_state.user["name"] = onboard_name
                    st.session_state.user["age"] = onboard_age
                    st.session_state.user["onboarded"] = True
                    SessionManager.save_to_db(st.session_state.user) # SQL Save
                    st.success(f"🎉 Πανέτοιμα! Το προφίλ του/της {onboard_name} δημιουργήθηκε!")
                    time.sleep(1.5)
                    st.session_state.page = "hub"
                    st.rerun()

    # --- PAGE: WORLD HUB (UPGRADED UI) ---
    elif st.session_state.page == "hub":
        render_hud()
        st.title("🗺️ Διάλεξε τον Κόσμο σου")
        
        if SessionManager.check_screen_time():
            st.error("⏰ **Screen Time Guard:** Συμπληρώθηκε το ημερήσιο όριο χρήσης για το Free Plan! Ο Φοίβος πήγε να ξεκουραστεί. Αναβάθμισε σε Pro για απεριόριστο χρόνο.")
            return

        st.markdown("""
            <div style="background: linear-gradient(135deg, #6366f1, #4f46e5); color:white; padding:15px; border-radius:12px; margin-bottom:20px;">
                🎯 <b>Vocabulary Challenge:</b> Χρησιμοποίησε τη λέξη <b>"αστέρι"</b> στη συζήτηση με τον Φοίβο και κέρδισε <b>+50 XP Bonus!</b>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (name, data) in enumerate(AppConfig.THEMES.items()):
            with cols[i]:
                st.markdown(f"""
                    <div style='background: {data["bg"]}; padding:30px; border-radius:20px; border: 2px solid {data["color"]}; text-align:center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);'>
                        <h2 style='color: white; margin-bottom:15px;'>{data['icon']} {name}</h2>
                        <p style='color: #cbd5e1; font-size:14px; min-height:40px;'>Έτοιμος για περιπεριπέτεια;</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Είσοδος: {name}", key=name, use_container_width=True):
                    st.session_state.current_world = name
                    st.session_state.page = "adventure"
                    st.rerun()

    # --- PAGE: ADVENTURE (THE HEART + AFFECTIVE AVATAR) ---
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
        
        # ΝΕΟ: HCI Mood-Aware Avatar του Φοίβου βασισμένο στο Affective Core
        current_mood = st.session_state.user["mood"].lower()
        avatar_icon = "🧸✨"
        avatar_style = "border: 2px solid #10b981; background: rgba(16, 185, 129, 0.1);"
        if "κουρασμένος" in current_mood or "λυπημένος" in current_mood:
            avatar_icon = "🧸💤"
            avatar_style = "border: 2px solid #3b82f6; background: rgba(59, 130, 246, 0.1);"
        
        st.markdown(f"""
            <div style="padding: 15px; border-radius: 15px; {avatar_style} margin-bottom: 20px; display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 35px;">{avatar_icon}</div>
                <div>
                    <b style="color: white; font-size: 16px;">Ψηφιακός Μέντορας Φοίβος</b><br>
                    <span style="color: #cbd5e1; font-size: 14px;">Κατάσταση: Ανιχνεύω τη διάθεσή σου ως <i><b>{st.session_state.user['mood']}</b></i>. Είμαι έτοιμος να σε ακούσω!</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.user["history"]:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        user_speech = VoiceEngine.listen()
        if user_speech:
            st.session_state.user["history"].append({"role": "user", "content": user_speech})
            st.session_state.user["usage_count"] += 1 
            
            if "αστέρι" in user_speech.lower() and not st.session_state.user["vocab_bonus"]:
                st.session_state.user["vocab_bonus"] = True
                SessionManager.add_xp(50)
                st.toast("🎯 Bonus +50 XP! Χρησιμοποίησες τη Λέξη της Ημέρας!", icon="✨")

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

    # --- PAGE: PARENT DASHBOARD & COGNITIVE RADAR ---
    elif st.session_state.page == "parent_dashboard":
        st.title("📊 Dashboard Γονέα & Analytics")
        st.subheader(f"Συμπεράσματα και Πρόοδος για τον/την: {st.session_state.user['name']}")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Συνολικά XP", f"{st.session_state.user['xp']} XP", "20 XP σήμερα")
        with col_m2:
            st.metric("Τρέχον Επίπεδο", f"Level {st.session_state.user['level']}")
            
        st.write("### 🏅 Ψηφιακά Παράσημα (Achievements)")
        badges_col = st.columns(3)
        with badges_col[0]:
            st.success("🌱 **Πρώτο Βήμα**\n(Ξεκλείδωσε με την εγγραφή)")
        with badges_col[1]:
            if st.session_state.user["xp"] >= 60:
                st.success("🏝️ **Εξερευνητής**\n(Ξεκλείδωσε με 60+ XP)")
            else:
                st.code("🔒 Κλειδωμένο\n(Χρειάζεται 60 XP)")
        with badges_col[2]:
            if st.session_state.user["level"] >= 2:
                st.success("👑 **Master του Λόγου**\n(Ξεκλείδωσε στο Level 2)")
            else:
                st.code("🔒 Κλειδωμένο\n(Χρειάζεται Level 2)")

        st.write("---")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.write("### 📊 Παιδαγωγικό Προφίλ Δεξιοτήτων")
            categories = ['Λεξιλόγιο', 'Κριτική Σκέψη', 'Συναισθηματική Αυτορύθμιση', 'Ταχύτητα Απόκρισης', 'Κοινωνική Ενσυναίσθηση']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[4, 3, 5, 4, 4],
                theta=categories,
                fill='toself',
                marker=dict(color='#10b981')
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_chart2:
            st.write("### 📈 Καμπύλη Μάθησης (XP Progression)")
            fig_xp = go.Figure(data=go.Scatter(y=st.session_state.user["xp_history"], mode='lines+markers', line=dict(color='#10b981', width=3)))
            fig_xp.update_layout(title="Εξέλιξη Πόντων Εμπειρίας", xaxis_title="Αλληλεπιδράσεις", yaxis_title="XP")
            st.plotly_chart(fig_xp, use_container_width=True)
        
        st.write("### 🎭 Συναισθηματικό Ιστορικό (Mood Tracker)")
        st.info(f"Η τελευταία καταγεγραμμένη διάθεση του παιδιού είναι: **{st.session_state.user['mood']}**")

    # --- PAGE: EDUCATOR PORTAL ---
    elif st.session_state.page == "educator_portal":
        st.title("🏫 Educator Portal (Στατιστικά Τάξης)")
        st.subheader("Συγκεντρωτική εικόνα για τους συνεργαζόμενους Παιδικούς Σταθμούς / Νηπιαγωγεία")
        
        st.info("💡 Αυτό το Dashboard εμφανίζεται στους εκπαιδευτικούς φορείς που αγοράζουν το B2B Enterprise πακέτο μας.")
        
        class_data = pd.DataFrame({
            'Μαθητής': ['Νικόλας', 'Μαρία', 'Γιώργος', 'Ελένη', 'Δημήτρης'],
            'Εβδομαδιαία XP': [120, 240, 90, 310, 150],
            'Κυρίαρχο Συναίσθημα': ['Χαρούμενος', 'Ενθουσιώδης', 'Κουρασμένος', 'Χαρούμενος', 'Ήρεμος']
        })
        
        st.write("### 📈 Πρόοδος Μαθητών Τμήματος Α1")
        st.table(class_data)
        
        fig_class = go.Figure([go.Bar(x=class_data['Μαθητής'], y=class_data['Εβδομαδιαία XP'], marker_color='#6366f1')])
        fig_class.update_layout(title="Σύγκριση XP Τάξης", xaxis_title="Μαθητές", yaxis_title="Συνολικά XP")
        st.plotly_chart(fig_class, use_container_width=True)

    # --- PAGE: PROFILE SETTINGS ---
    elif st.session_state.page == "profile_settings":
        st.title("⚙️ Ρυθμίσεις Προφίλ")
        st.write("Διαχείριση στοιχείων του μικρού μαθητή.")
        
        new_name = st.text_input("Όνομα Παιδιού:", value=st.session_state.user["name"])
        new_age = st.number_input("Ηλικία Παιδιού:", min_value=3, max_value=12, value=st.session_state.user["age"])
        
        if st.button("💾 Αποθήκευση Αλλαγών", use_container_width=True):
            st.session_state.user["name"] = new_name
            st.session_state.user["age"] = new_age
            SessionManager.save_to_db(st.session_state.user) # SQL Update
            st.success("Το προφίλ ενημερώθηκε επιτυχώς στη μόνιμη βάση!")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()
