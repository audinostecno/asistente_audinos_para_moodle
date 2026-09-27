import os
import re
import ollama
import streamlit as st

st.set_page_config(
    page_title="Asistente de Educación Musical - Audinos",
    page_icon="🎵",
    layout="centered",
)

# ==========================================
# CONFIGURACIÓN DEL LOGO Y BARRA LATERAL
# ==========================================
ARCHIVO_LOGO = "logo_audinos_abreviado_color.png"

with st.sidebar:
    if os.path.exists(ARCHIVO_LOGO):
        st.image(ARCHIVO_LOGO, width=140)
    else:
        st.info(f"💡 Colocá la imagen `{ARCHIVO_LOGO}` en la carpeta del proyecto para visualizarla.")
    
    st.markdown("---")
    st.markdown("### 📋 Instrucciones de uso")
    st.markdown(
        "1. **Escribí tu consulta** en la barra de chat inferior.\n"
        "2. El asistente buscará la información en los **libros y cuadernillos** cargados en la carpeta `Fuentes`.\n"
        "3. Te devolverá una respuesta basada exclusivamente en los textos, indicando las páginas de referencia."
    )
    st.markdown("---")
    st.write("🎵 *Modo Offline — Audinos*")

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.title("🎵 Asistente Pedagógico de Educación Musical")
st.write("Consulta basada en los cuadernillos de cátedra (modo offline).")

MODELO = "qwen2.5:7b"
CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_FUENTES = os.path.join(CARPETA_PROYECTO, "Fuentes")
RUTA_RESPALDO = r"C:\Users\Usuario\Documents\Programacion\Asistente IA sin conexión\Fuentes"

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
def indexar_cuadernillos():
    paginas_extraidas = []
    diagnostico = []

    if os.path.exists(CARPETA_FUENTES):
        ruta_trabajo = CARPETA_FUENTES
    elif os.path.exists(RUTA_RESPALDO):
        ruta_trabajo = RUTA_RESPALDO
    else:
        diagnostico.append("❌ No existe la carpeta Fuentes.")
        return paginas_extraidas, diagnostico

    archivos = [f for f in os.listdir(ruta_trabajo) if f.lower().endswith('.pdf')]
    diagnostico.append(f"📁 Carpeta usada: {ruta_trabajo}")
    diagnostico.append(f"📄 PDFs encontrados: {', '.join(archivos) if archivos else 'NINGUNO'}")
    diagnostico.append(f"🔧 Extractor en uso: {'PyMuPDF' if TIENE_FITZ else 'pypdf'}")

    if not archivos:
        return paginas_extraidas, diagnostico

    for archivo in archivos:
        ruta = os.path.join(ruta_trabajo, archivo)
        try:
            textos = extraer_paginas_pdf(ruta)
            chars = sum(len(t) for t in textos)
            diagnostico.append(f"✅ {archivo}: {len(textos)} páginas, {chars} caracteres extraídos")
            for num_pag, texto in enumerate(textos):
                if texto and len(texto.strip()) > 20:
                    limpio = limpiar_texto(texto)
                    if len(limpio) > 20:
                        paginas_extraidas.append({
                            "archivo": archivo,
                            "pagina": num_pag + 1,
                            "texto": limpio,
                            "texto_lower": limpio.lower(),
                        })
        except Exception as e:
            diagnostico.append(f"❌ Error leyendo {archivo}: {type(e).__name__}: {e}")

    diagnostico.append(f"📚 Total de páginas indexadas: {len(paginas_extraidas)}")
    return paginas_extraidas, diagnostico


with st.spinner("📖 Procesando cuadernillos iniciales..."):
    base_de_datos, diagnostico = indexar_cuadernillos()

with st.expander("🔍 Diagnóstico de indexación", expanded=(len(base_de_datos) == 0)):
    for linea in diagnostico:
        st.write(linea)

if base_de_datos:
    st.success(f"📚 {len(base_de_datos)} páginas indexadas correctamente.")
else:
    st.error("❌ No se pudo indexar ninguna página.")


def buscar_fragmentos(consulta: str, db: list, max_paginas: int = 3) -> list:
    palabras = [normalizar(p) for p in re.findall(r'\b\w+\b', consulta) if len(p) > 2]
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

prompt_usuario = st.chat_input("Hacé una consulta sobre los cuadernillos...")

if prompt_usuario:
    st.chat_message("user").write(prompt_usuario)
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})

    # --- AGREGADO: Spinner que muestra cuando está buscando en el PDF ---
    with st.spinner("🔍 Buscando información en los cuadernillos..."):
        fragmentos = buscar_fragmentos(prompt_usuario, base_de_datos, max_paginas=3)
        
    contexto = ""
    fuentes_usadas = []

    for _, item in fragmentos:
        contexto += f"\n[Fuente: {item['archivo']}, pág. {item['pagina']}]\n{item['texto'][:1000]}\n"
        fuentes_usadas.append(f"{item['archivo']} (pág. {item['pagina']})")

    if fuentes_usadas:
        with st.expander("📄 Fuentes encontradas para esta consulta"):
            for f in fuentes_usadas:
                st.write(f"• {f}")

    system_prompt = (
        "Sos un asistente pedagógico de Educación Musical. "
        "Responde ÚNICAMENTE basándote en el texto de los cuadernillos provistos. "
        "Si la información no está en el texto, decí: 'La información no se encuentra en las páginas consultadas.' "
        "No inventes datos ni conceptos externos."
    )

    mensajes_ollama = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.mensajes[-4:-1]:
        mensajes_ollama.append({"role": msg["role"], "content": msg["content"]})

    if contexto:
        contenido_usuario = f"TEXTO DE LOS CUADERNILLOS:\n{contexto}\n\nPREGUNTA DEL USUARIO: {prompt_usuario}"
    else:
        contenido_usuario = f"AVISO: No se encontraron coincidencias.\n\nPREGUNTA DEL USUARIO: {prompt_usuario}"

    mensajes_ollama.append({"role": "user", "content": contenido_usuario})

    with st.chat_message("assistant"):
        def generar_respuesta():
            stream = ollama.chat(
                model=MODELO,
                messages=mensajes_ollama,
                options={"temperature": 0.1, "num_ctx": 2048},
                stream=True,
            )
            for chunk in stream:
                yield chunk.get("message", {}).get("content", "")

        try:
            # --- AGREGADO: Spinner que muestra cuando Ollama está pensando ---
            with st.spinner("🧠 Pensando la respuesta..."):
                respuesta_completa = st.write_stream(generar_respuesta)
                
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_completa})
        except Exception as e:
            st.error(f"❌ Error al consultar Ollama: Asegurate de que la aplicación esté abierta. Detalle: {e}")