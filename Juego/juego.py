import streamlit as st
import cv2
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Roldós Duel Red & Green", layout="centered")

# --- DISEÑO CSS PERSONALIZADO (ROJO Y VERDE) ---
st.markdown("""
    <style>
    /* Fondo Oscuro con matices */
    .main { background: radial-gradient(circle, #0a1a0a 0%, #1a0505 100%); }
    
    /* Título con Efecto Neón Rojo y Verde */
    .neon-title {
        text-align: center;
        color: #fff;
        font-family: 'Arial Black';
        font-size: 38px;
        text-shadow: 0 0 10px #22c55e, 0 0 20px #ef4444;
        margin-bottom: 5px;
    }
    .neon-subtitle {
        text-align: center;
        color: #22c55e;
        font-family: 'Courier New';
        font-size: 16px;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    
    /* Contenedores con bordes Rojo/Verde */
    .step-card {
        background: rgba(0, 0, 0, 0.6);
        padding: 25px;
        border-radius: 20px;
        border-top: 4px solid #22c55e;
        border-bottom: 4px solid #ef4444;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Botones Estilo Dual */
    .stButton>button {
        width: 100%;
        border: none;
        border-radius: 12px;
        background: linear-gradient(90deg, #166534 0%, #991b1b 100%);
        color: white;
        font-weight: bold;
        font-size: 18px;
        padding: 12px;
        transition: 0.4s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #22c55e 0%, #ef4444 100%);
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
        transform: translateY(-2px);
    }
    
    /* Personalización de la barra de progreso de Streamlit */
    .stProgress > div > div > div > div {
        background-color: #22c55e;
    }
    
    /* Estilo para la cámara */
    .stCamera { border: 3px solid #166534; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon-title'>JAIME ROLDÓS AGUILERA</h1>", unsafe_allow_html=True)
st.markdown("<p class='neon-subtitle'>🛡️ Duel System: Red vs Green 🛡️</p>", unsafe_allow_html=True)

# --- LÓGICA DE ESTADO ---
if 'paso' not in st.session_state: st.session_state.paso = 1
for key in ['img1_base', 'img1_pose', 'img2_base', 'img2_pose']:
    if key not in st.session_state: st.session_state[key] = None

def procesar_imagen(uploaded_file):
    if uploaded_file is not None:
        file_bytes = np.frombuffer(uploaded_file.getvalue(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return cv2.flip(img, 1) # Vista espejo corregida
    return None

def calcular_puntos(base, pose):
    g1 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(pose, cv2.COLOR_BGR2GRAY)
    g1 = cv2.GaussianBlur(g1, (21, 21), 0)
    g2 = cv2.GaussianBlur(g2, (21, 21), 0)
    diff = cv2.absdiff(g1, g2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    return np.sum(thresh) / 100000

# --- PROGRESO DE TURNOS ---
st.progress((st.session_state.paso - 1) / 4)

# --- FLUJO DEL JUEGO ---

if st.session_state.paso == 1:
    st.markdown("<div class='step-card'><h2 style='color:#22c55e;'>🟢 ONICHAN 1: BASE</h2><p style='color:#ddd;'>Iniciando escaneo estático...</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c1")
    if foto:
        st.session_state.img1_base = procesar_imagen(foto)
        if st.button("CALIBRAR ENERGÍA ✅"):
            st.session_state.paso = 2
            st.rerun()

elif st.session_state.paso == 2:
    st.markdown("<div class='step-card'><h2 style='color:#ef4444;'>🔴 ONICHAN 1: POSE</h2><p style='color:#ddd;'>¡GENERA DINAMISMO AHORA!</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c2")
    if foto:
        st.session_state.img1_pose = procesar_imagen(foto)
        if st.button("CARGAR RESULTADO ⚡"):
            st.session_state.paso = 3
            st.rerun()

elif st.session_state.paso == 3:
    st.markdown("<div class='step-card'><h2 style='color:#22c55e;'>🟢 ONICHAN 2: BASE</h2><p style='color:#ddd;'>Oponente en posición de inicio...</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c3")
    if foto:
        st.session_state.img2_base = procesar_imagen(foto)
        if st.button("CALIBRAR ENERGÍA ✅"):
            st.session_state.paso = 4
            st.rerun()

elif st.session_state.paso == 4:
    st.markdown("<div class='step-card'><h2 style='color:#ef4444;'>🔴 ONICHAN 2: POSE</h2><p style='color:#ddd;'>¡DEMUESTRA TU MÁXIMO PODER!</p></div>", unsafe_allow_html=True)
    foto = st.camera_input("Capturar", key="c4")
    if foto:
        st.session_state.img2_pose = procesar_imagen(foto)
        if st.button("🏆 FINALIZAR DUELO"):
            st.session_state.paso = 5
            st.rerun()

elif st.session_state.paso == 5:
    with st.spinner('🧬 PROCESANDO DIFERENCIA DE PÍXELES...'):
        time.sleep(2.5)
        
    s1 = int(calcular_puntos(st.session_state.img1_base, st.session_state.img1_pose))
    s2 = int(calcular_puntos(st.session_state.img2_base, st.session_state.img2_pose))
    
    st.markdown("<div class='step-card'><h2>📊 RESULTADO DEL ESCÁNER</h2></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color:#22c55e;'>JUGADOR 1</h3>", unsafe_allow_html=True)
        st.title(f"{s1}")
        st.write("PUNTOS DE ACCIÓN")
    with col2:
        st.markdown("<h3 style='color:#ef4444;'>JUGADOR 2</h3>", unsafe_allow_html=True)
        st.title(f"{s2}")
        st.write("PUNTOS DE ACCIÓN")

    st.write("---")
    if s1 > s2:
        st.balloons()
        st.success(f"🎊 ¡DOMINIO TOTAL DEL JUGADOR 1! (+{s1-s2})")
    elif s2 > s1:
        st.balloons()
        st.success(f"🎊 ¡DOMINIO TOTAL DEL JUGADOR 2! (+{s2-s1})")
    else:
        st.info("🤝 EQUILIBRIO PERFECTO DE ENERGÍAS.")
        
    st.markdown("<p style='text-align:center; font-weight:bold; color:#22c55e;'>'Este Ecuador Amazónico, desde siempre y hasta siempre, ¡Viva la Patria!'</p>", unsafe_allow_html=True)
    
    if st.button("🎮 REINICIAR SISTEMA"):
        st.session_state.paso = 1
        st.rerun()
