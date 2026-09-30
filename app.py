import streamlit as st
import os
import random
import time

# Intentamos importar las librerías de IA. Si no están, avisamos luego en la app.
try:
    from openai import OpenAI
    import google.generativeai as genai
    LIBRERIAS_IA_INSTALADAS = True
except ImportError:
    LIBRERIAS_IA_INSTALADAS = False

# Configuración de la página
st.set_page_config(page_title="Juegos Musicales - LAC", page_icon="🎮", layout="centered")

# --- FUNCIÓN: BUSCADOR INTELIGENTE DE ARCHIVOS ---
def buscar_archivo(nombre_base, tipo="audio"):
    extensiones = ['.mp3', '.wav', '.ogg'] if tipo == "audio" else ['.png', '.jpg', '.jpeg']
    variaciones = [
        f"{nombre_base}", 
        f"{nombre_base} 2", 
        f"{nombre_base}2", 
        f"{nombre_base} (2)",
        f"{nombre_base.capitalize()}"
    ]
    for var in variaciones:
        for ext in extensiones:
            if os.path.exists(f"{var}{ext}"):
                return f"{var}{ext}"
    return None

# --- INYECTAR CSS MEJORADO ---
st.markdown("""
    <style>
    /* 1. Comprimir espacios y evitar que choque arriba */
    .block-container {
        padding-top: 5.5rem !important; 
        padding-bottom: 1rem !important;
        max-width: 750px !important; 
    }
    
    /* MAGIA PARA PC: Si es una pantalla grande (compu), achica todo al 85% automáticamente */
    @media (min-width: 768px) {
        .block-container {
            zoom: 0.85; 
        }
    }
    
    /* Aplastar el espacio vacío gigante entre los elementos */
    [data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }
    
    /* 2. Achicar las CARTAS del memotest y juntar sus elementos internos */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.3rem !important; 
    }
    [data-testid="stVerticalBlockBorderWrapper"] div {
        gap: 0.1rem !important; 
    }
    
    /* 3. Imágenes ESPECÍFICAS de las cartas (Memotest) */
    [data-testid="stVerticalBlockBorderWrapper"] img { 
        background-color: white; 
        border-radius: 8px; 
        padding: 4px;
        max-height: 65px !important; 
        width: auto;
        object-fit: contain;
        margin: 0 auto;
        display: block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    } 
    
    /* Regla general para no deformar imágenes sueltas */
    img {
        object-fit: contain;
    }
    
    /* 4. Botones extra finitos y compactos */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px;
        font-weight: bold; 
        padding: 0.1rem !important; 
        min-height: 28px !important;
        transition: all 0.2s ease-in-out;
    }

    /* 5. Reproductor de audio ultra compacto */
    audio {
        width: 100% !important;
        height: 35px !important;
    }
    
    /* Quitar bordes y forzar barra lateral */
    [data-testid="stSidebar"] {
        border-right: 1px solid #e9ecef;
    }

    /* Ajustar los títulos para que no tengan tanto margen */
    h1 {
        padding-top: 0 !important;
    }

    /* Badges de Puntaje */
    .score-badge {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white; 
        padding: 8px 15px;
        border-radius: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(255,107,107,0.3);
        margin-bottom: 25px !important;
    }
    
    /* Cajas de Feedback más pequeñas */
    .feedback-box {
        padding: 10px 14px;
        border-radius: 10px;
        margin-top: 5px;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .feedback-correct { background-color: #d4edda; color: #155724; border-left: 4px solid #28a745; }
    .feedback-incorrect { background-color: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
    </style>
""", unsafe_allow_html=True)

# Cabecera
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("juan_cartoon.png"): 
        st.image("juan_cartoon.png", width=110)
with col2:
    st.title("🎮 Sala de Juegos - LAC")
    st.caption("¡Poné a prueba lo que aprendimos en clase!")

# --- BANCOS DE PREGUNTAS ---
banco_escalera = [
    {"nota": "SOL", "opciones": ["Do y Mi", "Fa y La", "La y Si"], "correcta": "Fa y La"},
    {"nota": "RE", "opciones": ["Do y Mi", "Fa y Sol", "Si y Do"], "correcta": "Do y Mi"},
    {"nota": "DO", "opciones": ["Mi y Fa", "Sol y La", "Si y Re"], "correcta": "Si y Re"},
    {"nota": "MI", "opciones": ["Re y Fa", "Sol y Si", "Do y Mi"], "correcta": "Re y Fa"},
    {"nota": "FA", "opciones": ["Mi y Sol", "Re y La", "Si y Do"], "correcta": "Mi y Sol"},
    {"nota": "LA", "opciones": ["Fa y Do", "Sol y Si", "Mi y Re"], "correcta": "Sol y Si"},
    {"nota": "SI", "opciones": ["La y Do", "Sol y Re", "Fa y Mi"], "correcta": "La y Do"}
]

banco_pentagrama = [
    {"img": "clave_de_sol_nota_do.png", "opciones": ["Do", "Re", "Mi"], "correcta": "Do"},
    {"img": "clave_de_sol_nota_re.png", "opciones": ["Re", "Fa", "Sol"], "correcta": "Re"},
    {"img": "clave_de_sol_nota_dosostenido.png", "opciones": ["Do", "Do sostenido", "Re bemol"], "correcta": "Do sostenido"},
    {"img": "clave_de_sol_nota_mib.png", "opciones": ["Mi", "Re sostenido", "Mi bemol"], "correcta": "Mi bemol"},
    {"img": "clave_de_sol_nota_fa.png", "opciones": ["Fa", "La", "Si"], "correcta": "Fa"}
]

banco_intervalos = [
    {"pregunta": "¿Qué distancia hay entre Re y Sol?", "opciones": ["Tercera", "Cuarta", "Quinta"], "correcta": "Cuarta"},
    {"pregunta": "¿Qué distancia hay entre Do y Mi?", "opciones": ["Segunda", "Tercera", "Cuarta"], "correcta": "Tercera"}
]

banco_ritmos = [
    {"audio": "corto corto largo audio", "img_correcta": "corto corto largo imagen.png"},
    {"audio": "corto largo corto audio", "img_correcta": "corto largo corto imagen.png"},
    {"audio": "corto largo corto corto audio", "img_correcta": "corto largo corto corto imagen.png"}
]

instrumentos_memotest = ["violin", "trompeta", "piano", "flauta_traversa"]

banco_alturas = [
    {"grave": "tuba", "agudo": "flauta_traversa"},
    {"grave": "contrabajo", "agudo": "violin"}
]

# --- INICIALIZAR MEMORIA ---
if 'puntaje' not in st.session_state: st.session_state.puntaje = 0
if 'juegos_completados' not in st.session_state: st.session_state.juegos_completados = []
if 'respuestas_guardadas' not in st.session_state: st.session_state.respuestas_guardadas = {}
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

if 'preguntas_n2' not in st.session_state: 
    st.session_state.preguntas_n2 = random.sample(banco_escalera, min(3, len(banco_escalera)))
if 'preguntas_n3' not in st.session_state: 
    st.session_state.preguntas_n3 = random.sample(banco_pentagrama, min(3, len(banco_pentagrama)))
if 'preguntas_n5' not in st.session_state: 
    st.session_state.preguntas_n5 = random.sample(banco_intervalos, min(2, len(banco_intervalos)))
if 'pregunta_n6' not in st.session_state: 
    st.session_state.pregunta_n6 = random.choice(banco_ritmos)
if 'pregunta_n8' not in st.session_state: 
    st.session_state.pregunta_n8 = random.choice(banco_alturas)

def generar_mazo(modalidad):
    deck = []
    for inst in instrumentos_memotest:
        img_file = buscar_archivo(inst, "imagen") or f"{inst}.png"
        audio_file = buscar_archivo(inst, "audio") or f"{inst}.mp3"
        
        if modalidad == "1. Imagen vs Nombre":
            deck.append({"id": inst, "tipo": "img", "valor": img_file})
            deck.append({"id": inst, "tipo": "texto", "valor": inst.replace('_', ' ').upper()})
        elif modalidad == "2. Sonido vs Imagen":
            deck.append({"id": inst, "tipo": "audio", "valor": audio_file})
            deck.append({"id": inst, "tipo": "img", "valor": img_file})
        elif modalidad == "3. Sonido vs Nombre":
            deck.append({"id": inst, "tipo": "audio", "valor": audio_file})
            deck.append({"id": inst, "tipo": "texto", "valor": inst.replace('_', ' ').upper()})
    random.shuffle(deck)
    return deck

# Menú lateral
st.sidebar.title("📌 Menú de Desafíos")
juego_actual = st.sidebar.radio("Elegí un nivel:", 
    ["1. Historia y Orígenes", "2. La Escalera de Notas", "3. El Pentagrama Visual", 
     "4. Sonido, Eco y Figuras", "5. Calculadora de Intervalos", "6. 📝 Dictado Rítmico", 
     "7. 🃏 Memotest de Instrumentos", "8. ⚖️ Batalla: Grave vs Agudo", "9. 🤖 Asistente Musical IA"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"<div class='score-badge'>🏆 Puntaje: {st.session_state.puntaje} pts</div>", unsafe_allow_html=True)

if st.sidebar.button("🔄 Reiniciar / Mezclar Todo"):
    st.session_state.clear()
    st.rerun()

# ==================================
# 1. HISTORIA Y ORÍGENES
# ==================================
if juego_actual == "1. Historia y Orígenes":
    st.header("📜 Nivel 1: Historia de las Notas")
    
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel1", {})
    completado = "nivel1" in st.session_state.juegos_completados

    q1 = st.radio("1. ¿Dónde se encontró la partitura musical más antigua hace 3400 años?", 
                  ["Egipto", "Roma", "Siria", "Grecia"], 
                  index=None if "q1" not in resp_guardadas else ["Egipto", "Roma", "Siria", "Grecia"].index(resp_guardadas["q1"]) if resp_guardadas["q1"] in ["Egipto", "Roma", "Siria", "Grecia"] else None,
                  key="n1_q1", disabled=completado)
    
    q2 = st.radio("2. ¿Qué monje italiano ideó los nombres de las notas en el siglo XI?", 
                  ["San Juan", "Guido D'Arezzo", "Papa Gregorio"], 
                  index=None if "q2" not in resp_guardadas else ["San Juan", "Guido D'Arezzo", "Papa Gregorio"].index(resp_guardadas["q2"]) if resp_guardadas["q2"] in ["San Juan", "Guido D'Arezzo", "Papa Gregorio"] else None,
                  key="n1_q2", disabled=completado)
    
    q3 = st.radio("3. ¿Por qué se reemplazó la sílaba 'Ut' por la nota 'Do'?", 
                  ["Porque sobraba una letra", "Porque era el nombre de una diosa", "Porque Do era más fácil de pronunciar"], 
                  index=None if "q3" not in resp_guardadas else ["Porque sobraba una letra", "Porque era el nombre de una diosa", "Porque Do era más fácil de pronunciar"].index(resp_guardadas["q3"]) if resp_guardadas["q3"] in ["Porque sobraba una letra", "Porque era el nombre de una diosa", "Porque Do era más fácil de pronunciar"] else None,
                  key="n1_q3", disabled=completado)
    
    if not completado:
        if st.button("Corregir Nivel 1", type="primary"):
            st.session_state.respuestas_guardadas["nivel1"] = {"q1": q1, "q2": q2, "q3": q3}
            puntos = 0
            if q1 == "Siria": puntos += 10
            if q2 == "Guido D'Arezzo": puntos += 10
            if q3 == "Porque Do era más fácil de pronunciar": puntos += 10
            
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel1")
            st.rerun()
    else:
        q1_user = resp_guardadas.get("q1")
        q2_user = resp_guardadas.get("q2")
        q3_user = resp_guardadas.get("q3")

        st.subheader("📋 Resultados de tu Intento:")
        
        if q1_user == "Siria":
            st.markdown("<div class='feedback-box feedback-correct'><b>1. Correcto! (+10 pts)</b> La partitura más antigua se halló en Ugarit, Siria.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>1. Incorrecto.</b> Elegiste: {q1_user or 'Sin responder'}. La respuesta correcta era <b>Siria</b>.</div>", unsafe_allow_html=True)

        if q2_user == "Guido D'Arezzo":
            st.markdown("<div class='feedback-box feedback-correct'><b>2. Correcto! (+10 pts)</b> Guido D'Arezzo creó el sistema de notación musical.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>2. Incorrecto.</b> Elegiste: {q2_user or 'Sin responder'}. La respuesta correcta era <b>Guido D'Arezzo</b>.</div>", unsafe_allow_html=True)

        if q3_user == "Porque Do era más fácil de pronunciar":
            st.markdown("<div class='feedback-box feedback-correct'><b>3. Correcto! (+10 pts)</b> 'Ut' fue cambiado por 'Do' para facilitar el solfeo vocal.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>3. Incorrecto.</b> Elegiste: {q3_user or 'Sin responder'}. La respuesta correcta era <b>Porque Do era más fácil de pronunciar</b>.</div>", unsafe_allow_html=True)

# ==================================
# 2. LA ESCALERA DE NOTAS
# ==================================
elif juego_actual == "2. La Escalera de Notas":
    st.header("🪜 Nivel 2: Grados Conjuntos")
    st.write("Imaginá que las notas son una escalera. ¿Cuáles son las notas vecinas?")
    
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel2", {})
    completado = "nivel2" in st.session_state.juegos_completados
    
    respuestas_n2 = []
    for i, q in enumerate(st.session_state.preguntas_n2):
        u_resp = resp_guardadas.get(f"q_{i}")
        idx = q['opciones'].index(u_resp) if u_resp in q['opciones'] else None
        
        resp = st.radio(
            f"{i+1}. ¿Cuáles son las notas vecinas de **{q['nota']}**?", 
            q['opciones'], 
            key=f"n2_{i}", 
            index=idx,
            disabled=completado
        )
        respuestas_n2.append((resp, q['correcta'], q['nota']))

    if not completado:
        if st.button("Corregir Nivel 2", type="primary"):
            guardar_dict = {}
            puntos = 0
            for i, (seleccion, correcta, nota) in enumerate(respuestas_n2):
                guardar_dict[f"q_{i}"] = seleccion
                if seleccion == correcta:
                    puntos += 10
            
            st.session_state.respuestas_guardadas["nivel2"] = guardar_dict
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel2")
            st.rerun()
    else:
        st.subheader("📋 Resultados de tu Intento:")
        for i, (seleccion, correcta, nota) in enumerate(respuestas_n2):
            if seleccion == correcta:
                st.markdown(f"<div class='feedback-box feedback-correct'><b>{i+1}. Correcto! (+10 pts)</b> Las vecinas de <b>{nota}</b> son {correcta}.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-box feedback-incorrect'><b>{i+1}. Incorrecto.</b> Para <b>{nota}</b> elegiste '{seleccion or 'Sin responder'}'. Las vecinas correctas son <b>{correcta}</b>.</div>", unsafe_allow_html=True)

# ==================================
# 3. EL PENTAGRAMA VISUAL
# ==================================
elif juego_actual == "3. El Pentagrama Visual":
    st.header("🎼 Nivel 3: El Pentagrama")
    st.write("Mirá la imagen, prestá atención a la clave y a las alteraciones, y descubrí qué nota es.")
    
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel3", {})
    completado = "nivel3" in st.session_state.juegos_completados
    
    respuestas_n3 = []
    for i, q in enumerate(st.session_state.preguntas_n3):
        st.markdown(f"**Pregunta {i+1}:**")
        img_buscada = buscar_archivo(q['img'].replace('.png', ''), "imagen") or q['img']
        if os.path.exists(img_buscada):
            st.image(img_buscada, width=220)
        else:
            st.info(f"*(Imagen de la nota: {q['img']})*")
        
        u_resp = resp_guardadas.get(f"q_{i}")
        idx = q['opciones'].index(u_resp) if u_resp in q['opciones'] else None
        
        resp = st.radio("¿Qué nota ves arriba?", q['opciones'], key=f"n3_{i}", index=idx, disabled=completado)
        respuestas_n3.append((resp, q['correcta']))
        st.write("---")

    if not completado:
        if st.button("Corregir Nivel 3", type="primary"):
            guardar_dict = {}
            puntos = 0
            for i, (seleccion, correcta) in enumerate(respuestas_n3):
                guardar_dict[f"q_{i}"] = seleccion
                if seleccion == correcta:
                    puntos += 10
            
            st.session_state.respuestas_guardadas["nivel3"] = guardar_dict
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel3")
            st.rerun()
    else:
        st.subheader("📋 Resultados de tu Intento:")
        for i, (seleccion, correcta) in enumerate(respuestas_n3):
            if seleccion == correcta:
                st.markdown(f"<div class='feedback-box feedback-correct'><b>Pregunta {i+1}: ¡Correcto! (+10 pts)</b> Es {correcta}.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-box feedback-incorrect'><b>Pregunta {i+1}: Incorrecto.</b> La nota correcta es <b>{correcta}</b>.</div>", unsafe_allow_html=True)

# ==================================
# 4. SONIDO, ECO Y FIGURAS
# ==================================
elif juego_actual == "4. Sonido, Eco y Figuras":
    st.header("🔊 Nivel 4: Cualidades y Figuras")
    
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel4", {})
    completado = "nivel4" in st.session_state.juegos_completados

    opts_1 = ["El eco repite la palabra clara, la reverberación alarga el sonido", "Son exactamente lo mismo", "La reverberación solo ocurre al aire libre"]
    opts_2 = ["Altura", "Intensidad", "Timbre"]
    opts_3 = ["Negra", "Corchea", "Redonda", "Blanca"]

    q1 = st.radio("1. ¿Qué diferencia hay entre el Eco y la Reverberación?", opts_1,
                  index=opts_1.index(resp_guardadas["q1"]) if resp_guardadas.get("q1") in opts_1 else None, key="n4_q1", disabled=completado)
    q2 = st.radio("2. ¿Qué cualidad del sonido nos permite distinguir si es Fuerte o Suave?", opts_2,
                  index=opts_2.index(resp_guardadas["q2"]) if resp_guardadas.get("q2") in opts_2 else None, key="n4_q2", disabled=completado)
    q3 = st.radio("3. ¿Cuál de estas figuras musicales dura más tiempo?", opts_3,
                  index=opts_3.index(resp_guardadas["q3"]) if resp_guardadas.get("q3") in opts_3 else None, key="n4_q3", disabled=completado)

    if not completado:
        if st.button("Corregir Nivel 4", type="primary"):
            st.session_state.respuestas_guardadas["nivel4"] = {"q1": q1, "q2": q2, "q3": q3}
            puntos = (q1 == "El eco repite la palabra clara, la reverberación alarga el sonido")*10 + (q2 == "Intensidad")*10 + (q3 == "Redonda")*10
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel4")
            st.rerun()
    else:
        st.subheader("📋 Resultados de tu Intento:")
        q1_u, q2_u, q3_u = resp_guardadas.get("q1"), resp_guardadas.get("q2"), resp_guardadas.get("q3")
        
        if q1_u == "El eco repite la palabra clara, la reverberación alarga el sonido":
            st.markdown("<div class='feedback-box feedback-correct'><b>1. Correcto! (+10 pts)</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>1. Incorrecto.</b> La respuesta era <b>El eco repite la palabra clara, la reverberación alarga el sonido</b>.</div>", unsafe_allow_html=True)
            
        if q2_u == "Intensidad":
            st.markdown("<div class='feedback-box feedback-correct'><b>2. Correcto! (+10 pts)</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>2. Incorrecto.</b> La cualidad correcta es <b>Intensidad</b>.</div>", unsafe_allow_html=True)
            
        if q3_u == "Redonda":
            st.markdown("<div class='feedback-box feedback-correct'><b>3. Correcto! (+10 pts)</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>3. Incorrecto.</b> La figura de mayor duración es la <b>Redonda</b>.</div>", unsafe_allow_html=True)

# ==================================
# 5. CALCULADORA DE INTERVALOS
# ==================================
elif juego_actual == "5. Calculadora de Intervalos":
    st.header("🥁 Nivel 5: Compases e Intervalos")
    
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel5", {})
    completado = "nivel5" in st.session_state.juegos_completados
    
    opts_compas = ["Simple", "Compuesto"]
    q_compas = st.radio("1. ¿Un compás de 6/8 es simple o compuesto?", opts_compas,
                        index=opts_compas.index(resp_guardadas.get("q_compas")) if resp_guardadas.get("q_compas") in opts_compas else None,
                        key="n5_compas", disabled=completado)
    
    st.write("Calculá la distancia contando los grados (¡acordate de contar la primera y la última nota!)")
    respuestas_n5 = []
    for i, q in enumerate(st.session_state.preguntas_n5[:2]):
        u_resp = resp_guardadas.get(f"q_{i}")
        idx = q['opciones'].index(u_resp) if u_resp in q['opciones'] else None
        
        resp = st.radio(f"{i+2}. {q['pregunta']}", q['opciones'], key=f"n5_{i}", index=idx, disabled=completado)
        respuestas_n5.append((resp, q['correcta'], q['pregunta']))

    if not completado:
        if st.button("Corregir Nivel 5", type="primary"):
            guardar_dict = {"q_compas": q_compas}
            puntos = (q_compas == "Compuesto") * 10
            for i, (r, c, p) in enumerate(respuestas_n5):
                guardar_dict[f"q_{i}"] = r
                if r == c:
                    puntos += 10
            
            st.session_state.respuestas_guardadas["nivel5"] = guardar_dict
            st.session_state.puntaje += puntos
            st.session_state.juegos_completados.append("nivel5")
            st.rerun()
    else:
        st.subheader("📋 Resultados de tu Intento:")
        q_c_u = resp_guardadas.get("q_compas")
        if q_c_u == "Compuesto":
            st.markdown("<div class='feedback-box feedback-correct'><b>1. Correcto! (+10 pts)</b></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='feedback-box feedback-incorrect'><b>1. Incorrecto.</b> El 6/8 es un compás <b>Compuesto</b>.</div>", unsafe_allow_html=True)
            
        for i, (r, c, p) in enumerate(respuestas_n5):
            if r == c:
                st.markdown(f"<div class='feedback-box feedback-correct'><b>{i+2}. Correcto! (+10 pts)</b> {p} -> {c}.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-box feedback-incorrect'><b>{i+2}. Incorrecto.</b> La distancia correcta es <b>{c}</b>.</div>", unsafe_allow_html=True)

# ==================================
# 6. DICTADO RÍTMICO
# ==================================
elif juego_actual == "6. 📝 Dictado Rítmico":
    st.header("📝 Nivel 6: Correspondencia Rítmica")
    ritmo_actual = st.session_state.pregunta_n6
    
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel6", {})
    completado = "nivel6" in st.session_state.juegos_completados
    
    st.write("Escuchá atentamente el patrón rítmico y elegí la opción que corresponda:")
    
    audio_encontrado = buscar_archivo(ritmo_actual['audio'], "audio")
    if audio_encontrado: 
        st.audio(audio_encontrado)
    else: 
        st.error(f"Falta el archivo de audio: {ritmo_actual['audio']}.mp3 o .wav")
        
    st.write("¿Cuál de estos ritmos acaba de sonar?")
    
    if 'opciones_visuales_n6' not in st.session_state:
        opciones_visuales = [r['img_correcta'] for r in banco_ritmos]
        random.shuffle(opciones_visuales)
        st.session_state.opciones_visuales_n6 = opciones_visuales
    else:
        opciones_visuales = st.session_state.opciones_visuales_n6
    
    colA, colB, colC = st.columns(3)
    with colA: 
        if os.path.exists(opciones_visuales[0]):
            st.image(opciones_visuales[0], caption="Opción A", use_container_width=True) 
        else:
            st.info(f"Opción A: {opciones_visuales[0]}")
    with colB: 
        if os.path.exists(opciones_visuales[1]):
            st.image(opciones_visuales[1], caption="Opción B", use_container_width=True)
        else:
            st.info(f"Opción B: {opciones_visuales[1]}")
    with colC: 
        if os.path.exists(opciones_visuales[2]):
            st.image(opciones_visuales[2], caption="Opción C", use_container_width=True)
        else:
            st.info(f"Opción C: {opciones_visuales[2]}")
        
    opts_n6 = ["Opción A", "Opción B", "Opción C"]
    u_sel = resp_guardadas.get("q6")
    idx_sel = opts_n6.index(u_sel) if u_sel in opts_n6 else None
    
    q6 = st.radio("Seleccioná la opción correcta:", opts_n6, key="n6_radio", index=idx_sel, disabled=completado)
    
    if not completado:
        if st.button("Corregir Nivel 6", type="primary"):
            if q6:
                idx = int(q6.split(" ")[1].replace('A','0').replace('B','1').replace('C','2'))
                st.session_state.respuestas_guardadas["nivel6"] = {"q6": q6, "elegida_img": opciones_visuales[idx]}
                
                if opciones_visuales[idx] == ritmo_actual['img_correcta']:
                    st.session_state.puntaje += 20
                    st.session_state.juegos_completados.append("nivel6")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state.juegos_completados.append("nivel6")
                    st.rerun()
            else:
                st.warning("Por favor selecciona una opción antes de corregir.")
    else:
        st.subheader("📋 Resultados de tu Intento:")
        elegida_img = resp_guardadas.get("elegida_img")
        if elegida_img == ritmo_actual['img_correcta']:
            st.markdown("<div class='feedback-box feedback-correct'><b>¡Excelente oído rítmico! (+20 pts)</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>Incorrecto.</b> El ritmo correspondía a <b>{ritmo_actual['img_correcta'].replace('.png','')}</b>.</div>", unsafe_allow_html=True)

# ==================================
# 7. MEMOTEST INTERACTIVO
# ==================================
elif juego_actual == "7. 🃏 Memotest de Instrumentos":
    st.header("🃏 Nivel 7: Memotest de Instrumentos")
    st.write("Elegí una modalidad y encontrá las parejas correspondientes haciendo clic en cada carta.")
    
    modo_seleccionado = st.radio("Elegí la modalidad:", 
                                 ["1. Imagen vs Nombre", "2. Sonido vs Imagen", "3. Sonido vs Nombre"], 
                                 horizontal=True)
    
    if 'memo_modo_actual' not in st.session_state or st.session_state.memo_modo_actual != modo_seleccionado:
        st.session_state.memo_modo_actual = modo_seleccionado
        st.session_state.memo_deck = generar_mazo(modo_seleccionado)
        st.session_state.memo_flipped = []
        st.session_state.memo_matched = []
        st.rerun()

    deck = st.session_state.memo_deck
    dorso_img = buscar_archivo("logo_audinos_abreviado_color_sin_letras", "imagen")
    
    # Grid de 4x2 con ESPACIO REDUCIDO
    cols = st.columns(4, gap="small")
    for i in range(8):
        with cols[i % 4]:
            card_container = st.container(border=True)
            with card_container:
                if i in st.session_state.memo_matched:
                    st.markdown("✅ **Lista**")
                    if deck[i]['tipo'] == 'img':
                        if os.path.exists(deck[i]['valor']):
                            st.image(deck[i]['valor'], use_container_width=True)
                        else:
                            st.info(deck[i]['id'].upper())
                    elif deck[i]['tipo'] == 'texto':
                        st.markdown(f"**{deck[i]['valor']}**")
                    elif deck[i]['tipo'] == 'audio':
                        st.markdown("🔊 **Sonido**")
                        if os.path.exists(deck[i]['valor']):
                            st.audio(deck[i]['valor'])

                elif i in st.session_state.memo_flipped:
                    st.markdown("👀 **Volteada**")
                    if deck[i]['tipo'] == 'img':
                        if os.path.exists(deck[i]['valor']):
                            st.image(deck[i]['valor'], use_container_width=True)
                        else:
                            st.info(deck[i]['id'].upper())
                    elif deck[i]['tipo'] == 'texto':
                        st.markdown(f"**{deck[i]['valor']}**")
                    elif deck[i]['tipo'] == 'audio':
                        st.markdown("🔊 **Sonido**")
                        if os.path.exists(deck[i]['valor']):
                            st.audio(deck[i]['valor'])

                else:
                    if dorso_img and os.path.exists(dorso_img):
                        st.image(dorso_img, use_container_width=True)
                    else:
                        st.markdown("🎴 **Música**")
                        
                    if len(st.session_state.memo_flipped) < 2:
                        if st.button("👆", key=f"memo_btn_{i}", use_container_width=True):
                            st.session_state.memo_flipped.append(i)
                            st.rerun()
                    else:
                        st.button("⏳", key=f"memo_btn_disabled_{i}", disabled=True, use_container_width=True)

    if len(st.session_state.memo_flipped) == 2:
        c1, c2 = st.session_state.memo_flipped
        es_pareja_real = (deck[c1]['id'] == deck[c2]['id'])
        
        st.markdown("---")
        st.markdown("<h4 style='text-align: center; margin-top: -15px;'>🤔 ¿Hacen pareja?</h4>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ SÍ", use_container_width=True, type="primary"):
                if es_pareja_real:
                    st.success("¡Excelente! (+5 pts)")
                    st.session_state.puntaje += 5
                    st.session_state.memo_matched.extend([c1, c2])
                else:
                    st.error("¡Ups! No coinciden. (-2 pts)")
                    st.session_state.puntaje = max(0, st.session_state.puntaje - 2)
                
                time.sleep(1.5)
                st.session_state.memo_flipped = []
                st.rerun()
                
        with col_btn2:
            if st.button("❌ NO", use_container_width=True):
                if not es_pareja_real:
                    st.info("¡Bien escuchado! Seguí buscando.")
                else:
                    st.warning("¡Ay! SÍ eran pareja. (-2 pts)")
                    st.session_state.puntaje = max(0, st.session_state.puntaje - 2)
                
                time.sleep(1.5)
                st.session_state.memo_flipped = []
                st.rerun()

    if len(st.session_state.memo_matched) == 8 and "nivel7" not in st.session_state.juegos_completados:
        st.session_state.puntaje += 20
        st.session_state.juegos_completados.append("nivel7")
        st.success("🎉 ¡Completaste el Memotest! (+20 pts)")
        st.balloons()

# ==================================
# 8. BATALLA GRAVE VS AGUDO
# ==================================
elif juego_actual == "8. ⚖️ Batalla: Grave vs Agudo":
    st.header("⚖️ Nivel 8: Batalla de Alturas")
    st.write("Escuchá los audios de ambos instrumentos y determiná cuál tiene el registro más grave.")
    
    batalla = st.session_state.pregunta_n8
    resp_guardadas = st.session_state.respuestas_guardadas.get("nivel8", {})
    completado = "nivel8" in st.session_state.juegos_completados
    
    if 'orden_n8' not in st.session_state:
        opciones = [batalla['grave'], batalla['agudo']]
        random.shuffle(opciones)
        st.session_state.orden_n8 = opciones
    else:
        opciones = st.session_state.orden_n8
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**🔊 Instrumento A**")
        audio_a = buscar_archivo(opciones[0], "audio")
        if audio_a: 
            st.audio(audio_a)
        else: 
            st.error(f"Falta audio de {opciones[0]}")
        
    with colB:
        st.markdown("**🔊 Instrumento B**")
        audio_b = buscar_archivo(opciones[1], "audio")
        if audio_b: 
            st.audio(audio_b)
        else: 
            st.error(f"Falta audio de {opciones[1]}")
        
    opts_8 = ["Instrumento A", "Instrumento B"]
    u_q8 = resp_guardadas.get("q8")
    idx_q8 = opts_8.index(u_q8) if u_q8 in opts_8 else None
    
    q8 = st.radio("¿Cuál tiene el registro más GRAVE?", opts_8, key="n8_radio", index=idx_q8, disabled=completado)
    
    if not completado:
        if st.button("Corregir Nivel 8", type="primary"):
            if q8:
                st.session_state.respuestas_guardadas["nivel8"] = {"q8": q8}
                seleccionado = opciones[0] if q8 == "Instrumento A" else opciones[1]
                
                if seleccionado == batalla['grave']:
                    st.session_state.puntaje += 20
                    st.session_state.juegos_completados.append("nivel8")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state.juegos_completados.append("nivel8")
                    st.rerun()
            else:
                st.warning("Por favor selecciona una opción antes de corregir.")
    else:
        st.subheader("📋 Resultados de tu Intento:")
        u_q8 = resp_guardadas.get("q8")
        seleccionado = opciones[0] if u_q8 == "Instrumento A" else opciones[1]
        
        if seleccionado == batalla['grave']:
            st.markdown(f"<div class='feedback-box feedback-correct'><b>¡Exacto! (+20 pts)</b> El {batalla['grave'].replace('_', ' ')} es más grave.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-box feedback-incorrect'><b>Incorrecto.</b> El instrumento más grave era <b>{batalla['grave'].replace('_', ' ')}</b>.</div>", unsafe_allow_html=True)

# ==================================
# 9. ASISTENTE MUSICAL IA
# ==================================
elif juego_actual == "9. 🤖 Asistente Musical IA":
    st.header("🤖 Asistente Musical IA")
    st.write("¡Consultá lo que necesites sobre teoría, instrumentos o historia de la música!")
    
    if not LIBRERIAS_IA_INSTALADAS:
        st.error("⚠️ Faltan instalar las librerías de IA.")
        st.info("Abrí la terminal en tu computadora y ejecutá este comando:\n\n`pip install openai google-generativeai`")
    else:
        # 1. Elegir qué cerebro usar
        cerebro_elegido = st.selectbox(
            "🧠 Elegir Cerebro / API:",
            ["OpenAI (GPT-4o)", "Gemini 1", "Gemini 2", "Gemini 3", "Gemini 4"]
        )

        # 2. Función segura para leer las claves sin romper la app si no existe el archivo secrets.toml
        def obtener_clave(proveedor, indice=""):
            try:
                if proveedor == "openai":
                    return st.secrets["OPENAI_API_KEY"]
                elif proveedor == "gemini":
                    return st.secrets[f"GEMINI_API_KEY_{indice}"]
            except (FileNotFoundError, KeyError):
                return None

        # 3. Mostrar el historial del chat
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 4. Campo de entrada del usuario
        if prompt := st.chat_input("Escribí tu pregunta acá..."):
            
            # Guardamos y mostramos lo que escribió el usuario
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generamos la respuesta
            with st.chat_message("assistant"):
                respuesta_placeholder = st.empty()
                respuesta_completa = ""
                
                try:
                    # LÓGICA OPENAI
                    if cerebro_elegido == "OpenAI (GPT-4o)":
                        clave = obtener_clave("openai")
                        if not clave:
                            st.warning("Falta agregar 'OPENAI_API_KEY' en tu archivo .streamlit/secrets.toml")
                        else:
                            client = OpenAI(api_key=clave)
                            # Preparamos el historial para OpenAI
                            mensajes_api = [{"role": "system", "content": "Sos un profesor de música didáctico y amigable. Ayudás a estudiantes a entender conceptos musicales de forma sencilla y directa."}]
                            for m in st.session_state.chat_history:
                                mensajes_api.append({"role": m["role"], "content": m["content"]})
                            
                            # Llamada a la API
                            stream = client.chat.completions.create(
                                model="gpt-4o",
                                messages=mensajes_api,
                                stream=True
                            )
                            for chunk in stream:
                                if chunk.choices[0].delta.content is not None:
                                    respuesta_completa += chunk.choices[0].delta.content
                                    respuesta_placeholder.markdown(respuesta_completa + "▌")
                                    
                    # LÓGICA GEMINI
                    elif "Gemini" in cerebro_elegido:
                        indice = cerebro_elegido.split(" ")[1] # Saca el número 1, 2, 3 o 4
                        clave = obtener_clave("gemini", indice)
                        
                        if not clave:
                            st.warning(f"Falta agregar 'GEMINI_API_KEY_{indice}' en tu archivo .streamlit/secrets.toml")
                        else:
                            genai.configure(api_key=clave)
                            model = genai.GenerativeModel('gemini-1.5-pro')
                            
                            # Preparamos el historial para Gemini
                            mensajes_api = []
                            for m in st.session_state.chat_history[:-1]: # Excluimos el mensaje actual
                                role = "user" if m["role"] == "user" else "model"
                                mensajes_api.append({"role": role, "parts": [m["content"]]})
                            
                            chat = model.start_chat(history=mensajes_api)
                            response = chat.send_message(prompt, stream=True)
                            for chunk in response:
                                respuesta_completa += chunk.text
                                respuesta_placeholder.markdown(respuesta_completa + "▌")
                    
                    # Terminar de escribir la respuesta y guardarla
                    if respuesta_completa:
                        respuesta_placeholder.markdown(respuesta_completa)
                        st.session_state.chat_history.append({"role": "assistant", "content": respuesta_completa})

                except Exception as e:
                    st.error(f"Hubo un error de conexión con la IA. Detalle técnico: {e}")
