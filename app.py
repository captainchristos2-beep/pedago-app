import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI - Φοίβος", page_icon="🧸", layout="centered")

# Custom CSS για παιδική εμφάνιση
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #f0f8ff, #ffffff); }
    h1 { color: #1e88e5; font-family: 'Comic Sans MS', cursive, sans-serif; text-align: center;}
    .chat-bubble { background-color: #ffffff; border-radius: 20px; padding: 15px; border: 2px solid #64b5f6; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Σύνδεση με Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def speak_text(text):
    tts = gTTS(text=text, lang='el')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# 3. Μνήμη
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Είσαι ο Φοίβος, γλυκός βοηθός νηπιαγωγός. Μίλα απλά ελληνικά, σύντομα και κάνε ΜΙΑ ερώτηση."}]

# 4. Sidebar με Μασκότ
with st.sidebar:
    st.header("Ο Φοίβος!")
    image_path = os.path.join(os.getcwd(), "foivos_robot.png")
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    st.write("---")
    st.info("Γωνιά Δασκάλου")

st.markdown("<h1>🤖 Γεια! Είμαι ο Φοίβος!</h1>", unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 5. Μικρόφωνο
st.write("### Πάτα και μίλα μου!")
text = speech_to_text(language='el', start_prompt="🎤 Πάτα & Μίλα", stop_prompt="✅ Τέλος", key='foivos_final_mic')

if text:
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        st.session_state.messages.append({"role": "user", "content": text})
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )
        ai_reply = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        speak_text(ai_reply)
        st.rerun()
