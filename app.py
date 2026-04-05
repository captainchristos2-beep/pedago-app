import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time

# 1. Configuration & Premium Theme
st.set_page_config(page_title="PedaGO Pro v1.3", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Comfortaa:wght@700&display=swap');

    /* Background & Smooth Scrolling */
    .stApp {
        background: radial-gradient(circle at top left, #f8fafc, #e2e8f0);
    }

    /* Duolingo-style XP Bar */
    .xp-bar-container {
        width: 100%;
        background-color: #e2e8f0;
        border-radius: 10px;
        margin: 10px 0;
    }
    .xp-bar-fill {
        height: 12px;
        background: linear-gradient(90deg, #4ade80, #22c55e);
        border-radius: 10px;
        transition: width 0.5s ease-in-out;
    }

    /* MagicSchool Style Cards */
    .stChatMessage {
        border: none !important;
        background: white !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
        border-radius: 20px !important;
    }

    .main-title {
        font-family: 'Comfortaa', cursive;
        background: linear-gradient(90deg, #0284c7, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        text-align: center;
        font-weight: 700;
    }

    /* Level Badge */
    .level-badge {
        background: #fef08a;
        color: #854d0e;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. State Management (Gamification)
if "xp" not in st.session_state:
    st.session_state.xp = 10
if "level" not in st.session_state:
    st.session_state.level = 1
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": """Είσαι ο Φοίβος v1.3, ο πιο προηγμένος AI Παιδαγωγός. 
        Συνδυάζεις τη διασκέδαση του Duolingo με την ευφυΐα του MagicSchool.
        ΚΑΝΟΝΕΣ:
        1. ΠΟΤΕ μη δίνεις έτοιμη απάντηση. Αν το παιδί ρωτήσει 'τι είναι το 2+2', πες 'Αν έχεις δύο μήλα και σου δώσω άλλα δύο, πόσα θα έχεις στην τσάντα σου;'.
        2. Μίλα με ενθουσιασμό αλλά και βάθος.
        3. Επιβράβευσε την προσπάθεια ('Πολύ καλή σκέψη!', 'Είσαι πανέξυπνος!').
        4. Κράτα τις απαντήσεις μικρές (έως 2 προτάσεις)."""
    }]

# 3. AI & Audio Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='el')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except: pass

# 4. Sidebar (Dashboard)
with st.sidebar:
    st.markdown(f"### 🏆 Επίπεδο {st.session_state.level}")
    xp_percentage = (st.session_state.xp % 100)
    st.markdown(f"**XP: {st.session_state.xp}**")
    st.markdown(f"""<div class='xp-bar-container'><div class='xp-bar-fill' style='width: {xp_percentage}%'></div></div>""", unsafe_allow_html=True)
    st.write("---")
    st.success("✨ Magic Mode: Ενεργό")
    if st.button("🔄 Επαναφορά"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.xp = 10
        st.rerun()

# 5. Main UI
st.markdown("<h1 class='main-title'>PedaGO Pro</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center'><span class='level-badge'>v1.3 ADVANCED AI</span></div>", unsafe_allow_html=True)

# Chat Display
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🧸" if message["role"]=="assistant" else "🧒"):
            st.write(message["content"])

# 6. Interaction Zone
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.markdown("<div style='background: white; border-radius: 50px; padding: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    text = speech_to_text(language='el', start_prompt="🌟 Μίλησε στον Φοίβο", stop_prompt="✅ Τέλος", key='pro_mic')
    st.markdown("</div>", unsafe_allow_html=True)

if text:
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        st.session_state.messages.append({"role": "user", "content": text})
        
        # XP Gain logic
        st.session_state.xp += 15
        if st.session_state.xp % 100 == 0: st.session_state.level += 1

        with st.chat_message("assistant", avatar="🧸"):
            with st.spinner("🪄 Ο Φοίβος κάνει μαγικά..."):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.8
                )
                ai_reply = completion.choices[0].message.content
                st.write(ai_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        speak_text(ai_reply)
        st.rerun()

# 7. Professional Footer
st.markdown(
    """
    <div style='margin-top: 100px; border-top: 1px solid #e2e8f0; padding-top: 20px;'>
        <table style='width:100%; border:none;'>
            <tr>
                <td style='color: #94a3b8; font-size: 0.8rem;'>© 2026 PedaGO International</td>
                <td style='text-align:right; color: #94a3b8; font-size: 0.8rem;'>Made with ❤️ for PedaGO | Version 1.3</td>
            </tr>
        </table>
    </div>
    """, 
    unsafe_allow_html=True
)
