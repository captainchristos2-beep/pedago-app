# --- ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (MASCOT) ---
with st.sidebar:
    st.header("Ο Φοίβος!")
    
    # Προσπάθεια φόρτωσης εικόνας με σωστό path
    try:
        # Αυτό βρίσκει την εικόνα όπου κι αν τρέχει η εφαρμογή
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "foivos_robot.png")
        
        if os.path.exists(image_path):
            st.image(image_path, caption="Γεια! Θέλεις να παίξουμε;", use_container_width=True)
        else:
            st.warning("⚠️ Ανέβασε το αρχείο foivos_robot.png στο GitHub!")
    except Exception as e:
        st.error("Πρόβλημα στη φόρτωση")

    st.write("---")
    # ... υπόλοιπος κώδικας sidebar ...
