import os
import re
import streamlit as st
import google.generativeai as genai

try:
    from openai import OpenAI
    TIENE_OPENAI = True
except ImportError:
    TIENE_OPENAI = False

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
    st.write("Consulta basada en los cuadernillos y libros usados en clase.")

ARCHIVO_PDF = "libro_audinos.pdf"

# En la nube usaremos pypdf por defecto
from pypdf import PdfReader

def extraer_paginas_pdf(ruta: str):
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
        if "cerebro" in msg:
            st.caption(f"⚡ Respondido por: {msg['cerebro']}")

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
        prompt_pedagogico = f"""
        Sos el asistente virtual de la cátedra de Educación Musical para alumnos de 1er año de secundaria (12 y 13 años).
        Respondeles siempre de 'vos' con un tono amigable, didáctico, directo y alentador.
        
        REGLA MAESTRA DE DEDUCCIÓN:
        - Usá ESTRICTAMENTE la teoría del texto del libro. 
        - Si te dan ejemplos que no están escritos o preguntan distancias entre notas específicas, APLICÁ la lógica teórica del texto para resolverlo.
        
        MEMORIA DE LA CHARLA:
        {historial}

        TEXTO DEL LIBRO ENCONTRADO AHORA:
        {contexto}

        NUEVA PREGUNTA DEL ALUMNO: {prompt_usuario}
        
        Si la pregunta no tiene NADA que ver con el cuadernillo ni con la charla previa, deciles amablemente que anoten la duda para preguntarle al profe Juan.
        """
        
        with st.spinner("🧠 Redactando la explicación..."):
            
            # --- LISTA AUTOMÁTICA DE CEREBROS ---
            # El sistema intentará usar el primero. Si falla, pasa al segundo, y así sucesivamente.
            lista_cerebros = [
                {"nombre": "OpenAI (GPT-4o)", "tipo": "openai", "clave": st.secrets.get("OPENAI_API_KEY")},
                {"nombre": "Gemini (Clave 1)", "tipo": "gemini", "clave": st.secrets.get("GEMINI_API_KEY_1")},
                {"nombre": "Gemini (Clave 2)", "tipo": "gemini", "clave": st.secrets.get("GEMINI_API_KEY_2")},
                {"nombre": "Gemini (Clave 3)", "tipo": "gemini", "clave": st.secrets.get("GEMINI_API_KEY_3")},
                {"nombre": "Gemini (Clave 4)", "tipo": "gemini", "clave": st.secrets.get("GEMINI_API_KEY_4")}
            ]
            
            respuesta = None
            ultimo_error = None
            cerebro_exitoso = ""

            for cerebro in lista_cerebros:
                # Si la clave está vacía o no existe, salta al siguiente cerebro
                if not cerebro["clave"]:
                    continue
                
                try:
                    if cerebro["tipo"] == "openai":
                        if not TIENE_OPENAI: continue
                        client = OpenAI(api_key=cerebro["clave"])
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt_pedagogico}]
                        )
                        respuesta = response.choices[0].message.content
                        cerebro_exitoso = cerebro["nombre"]
                        break # ¡Éxito! Salimos del bucle
                        
                    elif cerebro["tipo"] == "gemini":
                        genai.configure(api_key=cerebro["clave"])
                        modelo_gemini = genai.GenerativeModel('gemini-1.5-flash')
                        respuesta = modelo_gemini.generate_content(prompt_pedagogico).text
                        cerebro_exitoso = cerebro["nombre"]
                        break # ¡Éxito! Salimos del bucle
                        
                except Exception as e:
                    # Si este cerebro falla (por ej. falta de saldo), guardamos el error y el bucle sigue con el próximo
                    ultimo_error = e
                    continue

            # --- MOSTRAR EL RESULTADO ---
            if respuesta:
                st.write(respuesta)
                st.caption(f"⚡ Respondido por: {cerebro_exitoso}")
                st.session_state.mensajes.append({
                    "role": "assistant", 
                    "content": respuesta,
                    "cerebro": cerebro_exitoso
                })
            else:
                st.error("¡Uf! Todos mis cerebros están sobrecargados de tantas consultas. Esperen 1 minutito y vuelvan a intentar.")
