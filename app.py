import streamlit as st
import urllib.parse
import urllib.request
import re
from html import unescape
from datetime import datetime

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Escáner de Huella Digital",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("🛡️ Escáner de Huella Digital")

st.caption(
    "Beta privada · Análisis preliminar de exposición pública en internet"
)

st.info(
    "Esta herramienta busca información públicamente accesible relacionada contigo. "
    "Los resultados pueden ser incompletos o contener falsos positivos."
)

st.success(
    "Privacidad/RGPD: los datos introducidos NO se almacenan ni se guardan en bases de datos. "
    "Solo se utilizan temporalmente para ejecutar búsquedas públicas."
)

with st.expander("ℹ️ Información importante"):

    st.markdown("""
### Qué hace esta herramienta
- Busca resultados públicos indexados en internet
- Detecta posibles señales de exposición digital
- Revisa PDFs, CVs y perfiles públicos
- Analiza presencia en LinkedIn e Instagram

### Qué NO hace
- No accede a cuentas privadas
- No elimina información automáticamente
- No garantiza encontrar toda la exposición existente
- No sustituye asesoramiento legal o auditorías de ciberseguridad
""")

st.divider()

# ---------------------------------------------------
# FORM
# ---------------------------------------------------

st.subheader("Datos para el análisis")

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input(
        "Nombre",
        placeholder="Ej. Alba"
    )

    apellidos = st.text_input(
        "Apellidos",
        placeholder="Ej. Rodríguez Fernández"
    )

    email = st.text_input(
        "Email",
        placeholder="Ej. nombre@email.com"
    )

with col2:
    telefono = st.text_input(
        "Teléfono",
        placeholder="Ej. +34 600 000 000"
    )

    linkedin = st.text_input(
        "Perfil de LinkedIn",
        placeholder="https://linkedin.com/in/..."
    )

    instagram = st.text_input(
        "Perfil de Instagram",
        placeholder="https://instagram.com/..."
    )

consentimiento = st.checkbox(
    "Confirmo que estoy analizando mis propios datos o cuento con consentimiento."
)

# ---------------------------------------------------
# SEARCH FUNCTION
# ---------------------------------------------------

def buscar_duckduckgo(query):

    url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            html = response.read().decode(
                "utf-8",
                errors="ignore"
            )

    except Exception as e:

        return [{
            "titulo": "Error en búsqueda",
            "url": "",
            "descripcion": str(e)
        }]

    resultados = []

    # Resultados principales
    bloques = re.findall(
        r'<a[^>]*class="result__a"[^>]*href="(.*?)"[^>]*>(.*?)</a>',
        html,
        re.DOTALL
    )

    # Snippets
    snippets = re.findall(
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        html,
        re.DOTALL
    )

    for i, bloque in enumerate(bloques[:5]):

        enlace = bloque[0]
        titulo = bloque[1]

        titulo_limpio = re.sub(
            "<.*?>",
            "",
            titulo
        )

        titulo_limpio = unescape(
            titulo_limpio
        ).strip()

        descripcion = ""

        if i < len(snippets):

            descripcion = re.sub(
                "<.*?>",
                "",
                snippets[i]
            )

            descripcion = unescape(
                descripcion
            ).strip()

        enlace = unescape(enlace).strip()

        resultados.append({
            "titulo": titulo_limpio,
            "url": enlace,
            "descripcion": descripcion
        })

    # Fallback
    if not resultados:

        resultados.append({
            "titulo": "No se pudieron extraer resultados automáticamente",
            "url": "https://www.google.com/search?q=" + urllib.parse.quote(query),
            "descripcion": "Abre esta búsqueda manual para revisar resultados públicos."
        })

    return resultados

# ---------------------------------------------------
# RISK ENGINE
# ---------------------------------------------------

def calcular_riesgo(texto):

    texto = texto.lower()

    puntos = 0
    motivos = []

    if (
        "pdf" in texto
        or "cv" in texto
        or "curriculum" in texto
        or "currículum" in texto
    ):

        puntos += 30
        motivos.append("posible documento público")

    if "linkedin" in texto:

        puntos += 15
        motivos.append("exposición profesional")

    if "instagram" in texto:

        puntos += 15
        motivos.append("exposición social")

    if (
        "email" in texto
        or "correo" in texto
        or "contacto" in texto
    ):

        puntos += 20
        motivos.append("posible dato de contacto")

    if (
        "teléfono" in texto
        or "telefono" in texto
        or "phone" in texto
    ):

        puntos += 25
        motivos.append("posible teléfono visible")

    if (
        "boe" in texto
        or "dni" in texto
        or "dirección" in texto
        or "address" in texto
    ):

        puntos += 35
        motivos.append("posible dato sensible")

    # Riesgo
    if puntos >= 45:

        riesgo = "Alto 🔴"

    elif puntos >= 20:

        riesgo = "Medio 🟠"

    else:

        riesgo = "Bajo 🟢"

    if not motivos:

        motivos.append("resultado público general")

    return riesgo, puntos, ", ".join(motivos)

# ---------------------------------------------------
# QUERY GENERATOR
# ---------------------------------------------------

def crear_queries():

    queries = []

    nombre_completo = (
        f"{nombre} {apellidos}"
    ).strip()

    if nombre_completo:

        queries.append(
            f'"{nombre_completo}"'
        )

        queries.append(
            f'"{nombre_completo}" pdf'
        )

        queries.append(
            f'"{nombre_completo}" cv OR curriculum'
        )

        queries.append(
            f'"{nombre_completo}" linkedin'
        )

        queries.append(
            f'"{nombre_completo}" instagram'
        )

    if email:

        queries.append(
            f'"{email}"'
        )

    if telefono:

        queries.append(
            f'"{telefono}"'
        )

    if linkedin:

        queries.append(
            linkedin
        )

    if instagram:

        queries.append(
            instagram
        )

    return queries

# ---------------------------------------------------
# EXECUTION
# ---------------------------------------------------

if st.button(
    "🔎 Ejecutar análisis real",
    type="primary"
):

    if not consentimiento:

        st.error(
            "Debes confirmar el consentimiento."
        )

        st.stop()

    queries = crear_queries()

    if not queries:

        st.error(
            "Introduce al menos un dato."
        )

        st.stop()

    st.divider()

    st.subheader(
        "Resumen del análisis"
    )

    resultados_globales = []

    total_resultados = 0
    total_puntos = 0

    with st.spinner(
        "Buscando resultados públicos..."
    ):

        for query in queries:

            resultados = buscar_duckduckgo(
                query
            )

            for resultado in resultados:

                texto = (
                    resultado["titulo"]
                    + " "
                    + resultado["descripcion"]
                    + " "
                    + resultado["url"]
                )

                riesgo, puntos, motivo = calcular_riesgo(
                    texto
                )

                total_resultados += 1
                total_puntos += puntos

                resultados_globales.append({

                    "query": query,

                    "titulo": resultado["titulo"],

                    "descripcion": resultado["descripcion"],

                    "url": resultado["url"],

                    "riesgo": riesgo,

                    "motivo": motivo,

                    "puntos": puntos
                })

    # ---------------------------------------------------
    # GLOBAL SCORE
    # ---------------------------------------------------

    score = min(
        int(total_puntos / max(len(queries), 1)),
        100
    )

    if score >= 60:

        nivel_global = "ALTO 🔴"

    elif score >= 30:

        nivel_global = "MEDIO 🟠"

    else:

        nivel_global = "BAJO 🟢"

    # ---------------------------------------------------
    # METRICS
    # ---------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Riesgo estimado",
        nivel_global
    )

    c2.metric(
        "Score",
        f"{score}/100"
    )

    c3.metric(
        "Resultados revisados",
        total_resultados
    )

    c4.metric(
        "Búsquedas ejecutadas",
        len(queries)
    )

    st.progress(score / 100)

    st.caption(
        f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    st.divider()

    # ---------------------------------------------------
    # RESULTS
    # ---------------------------------------------------

    st.subheader(
        "Resultados encontrados"
    )

    if not resultados_globales:

        st.warning(
            "No se encontraron resultados."
        )

    else:

        for item in resultados_globales:

            with st.container():

                st.markdown(
                    f"### {item['titulo']}"
                )

                st.write(
                    item["descripcion"]
                )

                st.markdown(
                    f"[Abrir resultado]({item['url']})"
                )

                st.write(
                    f"**Riesgo estimado:** {item['riesgo']}"
                )

                st.write(
                    f"**Motivo:** {item['motivo']}"
                )

                st.caption(
                    f"Búsqueda usada: {item['query']}"
                )

                st.markdown("---")

    # ---------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------

    st.subheader(
        "Recomendaciones iniciales"
    )

    recomendaciones = [

        "Revisar manualmente los resultados detectados.",

        "Solicitar retirada de PDFs o CVs antiguos si contienen datos personales.",

        "Reducir exposición de email y teléfono cuando sea posible.",

        "Revisar privacidad pública de LinkedIn e Instagram.",

        "Repetir el análisis periódicamente."
    ]

    for recomendacion in recomendaciones:

        st.markdown(
            f"- {recomendacion}"
        )

else:

    st.caption(
        "Introduce los datos y ejecuta el análisis."
    )