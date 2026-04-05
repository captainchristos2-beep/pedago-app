import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import random

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="PedaGO AI - Φοίβος", page_icon="🚀", layout="centered")

# 2. Advanced CSS για "Premium" Αίσθηση
st.markdown("""
    <style>
    /* Κλίση φόντου που θυμίζει ουρανό */
    .stApp { 
        background: linear-gradient(135deg, #e0f7fa 0%, #ffffff 100%); 
    }
    
    /* Στυλ για τις κάρτες των μηνυμάτων */
    .stChatMessage {
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-radius: 25px !important;
        border: 1px solid #e1e1e1;
    }

    /* Τίτλος με εφέ παιχνιδιού */
    .main-title {
        color: #0284c7;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    /* Κουμπί μικροφώνου */
    div.stButton > button {
        background-color: #0284c7;
        color: white;
        border-radius: 50px;
        padding: 10px 25px;
        border: none;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #0369a1;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Σύνδεση με Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def speak_text(text):
    """Μετατρέπει το κείμενο σε ήχο με βελτιωμένο autoplay"""
    try:
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
    except Exception:
        pass

# 4. Διαχείριση Μνήμης & Προσωπικότητας
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": """Είσαι ο Φοίβος, ο καλύτερος φίλος των παιδιών στο νηπιαγωγείο.
        - Το ύφος σου είναι χαρούμενο, καθησυχαστικό και γεμάτο φαντασία.
        - Χρησιμοποίησε λέξεις όπως 'φανταστικό', 'υπέροχα', 'πάμε να δούμε'.
        - Κράτα τις απαντήσεις κάτω από 25 λέξεις.
        - Κάθε απάντηση ΠΡΕΠΕΙ να τελειώνει με μια ερώτηση που προκαλεί το παιδί να περιγράψει κάτι (π.χ. 'Τι χρώμα έχει ο δικός σου δράκος;').
        - Αν το παιδί σου πει το όνομά του, να το χρησιμοποιείς συχνά."""
    }]

# 5. UI - Header & Μασκότ
st.markdown("<h1 class='main-title'>🧸 Φοίβος</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Ο AI βοηθός σου για παιχνίδι και μάθηση!</p>", unsafe_allow_html=True)

# Sidebar με ρυθμίσεις για τον δάσκαλο
with st.sidebar:
    st.title("⚙️ Ρυθμίσεις")
    difficulty = st.select_slider("Επίπεδο Λεξιλογίου", options=["Απλό", "Μεσαίο", "Πλούσιο"])
    st.write("---")
    if st.button("🗑️ Νέα Συζήτηση"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    st.info("Tip: Ο Φοίβος λειτουργεί καλύτερα όταν το παιδί μιλάει καθαρά κοντά στο μικρόφωνο.")

# Εμφάνιση μηνυμάτων
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🚀" if message["role"] == "user" else "🧸"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

# 6. Κεντρικό Σημείο Αλληλεπίδρασης
st.write("")
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Εδώ είναι η "καρδιά" της εφαρμογής
    text = speech_to_text(
        language='el', 
        start_prompt="🎤 Πάτα για να μιλήσεις", 
        stop_prompt="🛑 Σταμάτα", 
        key='foivos_ultra_mic'
    )

if text:
    if "last_processed" not in st.session_state or st.session_state.last_processed != text:
        st.session_state.last_processed = text
        st.session_state.messages.append({"role": "user", "content": text})
        
        # Εμφάνιση "Φοίβος σκέφτεται" με εφέ
        with st.status("Ο Φοίβος ακούει προσεκτικά...", expanded=False) as status:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.8, # Λίγο πιο δημιουργικό
            )
            ai_reply = completion.choices[0].message.content
            status.update(label="Ο Φοίβος βρήκε τι θα πει!", state="complete", expanded=False)

        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        speak_text(ai_reply)
        st.rerun()

# 7. Footer
st.markdown("<br><br><p style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>Made with ❤️ for PedaGO</p>", unsafe_allow_html=True)
