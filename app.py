import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time
import pandas as pd

# Safe Import για το Plotly για αποφυγή σφαλμάτων αν λείπει η βιβλιοθήκη
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. Βασικές Ρυθμίσεις Σελίδας
st.set_page_config(page_title="PedaGO AI v1.2.11", page_icon="🧸", layout="wide")

# Custom CSS για Μοντέρνα & Φιλική Εμφάνιση
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Outfit:wght@400;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Outfit', sans-serif; 
    }
    
    .stApp { 
        background: #f8fafc; 
    }
    
    .main-title {
        font-family: 'Comfortaa', cursive;
        font-size: 3.5rem;
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .setup-box {
        background: white;
        padding: 35px;
        border-radius: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }

    /* Βελτίωση των Chat Bubbles */
    .stChatMessage {
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Διαχείριση Κατάστασης (Session State)
if "state" not in st.session_state: st.session_state.state = "setup"
if "chat" not in st.session_state: st.session_state.chat = []
if "xp" not in st.session_state: st.session_state.xp = 0
if "audio" not in st.session_state: st.session_state.audio = ""
if "stats" not in st.session_state: st.session_state.stats = {"user": 0, "ai": 0}

# 3. Σύνδεση με Groq API
def get_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("⚠️ Το API Key δεν βρέθηκε στα Secrets του Streamlit!")
        return None

client = get_groq_client()

# 4. Sidebar: Πίνακας Ελέγχου & Στατιστικά
with st.sidebar:
    st.title("📊 Πρόοδος")
    st.metric("Πόντοι XP", st.session_state.xp)
    
    # Εμφάνιση γραφήματος μόνο αν υπάρχει η βιβλιοθήκη και δεδομένα
    if HAS_PLOTLY and (st.session_state.stats["user"] + st.session_state.stats["ai"] > 0):
        df = pd.DataFrame({
            "Ποιος": ["Παιδί", "Φοίβος"],
            "Λέξεις": [st.session_state.stats["user"], st.session_state.stats["ai"]]
        })
        fig = px.pie(df, values='Λέξεις', names='Ποιος', hole=0.4, 
                     color_discrete_sequence=['#0ea5e9', '#6366f1'])
        fig.update_layout(showlegend=False, height=220, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    if st.button("🔄 Νέα Συνεδρία"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# 5. Ροή Εφαρμογής (Screens)

# --- ΟΘΟΝΗ Α: ΡΥΘΜΙΣΕΙΣ (SETUP) ---
if st.session_state.state == "setup":
    st.markdown("<h1 class='main-title'>PedaGO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='setup-box'>", unsafe_allow_html=True)
        st.subheader("🛠️ Ρυθμίσεις Εκπαιδευτικού")
        with st.form("gate_form"):
            kid_name = st.text_input("Όνομα Παιδιού:", "Μαθητής")
            session_topic = st.text_input("Θέμα Συζήτησης:", "Τα ζώα του δάσους")
            
            if st.form_submit_button("✨ ΕΝΑΡΞΗ"):
                # Αρχικοποίηση του AI με τις οδηγίες του δασκάλου
                st.session_state.chat = [{
                    "role": "system", 
                    "content": f"Είσαι ο Φοίβος, ένας γλυκός βοηθός νηπιαγωγού. Μιλάς στον {kid_name} για το θέμα: {session_topic}. Μίλα απλά, χρησιμοποίησε emojis και κάνε πάντα μια ερώτηση στο τέλος. Μην δίνεις έτοιμες απαντήσεις."
                }]
                st.session_state.state = "active"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- ΟΘΟΝΗ Β: ΑΛΛΗΛΕΠΙΔΡΑΣΗ (CHAT) ---
elif st.session_state.state == "active":
    st.markdown("<h1 class='main-title'>🧸 Φοίβος</h1>", unsafe_allow_html=True)
    
    # Προβολή Ιστορικού
    for m in st.session_state.chat:
        if m["role"] != "system":
            avatar = "🧸" if m["role"] == "assistant" else "🧒"
            with st.chat_message(m["role"], avatar=avatar):
                st.write(m["content"])

    st.write("---")
    
    # Περιοχή Μικροφώνου
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        voice_input = speech_to_text(
            language='el', 
            start_prompt="🎤 Πάτα & Μίλησε", 
            stop_prompt="✅ Τέλος", 
            key='mic_v12_final'
        )

    if voice_input:
        # Αποφυγή επανάληψης του ίδιου μηνύματος
        if "last_v" not in st.session_state or st.session_state.last_v != voice_input:
            st.session_state.last_v = voice_input
            st.session_state.chat.append({"role": "user", "content": voice_input})
            st.session_state.stats["user"] += len(voice_input.split())
            st.session_state.xp += 10
            
            if client:
                with st.spinner("Ο Φοίβος ακούει..."):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile", 
                            messages=st.session_state.chat
                        )
                        reply_text = response.choices[0].message.content
                        st.session_state.chat.append({"role": "assistant", "content": reply_text})
                        st.session_state.stats["ai"] += len(reply_text.split())
                        
                        # Παραγωγή Ήχου (Text-to-Speech)
                        tts = gTTS(text=reply_text, lang='el')
                        audio_bio = io.BytesIO()
                        tts.write_to_fp(audio_bio)
                        audio_bio.seek(0)
                        audio_b64 = base64.b64encode(audio_bio.read()).decode()
                        st.session_state.audio = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Σφάλμα AI: {e}")

    # Αναπαραγωγή ήχου αν υπάρχει στην ουρά
    if st.session_state.audio:
        st.markdown(st.session_state.audio, unsafe_allow_html=True)
        st.session_state.audio = ""

# Footer
st.markdown("<p style='text-align:center; color:#94a3b8; margin-top:50px;'>Version 1.2.11 | PedaGO © 2026</p>", unsafe_allow_html=True)
