import streamlit as st
import os
import random

# Configuración de la página
st.set_page_config(page_title="Juegos Musicales - LAC", page_icon="🎮", layout="centered")

# Inyectar CSS para fondo blanco a imágenes y diseño
st.markdown("""
    <style>
    img { background-color: white; border-radius: 10px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("juan_cartoon.png"):
        st.image("juan_cartoon.png", width=120)
with col2:
    st.title("🎮 Mega Sala de Juegos - LAC Música")
    st.write("¡Poné a prueba lo que aprendimos en clase!")

# --- BANCOS DE PREGUNTAS (1 a 5) ---
banco_pentagrama = [
    {"img": "clave_de_sol_nota_do.png", "opciones": ["Do", "Re", "Mi"], "correcta": "Do"},
    {"img": "clave_de_sol_nota_re.png", "opciones": ["Re", "Fa", "Sol"], "correcta": "Re"},
    {"img": "clave_de_sol_nota_dosostenido.png", "opciones": ["Do", "Do sostenido", "Re bemol"], "correcta": "Do sostenido"},
    {"img": "clave_de_sol_nota_mib.png", "opciones": ["Mi", "Re sostenido", "Mi bemol"], "correcta": "Mi bemol"},
    {"img": "clave_de_sol_nota_fa.png", "opciones": ["Fa", "La", "Si"], "correcta": "Fa"},
    {"img": "clave_de_sol_nota_sol.png", "opciones": ["Fa", "Sol", "La"], "correcta": "Sol"},
    {"img": "clave_de_sol_nota_la.png", "opciones": ["Sol", "La", "Si"], "correcta": "La"},
    {"img": "clave_de_sol_nota_lasostenido.png", "opciones": ["La", "La sostenido", "Si bemol"], "correcta": "La sostenido"},
    {"img": "clave_de_sol_nota_sib.png", "opciones": ["Si", "Si bemol", "La sostenido"], "correcta": "Si bemol"},
    {"img": "clave_de_fa_nota_re.png", "opciones": ["Fa", "Re", "Si"], "correcta": "Re"},
    {"img": "clave_de_fa_nota_fa.png", "opciones": ["Re", "Fa", "La"], "correcta": "Fa"}
]

banco_intervalos = [
    {"pregunta": "¿Qué distancia hay entre Re y Sol?", "opciones": ["Tercera", "Cuarta", "Quinta"], "correcta": "Cuarta"},
    {"pregunta": "¿Qué distancia hay entre Do y Mi?", "opciones": ["Segunda", "Tercera", "Cuarta"], "correcta": "Tercera"},
    {"pregunta": "¿Qué distancia hay entre Mi y Si?", "opciones": ["Cuarta", "Quinta", "Sexta"], "correcta": "Quinta"},
    {"pregunta": "¿Qué distancia hay entre Fa y Sol?", "opciones": ["Primera", "Segunda", "Tercera"], "correcta": "Segunda"},
    {"pregunta": "¿Qué distancia hay entre Do y el siguiente Do?", "opciones": ["Sexta", "Séptima", "Octava"], "correcta": "Octava"}
]

# --- INICIALIZAR MEMORIA ---
if 'puntaje' not in st.session_state:
    st.session_state.puntaje = 0
if 'juegos_completados' not in st.session_state:
    st.session_state.juegos_completados = []
if 'preguntas_n3' not in st.session_state:
    st.session_state.preguntas_n3 = random.sample(banco_pentagrama, min(3, len(banco_pentagrama)))
if 'preguntas_n5' not in st.session_state:
    st.session_state.preguntas_n5 = random.sample(banco_intervalos, 2)

# --- MENÚ LATERAL ---
st.sidebar.title("📌 Menú de Desafíos")
juego_actual = st.sidebar.radio("Elegí un nivel:", 
    ["1. Historia y Orígenes", 
     "2. La Escalera de Notas", 
     "3. El Pentagrama Visual", 
     "4. Sonido, Eco y Figuras", 
     "5. Calculadora de Intervalos",
     "6. 🔊 Laboratorio de Cualidades",
     "7. 🎼 Arquitectura y Forma",
     "8. 🔍 Detectives de Instrumentos"])

st.sidebar.markdown("---")
st.sidebar.title(f"🏆 Puntaje total: {st.session_state.puntaje}")
if st.sidebar.button("Jugar de nuevo (Mezclar)"):
    st.session_state.puntaje = 0
    st.session_state.juegos_completados = []
    st.session_state.preguntas_n3 = random.sample(banco_pentagrama, min(3, len(banco_pentagrama)))
    st.session_state.preguntas_n5 = random.sample(banco_intervalos, 2)
    st.rerun()

# ==========================================
# JUEGOS ORIGINALES (1 al 5)
# ==========================================
if juego_actual == "1. Historia y Orígenes":
    st.header("📜 Nivel 1: Historia de las Notas")
    q1 = st.radio("1. ¿Dónde se encontró la partitura más antigua hace 3400 años?", ["Egipto", "Roma", "Siria"], index=None)
    q2 = st.radio("2. ¿Qué monje ideó los nombres de las notas?", ["San Juan", "Guido D'Arezzo", "Papa Gregorio"], index=None)
    q3 = st.radio("3. ¿Por qué se reemplazó 'Ut' por 'Do'?", ["Sobraba una letra", "Do era más fácil de pronunciar"], index=None)
    if st.button("Corregir Nivel 1"):
        if "nivel1" not in st.session_state.juegos_completados:
            puntos = (q1 == "Siria")*10 + (q2 == "Guido D'Arezzo")*10 + (q3 == "Do era más fácil de pronunciar")*10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel1")
            st.success(f"¡Sumaste {puntos} puntos!")
        else: st.warning("Ya completaste este nivel.")

elif juego_actual == "2. La Escalera de Notas":
    st.header("🪜 Nivel 2: Grados Conjuntos")
    q1 = st.radio("1. Notas vecinas de SOL:", ["Do y Mi", "Fa y La", "La y Si"], index=None)
    q2 = st.radio("2. Notas vecinas de RE:", ["Do y Mi", "Fa y Sol", "Si y Do"], index=None)
    if st.button("Corregir Nivel 2"):
        if "nivel2" not in st.session_state.juegos_completados:
            puntos = (q1 == "Fa y La")*10 + (q2 == "Do y Mi")*10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel2")
            st.success(f"¡Sumaste {puntos} puntos!")
        else: st.warning("Ya completaste este nivel.")

elif juego_actual == "3. El Pentagrama Visual":
    st.header("🎼 Nivel 3: El Pentagrama (Aleatorio)")
    respuestas_n3 = []
    for i, q in enumerate(st.session_state.preguntas_n3):
        if os.path.exists(q['img']): st.image(q['img'], width=200)
        resp = st.radio(f"Pregunta {i+1}: ¿Qué nota es?", q['opciones'], key=f"n3_{i}", index=None)
        respuestas_n3.append((resp, q['correcta']))
    if st.button("Corregir Nivel 3"):
        if "nivel3" not in st.session_state.juegos_completados:
            puntos = sum(10 for r, c in respuestas_n3 if r == c)
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel3")
            st.success(f"¡Sumaste {puntos} puntos!")
        else: st.warning("Ya completaste este nivel.")

elif juego_actual == "4. Sonido, Eco y Figuras":
    st.header("🔊 Nivel 4: Cualidades y Figuras")
    q1 = st.radio("Cualidad que distingue Fuerte de Suave:", ["Altura", "Intensidad", "Timbre"], index=None)
    q2 = st.radio("Figura que dura más:", ["Negra", "Corchea", "Redonda"], index=None)
    if st.button("Corregir Nivel 4"):
        if "nivel4" not in st.session_state.juegos_completados:
            puntos = (q1 == "Intensidad")*10 + (q2 == "Redonda")*10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel4")
            st.success(f"¡Sumaste {puntos} puntos!")
        else: st.warning("Ya completaste este nivel.")

elif juego_actual == "5. Calculadora de Intervalos":
    st.header("🥁 Nivel 5: Compases e Intervalos")
    q_compas = st.radio("¿Un compás de 6/8 es simple o compuesto?", ["Simple", "Compuesto"], index=None)
    respuestas_n5 = []
    for i, q in enumerate(st.session_state.preguntas_n5):
        resp = st.radio(q['pregunta'], q['opciones'], key=f"n5_{i}", index=None)
        respuestas_n5.append((resp, q['correcta']))
    if st.button("Corregir Nivel 5"):
        if "nivel5" not in st.session_state.juegos_completados:
            puntos = (q_compas == "Compuesto")*10 + sum(10 for r, c in respuestas_n5 if r == c)
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel5")
            st.success(f"¡Sumaste {puntos} puntos!")
        else: st.warning("Ya completaste este nivel.")

# ==========================================
# NUEVOS JUEGOS INTELIGENTES (6, 7 y 8)
# ==========================================

elif juego_actual == "6. 🔊 Laboratorio de Cualidades":
    st.header("🔊 Nivel 6: Osciloscopio Acústico")
    st.write("Escuchá los audios y descubrí qué cualidad los diferencia radicalmente.")
    
    st.subheader("Desafío A: Sonido 1 vs Sonido 2")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Sonido 1:")
        st.audio("https://upload.wikimedia.org/wikipedia/commons/1/1d/Violin_for_dummies_1.ogg") # Agudo
    with col2:
        st.write("Sonido 2:")
        st.audio("https://upload.wikimedia.org/wikipedia/commons/8/86/Double_bass_scale.ogg") # Grave
    qA = st.radio("¿Qué cualidad física diferencia al Sonido 1 del Sonido 2?", ["Altura (Agudo vs Grave)", "Intensidad (Fuerte vs Suave)", "Duración (Largo vs Corto)"], index=None)

    st.subheader("Desafío B: Sonido 3 vs Sonido 4")
    col3, col4 = st.columns(2)
    with col3:
        st.write("Sonido 3 (Gong):")
        st.audio("https://upload.wikimedia.org/wikipedia/commons/a/ae/Gong_2.ogg") # Largo
    with col4:
        st.write("Sonido 4 (Redoblante):")
        st.audio("https://upload.wikimedia.org/wikipedia/commons/3/30/Snare_drum.ogg") # Corto
    qB = st.radio("¿Qué cualidad diferencia al Sonido 3 del Sonido 4?", ["Timbre", "Duración (Persistencia en el tiempo)", "Altura"], index=None)

    if st.button("Corregir Nivel 6"):
        if "nivel6" not in st.session_state.juegos_completados:
            puntos = (qA == "Altura (Agudo vs Grave)")*10 + (qB == "Duración (Persistencia en el tiempo)")*10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel6")
            st.success(f"¡Sumaste {puntos} puntos! Tal como dice la pág 14, la frecuencia altera la altura y la persistencia la duración.")
        else: st.warning("Ya completaste este nivel.")

elif juego_actual == "7. 🎼 Arquitectura y Forma":
    st.header("🎼 Nivel 7: Forma Musical")
    
    st.subheader("Modo 1: Transición vs Juxtaposición")
    st.write("Escuchá el corte de Babasónicos ('El Colmo') desde el segundo 50. ¿Cómo es el cambio?")
    st.video("https://www.youtube.com/watch?v=FqE4y7IuT3E", start_time=48)
    q1 = st.radio("El cambio a la parte rápida es:", ["Por Yuxtaposición (corte abrupto)", "Por Transición (cambio gradual)"], index=None)

    st.subheader("Modo 2: Rompecabezas de 'Mariposa Tecnicolor'")
    st.write("Armá la estructura correcta de la canción de Fito Páez seleccionando el orden:")
    p1 = st.selectbox("Posición 1:", ["-", "Estribillo C", "Intro", "Pre-estribillo B", "Estrofa A"])
    p2 = st.selectbox("Posición 2:", ["-", "Estribillo C", "Estrofa A", "Pre-estribillo B", "Intro"])
    p3 = st.selectbox("Posición 3:", ["-", "Estrofa A'", "Estribillo C", "Pre-estribillo B", "Intro"])
    p4 = st.selectbox("Posición 4:", ["-", "Pre-estribillo B", "Estribillo C", "Estrofa A", "Intro"])
    p5 = st.selectbox("Posición 5:", ["-", "Estribillo C", "Pre-estribillo B", "Estrofa A", "Intro"])

    if st.button("Corregir Nivel 7"):
        if "nivel7" not in st.session_state.juegos_completados:
            puntos = (q1 == "Por Yuxtaposición (corte abrupto)")*10
            estructura_correcta = (p1=="Intro" and p2=="Estrofa A" and p3=="Estrofa A'" and p4=="Pre-estribillo B" and p5=="Estribillo C")
            if estructura_correcta: puntos += 10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel7")
            st.success(f"¡Estructura analizada! Sumaste {puntos} puntos.")
        else: st.warning("Ya completaste este nivel.")

elif juego_actual == "8. 🔍 Detectives de Instrumentos":
    st.header("🔍 Nivel 8: Detectives de la Orquesta")
    st.write("Clasificá rápidamente los instrumentos de las fotos.")
    
    colA, colB = st.columns(2)
    with colA:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Violin_VL100.png/300px-Violin_VL100.png", width=150)
        q_inst1 = st.radio("Instrumento 1:", ["Cuerda Frotada", "Viento Madera", "Percusión"], key="i1")
        
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Bass_drum.jpg/300px-Bass_drum.jpg", width=150)
        q_inst2 = st.radio("Instrumento 2:", ["Cuerda Pulsada", "Viento Metal", "Percusión Membrana"], key="i2")

    with colB:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Yamaha_Trumpet_YTR-8335LA_crop.jpg/300px-Yamaha_Trumpet_YTR-8335LA_crop.jpg", width=150)
        q_inst3 = st.radio("Instrumento 3:", ["Viento Metal", "Percusión", "Cuerda Percutida"], key="i3")

        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flute_with_B_foot_joint.jpg/300px-Flute_with_B_foot_joint.jpg", width=150)
        q_inst4 = st.radio("Instrumento 4:", ["Cuerda Frotada", "Viento Madera", "Viento Metal"], key="i4")

    if st.button("Corregir Nivel 8"):
        if "nivel8" not in st.session_state.juegos_completados:
            puntos = (q_inst1 == "Cuerda Frotada")*10 + (q_inst2 == "Percusión Membrana")*10 + (q_inst3 == "Viento Metal")*10 + (q_inst4 == "Viento Madera")*10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel8")
            st.success(f"¡Caso resuelto, Detective! Sumaste {puntos} puntos.")
            st.balloons()
        else: st.warning("Ya completaste este nivel.")
