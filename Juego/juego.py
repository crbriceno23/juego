import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np

# Configuración STUN para que funcione en cualquier red (HTTP/Cloud)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

st.set_page_config(page_title="Onichan Duel Live", layout="centered")
st.title("⚔️ ONICHAN DUEL: LIVE")

# Variables de puntaje usando session_state
if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0

# Botón de reinicio
if st.button('🔄 REINICIAR DUELO'):
    st.session_state.puntos_izq = 0
    st.session_state.puntos_der = 0
    st.rerun()

class DuelProcessor(VideoTransformerBase):
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        mitad = w // 2

        # Analizar movimiento
        fgmask = self.fgbg.apply(img)
        _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        
        mov_izq = cv2.countNonZero(fgmask[:, :mitad])
        mov_der = cv2.countNonZero(fgmask[:, mitad:])

        # Lógica de puntaje (Umbral de 3000 píxeles para detectar movimiento real)
        if mov_izq > 3000: st.session_state.puntos_izq += 1
        if mov_der > 3000: st.session_state.puntos_der += 1

        # --- INTERFAZ VISUAL ---
        # Títulos arriba
        cv2.rectangle(img, (0, 0), (w, 50), (20, 20, 20), -1)
        cv2.putText(img, "ONICHAN 1", (40, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 0, 255), 2)
        cv2.putText(img, "ONICHAN 2", (mitad + 40, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.9, (255, 0, 0), 2)

        # Línea divisoria
        cv2.line(img, (mitad, 50), (mitad, h), (255, 255, 255), 2)

        # Barras de Energía (Abajo)
        p_izq = min(st.session_state.puntos_izq, 300)
        p_der = min(st.session_state.puntos_der, 300)
        
        # Jugador 1 (Rojo)
        cv2.rectangle(img, (10, h-30), (10 + p_izq, h-10), (0, 0, 255), -1)
        # Jugador 2 (Azul)
        cv2.rectangle(img, (mitad + 10, h-30), (mitad + 10 + p_der, h-10), (255, 0, 0), -1)

        # Mensaje de Ganador
        if st.session_state.puntos_izq >= 300:
            cv2.putText(img, "WINNER: ONICHAN 1", (w//10, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 255, 0), 3)
        elif st.session_state.puntos_der >= 300:
            cv2.putText(img, "WINNER: ONICHAN 2", (mitad + 20, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 255, 0), 3)

        return img

# --- LANZAR STREAMER SIN AUDIO ---
webrtc_streamer(
    key="onichan-duel",
    video_transformer_factory=DuelProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False}, # DESACTIVA EL MICRÓFONO
)

st.write(f"📊 **Puntos 1:** {st.session_state.puntos_izq} | **Puntos 2:** {st.session_state.puntos_der}")