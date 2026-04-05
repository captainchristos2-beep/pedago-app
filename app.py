import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import datetime
import pandas as pd
import plotly.express as px

# =================================================================
# 1. ΠΡΟΗΓΜΕΝΕΣ ΡΥΘΜΙΣΕΙΣ & ΘΕΜΑΤΟΛΟΓΙΑ (UI/UX)
# =================================================================
st.set_page_config(
    page_title="PedaGO AI Elite v1.2",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS για ανώτερη αισθητική (Premium Look)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;700&family=Outfit:wght@300;500;800&display=swap');

    :root {
        --primary: #0ea5e9;
        --secondary: #6366f1;
        --soft-bg: #f8fafc;
    }

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%); }

    /* Glassmorphism Cards */
    .premium-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 30px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
    }

    .main-title {
        font-family: 'Comfortaa', cursive;
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }

    /* Custom Chat Bubbles */
    .stChatMessage {
        border-radius: 20px !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    }

    /* Animation for Mic */
    .mic-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        background: white;
        border-radius: 50px;
        box-shadow: 0 10px 25px rgba(14, 165, 233, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. ΔΙΑΧΕΙΡΙΣΗ ΚΑΤΑΣΤΑΣΗΣ (SESSION STATE)
# =================================================================
if "app_state" not in st.session_state: st.session_state.app_state = "setup"
if "messages" not in st.session_state: st.session_state.messages = []
if "xp" not in st.session_state: st.session_state.xp = 0
if "logs" not in st.session_state: st.session_state.logs = []
if "metrics" not in st.session_state: st.session_state.metrics = {"user_words": 0, "ai_words": 0, "turns": 0}
if "audio_html" not in st.session_state: st.session_state.audio_html = ""

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# =================================================================
# 3. ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ (AUDIO & ANALYTICS)
# =================================================================
def get_tts_html(text):
    try:
        tts = gTTS(text=text, lang='el')
        b = io.BytesIO()
        tts.write_to_fp(b)
        b.seek(0)
        encoded = base64.b64encode(b.read()).decode()
        return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{encoded}" type="audio/mp3"></audio>'
    except: return ""

def update_metrics(text, role):
    words = len(text.split())
    if role == "user":
        st.session_state.metrics["user_words"] += words
        st.session_state.metrics["turns"] += 1
    else:
        st.session_state.metrics["ai_words"] += words

# =================================================================
# 4. SIDEBAR: DASHBOARD ΕΚΠΑΙΔΕΥΤΙΚΟΥ
# =================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3884/3884851.png", width=80)
    st.title("🛡️ Dashboard v1.2")
    
    st.markdown("### 📊 Στατιστικά Συνεδρίας")
    st.metric("Συνολικά XP", st.session_state.xp)
    st.metric("Ανταλλαγές", st.session_state.metrics["turns"])
    
    # Γράφημα Συμμετοχής
    if st.session_state.metrics["turns"] > 0:
        data = pd.DataFrame({
            "Πλευρά": ["Παιδί", "Φοίβος"],
            "Λέξεις": [st.session_state.metrics["user_words"], st.session_state.metrics["ai_words"]]
        })
        fig = px.pie(data, values='Λέξεις', names='Πλευρά', hole=.4, color_discrete_sequence=['#0ea5e9', '#6366f1'])
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=150)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Καθαρισμός & Έξοδος"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

# =================================================================
# 5. ΚΥΡΙΕΣ ΟΘΟΝΕΣ (LOGIC)
# =================================================================

# --- ΟΘΟΝΗ Α: ΡΥΘΜΙΣΗ (TEACHER GATE) ---
if st.session_state.app_state == "setup":
    st.markdown("<h1 class='main-title'>PedaGO Elite</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ Ρυθμίσεις Εκπαιδευτικού")
        with st.form("settings_form"):
            child_name = st.text_input("Όνομα Παιδιού:", "Μικρός Εξερευνητής")
            topic = st.text_input("Θέμα:", "Τα ζώα της θάλασσας")
            focus = st.multiselect("Εστίαση:", ["Λεξιλόγιο", "Κριτική Σκέψη", "Ενσυναίσθηση"], ["Λεξιλόγιο"])
            
            if st.form_submit_button("✨ Έναρξη Μαγείας"):
                st.session_state.app_state = "active"
                sys_prompt = f"Είσαι ο Φοίβος, AI βοηθός νηπιαγωγού. Μιλάς στον/στην {child_name}. Θέμα: {topic}. Εστίαση: {focus}. Μίλα απλά, κάνε ερωτήσεις, χρησιμοποίησε emojis. Ποτέ μην δίνεις έτοιμη απάντηση."
                st.session_state.messages = [{"role": "system", "content": sys_prompt}]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- ΟΘΟΝΗ Β: ΑΛΛΗΛΕΠΙΔΡΑΣΗ (CHILD MODE) ---
elif st.session_state.app_state == "active":
    st.markdown(f"<h1 class='main-title'>🧸 Γεια σου!</h1>", unsafe_allow_html=True)
    
    # Εμφάνιση Μηνυμάτων
    for m in st.session_state.messages:
        if m["role"] != "system":
            avatar = "🧸" if m["role"] == "assistant" else "🧒"
            with st.chat_message(m["role"], avatar=avatar):
                st.write(m["content"])

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Ζώνη Μικροφώνου
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div class='mic-container'>", unsafe_allow_html=True)
        voice_text = speech_to_text(language='el', start_prompt="🎤 Πάτα και Μίλα", stop_prompt="✅ Τέλος", key='voice_input_v12')
        st.markdown("</div>", unsafe_allow_html=True)

    if voice_text:
        if "last_v" not in st.session_state or st.session_state.last_v != voice_text:
            st.session_state.last_v = voice_text
            st.session_state.messages.append({"role": "user", "content": voice_text})
            update_metrics(voice_text, "user")
            st.session_state.xp += 15
            
            with st.chat_message("assistant", avatar="🧸"):
                with st.spinner("Ο Φοίβος σε ακούει..."):
                    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages)
                    reply = resp.choices[0].message.content
                    st.write(reply)
                    update_metrics(reply, "assistant")
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.session_state.audio_html = get_tts_html(reply)
                    st.rerun()

    # Audio Playback
    if st.session_state.audio_html:
        st.markdown(st.session_state.audio_html, unsafe_allow_html=True)
        st.session_state.audio_html = ""

# =================================================================
# 6. FOOTER
# =================================================================
st.markdown(f"<div style='text-align:center; color:#94a3b8; padding:50px;'>PedaGO AI | Version 1.2.9 Elite | © 2026</div>", unsafe_allow_html=True)
