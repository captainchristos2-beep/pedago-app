import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import random

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(
    page_title="PedaGO Ultra Pro v2.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS for High-End UX
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Outfit:wght@300;600;800&display=swap');
    
    :root {
        --primary: #0ea5e9;
        --secondary: #6366f1;
        --accent: #f59e0b;
        --bg: #f8fafc;
    }

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: var(--bg); }

    /* Custom Containers */
    .main-card {
        background: white;
        border-radius: 35px;
        padding: 3rem;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        text-align: center;
        margin-top: 2rem;
    }

    .hero-text {
        font-family: 'Comfortaa', cursive;
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    /* Achievement & XP System Styling */
    .badge-container { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 15px 0; }
    .xp-pill {
        background: #f0f9ff;
        color: #0369a1;
        padding: 5px 20px;
        border-radius: 50px;
        font-weight: 700;
        border: 1px solid #bae6fd;
    }

    /* Chat Styling */
    .stChatMessage {
        border-radius: 25px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        transition: transform 0.2s;
    }
    .stChatMessage:hover { transform: scale(1.01); }

    /* Buttons */
    .stButton>button {
        border-radius: 20px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(14, 165, 233, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE LOGIC & UTILITIES ---
if "app_state" not in st.session_state: st.session_state.app_state = "gate"
if "xp" not in st.session_state: st.session_state.xp = 0
if "lvl" not in st.session_state: st.session_state.lvl = 1
if "badges" not in st.session_state: st.session_state.badges = []
if "history" not in st.session_state: st.session_state.history = []
if "goal" not in st.session_state: st.session_state.goal = ""

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='el')
        b = io.BytesIO()
        tts.write_to_fp(b)
        b.seek(0)
        encoded = base64.b64encode(b.read()).decode()
        html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{encoded}" type="audio/mp3"></audio>'
        st.markdown(html, unsafe_allow_html=True)
    except Exception: pass

def check_achievements():
    if st.session_state.xp >= 100 and "🌟 Αστέρι" not in st.session_state.badges:
        st.session_state.badges.append("🌟 Αστέρι")
    if st.session_state.xp >= 300 and "🧙 Μάγος" not in st.session_state.badges:
        st.session_state.badges.append("🧙 Μάγος")
    if len(st.session_state.history) > 10 and "🗣️ Πολυλογάς" not in st.session_state.badges:
        st.session_state.badges.append("🗣️ Πολυλογάς")

# --- 3. UI SCREENS ---

# SCREEN 1: TEACHER GATE
if st.session_state.app_state == "gate":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-text'>PedaGO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.3rem; color:#64748b;'>Ολοκληρωμένο Σύστημα Παιδαγωγικής Αλληλεπίδρασης</p>", unsafe_allow_html=True)
    
    st.markdown("<br><div style='max-width:500px; margin:auto;'>", unsafe_allow_html=True)
    with st.form("init_form"):
        st.subheader("⚙️ Ρυθμίσεις Εκπαιδευτικού")
        topic = st.text_input("Θέμα Δραστηριότητας:", placeholder="π.χ. Προστασία του περιβάλλοντος")
        persona = st.selectbox("Προσωπικότητα Φοίβου:", ["Ενθουσιώδης", "Ήρεμος", "Εξερευνητής"])
        mode = st.radio("Στόχος:", ["Ελεύθερη Συζήτηση", "Επίλυση Προβλήματος", "Εκμάθηση Λεξιλογίου"])
        
        start = st.form_submit_button("🚀 ΕΝΑΡΞΗ ΣΥΝΕΔΡΙΑΣ")
        if start:
            st.session_state.goal = topic
            sys_prompt = f"Είσαι ο Φοίβος, {persona} AI βοηθός. Στόχος: {topic} μέσω {mode}. Μίλα απλά σε παιδιά, κάνε 1 ερώτηση τη φορά, χρησιμοποίησε emojis. Ποτέ μην δίνεις έτοιμη απάντηση."
            st.session_state.history = [{"role": "system", "content": sys_prompt}]
            st.session_state.app_state = "active"
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# SCREEN 2: ACTIVE INTERACTION
elif st.session_state.app_state == "active":
    # Sidebar Dashboard
    with st.sidebar:
        st.title("🏆 Πρόοδος")
        st.metric("Επίπεδο", st.session_state.lvl)
        st.write(f"XP: {st.session_state.xp}")
        st.progress(min((st.session_state.xp % 100) / 100, 1.0))
        st.markdown("---")
        st.subheader("🏅 Μετάλλια")
        for b in st.session_state.badges:
            st.markdown(f"<span class='xp-pill'>{b}</span>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔒 Κλείσιμο Μαθήματος"):
            st.session_state.app_state = "analytics"
            st.rerun()

    # Main Chat Area
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        st.markdown("<h2 style='text-align:center; font-family:Comfortaa;'>🧸 Φοίβος</h2>", unsafe_allow_html=True)
        
        # Chat History Rendering
        for m in st.session_state.history:
            if m["role"] != "system":
                avatar = "🧸" if m["role"] == "assistant" else "🧒"
                with st.chat_message(m["role"], avatar=avatar):
                    st.write(m["content"])

        # Interaction Zone
        st.markdown("<br><div style='position: sticky; bottom: 20px; background:white; padding:20px; border-radius:30px; box-shadow:0 -10px 30px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        cols = st.columns([4, 1])
        with cols[0]:
            voice_data = speech_to_text(language='el', start_prompt="🎤 Πες κάτι στον Φοίβο...", stop_prompt="✅ Τέλος", key='voice_v2')
        with cols[1]:
            if st.button("🔄 Clear"):
                st.session_state.history = [st.session_state.history[0]]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if voice_data:
            if "last_v" not in st.session_state or st.session_state.last_v != voice_data:
                st.session_state.last_v = voice_data
                st.session_state.history.append({"role": "user", "content": voice_data})
                
                # Gamification update
                st.session_state.xp += 20
                if st.session_state.xp // 100 > st.session_state.lvl - 1:
                    st.session_state.lvl += 1
                check_achievements()

                with st.chat_message("assistant", avatar="🧸"):
                    with st.spinner("💭 Ο Φοίβος σκέφτεται..."):
                        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.history)
                        reply = resp.choices[0].message.content
                        st.write(reply)
                
                st.session_state.history.append({"role": "assistant", "content": reply})
                play_audio(reply)
                st.rerun()

# SCREEN 3: ANALYTICS & REPORT
elif st.session_state.app_state == "analytics":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("📊 Παιδαγωγική Αναφορά")
    st.markdown(f"**Συνεδρία για:** {st.session_state.goal}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Συνολικά XP", st.session_state.xp)
    col2.metric("Επίπεδο που έφτασε", st.session_state.lvl)
    col3.metric("Ανταλλαγές μηνυμάτων", len(st.session_state.history) - 1)
    
    st.markdown("### 📝 Ιστορικό Δραστηριότητας")
    for msg in st.session_state.history:
        if msg["role"] != "system":
            color = "#0ea5e9" if msg["role"] == "user" else "#6366f1"
            st.markdown(f"<p style='color:{color}'><b>{msg['role'].upper()}:</b> {msg['content']}</p>", unsafe_allow_html=True)
            
    if st.button("🏠 Επιστροφή στην Αρχική"):
        st.session_state.app_state = "gate"
        st.session_state.xp = 0
        st.session_state.lvl = 1
        st.session_state.badges = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. FOOTER ---
st.markdown(
    """
    <div style='text-align: center; padding: 30px; color: #94a3b8; font-size: 0.85rem;'>
        <b>PedaGO Ultra Pro v2.0</b> | 2026 Edition | Advanced Pedagogy AI<br>
        Designed for Excellence | Version 2.0.1
    </div>
    """, 
    unsafe_allow_html=True
)
