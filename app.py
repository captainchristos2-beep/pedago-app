import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io
import os
import time

# =================================================================
# 1. SUBSCRIPTION & AUTH UI (PAYWALL)
# =================================================================
st.set_page_config(page_title="PedaGO Pro - Subscription Management", layout="wide")

st.markdown("""
    <style>
    .premium-badge {
        background: linear-gradient(90deg, #ffd700, #ff8c00);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .pricing-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #e2e8f0;
        text-align: center;
        transition: 0.3s;
    }
    .pricing-card:hover { border-color: #3b82f6; transform: translateY(-5px); }
    </style>
    """, unsafe_allow_html=True)

# 2. USER DATABASE (MOCKUP - Εδώ θα συνδεθεί αργότερα η SQL σου)
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "user_plan" not in st.session_state: st.session_state.user_plan = "Free" # Free ή Premium
if "usage_count" not in st.session_state: st.session_state.usage_count = 0

# 3. SIDEBAR: SUBSCRIPTION STATUS
with st.sidebar:
    st.title("👤 Ο Λογαριασμός μου")
    if st.session_state.is_logged_in:
        st.write(f"Χρήστης: **Δάσκαλος / Γονέας**")
        if st.session_state.user_plan == "Premium":
            st.markdown("<span class='premium-badge'>PREMIUM MEMBER</span>", unsafe_allow_html=True)
        else:
            st.warning("Είσαι στο Δωρεάν Πλάνο")
            if st.button("🚀 Αναβάθμιση σε Pro"):
                st.session_state.show_paywall = True
    else:
        st.info("Παρακαλώ συνδεθείτε")

# =================================================================
# 4. THE PAYWALL SCREEN
# =================================================================
def show_pricing():
    st.markdown("<h1 style='text-align:center;'>Επίλεξε το πλάνο σου 💎</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""<div class='pricing-card'>
            <h2>Δωρεάν</h2>
            <h1>0€</h1>
            <p>• 3 Μηνύματα/μέρα</p>
            <p>• Βασικό AI</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Συνέχεια με Free", use_container_width=True):
            st.session_state.is_logged_in = True
            st.session_state.user_plan = "Free"
            st.rerun()

    with c2:
        st.markdown("""<div class='pricing-card' style='border-color:#ffd700;'>
            <h2>Premium Pro</h2>
            <h1>9.99€ <small>/μήνα</small></h1>
            <p>• Απεριόριστη Ομιλία</p>
            <p>• Όλοι οι κόσμοι Genesis</p>
            <p>• Φωνή Υψηλής Ποιότητας</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Απόκτησε το Pro 💳", use_container_width=True):
            # Εδώ θα έμπαινε το Stripe Link
            st.success("Η πληρωμή ολοκληρώθηκε! (Demo)")
            st.session_state.is_logged_in = True
            st.session_state.user_plan = "Premium"
            st.rerun()

# =================================================================
# 5. CORE APP LOGIC WITH LIMITS
# =================================================================
if not st.session_state.is_logged_in:
    show_pricing()
else:
    # Εδώ ξεκινάει ο κώδικας του Genesis που φτιάξαμε πριν
    st.title("🧸 PedaGO Genesis")
    
    # Check Limits
    if st.session_state.user_plan == "Free" and st.session_state.usage_count >= 3:
        st.error("🛑 Έφτασες το όριο για σήμερα! Αναβάθμισε σε Pro για να συνεχίσεις το παιχνίδι.")
        if st.button("🚀 Αναβάθμιση Τώρα"):
            st.session_state.is_logged_in = False
            st.rerun()
    else:
        st.write(f"Στόχος: Μάθηση μέσω παιχνιδιού. (Χρήση: {st.session_state.usage_count}/3)")
        
        # Εδώ μπαίνει το μικρόφωνο
        voice = speech_to_text(language='el', key='saas_mic')
        if voice:
            st.session_state.usage_count += 1
            st.write(f"Το παιδί είπε: {voice}")
            # AI Logic...
