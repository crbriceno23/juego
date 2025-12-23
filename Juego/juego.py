import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np
import time

# CONFIGURACIÓN STUN ULTRA COMPATIBLE
# Estos servidores ayudan a que la cámara del celular conecte a través de datos móviles (4G/5G)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun.services.mozilla.com"]}
    ]}
)

st.set_page_config(page_title="Jaime Roldos Aguilera - Duel", layout="centered")

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    .title-container {
        text-align: center;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Arial Black';
        font-size: 35px;
    }
    .vs-container { text-align: center; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-container'>JAIME ROLDOS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<div class='vs-container'>⚔️ ONICHAN 1 vs ONICHAN 2 ⚔️</div>", unsafe_allow_html=True)

if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0
if 'inicio_juego' not in st.session_state: st.session_state.inicio_juego = None

c1, c2 = st.columns(2)
with c1:
    if st.button('🚀 INICIAR CONTEO'):
        st.session_state.puntos_izq = 0
        st.session_state.puntos_der = 0
        st.session_state.inicio_juego = time.time()
with c2:
    if st.button('🔄 REINICIAR'):
        st.session_state.puntos_izq = 0
        st.session_state.puntos_der = 0
        st.session_state.inicio_juego = None
        st.rerun()

class PrecisionDuelTransformer(VideoTransformerBase):
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        mitad = w // 2
        ahora = time.time()

        juego_activo = False
        if st.session_state.inicio_juego is not None:
            t_pasado = ahora - st.session_state.inicio_juego
            if t_pasado < 4:
                contador = 3 - int(t_pasado)
                cv2.rectangle(img, (0, 0), (w, h), (0, 0, 0), -1)
                if contador > 0:
                    cv2.putText(img, f"EMPIEZA EN: {contador}", (w//6, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
                else:
                    cv2.putText(img, "¡YA!", (w//2-50, h//2), cv2.FONT_HERSHEY_TRIPLEX, 3, (0, 255, 0), 5)
                return img
            else:
                juego_activo = True

        fgmask = self.fgbg.apply(img)
        if juego_activo and st.session_state.puntos_izq < 300 and st.session_state.puntos_der < 300:
            _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            m_izq = cv2.countNonZero(fgmask[:, :mitad])
            m_der = cv2.countNonZero(fgmask[:, mitad:])
            if m_izq > 4000: st.session_state.puntos_izq += 2
            if m_der > 4000: st.session_state.puntos_der += 2

        # Dibujo de interfaz
        cv2.rectangle(img, (0,0), (w, 40), (20,20,20), -1)
        cv2.putText(img, "O1", (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 150, 255), 2)
        cv2.putText(img, "O2", (mitad + 20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 150), 2)
        cv2.line(img, (mitad, 40), (mitad, h), (200, 200, 200), 1)

        # Barras
        cv2.rectangle(img, (10, h-25), (10+min(st.session_state.puntos_izq, mitad-20), h-10), (0, 0, 255), -1)
        cv2.rectangle(img, (mitad+10, h-25), (mitad+10+min(st.session_state.puntos_der, mitad-20), h-10), (255, 0, 0), -1)

        if st.session_state.puntos_izq >= 300:
            cv2.putText(img, "GANO 1", (10, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        elif st.session_state.puntos_der >= 300:
            cv2.putText(img, "GANO 2", (mitad+10, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)

        return img

# LANZADOR OPTIMIZADO PARA CELULARES
webrtc_streamer(
    key="juego-vfinal",
    video_transformer_factory=PrecisionDuelTransformer,
    rtc_configuration=RTC_CONFIGURATION,
    # Estos constraints ayudan a que el celular no se bloquee por pedir mucha calidad
    media_stream_constraints={
        "video": {
            "width": {"ideal": 480}, 
            "frameRate": {"ideal": 15},
            "facingMode": "user" # Fuerza la cámara frontal
        },
        "audio": False
    },
    async_processing=True,
)
