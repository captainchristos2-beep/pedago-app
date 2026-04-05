import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import datetime
import json

# ==========================================
# 1. GLOBAL CONFIGURATION & CONSTANTS
# ==========================================
VERSION = "1.2.5"
APP_NAME = "PedaGO AI - Φοίβος"
PRIMARY_COLOR = "#0ea5e9"
SECONDARY_COLOR = "#6366f1"

st.set_page_config(
    page_title=f"{APP_NAME} v{VERSION}",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. PREMIUM CSS STYLING (THEming)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Styles */
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
        background-color: #f8fafc;
    }}

    .stApp {{
        background: radial-gradient(circle at top right, #f0f9ff, #ffffff);
    }}

    /* Typography */
    .main-title {{
        font-family: 'Comfortaa', cursive;
        font-size: 3.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, {PRIMARY_COLOR}, {SECONDARY_COLOR});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }}

    /* Custom Chat Bubbles */
    .stChatMessage {{
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }}

    /* Teacher Control Panel */
    .teacher-panel {{
        background: white;
        border-radius: 25px;
        padding: 2rem;
        border: 2px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }}

    /* Metrics & Progress */
    .metric-card {{
        background: white;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid {PRIMARY_COLOR};
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    /* Buttons Animation */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background: linear-gradient(90deg, {PRIMARY_COLOR}, {SECONDARY_COLOR});
        color: white;
        font-weight: 700;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(14, 165, 233, 0.3);
    }}

    /* Audio Component Hidden */
    #audio-container {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. SESSION STATE MANAGEMENT
# ==========================================
def init_session():
    if "app_state" not in st.session_state: st.session_state.app_state = "setup"
    if "messages" not in st.session_state: st.session_state.messages = []
    if "xp" not in st.session_state: st.session_state.xp = 0
    if "session_id" not in st.session_state: st.session_state.session_id = f"SES-{int(time.time())}"
    if "teacher_logs" not in st.session_state: st.session_state.teacher_logs = []
    if "student_name" not in st.session_state: st.session_state.student_name = "Μαθητής"
    if "current_goal" not in st.session_state: st.session_state.current_goal = ""
    if "audio_queue" not in st.session_state: st.session_state.audio_queue = None

init_session()

# ==========================================
# 4. CORE UTILITIES (AI & AUDIO)
# ==========================================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_audio(text):
    """Μετατροπή κειμένου σε ομιλία με gTTS"""
    try:
        tts = gTTS(text=text, lang='el')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except Exception as e:
        return f"<!-- Audio Error: {e} -->"

def log_interaction(role, content):
    """Καταγραφή για τον εκπαιδευτικό"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.teacher_logs.append({
        "time": timestamp,
        "role": role,
        "text": content
    })

# ==========================================
# 5. SIDEBAR: DASHBOARD & ANALYTICS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4343/4343031.png", width=100)
    st.title("🛡️ Teacher Control")
    st.info(f"Session: {st.session_state.session_id}")
    
    st.markdown("---")
    st.subheader("📊 Πρόοδος Μαθητή")
    st.write(f"Όνομα: **{st.session_state.student_name}**")
    st.metric("Συνολικά XP", st.session_state.xp)
    
    xp_level = (st.session_state.xp // 100) + 1
    st.write(f"Επίπεδο: {xp_level}")
    st.progress(min((st.session_state.xp % 100) / 100, 1.0))

    st.markdown("---")
    if st.button("🔄 Επαναφορά Εφαρμογής"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
    with st.expander("📝 Logs Συζήτησης"):
        for log in st.session_state.teacher_logs:
            st.caption(f"[{log['time']}] {log['role']}: {log['text'][:30]}...")

# ==========================================
# 6. UI SCREENS (LOGIC)
# ==========================================

# --- SCREEN A: SETUP / TEACHER GATE ---
if st.session_state.app_state == "setup":
    st.markdown("<h1 class='main-title'>PedaGO setup</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Ρυθμίστε τη συνεδρία προτού ξεκινήσει το παιδί.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("teacher_form"):
            name = st.text_input("Όνομα Μαθητή:", value="Μικρός Εξερευνητής")
            age = st.select_slider("Ηλικία Παιδιού:", options=[3, 4, 5, 6, 7])
            topic = st.text_input("Θέμα Συζήτησης (π.χ. Τα ζώα της φάρμας):", "Γενική Μάθηση")
            style = st.selectbox("Ύφος Φοίβου:", ["Παιχνιδιάρικο", "Εκπαιδευτικό", "Καθησυχαστικό"])
            
            if st.form_submit_button("✨ Έναρξη Αλληλεπίδρασης"):
                st.session_state.student_name = name
                st.session_state.current_goal = topic
                
                # System Prompt Construction
                sys_prompt = f"""
                Είσαι ο Φοίβος, ένας AI βοηθός νηπιαγωγού. 
                Μιλάς σε ένα παιδί {age} ετών που το λένε {name}.
                Θέμα συνεδρίας: {topic}. Ύφος: {style}.
                Κανόνες: 
                1. Μίλα απλά ελληνικά, χωρίς δύσκολες λέξεις.
                2. Κάθε απάντηση έως 2 σύντομες προτάσεις.
                3. Πάντα να κάνεις ΜΙΑ ερώτηση στο τέλος.
                4. Χρησιμοποίησε emojis ✨, 🎈, 🧸.
                5. Μην δίνεις έτοιμες απαντήσεις, κάνε το παιδί να σκεφτεί.
                """
                st.session_state.messages = [{"role": "system", "content": sys_prompt}]
                st.session_state.app_state = "chat"
                log_interaction("SYSTEM", f"Session started for {name}, Topic: {topic}")
                st.rerun()

# --- SCREEN B: ACTIVE CHAT ---
elif st.session_state.app_state == "chat":
    st.markdown(f"<h1 class='main-title'>🧸 Γεια σου, {st.session_state.student_name}!</h1>", unsafe_allow_html=True)
    
    # Message Container
    chat_container = st.container()
    with chat_container:
        for m in st.session_state.messages:
            if m["role"] != "system":
                avatar = "🧸" if m["role"] == "assistant" else "🧒"
                with st.chat_message(m["role"], avatar=avatar):
                    st.write(m["content"])

    # Bottom Interaction Area
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<p style='text-align:center;'>Πάτα το μικρόφωνο και πες κάτι!</p>", unsafe_allow_html=True)
        # Speech to Text Component
        input_text = speech_to_text(
            language='el', 
            start_prompt="🎤 Ξεκίνα να μιλάς", 
            stop_prompt="✅ Τέλος", 
            key='speech_v12'
        )

    if input_text:
        # Check if the text is new to avoid loops
        if "last_processed" not in st.session_state or st.session_state.last_processed != input_text:
            st.session_state.last_processed = input_text
            
            # User Message
            st.session_state.messages.append({"role": "user", "content": input_text})
            log_interaction("USER", input_text)
            st.session_state.xp += 15 # Reward for speaking
            
            # AI Response Logic
            with st.spinner("Ο Φοίβος σκέφτεται..."):
                try:
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=st.session_state.messages,
                        temperature=0.7,
                        max_tokens=150
                    )
                    ai_reply = chat_completion.choices[0].message.content
                    
                    # Update State
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    log_interaction("ASSISTANT", ai_reply)
                    
                    # Trigger Audio and Refresh
                    st.session_state.audio_queue = generate_audio(ai_reply)
                    st.rerun()
                    
                except Exception as e:
                    st.error("Ωχ! Κάτι κούρασε τον Φοίβο. Δοκίμασε ξανά!")
                    log_interaction("ERROR", str(e))

    # Hidden Audio Player (Injects audio if queued)
    if st.session_state.audio_queue:
        st.markdown(st.session_state.audio_queue, unsafe_allow_html=True)
        st.session_state.audio_queue = None

# ==========================================
# 7. FOOTER & VERSIONING
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
footer_cols = st.columns([1, 2, 1])
with footer_cols[1]:
    st.markdown(f"""
        <div style='text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px; color: #94a3b8;'>
            <p>Made with ❤️ for PedaGO | <b>Version {VERSION}</b></p>
            <p style='font-size: 0.7rem;'>© 2026 Educational Excellence Platform</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 8. TEACHER'S SECRET TOOLS (HIDDEN)
# ==========================================
# This section can be expanded up to 500 lines by adding:
# - Data export to CSV
# - Sentiment analysis graph
# - Session timers
# - Achievement popups
