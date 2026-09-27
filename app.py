import os
import re
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="Asistente de Educación Musical - Audinos",
    page_icon="🎵",
    layout="centered",
)

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.title("🎵 Asistente Pedagógico de Educación Musical")
st.write("Consulta basada en los cuadernillos y libros oficiales de la cátedra.")

ARCHIVO_PDF = "libro_audinos.pdf"  # Aquí irá tu PDF unificado

# Intentamos cargar librerías de lectura de PDF
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
        return paginas_extraidas, f"❌ No se encuentra el archivo {ARCHIVO_PDF} en el repositorio."

    try:
        textos = extraer_paginas_pdf(ARCHIVO_PDF)
        for num_pag, texto in enumerate(textos):
            if texto and len(texto.strip()) > 20:
                limpio = limpiar_texto(texto)
                if len(limpio) > 20:
                    paginas_extraidas.append({
                        "pagina": num_pag + 1,
                        "texto": limpio,
                    })
        return paginas_extraidas, "✅ Libro indexado correctamente."
    except Exception as e:
        return paginas_extraidas, f"❌ Error leyendo el PDF: {e}"


with st.spinner("📖 Indexando los libros de la cátedra..."):
    base_de_datos, mensaje_estado = indexar_libro()

st.info(mensaje_estado)


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

prompt_usuario = st.chat_input("Hacé una consulta sobre los libros...")

if prompt_usuario:
    st.chat_message("user").write(prompt_usuario)
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})

    with st.spinner("🔍 Buscando información en los textos..."):
        fragmentos = buscar_fragmentos(prompt_usuario, base_de_datos, max_paginas=3)
        
    contexto = ""
    fuentes_usadas = []

    for item in fragmentos:
        contexto += f"\n[Página {item['pagina']}]\n{item['texto'][:1200]}\n"
        fuentes_usadas.append(f"Página {item['pagina']}")

    if fuentes_usadas:
        with st.expander("📄 Referencias encontradas en el libro"):
            for f in fuentes_usadas:
                st.write(f"• {f}")

    # Estructura estricta para evitar alucinaciones (que no invente)
    if contexto:
        respuesta_final = f"Basándome estrictamente en los libros de la cátedra, encontré la siguiente referencia:\n\n{contexto[:2500]}\n\n*(Nota: Consulta las páginas indicadas arriba para profundizar en los detalles).* "
    else:
        respuesta_final = "La información solicitada no se encuentra en las páginas de los libros consultados. Para evitar desinformar, prefiero no especular."

    with st.chat_message("assistant"):
        st.write(respuesta_final)
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_final})
