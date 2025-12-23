import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np
import time

# --- CONFIGURACIÓN DE RED (STUN) ---
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302", "stun:stun3.l.google.com:19302"]}
    ]}
)

# --- DISEÑO Y ESTILO ---
st.set_page_config(page_title="Jaime Roldos Aguilera - Duel", layout="centered")

st.markdown("""
    <style>
    .title-container {
        text-align: center;
        padding: 10px;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Arial Black';
        font-size: 50px;
    }
    .vs-container {
        text-align: center;
        font-size: 24px;
        color: #ffffff;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-container'>JAIME ROLDOS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<div class='vs-container'>⚔️ ONICHAN 1 vs ONICHAN 2 ⚔️</div>", unsafe_allow_html=True)

# --- VARIABLES DE ESTADO ---
if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0
if 'inicio_juego' not in st.session_state: st.session_state.inicio_juego = None # Almacena el tiempo de inicio

# --- BOTONES DE CONTROL ---
col_c1, col_c2 = st.columns(2)
with col_c1:
    if st.button('🚀 ¡INICIAR CUENTA REGRESIVA!'):
        st.session_state.puntos_izq = 0
        st.session_state.puntos_der = 0
        st.session_state.inicio_juego = time.time() # Registra el momento exacto
with col_c2:
    if st.button('🔄 REINICIAR TODO'):
        st.session_state.puntos_izq = 0
        st.session_state.puntos_der = 0
        st.session_state.inicio_juego = None
        st.rerun()

class PrecisionDuelTransformer(VideoTransformerBase):
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=15, varThreshold=50)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        mitad = w // 2
        ahora = time.time()

        # 1. LÓGICA DE CUENTA REGRESIVA
        juego_activo = False
        if st.session_state.inicio_juego is not None:
            tiempo_pasado = ahora - st.session_state.inicio_juego
            
            if tiempo_pasado < 4: # Los primeros 4 segundos son de cuenta regresiva
                contador = 3 - int(tiempo_pasado)
                if contador > 0:
                    # Dibujar Fondo Oscuro para el contador
                    cv2.rectangle(img, (0, 0), (w, h), (0, 0, 0), -1)
                    cv2.putText(img, "EL JUEGO COMIENZA EN:", (w//6, h//2 - 50), 
                                cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, str(contador), (w//2 - 40, h//2 + 80), 
                                cv2.FONT_HERSHEY_TRIPLEX, 5, (0, 255, 255), 10)
                else:
                    cv2.putText(img, "¡YA!", (w//2 - 100, h//2 + 50), 
                                cv2.FONT_HERSHEY_TRIPLEX, 5, (0, 255, 0), 10)
                return img
            else:
                juego_activo = True

        # 2. DETECCIÓN DE MOVIMIENTO (Solo si el juego está activo)
        fgmask = self.fgbg.apply(img)
        if juego_activo and st.session_state.puntos_izq < 300 and st.session_state.puntos_der < 300:
            _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            
            mov_izq = cv2.countNonZero(fgmask[:, :mitad])
            mov_der = cv2.countNonZero(fgmask[:, mitad:])

            if mov_izq > 6000: st.session_state.puntos_izq += 2
            if mov_der > 6000: st.session_state.puntos_der += 2

        # 3. INTERFAZ GRÁFICA
        cv2.rectangle(img, (0,0), (w, 50), (20,20,20), -1)
        cv2.putText(img, "ONICHAN 1", (40, 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 150, 255), 2)
        cv2.putText(img, "ONICHAN 2", (mitad + 40, 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 150), 2)
        cv2.line(img, (mitad, 50), (mitad, h), (200, 200, 200), 1)

        # Barras de Energía
        p_izq = min(st.session_state.puntos_izq, 300)
        p_der = min(st.session_state.puntos_der, 300)
        cv2.rectangle(img, (20, h-40), (20+p_izq, h-15), (0, 0, 255), -1)
        cv2.rectangle(img, (mitad+20, h-40), (mitad+20+p_der, h-15), (255, 0, 0), -1)

        # Victoria
        if st.session_state.puntos_izq >= 300:
            cv2.putText(img, "GANADOR: ONICHAN 1", (20, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 3)
        elif st.session_state.puntos_der >= 300:
            cv2.putText(img, "GANADOR: ONICHAN 2", (mitad+20, h//2), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 3)

        return img

# --- LANZADOR DEL JUEGO ---
webrtc_streamer(
    key="duelo-final",
    video_transformer_factory=PrecisionDuelTransformer,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

# --- MÉTRICAS ---
st.write("---")
c1, c2 = st.columns(2)
c1.metric("Energía Onichan 1", f"{st.session_state.puntos_izq}/300")
c2.metric("Energía Onichan 2", f"{st.session_state.puntos_der}/300")
