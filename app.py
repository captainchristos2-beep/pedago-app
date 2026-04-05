import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI - Φοίβος", page_icon="🧸", layout="centered")

# Custom CSS για πιο όμορφη, παιδική εμφάνιση
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(to bottom, #e0f2fe, #ffffff); 
    }
    h1 { 
        color: #0284c7; 
        font-family: 'Comic Sans MS', cursive, sans-serif; 
        text-align: center;
        text-shadow: 2px 2px #bae6fd;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 5px;
    }
    /* Στυλ για το κεντράρισμα του μικροφώνου */
    .mic-container {
        display: flex;
        justify-content: center;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Σύνδεση με Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def speak_text(text):
    """Μετατρέπει το κείμενο σε ήχο και τον αναπαράγει αυτόματα"""
    try:
        tts = gTTS(text=text, lang='el')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        # Χρήση iframe hack για καλύτερο autoplay
        audio_html = f"""
            <iframe src="data:audio/mp3;base64,{b64}" allow="autoplay" style="display:none" id="iframeAudio">
            </iframe>
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Κάτι πήγε στραβά με τον ήχο: {e}")

# 3. Αρχικοποίηση Μνήμης (System Prompt)
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": """Είσαι ο Φοίβος, ένας ενθουσιώδης και γλυκός βοηθός νηπιαγωγού. 
        1. Μίλα με πολύ απλά ελληνικά (για παιδιά 4-6 ετών).
        2. Χρησιμοποίησε πάντα emojis (🧸, ✨, 🎈). 
        3. Μην γράφεις πάνω από 2 σύντομες προτάσεις.
        4. Κάνε πάντα ΜΙΑ ερώτηση στο τέλος για να συνεχιστεί η κουβέντα.
        5. Αν το παιδί πει κάτι που δεν βγάζει νόημα, απάντα: 'Δεν είμαι σίγουρος αν κατάλαβα, αλλά μου αρέσει που μου μιλάς! Θέλεις να μου το ξαναπείς;'"""
    }]

# 4. Sidebar με Μασκότ
with st.sidebar:
    st.header("🧸 Ο Φοίβος!")
    # Προσπάθεια φόρτωσης εικόνας αν υπάρχει
    image_path = os.path.join(os.getcwd(), "foivos_robot.png")
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.info("Εδώ θα εμφανιστεί η εικόνα του Φοίβου μόλις την ανεβάσεις στο GitHub!")
    
    st.write("---")
    if st.button("Καθαρισμός Συζήτησης 🗑️"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

st.markdown("<h1>🤖 Γεια! Είμαι ο Φοίβος!</h1>", unsafe_allow_html=True)

# Εμφάνιση ιστορικού συζήτησης με εικονίδια
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🧸"):
            st.write(message["content"])

# 5. Μικρόφωνο και Λογική
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🎤 Πάτα το κουμπί και μίλα μου!</h3>", unsafe_allow_html=True)

# Κεντράρισμα του κουμπιού μικροφώνου
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    text = speech_to_text(
        language='el', 
        start_prompt="Start Recording", 
        stop_prompt="Stop", 
        key='foivos_mic'
    )

if text:
    # Αποφυγή διπλής επεξεργασίας του ίδιου κειμένου
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        
        # Προσθήκη μηνύματος χρήστη
        st.session_state.messages.append({"role": "user", "content": text})
        
        # Εμφάνιση spinner όσο σκέφτεται το AI
        with st.spinner("Ο Φοίβος σε ακούει..."):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages
                )
                ai_reply = completion.choices[0].message.content
                
                # Προσθήκη απάντησης AI
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
                # Αναπαραγωγή ήχου και ανανέωση σελίδας
                speak_text(ai_reply)
                st.rerun()
            except Exception as e:
                st.error("Ωχ! Ο Φοίβος κουράστηκε λίγο. Δοκίμασε ξανά σε ένα λεπτό!")
