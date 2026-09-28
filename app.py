import os
import re
import streamlit as st
import google.generativeai as genai

# Configuración inicial de la página
st.set_page_config(
    page_title="Asistente de Educación Musical - LAC",
    page_icon="🎵",
    layout="centered",
)

# Diseño de la cabecera con la imagen y el título
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("juan_cartoon.png"):
        st.image("juan_cartoon.png", width=120)
with col2:
    st.title("🎵 Asistente online para LAC Música")
    st.write("Consulta basada en los cuadernillos y libros usados en clase del Profe Juan Tamburelli.")

ARCHIVO_PDF = "libro_audinos.pdf"

# Configuración de la IA
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelo_ia = genai.GenerativeModel('gemini-3.8-flash')
    usa_ia = True
except Exception:
    usa_ia = False

try:
    import fitz
    TIENE_FITZ = True
except ImportError:
    TIENE_FITZ = False

if not TIENE_FITZ:
    from pypdf import PdfReader

def extraer_paginas_pdf(ruta: str):
    if TIENE_FITZ:
        doc = fitz.open(ruta)
        textos = [pag.get_text() for pag in doc]
        doc.close()
        return textos
    else:
        lector = PdfReader(ruta)
        return [(p.extract_text() or "") for p in lector.pages]

def limpiar_texto(texto: str) -> str:
    texto = " ".join(texto.split())
    return texto.strip()

def normalizar(texto: str) -> str:
    texto = texto.lower()
    for acento, plano in {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ü':'u','ñ':'n'}.items():
        texto = texto.replace(acento, plano)
    return texto

@st.cache_resource
def indexar_libro():
    paginas_extraidas = []
    if not os.path.exists(ARCHIVO_PDF):
        return paginas_extraidas, f"❌ No se encuentra el archivo {ARCHIVO_PDF}."

    try:
        textos = extraer_paginas_pdf(ARCHIVO_PDF)
        for num_pag, texto in enumerate(textos):
            if texto and len(texto.strip()) > 20:
                limpio = limpiar_texto(texto)
                paginas_extraidas.append({"pagina": num_pag + 1, "texto": limpio})
        return paginas_extraidas, "✅ Libro indexado correctamente."
    except Exception as e:
        return paginas_extraidas, f"❌ Error leyendo el PDF: {e}"

with st.spinner("📖 Indexando los libros de la cátedra..."):
    base_de_datos, mensaje_estado = indexar_libro()

if not usa_ia:
    st.warning("Falta configurar la API Key de Gemini en los Secrets de Streamlit.")

def buscar_fragmentos(consulta: str, db: list, max_paginas: int = 3):
    ignoradas = {'de', 'el', 'la', 'en', 'un', 'es', 'se', 'lo', 'su', 'al', 'ha', 'tu', 'te', 'que', 'con', 'por', 'una', 'los', 'las'}
    palabras = [normalizar(p) for p in re.findall(r'\b\w+\b', consulta) if len(p) > 1 and normalizar(p) not in ignoradas]
    
    resultados = []
    for item in db:
        texto = normalizar(item["texto"])
        coincidencias = sum(1 for p in palabras if p in texto)
        if coincidencias > 0:
            resultados.append((coincidencias, item))
    resultados.sort(key=lambda x: x[0], reverse=True)
    return resultados[:max_paginas]

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt_usuario = st.chat_input("Hacé una consulta sobre los temas de clase...")

if prompt_usuario:
    st.chat_message("user").write(prompt_usuario)
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})

    with st.spinner("🔍 Buscando en los apuntes..."):
        fragmentos = buscar_fragmentos(prompt_usuario, base_de_datos, max_paginas=3)
        
    contexto = ""
    for _, item in fragmentos:
        contexto += f"\n[Página {item['pagina']}]\n{item['texto'][:1200]}\n"

    historial = ""
    for msg in st.session_state.mensajes[-5:-1]: 
        rol = "Alumno" if msg["role"] == "user" else "Asistente"
        historial += f"{rol}: {msg['content']}\n"

    with st.chat_message("assistant"):
        if (contexto or historial) and usa_ia:
            prompt_pedagogico = f"""
            Sos el asistente virtual de la cátedra de Educación Musical para alumnos de 1er año de secundaria (12 y 13 años).
            Respondeles siempre de 'vos' con un tono amigable, didáctico, directo y alentador.
            
            REGLA MAESTRA DE DEDUCCIÓN:
            - Usá ESTRICTAMENTE la teoría del texto del libro. 
            - Si te dan ejemplos que no están escritos o preguntan distancias entre notas específicas, APLICÁ la lógica teórica del texto para resolverlo (ej: contando grados para intervalos o analizando amplitud para intensidad).
            
            MEMORIA DE LA CHARLA (Para entender el contexto de la nueva pregunta):
            {historial}

            TEXTO DEL LIBRO ENCONTRADO AHORA:
            {contexto}

            NUEVA PREGUNTA DEL ALUMNO: {prompt_usuario}
            
            Si la pregunta no tiene NADA que ver con el cuadernillo ni con la charla previa, deciles amablemente que anoten la duda para preguntarle al profe Juan.
            """
            with st.spinner("🧠 Redactando la explicación..."):
                try:
                    respuesta = modelo_ia.generate_content(prompt_pedagogico).text
                    st.write(respuesta)
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
                except Exception as e:
                    if "429" in str(e) or "Quota" in str(e):
                        st.warning("¡Uf! Me están haciendo muchas preguntas al mismo tiempo. Esperen 1 minutito y vuelvan a intentar.")
                    else:
                        st.error(f"Error técnico: {e}")
        else:
            respuesta_final = "Esa información no está en las páginas del cuadernillo. ¡Anotá la duda y preguntale al profe Juan en la próxima clase!"
            st.write(respuesta_final)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_final})
