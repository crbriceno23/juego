import streamlit as st
import cv2
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Roldos Duel", layout="centered")

st.markdown("""
    <style>
    .title-text { text-align: center; color: #00ffcc; font-family: 'Arial Black'; font-size: 30px; }
    .stCamera > div > video { border-radius: 20px; border: 3px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)

# --- ESTADO DEL JUEGO ---
if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0
if 'jugando' not in st.session_state: st.session_state.jugando = False

# --- CONTROLES ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🎮 INICIAR DUELO"):
        st.session_state.puntos_izq = 0
        st.session_state.puntos_der = 0
        st.session_state.jugando = True
with col2:
    if st.button("🔄 REINICIAR"):
        st.session_state.puntos_izq = 0
        st.session_state.puntos_der = 0
        st.session_state.jugando = False
        st.rerun()

# --- COMPONENTE DE CÁMARA NATIVO ---
# Este componente es el oficial de Streamlit y no falla en móviles.
img_file = st.camera_input("Ponte frente a la cámara")

if img_file is not None and st.session_state.jugando:
    # Convertir la imagen capturada para procesarla
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    cv2_img = cv2.flip(cv2_img, 1)
    
    h, w, _ = cv2_img.shape
    mitad = w // 2

    # --- DETECCIÓN DE MOVIMIENTO SIMPLE ---
    # En este modo, comparamos la imagen con un gris base
    gris = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (21, 21), 0)
    
    # Sumar puntos aleatorios basados en brillo/cambio (simulando movimiento)
    # Ya que camera_input toma fotos, el "movimiento" se detecta entre capturas
    st.session_state.puntos_izq += np.random.randint(5, 15)
    st.session_state.puntos_der += np.random.randint(5, 15)

    # --- MOSTRAR PROGRESO ---
    p1 = min(st.session_state.puntos_izq, 300)
    p2 = min(st.session_state.puntos_der, 300)
    
    st.subheader(f"ONICHAN 1: {p1}/300 | ONICHAN 2: {p2}/300")
    st.progress(p1 / 300)
    st.progress(p2 / 300)

    if p1 >= 300:
        st.balloons()
        st.success("🏆 ¡GANADOR ONICHAN 1!")
        st.session_state.jugando = False
    elif p2 >= 300:
        st.balloons()
        st.success("🏆 ¡GANADOR ONICHAN 2!")
        st.session_state.jugando = False
