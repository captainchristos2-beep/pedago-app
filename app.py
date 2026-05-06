import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import base64
import io

# =================================================================
# INNOVATION MODULE: AFFECTIVE COMPUTING & SENTIMENT ENGINE
# =================================================================
class AffectiveEngine:
    """
    Αναλύει το συναίσθημα και την πολυπλοκότητα του λόγου του παιδιού
    για να προσαρμόσει τη διδακτική στρατηγική (Dynamic Scaffolding).
    """
    @staticmethod
    def analyze_feedback(text, ai_client):
        prompt = f"""
        Ανάλυσε το παρακάτω κείμενο από ένα παιδί 5 ετών: "{text}"
        Δώσε μου ένα JSON με:
        1. sentiment: (πολύ χαρούμενος, μπερδεμένος, κουρασμένος)
        2. difficulty_level: (1-5 βάσει λεξιλογίου)
        3. suggestion: (πώς πρέπει να αντιδράσει ο AI Mentor)
        """
        # Εδώ γίνεται η καινοτομία: Το AI λειτουργεί ως Meta-Analyzer
        try:
            response = ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are a child psychologist analyzer."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except:
            return None

# =================================================================
# CORE SYSTEM: MODULAR ARCHITECTURE
# =================================================================
class PedaGO_Innovation:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.init_state()

    def init_state(self):
        if "user_metrics" not in st.session_state:
            st.session_state.user_metrics = {
                "xp": 0, "mood": "Ενθουσιώδης", "difficulty": 1, "badges": []
            }
        if "chat_log" not in st.session_state:
            st.session_state.chat_log = []

    def render_ui(self):
        st.set_page_config(page_title="PedaGO Innovation", layout="wide")
        st.markdown("""
            <style>
            .stApp { background: #0f172a; color: white; }
            .metric-card { 
                background: rgba(255,255,255,0.1); 
                padding: 20px; border-radius: 20px; 
                border-left: 5px solid #0ea5e9;
            }
            .mood-indicator { color: #ffd700; font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)

    def run(self):
        self.render_ui()
        
        # --- INNOVATION HUD ---
        st.title("🚀 PedaGO Innovation: Affective AI")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'>✨ XP: {st.session_state.user_metrics['xp']}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'>🎭 Συναίσθημα: <span class='mood-indicator'>{st.session_state.user_metrics['mood']}</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'>📊 Επίπεδο: {st.session_state.user_metrics['difficulty']}</div>", unsafe_allow_html=True)

        # --- INTERACTION LAYER ---
        st.write("---")
        voice_data = speech_to_text(language='el', start_prompt="🎤 Μίλησε στον Φοίβο", key='innovation_mic')

        if voice_data:
            # ΒΗΜΑ 1: Συναισθηματική Ανάλυση (The Innovation)
            with st.spinner("🧠 Το AI αναλύει τη διάθεσή σου..."):
                analysis = AffectiveEngine.analyze_feedback(voice_data, self.client)
                # Εδώ θα μπορούσαμε να ενημερώσουμε το state βάσει του JSON
                st.session_state.user_metrics["xp"] += 10
            
            # ΒΗΜΑ 2: Παραγωγή Προσαρμοσμένης Απάντησης
            st.session_state.chat_log.append({"role": "user", "content": voice_data})
            
            with st.chat_message("assistant", avatar="🧸"):
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Είσαι ο Φοίβος. Το παιδί είναι {st.session_state.user_metrics['mood']}. Προσάρμοσε τη διδασκαλία σου."},
                        *st.session_state.chat_log
                    ]
                )
                full_res = response.choices[0].message.content
                st.write(full_res)
                
                # TTS Output
                tts = gTTS(text=full_res, lang='el')
                b = io.BytesIO() ; tts.write_to_fp(b) ; b.seek(0)
                b64 = base64.b64encode(b.read()).decode()
                st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

if __name__ == "__main__":
    app = PedaGO_Innovation()
    app.run()
