import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI", page_icon="🤖")

# 2. Σύνδεση με Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Λειτουργία για μετατροπή κειμένου σε ήχο (TTS)
def speak_text(text):
    tts = gTTS(text=text, lang='el')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    # Αυτός ο κώδικας κάνει τον ήχο να παίζει αυτόματα (autoplay)
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# 3. Μνήμη συνομιλίας
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Είσαι ο Φοίβος, γλυκός βοηθός νηπιαγωγός. Μίλα απλά ελληνικά, πολύ σύντομα (15-20 λέξεις) και κάνε μια ερωτησούλα."}
    ]

st.title("🤖 Ο Φοίβος μιλάει!")

# Εμφάνιση παλιών μηνυμάτων
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 4. Μικρόφωνο
st.write("---")
text = speech_to_text(language='el', start_prompt="🎤 Πάτα και μίλα στον Φοίβο", stop_prompt="✅ Τέλος", key='my_mic')

# 5. Λογική Απάντησης
if text:
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        
        st.session_state.messages.append({"role": "user", "content": text})
        with st.chat_message("user"):
            st.write(text)

        with st.spinner("Ο Φοίβος ετοιμάζει την απάντηση..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )
            ai_reply = completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            # Εδώ ο Φοίβος μιλάει!
            speak_text(ai_reply)
            
        st.rerun()
