import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import pandas as pd

# Safe Import για το Plotly
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. Βασικές Ρυθμίσεις
st.set_page_config(page_title="PedaGO AI v1.2.11", page_icon="🧸", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Outfit:wght@400;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: #f8fafc; }
    .main-title {
        font-family: 'Comfortaa', cursive;
        font-size: 3.5rem;
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .setup-box {
        background: white;
        padding: 30px;
        border-radius: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State
if "state" not in st.session_state: st.session_state.state = "setup"
if "chat" not in st.session_state: st.session_state.chat = []
if "xp" not in st.session_state: st.session_state.xp = 0
if "audio" not in st.session_state: st.session_state.audio = ""
if "stats" not in st.session_state: st.session_state.stats = {"user": 0, "ai": 0}

# 3. Groq Client
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("⚠️ Πρόβλημα με το API Key στα Secrets!")
        return None

client = get_client()

# 4. Sidebar Dashboard
with st.sidebar:
    st.title("📊 Πρόοδος")
    st.metric("Πόντοι XP", st.session_state.xp)
    
    if HAS_PLOTLY and (st.session_state.stats["user"] + st.session_state.stats["ai"] > 0):
        df = pd.DataFrame({
            "Ποιος": ["Παιδί", "Φοίβος"],
            "Λέξεις": [st.session_state.stats["user"], st.session_state.stats["ai"]]
        })
        fig = px.pie(df, values='Λέξεις', names='Ποιος', hole=0.4, color_discrete_sequence=['#0ea5e9', '#6366f1'])
        fig.update_layout(showlegend=False, height=200, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    elif not HAS_PLOTLY:
        st.warning("Το Plotly δεν είναι εγκατεστημένο (requirements.txt)")

    st.write("---")
    if st.button("🔄 Restart"):
        for k in st.session_state.keys(): del st.session_state[k]
        st.rerun()

# 5. Ροή Εφαρμογής
if st.session_state.state == "setup":
    st.markdown("<h1 class='main-title'>PedaGO Elite</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='setup-box'>", unsafe_allow_html=True)
        st.subheader("🛠️ Ρυθμίσεις")
        with st.form("gate"):
            kid = st.text_input("Όνομα:", "Μαθητής")
            topic = st.text_input("Θέμα:", "Ζώα")
            if st.form_submit_button("✨ ΕΝΑΡΞΗ"):
                st.session_state.chat = [{"role": "system", "content": f"Είσαι ο Φοίβος. Μιλάς στον {kid} για {topic}. Απλά ελληνικά, emojis, ερωτήσεις."}]
                st.session_state.state = "active"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.state == "active":
    st.markdown("<h1 class='main-title'>🧸 Φοίβος</h1>", unsafe_allow_html=True)
    
    for m in st.session_state.chat:
        if m["role"] != "system":
            with st.chat_message(m["role"], avatar="🧸" if m["role"]=="assistant" else "🧒"):
                st.write(m["content"])

    st.write("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        voice = speech_to_text(language='el', start_prompt="🎤 Πάτα & Μίλησε", stop_prompt="✅ Τέλος", key='mic_v11')

    if voice:
        if "last_v" not in st.session_state or st.session_state.last_v != voice:
            st.session_state.last_v = voice
            st.session_state.chat.append({"role": "user", "content": voice})
            st.session_state.stats["user"] += len(voice.split())
            st.session_state.xp += 10
            
            if client:
                with st.spinner("Σκέφτομαι..."):
                    r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.chat)
                    rep = r.choices[0].message.content
                    st.session_state.chat.append({"role": "assistant", "content": rep})
                    st.session_state.stats["ai"] += len(rep.split())
                    
                    # Ήχος
                    tts = gTTS(text=rep, lang='el')
                    b = io.BytesIO()
                    tts.write_to_fp(b)
                    b.seek(0)
                    b64 = base64.b64encode(b.read()).decode()
                    st.session_state.audio = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                    st.rerun()

    if st.session_state.audio:
        st.markdown(st.session_state.audio, unsafe_allow_html=True)
        st.session_state.audio = ""

st.markdown("<p style='text-align:center; color:#94a3b8; margin-top:50px;'>v1.2.11 | PedaGO © 2026</p>", unsafe_allow_html=True)
