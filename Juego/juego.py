import streamlit as st
import cv2
import numpy as np
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Roldós Duel Poses", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .title { text-align: center; color: #00ffcc; font-family: 'Arial Black'; font-size: 35px; margin-bottom: 0px; }
    .subtitle { text-align: center; color: white; font-size: 18px; margin-bottom: 30px; }
    .step-box { background-color: #1e2129; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffcc; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00ffcc; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>⚔️ DUELO DE POSES DINÁMICAS ⚔️</p>", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if 'paso' not in st.session_state: st.session_state.paso = 1
for key in ['img1_base', 'img1_pose', 'img2_base', 'img2_pose']:
    if key not in st.session_state: st.session_state.img1_base = None

def procesar_imagen(uploaded_file):
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.getvalue(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        # VOLTEAR LA IMAGEN (Flip 1 = Horizontal) para que NO salga invertida
        img = cv2.flip(img, 1)
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
    st.markdown("<div class='step-box'><h3>👤 JUGADOR 1: Foto Normal</h3><p>Quédate quieto para calibrar tu energía base.</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar Base", key="c1")
    if foto:
        st.session_state.img1_base = procesar_imagen(foto)
        if st.button("Siguiente ➡️"):
            st.session_state.paso = 2
            st.rerun()

# PASO 2: Onichan 1 - Foto Dinámica
elif st.session_state.paso == 2:
    st.markdown("<div class='step-box'><h3>🔥 JUGADOR 1: ¡DINÁMICO!</h3><p>¡Haz una pose con mucho movimiento!</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar Pose", key="c2")
    if foto:
        st.session_state.img1_pose = procesar_imagen(foto)
        if st.button("Confirmar y pasar al Jugador 2 ➡️"):
            st.session_state.paso = 3
            st.rerun()

# PASO 3: Onichan 2 - Foto Normal
elif st.session_state.paso == 3:
    st.markdown("<div class='step-box'><h3>👤 JUGADOR 2: Foto Normal</h3><p>Calibrando energía base del oponente.</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar Base", key="c3")
    if foto:
        st.session_state.img2_base = procesar_imagen(foto)
        if st.button("Siguiente ➡️"):
            st.session_state.paso = 4
            st.rerun()

# PASO 4: Onichan 2 - Foto Dinámica
elif st.session_state.paso == 4:
    st.markdown("<div class='step-box'><h3>🔥 JUGADOR 2: ¡DINÁMICO!</h3><p>¡Libera todo tu poder!</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar Pose", key="c4")
    if foto:
        st.session_state.img2_pose = procesar_imagen(foto)
