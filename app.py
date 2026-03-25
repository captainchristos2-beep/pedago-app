import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text

# --- 1. ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ (ΕΜΦΑΝΙΣΗ) ---
st.set_page_config(page_title="PedaGO AI - Ο Φοίβος", page_icon="🤖", layout="centered")

# Custom CSS για να φαίνεται φιλικό προς τα παιδιά
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #e3f2fd, #ffffff); }
    .kid-title { font-family: 'Comic Sans MS', cursive; color: #2e7d32; text-align: center; }
    .bot-bubble { 
        background-color: #ffffff; 
        border-radius: 20px; 
        padding: 20px; 
        border: 3px solid #4CAF50; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        font-size: 1.2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ΣΥΝΔΕΣΗ ΜΕ ΤΟ ΔΩΡΕΑΝ API (GROQ) ---
# Σημαντικό: Πρέπει να έχεις ορίσει το GROQ_API_KEY στα Secrets του Streamlit
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Σφάλμα: Ξέχασες να βάλεις το GROQ_API_KEY στα Secrets του Streamlit!")

# --- 3. ΜΝΗΜΗ & ΠΑΙΔΑΓΩΓΙΚΕΣ ΟΔΗΓΙΕΣ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
        Είσαι ο 'Φοίβος', ένας γλυκός και υπομονετικός βοηθός νηπιαγωγός. 
        - Απευθύνεσαι σε παιδιά 4-6 ετών. 
        - Μίλα απλά ελληνικά, χωρίς δύσκολες έννοιες.
        - Μην δίνεις έτοιμες απαντήσεις, κάνε ερωτήσεις που προκαλούν τη φαντασία τους.
        - Οι απαντήσεις σου πρέπει να είναι πολύ σύντομες (1-2 προτάσεις το πολύ).
        - Αν το παιδί πει κάτι λάθος, ενθάρρυνέ το με αγάπη.
        """}
    ]

# --- 4. ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (ΓΩΝΙΑ ΕΚΠΑΙΔΕΥΤΙΚΟΥ) ---
with st.sidebar:
    st.header("🍎 Για τον Παιδαγωγό")
    st.write("Εδώ θα βλέπετε την πρόοδο της τάξης.")
    access_code = st.text_input("Κωδικός PIN", type="password")
    if access_code == "1234":
        st.success("Πρόσβαση Εγκεκριμένη")
        st.write("**Στατιστικά Ημέρας:**")
        st.info("- Ενδιαφέροντα: Φύση, Ζώα\n- Συμμετοχή: Υψηλή")
        st.download_button("📜 Λήψη Αναφοράς (PDF)", "Δεδομένα δραστηριότητας...", file_name="anafora_foivos.txt")
    else:
        st.caption("Είσοδος μόνο με κωδικό.")

# --- 5. ΚΥΡΙΟ ΠΕΡΙΒΑΛΛΟΝ ΠΑΙΔΙΟΥ ---
st.markdown("<h1 class='kid-title'>🤖 Γεια! Είμαι ο Φοίβος!</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Πάτα το μικρόφωνο και πες μου κάτι!</p>", unsafe_allow_html=True)

# Εμφάνιση ιστορικού συζήτησης (για να βλέπει το παιδί τι είπε)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# --- 6. ΛΕΙΤΟΥΡΓΙΑ ΜΙΚΡΟΦΩΝΟΥ (SPEECH TO TEXT) ---
# Το παιδί πατάει και μιλάει - Το AI το μετατρέπει αυτόματα σε κείμενο στα Ελληνικά
text = speech_to_text(
    language='el', 
    start_prompt="🎤 Πάτα για να μιλήσεις", 
    stop_prompt="✅ Τέλος", 
    key='speech'
)

if text:
    # 1. Προσθήκη του μηνύματος του παιδιού στη μνήμη
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    # 2. Απάντηση από το AI (Χρήση του Llama 3.3 70B - Δωρεάν μέσω Groq)
    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile", # Το πιο δυνατό δωρεάν μοντέλο
                temperature=0.7,
            )
            ai_reply = chat_completion.choices[0].message.content
            
            # Εμφάνιση απάντησης με όμορφο bubble
            st.markdown(f"<div class='bot-bubble'>{ai_reply}</div>", unsafe_allow_html=True)
            
            # Αποθήκευση απάντησης στη μνήμη
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            st.error("Κάτι πήγε λάθος στη σύνδεση. Δοκίμασε ξανά σε λίγο!")