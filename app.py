import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text

# Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI", page_icon="🤖")

# Σύνδεση με Groq - Τραβάει το κλειδί από τα Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Κάτι τρέχει με το κλειδί στα Secrets!")

# Μνήμη συνομιλίας
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Είσαι ο Φοίβος, γλυκός βοηθός νηπιαγωγός. Μίλα απλά ελληνικά."}
    ]

st.title("🤖 Ο Φοίβος είναι εδώ!")

# Εμφάνιση παλιών μηνυμάτων
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Μικρόφωνο
st.write("---")
text = speech_to_text(language='el', start_prompt="🎤 Πάτα για να μιλήσεις", stop_prompt="✅ Τέλος", key='speech')

if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    # Απάντηση από το AI
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state.messages
    )
    ai_reply = completion.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.rerun()
