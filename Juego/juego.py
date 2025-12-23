import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoProcessorBase
import cv2
import numpy as np
import time

# --- CONFIGURACIÓN DE RED ROBUSTA ---
# Usamos servidores STUN globales de Google para que el celular conecte sí o sí
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}]}
)

st.set_page_config(page_title="Roldós Duel Live", layout="centered")

st.markdown("""
    <style>
    .title-text { text-align: center; color: #00ffcc; font-family: 'Arial Black'; font-size: 35px; text-shadow: 2px 2px #000; }
    .vs-text { text-align: center; color: white; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<p class='vs-text'>ONICHAN 1 vs ONICHAN 2</p>", unsafe_allow_html=True)

# Variables de puntaje
if 'puntos_izq' not in st.session_state: st.session_state.puntos_izq = 0
if 'puntos_der' not in st.session_state: st.session_state.puntos_der = 0
if 'estado' not in st.session_state: st.session_state.estado = "ESPERA"
if 't_inicio' not in st.session_state: st.session_state.t_inicio = 0

def comenzar():
    st.session_state.puntos_izq = 0
    st.session_state.puntos_der = 0
    st.session_state.estado = "CUENTA"
    st.session_state.t_inicio = time.time()

if st.button("🚀 COMENZAR DUELO"):
    comenzar()

class DuelProcessor(VideoProcessorBase):
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=40)

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        mitad = w // 2
        ahora = time.time()

        # 1. CUENTA REGRESIVA
        if st.session_state.estado == "CUENTA":
            pasado = ahora - st.session_state.t_inicio
            if pasado < 4:
                cv2.rectangle(img, (0,0), (w,h), (0,0,0), -1)
                num = 3 - int(pasado)
                texto = f"EMPIEZA EN: {num}" if num > 0 else "¡YA!"
                cv2.putText(img, texto, (w//6, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
                return frame.from_ndarray(img, format="bgr24")
            else:
                st.session_state.estado = "JUEGO"

        # 2. LÓGICA DE JUEGO (MOVIMIENTO)
        if st.session_state.estado == "JUEGO":
            fgmask = self.fgbg.apply(img)
            m_izq = cv2.countNonZero(fgmask[:, :mitad])
            m_der = cv2.countNonZero(fgmask[:, mitad:])

            if st.session_state.puntos_izq < 300 and st.session_state.puntos_der < 300:
                if m_izq > 5000: st.session_state.puntos_izq += 2
                if m_der > 5000: st.session_state.puntos_der += 2

        # 3. INTERFAZ
        cv2.rectangle(img, (0,0), (w, 40), (20,20,20), -1)
        cv2.putText(img, "ONICHAN 1", (20, 30), 1, 1.2, (0, 150, 255), 2)
        cv2.putText(img, "ONICHAN 2", (mitad + 20, 30), 1, 1.2, (0, 255, 150), 2)
        cv2.line(img, (mitad, 40), (mitad, h), (200, 200, 200), 1)

        # Barras
        cv2.rectangle(img, (10, h-30), (10 + st.session_state.puntos_izq, h-10), (0,0,255), -1)
        cv2.rectangle(img, (mitad+10, h-30), (mitad + 10 + st.session_state.puntos_der, h-10), (255,0,0), -1)

        return frame.from_ndarray(img, format="bgr24")

# --- EL SECRETO PARA QUE NO DÉ ERROR DE CONEXIÓN ---
webrtc_streamer(
    key="duel-roldos-live",
    video_processor_factory=DuelProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={
        "video": {"width": 480, "height": 360, "frameRate": 15}, # Baja resolución = Conexión rápida
        "audio": False
    },
    async_processing=True,
)

st.write(f"Puntos: {st.session_state.puntos_izq} | {st.session_state.puntos_der}")
