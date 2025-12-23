import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np

# Configuración de Red para Web
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# --- DISEÑO ESTILO DETECTOR DE EMOCIONES (CSS) ---
st.set_page_config(page_title="Jaime Roldos Aguilera - Duel", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .title-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Helvetica';
    }
    .vs-container {
        text-align: center;
        font-size: 24px;
        color: #ffffff;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-container'>JAIME ROLDOS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<div class='vs-container'>⚔️ ONICHAN 1 vs ONICHAN 2 ⚔️</div>", unsafe_allow_html=True)

# --- VARIABLES DE SESIÓN ---
if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0

# Botón de Reinicio con estilo
if st.button('🔄 REINICIAR DUELO'):
    st.session_state.puntos_izq = 0
    st.session_state.puntos_der = 0
    st.rerun()

class PrecisionDuelTransformer(VideoTransformerBase):
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=40)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        mitad = w // 2

        # 1. DETECCIÓN MEJORADA (Morfología)
        fgmask = self.fgbg.apply(img)
        kernel = np.ones((5,5), np.uint8)
        # Eliminamos ruido y unimos áreas de movimiento
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)
        
        # 2. CALCULAR MOVIMIENTO POR ÁREA DE CONTORNOS
        def get_movement_score(mask_part):
            contours, _ = cv2.findContours(mask_part, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            score = 0
            for cnt in contours:
                if cv2.contourArea(cnt) > 500: # Filtro de tamaño para precisión
                    score += cv2.contourArea(cnt)
            return score

        score_izq = get_movement_score(fgmask[:, :mitad])
        score_der = get_movement_score(fgmask[:, mitad:])

        # Sumar puntos si se supera el umbral de movimiento
        if st.session_state.puntos_izq < 300 and st.session_state.puntos_der < 300:
            if score_izq > 8000: st.session_state.puntos_izq += 3
            if score_der > 8000: st.session_state.puntos_der += 3

        # --- INTERFAZ SOBRE VIDEO ---
        # Cabecera Onichan
        cv2.rectangle(img, (0,0), (w, 50), (30,30,30), -1)
        cv2.putText(img, "ONICHAN 1", (w//8, 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 200, 255), 2)
        cv2.putText(img, "ONICHAN 2", (mitad + w//8, 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 150), 2)

        # Línea Neon
        cv2.line(img, (mitad, 50), (mitad, h), (150, 150, 150), 1)

        # Barras Estilo Moderno
        p_izq = min(st.session_state.puntos_izq, 300)
        p_der = min(st.session_state.puntos_der, 300)

        # Lado Izquierdo
        cv2.rectangle(img, (20, h-40), (20+p_izq, h-15), (255, 200, 0), -1)
        # Lado Derecho
        cv2.rectangle(img, (mitad+20, h-40), (mitad+20+p_der, h-15), (0, 255, 100), -1)

        # Mensajes de Victoria
        if st.session_state.puntos_izq >= 300:
            cv2.putText(img, "🏆 VICTORIA 1 🏆", (w//10, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1.1, (255, 255, 255), 3)
        elif st.session_state.puntos_der >= 300:
            cv2.putText(img, "🏆 VICTORIA 2 🏆", (mitad + 20, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1.1, (255, 255, 255), 3)

        return img

# --- COMPONENTE WEB ---
webrtc_streamer(
    key="onichan-live-duel",
    video_transformer_factory=PrecisionDuelTransformer,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
)

# --- MÉTRICAS DEBAJO (Estilo Emotion Detector) ---
st.write("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("😀 ONICHAN 1")
    st.progress(min(st.session_state.puntos_izq / 300, 1.0))
    st.metric("Puntos", f"{st.session_state.puntos_izq} / 300")

with col2:
    st.subheader("😄 ONICHAN 2")
    st.progress(min(st.session_state.puntos_der / 300, 1.0))
    st.metric("Puntos", f"{st.session_state.puntos_der} / 300")

st.info("💡 Mueve tu cuerpo en las zonas laterales para generar energía. ¡Gana el primero en llenar la barra!")
