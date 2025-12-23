import streamlit as st
import cv2
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Roldós Duel Poses", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .title { text-align: center; color: #00ffcc; font-family: 'Arial Black'; font-size: 35px; border-bottom: 2px solid #00ffcc; }
    .status { text-align: center; color: #ff0055; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>🔥 DUELO DE ENERGÍA DINÁMICA 🔥</p>", unsafe_allow_html=True)

# --- LÓGICA DE COMPARACIÓN ---
def calcular_energia(img_base, img_pose):
    # Convertir a escala de grises para comparar
    g1 = cv2.cvtColor(img_base, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(img_pose, cv2.COLOR_BGR2GRAY)
    
    # Calcular la diferencia absoluta entre las dos fotos
    diff = cv2.absdiff(g1, g2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    
    # El puntaje es cuántos píxeles cambiaron (movimiento/dinamismo)
    score = np.sum(thresh) / 100000 
    return score, thresh

# --- INTERFAZ ---
col1, col2 = st.columns(2)

with col1:
    st.header("ONICHAN 1")
    f1_base = st.camera_input("1. Foto Normal", key="o1_b")
    f1_pose = st.camera_input("2. ¡PUESTA DINÁMICA!", key="o1_p")

with col2:
    st.header("ONICHAN 2")
    f2_base = st.camera_input("1. Foto Normal", key="o2_b")
    f2_pose = st.camera_input("2. ¡PUESTA DINÁMICA!", key="o2_p")

if f1_base and f1_pose and f2_base and f2_pose:
    # Procesar Jugador 1
    img1_b = cv2.imdecode(np.frombuffer(f1_base.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    img1_p = cv2.imdecode(np.frombuffer(f1_pose.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    score1, mapa1 = calcular_energia(img1_b, img1_p)
    
    # Procesar Jugador 2
    img2_b = cv2.imdecode(np.frombuffer(f2_base.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    img2_p = cv2.imdecode(np.frombuffer(f2_pose.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    score2, mapa2 = calcular_energia(img2_b, img2_p)
    
    st.write("---")
    st.subheader("📊 RESULTADOS DEL ESCÁNER DE ENERGÍA")
    
    res1, res2 = st.columns(2)
    res1.metric("Energía Onichan 1", f"{int(score1)} pts")
    res2.metric("Energía Onichan 2", f"{int(score2)} pts")
    
    # Mostrar el "Aura" (la diferencia de movimiento)
    with res1:
        st.image(mapa1, caption="Aura de Movimiento 1", use_container_width=True)
    with res2:
        st.image(mapa2, caption="Aura de Movimiento 2", use_container_width=True)

    # --- DECLARAR GANADOR ---
    if score1 > score2:
        st.balloons()
        st.success(f"🏆 ¡ONICHAN 1 ES MÁS DINÁMICO POR {int(score1 - score2)} PUNTOS!")
    elif score2 > score1:
        st.balloons()
        st.success(f"🏆 ¡ONICHAN 2 ES MÁS DINÁMICO POR {int(score2 - score1)} PUNTOS!")
    else:
        st.info("¡EMPATE ENERGÉTICO! Ambos son igual de cracks.")

st.info("💡 Instrucciones: Primero tómate una foto serio. Luego, tómate la segunda moviendo los brazos o saltando. ¡El sistema detectará quién cambió más!")
