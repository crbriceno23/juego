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
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00ffcc; color: black; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>⚔️ DUELO DE POSES DINÁMICAS ⚔️</p>", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'img1_base' not in st.session_state: st.session_state.img1_base = None
if 'img1_pose' not in st.session_state: st.session_state.img1_pose = None
if 'img2_base' not in st.session_state: st.session_state.img2_base = None
if 'img2_pose' not in st.session_state: st.session_state.img2_pose = None

def procesar_imagen(uploaded_file):
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.getvalue(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        # NO INVERTIDA: Voltear horizontalmente para vista natural
        img = cv2.flip(img, 1)
        return img
    return None

def calcular_puntos(base, pose):
    g1 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(pose, cv2.COLOR_BGR2GRAY)
    # Suavizar para reducir ruido de la cámara
    g1 = cv2.GaussianBlur(g1, (21, 21), 0)
    g2 = cv2.GaussianBlur(g2, (21, 21), 0)
    diff = cv2.absdiff(g1, g2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    return np.sum(thresh) / 100000

# --- FLUJO DEL JUEGO ---

# PASO 1: Onichan 1 - Foto Normal
if st.session_state.paso == 1:
    st.markdown("<div class='step-box'><h3>👤 JUGADOR 1: Foto Normal</h3><p>Calibrando energía base...</p></div>", unsafe_allow_html=True)
    foto1b = st.camera_input("Capturar", key="c1")
    if foto1b:
        st.session_state.img1_base = procesar_imagen(foto1b)
        if st.button("CONFIRMAR Y SIGUIENTE ➡️"):
            st.session_state.paso = 2
            st.rerun()

# PASO 2: Onichan 1 - Foto Dinámica
elif st.session_state.paso == 2:
    st.markdown("<div class='step-box'><h3>🔥 JUGADOR 1: ¡DINÁMICO!</h3><p>¡Haz tu pose con más movimiento!</p></div>", unsafe_allow_html=True)
    foto1p = st.camera_input("Capturar", key="c2")
    if foto1p:
        st.session_state.img1_pose = procesar_imagen(foto1p)
        if st.button("PASAR AL JUGADOR 2 ➡️"):
            st.session_state.paso = 3
            st.rerun()

# PASO 3: Onichan 2 - Foto Normal
elif st.session_state.paso == 3:
    st.markdown("<div class='step-box'><h3>👤 JUGADOR 2: Foto Normal</h3><p>Turno del oponente. Calibrando...</p></div>", unsafe_allow_html=True)
    foto2b = st.camera_input("Capturar", key="c3")
    if foto2b:
        st.session_state.img2_base = procesar_imagen(foto2b)
        if st.button("CONFIRMAR Y SIGUIENTE ➡️"):
            st.session_state.paso = 4
            st.rerun()

# PASO 4: Onichan 2 - Foto Dinámica
elif st.session_state.paso == 4:
    st.markdown("<div class='step-box'><h3>🔥 JUGADOR 2: ¡DINÁMICO!</h3><p>¡Muestra tu máximo poder!</p></div>", unsafe_allow_html=True)
    foto2p = st.camera_input("Capturar", key="c4")
    if foto2p:
        st.session_state.img2_pose = procesar_imagen(foto2p)
        st.write("✅ Foto capturada con éxito.")
        if st.button("🏆 VER QUIÉN GANÓ"):
            st.session_state.paso = 5
            st.rerun()

# PASO 5: RESULTADOS
elif st.session_state.paso == 5:
    with st.spinner('🧬 Analizando biometría dinámica...'):
        time.sleep(2)
        
    s1 = calcular_puntos(st.session_state.img1_base, st.session_state.img1_pose)
    s2 = calcular_puntos(st.session_state.img2_base, st.session_state.img2_pose)
    
    st.markdown("<h2 style='text-align: center;'>📊 RESULTADOS FINALES</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("Puntos J1", f"{int(s1)} pts")
    c2.metric("Puntos J2", f"{int(s2)} pts")
    
    st.write("---")
    if s1 > s2:
        st.balloons()
        st.success("🎊 ¡EL GANADOR ES EL JUGADOR 1! 🎊")
        st.info("¡Este Ecuador Amazónico, desde siempre y hasta siempre, viva la patria!")
    elif s2 > s1:
        st.balloons()
        st.success("🎊 ¡EL GANADOR ES EL JUGADOR 2! 🎊")
        st.info("¡Este Ecuador Amazónico, desde siempre y hasta siempre, viva la patria!")
    else:
        st.info("¡EMPATE! Niveles de energía equilibrados.")
        
    if st.button("🎮 JUGAR DE NUEVO"):
        st.session_state.paso = 1
        st.session_state.img1_base = None
        st.session_state.img1_pose = None
        st.session_state.img2_base = None
        st.session_state.img2_pose = None
        st.rerun()
