import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os # Για να βρούμε την εικόνα

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI - Φοίβος", page_icon="🧸", layout="centered")

# Custom CSS για πιο παιδική εμφάνιση
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #f0f8ff, #ffffff); }
    .stChatFloatingInput { background-color: transparent !important; }
    h1, h2, h3 { color: #1e88e5; font-family: 'Comic Sans MS', cursive, sans-serif; text-align: center;}
    .chat-bubble { background-color: #ffffff; border-radius: 20px; padding: 15px; border: 2px solid #64b5f6; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. Σύνδεση με Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Λειτουργία TTS (Text-to-Speech)
def speak_text(text):
    tts = gTTS(text=text, lang='el')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# 3. Μνήμη συνομιλίας
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Είσαι ο Φοίβος, γλυκός βοηθός νηπιαγωγός. Μίλα απλά ελληνικά, πολύ σύντομα (max 20 λέξεις) και κάνε ΜΙΑ ερώτηση."}
    ]

# --- ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (MASCOT & TEACHER) ---
with st.sidebar:
    st.header("Ο Φοίβος!")
    
    # Προσθήκη Μασκότ - Βεβαιώσου ότι το αρχείο είναι στο GitHub
    try:
        image_path = os.path.join(os.getcwd(), "foivos_robot.png")
        if os.path.exists(image_path):
            st.image(image_path, caption="Γεια! Θέλεις να παίξουμε;")
        else:
            st.caption("(Δεν βρέθηκε η εικόνα)")
    except Exception as e:
        st.caption("(Πρόβλημα στη φόρτωση εικόνας)")

    st.write("---")
    st.header("🍎 Γωνιά Δασκάλου")
    st.info("Εδώ θα βλέπετε την πρόοδο της τάξης (λειτουργία PRO).")

# 4. Κύριο Περιβάλλον
st.markdown("<h1>🤖 Γεια! Είμαι ο Φοίβος!</h1>", unsafe_allow_html=True)

# Εμφάνιση παλιών μηνυμάτων
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 5. Μικρόφωνο
st.write("---")
st.write("### Πάτα το μικρόφωνο και μίλα μου!")
text = speech_to_text(language='el', start_prompt="🎤 Πάτα & Μίλα", stop_prompt="✅ Τέλος", key='foivos_mic_v2')

# 6. Λογική Απάντησης
if text:
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        
        st.session_state.messages.append({"role": "user", "content": text})
        with st.chat_message("user"):
            st.write(text)

        with st.spinner("Ο Φοίβος σκέφτεται..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )
            ai_reply = completion.choices[0].message.content
            
            # Εμφάνιση απάντησης με bubble
            st.markdown(f"<div class='chat-bubble'>{ai_reply}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            # Ο Φοίβος μιλάει!
            speak_text(ai_reply)
            
        st.rerun()
