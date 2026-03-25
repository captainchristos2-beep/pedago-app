import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI", page_icon="🤖")

# 2. Σύνδεση με Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Κάτι τρέχει με το κλειδί στα Secrets!")

# 3. Μνήμη συνομιλίας
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Είσαι ο Φοίβος, γλυκός βοηθός νηπιαγωγός. Μίλα απλά ελληνικά, σύντομα και κάνε ΜΙΑ ερώτηση κάθε φορά."}
    ]

st.title("🤖 Ο Φοίβος είναι εδώ!")

# Εμφάνιση παλιών μηνυμάτων
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 4. Μικρόφωνο
st.write("---")
# Χρησιμοποιούμε το κουμπί μικροφώνου
text = speech_to_text(language='el', start_prompt="🎤 Πάτα για να μιλήσεις", stop_prompt="✅ Τέλος", key='speech')

# 5. Λογική Απάντησης (Εδώ βάλαμε το "φρένο")
if text and "last_input" not in st.session_state or st.session_state.get("last_input") != text:
    st.session_state.last_input = text # Αποθηκεύουμε τι είπαμε για να μην το ξαναδιαβάσει
    
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    # Απάντηση από το AI
    with st.spinner("Ο Φοίβος σκέφτεται..."):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )
        ai_reply = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        
    st.rerun() # Κάνει refresh για να εμφανιστεί η απάντηση και να καθαρίσει το μικρόφωνο
