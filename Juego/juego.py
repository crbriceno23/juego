import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np
import time

# Configuración de servidores STUN de Google y Mozilla (Estándar global)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}, {"urls": ["stun:stun.services.mozilla.com"]}]}
)

st.set_page_config(page_title="Roldós Duel", layout="centered")

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #00ffcc; color: black; font-weight: bold; }
    .title-text { text-align: center; color: #00ffcc; font-family: 'Courier New'; font-size: 30px; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)
st.write("---")

# --- LÓGICA DE ESTADO ---
if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0
if 'estado' not in st.session_state: st.session_state.estado = "ESPERA" # ESPERA, CUENTA, JUEGO
if 'timer' not in st.session_state: st.session_state.timer = 0

def iniciar_duelo():
    st.session_state.puntos_izq = 0
    st.session_state.puntos_der = 0
    st.session_state.estado = "CUENTA"
    st.session_state.timer = time.time()

def reiniciar():
    st.session_state.estado = "ESPERA"
    st.session_state.puntos_izq = 0
    st.session_state.puntos_der = 0
    st.rerun()

# --- BOTONES ---
if st.session_state.estado == "ESPERA":
    st.button("🎮 COMENZAR DESAFÍO", on_click=iniciar_duelo)
else:
    st.button("🔄 REINICIAR", on_click=reiniciar)

class DuelTransformer(VideoTransformerBase):
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=40)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        mitad = w // 2
        
        # 1. CUENTA REGRESIVA SOBRE EL VIDEO
        if st.session_state.estado == "CUENTA":
            transcurrido = time.time() - st.session_state.timer
            cv2.rectangle(img, (0,0), (w,h), (0,0,0), -1)
            
            if transcurrido < 3:
                num = 3 - int(transcurrido)
                cv2.putText(img, str(num), (w//2-50, h//2+50), cv2.FONT_HERSHEY_TRIPLEX, 6, (0, 255, 255), 15)
            else:
                st.session_state.estado = "JUEGO"
            return img

        # 2. PROCESAMIENTO DE DUELO (SOLO EN ESTADO JUEGO)
        if st.session_state.estado == "JUEGO":
            fgmask = self.fgbg.apply(img)
            _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            
            # Solo sumamos si no hay ganador
            if st.session_state.puntos_izq < 300 and st.session_state.puntos_der < 300:
                m_izq = cv2.countNonZero(fgmask[:, :mitad])
                m_der = cv2.countNonZero(fgmask[:, mitad:])
                
                if m_izq > 5000: st.session_state.puntos_izq += 3
                if m_der > 5000: st.session_state.puntos_der += 3

        # --- DIBUJAR INTERFAZ ---
        # Nombres
        cv2.putText(img, "ONICHAN 1", (30, 40), 1, 1.5, (0, 0, 255), 2)
        cv2.putText(img, "ONICHAN 2", (mitad + 30, 40), 1, 1.5, (255, 0, 0), 2)
        cv2.line(img, (mitad, 0), (mitad, h), (255,255,255), 2)

        # Barras de Energía
        p_izq = min(st.session_state.puntos_izq, 300)
        p_der = min(st.session_state.puntos_der, 300)
        cv2.rectangle(img, (20, h-30), (20+p_izq, h-10), (0, 0, 255), -1)
        cv2.rectangle(img, (mitad+20, h-30), (mitad+20+p_der, h-10), (255, 0, 0), -1)

        # Ganador
        if st.session_state.puntos_izq >= 300:
            cv2.putText(img, "GANADOR 1", (50, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 255, 0), 3)
        elif st.session_state.puntos_der >= 300:
            cv2.putText(img, "GANADOR 2", (mitad+50, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 255, 0), 3)

        return img

# --- LANZADOR WEB ---
ctx = webrtc_streamer(
    key="duelo-final-roldos",
    video_transformer_factory=DuelTransformer,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={
        "video": {"width": {"ideal": 480}, "frameRate": {"ideal": 15}},
        "audio": False
    },
    async_processing=True,
)

if ctx.state.playing:
    st.info("Cámara activa. ¡Presiona el botón verde para iniciar el conteo!")
else:
    st.warning("Haz clic en 'START' arriba para encender la cámara primero.")
