import streamlit as st
import cv2
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Roldós Duel Poses", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .title { text-align: center; color: #00ffcc; font-family: 'Arial Black'; font-size: 35px; }
    .step-box { background-color: #1e2129; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffcc; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'img1_base' not in st.session_state: st.session_state.img1_base = None
if 'img1_pose' not in st.session_state: st.session_state.img1_pose = None
if 'img2_base' not in st.session_state: st.session_state.img2_base = None
if 'img2_pose' not in st.session_state: st.session_state.img2_pose = None

def procesar_imagen(uploaded_file):
    if uploaded_file is not None:
        img = cv2.imdecode(np.frombuffer(uploaded_file.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        return img
    return None

def calcular_puntos(base, pose):
    g1 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(pose, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(g1, g2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    return np.sum(thresh) / 100000

# --- FLUJO DEL JUEGO ---

# PASO 1: Onichan 1 - Foto Normal
if st.session_state.paso == 1:
    st.markdown("<div class='step-box'><h3>👤 JUGADOR 1: Foto Normal</h3><p>Ponte serio y quédate quieto.</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c1")
    if foto:
        st.session_state.img1_base = procesar_imagen(foto)
        if st.button("Siguiente ➡️"):
            st.session_state.paso = 2
            st.rerun()

# PASO 2: Onichan 1 - Foto Dinámica
elif st.session_state.paso == 2:
    st.markdown("<div class='step-box'><h3>🔥 JUGADOR 1: ¡DINÁMICO!</h3><p>¡Mueve los brazos o haz una pose épica!</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c2")
    if foto:
        st.session_state.img1_pose = procesar_imagen(foto)
        if st.button("Confirmar y pasar al Jugador 2 ➡️"):
            st.session_state.paso = 3
            st.rerun()

# PASO 3: Onichan 2 - Foto Normal
elif st.session_state.paso == 3:
    st.markdown("<div class='step-box'><h3>👤 JUGADOR 2: Foto Normal</h3><p>Turno del oponente. Quédate quieto.</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c3")
    if foto:
        st.session_state.img2_base = procesar_imagen(foto)
        if st.button("Siguiente ➡️"):
            st.session_state.paso = 4
            st.rerun()

# PASO 4: Onichan 2 - Foto Dinámica
elif st.session_state.paso == 4:
    st.markdown("<div class='step-box'><h3>🔥 JUGADOR 2: ¡DINÁMICO!</h3><p>¡Supera la pose del Jugador 1!</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c4")
    if foto:
        st.session_state.img2_pose = procesar_imagen(foto)
        if st.button("VER RESULTADOS FINALES 🏆"):
            st.session_state.paso = 5
            st.rerun()

# PASO 5: RESULTADOS
elif st.session_state.paso == 5:
    s1 = calcular_puntos(st.session_state.img1_base, st.session_state.img1_pose)
    s2 = calcular_puntos(st.session_state.img2_base, st.session_state.img2_pose)
    
    st.markdown("<h2 style='text-align: center;'>📊 PUNTAJE DE ENERGÍA</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("Onichan 1", f"{int(s1)} pts")
    col2.metric("Onichan 2", f"{int(s2)} pts")
    
    if s1 > s2:
        st.balloons()
        st.success(f"🏆 ¡VICTORIA PARA EL JUGADOR 1!")
    elif s2 > s1:
        st.balloons()
        st.success(f"🏆 ¡VICTORIA PARA EL JUGADOR 2!")
    else:
        st.info("¡EMPATE! Ambos tienen la misma energía.")
        
    if st.button("🎮 JUGAR DE NUEVO"):
        st.session_state.paso = 1
        st.session_state.img1_base = None
        st.session_state.img1_pose = None
        st.session_state.img2_base = None
        st.session_state.img2_pose = None
        st.rerun()
