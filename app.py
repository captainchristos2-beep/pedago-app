import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time

# 1. Βασική Ρύθμιση
st.set_page_config(page_title="PedaGO AI v1.2", page_icon="🧸", layout="centered")

# 2. Επαγγελματικό UI με Custom CSS (Premium Look)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Comfortaa', cursive;
    }

    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }

    /* Φούσκες μηνυμάτων τύπου iOS/WhatsApp */
    .stChatMessage {
        border-radius: 20px !important;
        margin-bottom: 15px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }

    /* Ο τίτλος της εφαρμογής */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: #0284c7;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }

    /* Footer στυλ */
    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 50px;
        padding: 20px;
    }

    /* Animation για το μικρόφωνο */
    .mic-section {
        background: white;
        border-radius: 30px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid #e0f2fe;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Σύνδεση με Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def speak_text(text):
    """Εξελιγμένη μετατροπή κειμένου σε ήχο"""
    tts = gTTS(text=text, lang='el')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    audio_html = f"""
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# 4. Μνήμη & Σύστημα (v1.2 Logic)
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": """Είσαι ο Φοίβος, ο πιο εξελιγμένος AI βοηθός νηπιαγωγού στον κόσμο. 
        - Το ύφος σου είναι εξαιρετικά στοργικό, ενθουσιώδες και παιδαγωγικό.
        - Μίλα απλά αλλά ενθάρρυνε την κριτική σκέψη.
        - Χρησιμοποίησε emojis ✨, 🌈, 🍎, 🎨.
        - Κάθε απάντηση πρέπει να είναι έως 2 προτάσεις και να τελειώνει με μια ερώτηση ανοιχτού τύπου."""
    }]

# 5. Κύριο Περιεχόμενο
st.markdown("<h1 class='main-header'>🧸 Φοίβος</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #0ea5e9; font-weight: 500;'>Η έξυπνη παρέα σου για μάθηση!</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3048/3048122.png", width=100) # Εικονίδιο αν δεν έχεις το foivos_robot
    st.title("PedaGO Dashboard")
    st.markdown("---")
    if st.button("🗑️ Νέα Συζήτηση"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    st.caption("Version: 1.2 Premium")

# Display Messages
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🚀" if message["role"] == "user" else "🧸"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

# 6. Interaction Zone (Το Μικρόφωνο)
st.markdown("<br>", unsafe_allow_html=True)
with st.container():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("<div class='mic-section'>", unsafe_allow_html=True)
        text = speech_to_text(
            language='el', 
            start_prompt="🎤 Πάτα & Μίλησε στον Φοίβο", 
            stop_prompt="🛑 Σταμάτα", 
            key='foivos_v1_2'
        )
        st.markdown("</div>", unsafe_allow_html=True)

if text:
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        st.session_state.messages.append({"role": "user", "content": text})
        
        with st.chat_message("assistant", avatar="🧸"):
            message_placeholder = st.empty()
            with st.spinner("Ο Φοίβος ετοιμάζει την απάντηση..."):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.8
                )
                ai_reply = completion.choices[0].message.content
                message_placeholder.write(ai_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        speak_text(ai_reply)
        time.sleep(1) # Μικρή καθυστέρηση
