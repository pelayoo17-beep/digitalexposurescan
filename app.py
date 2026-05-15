import streamlit as st
import urllib.parse
import urllib.request
import re
from html import unescape
from datetime import datetime

st.set_page_config(
    page_title="Escáner de Huella Digital",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Escáner de Huella Digital")
st.caption("Beta privada · Análisis preliminar de exposición pública en internet")

st.info(
    "Esta herramienta está en fase beta. Los resultados pueden ser incompletos o contener falsos positivos. "
    "El objetivo es ayudarte a identificar señales públicas de exposición digital."
)

st.success(
    "Privacidad/RGPD: los datos introducidos no se almacenan en ninguna base de datos. "
    "Se usan únicamente durante la sesión para ejecutar las búsquedas públicas."
)

with st.expander("ℹ️ Qué hace y qué no hace esta herramienta", expanded=False):
    st.markdown("""
**Qué hace:**
- Busca resultados públicos indexados en internet.
- Revisa posibles coincidencias con nombre, email, teléfono, LinkedIn e Instagram.
- Clasifica hallazgos por nivel de riesgo estimado.

**Qué no hace:**
- No accede a cuentas privadas.
- No elimina información automáticamente.
- No garantiza que encuentre toda la información existente.
- No sustituye asesoramiento legal ni auditoría de ciberseguridad.
""")

st.divider()

st.subheader("Datos para el análisis")

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre", placeholder="Ej. Alba")
    apellidos = st.text_input("Apellidos", placeholder="Ej. Rodríguez Fernández")
    email = st.text_input("Email", placeholder="Ej. nombre@email.com")

with col2:
    telefono = st.text_input("Teléfono", placeholder="Ej. +34 600 000 000")
    linkedin = st.text_input("Perfil de LinkedIn", placeholder="https://www.linkedin.com/in/...")
    instagram = st.text_input("Perfil de Instagram", placeholder="https://www.instagram.com/...")

consentimiento = st.checkbox(
    "Confirmo que estoy analizando mis propios datos o cuento con consentimiento de la persona analizada."
)


def buscar_duckduckgo(query):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [{
            "titulo": "Error en búsqueda",
            "url": "",
            "descripcion": str(e)
        }]

    resultados = []

    bloques = re.findall(
        r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>.*?<a class="result__snippet".*?>(.*?)</a>',
        html,
        re.DOTALL
    )

    for enlace, titulo, descripcion in bloques[:5]:
        titulo_limpio = re.sub("<.*?>", "", titulo)
        descripcion_limpia = re.sub("<.*?>", "", descripcion)

        resultados.append({
            "titulo": unescape(titulo_limpio).strip(),
            "url": unescape(enlace).strip(),
            "descripcion": unescape(descripcion_limpia).strip()
        })

    return resultados


def calcular_riesgo(texto):
    texto = texto.lower()
    puntos = 0
    motivos = []

    if "pdf" in texto or "cv" in texto or "curriculum" in texto or "currículum" in texto:
        puntos += 30
        motivos.append("posible documento público")

    if "linkedin" in texto:
        puntos += 15
        motivos.append("exposición profesional")

    if "instagram" in texto:
        puntos += 15
        motivos.append("exposición social")

    if "email" in texto or "correo" in texto or "contacto" in texto:
        puntos += 20
        motivos.append("posible dato de contacto")

    if "teléfono" in texto or "telefono" in texto or "phone" in texto:
        puntos += 25
        motivos.append("posible teléfono visible")

    if "boe" in texto or "dni" in texto or "dirección" in texto or "address" in texto:
        puntos += 35
        motivos.append("posible dato sensible")

    if puntos >= 45:
        riesgo = "Alto 🔴"
    elif puntos >= 20:
        riesgo = "Medio 🟠"
    else:
        riesgo = "Bajo 🟢"

    if not motivos:
        motivos.append("resultado público general")

    return riesgo, puntos, ", ".join(motivos)


def crear_queries():
    nombre_completo = f"{nombre} {apellidos}".strip()
    queries = []

    if nombre_completo:
        queries.append(f'"{nombre_completo}"')
        queries.append(f'"{nombre_completo}" pdf')
        queries.append(f'"{nombre_completo}" cv OR curriculum')
        queries.append(f'"{nombre_completo}" linkedin')
        queries.append(f'"{nombre_completo}" instagram')

    if email:
        queries.append(f'"{email}"')

    if telefono:
        queries.append(f'"{telefono}"')

    if linkedin:
        queries.append(f'"{linkedin}"')

    if instagram:
        queries.append(f'"{instagram}"')

    return queries


if st.button("🔎 Ejecutar análisis real", type="primary"):
    if not consentimiento:
        st.error("Para ejecutar el análisis debes confirmar el consentimiento.")
        st.stop()

    queries = crear_queries()

    if not queries:
        st.error("Introduce al menos un dato para ejecutar la búsqueda.")
        st.stop()

    total_resultados = 0
    total_puntos = 0
    altos = 0
    medios = 0
    bajos = 0

    st.divider()
    st.subheader("Resumen del análisis")

    with st.spinner("Buscando resultados públicos indexados..."):
        resultados_globales = []

        for query in queries:
            resultados = buscar_duckduckgo(query)

            for resultado in resultados:
                texto = resultado["titulo"] + " " + resultado["descripcion"] + " " + resultado["url"]
                riesgo, puntos, motivo = calcular_riesgo(texto)

                total_resultados += 1
                total_puntos += puntos

                if "Alto" in riesgo:
                    altos += 1
                elif "Medio" in riesgo:
                    medios += 1
                else:
                    bajos += 1

                resultados_globales.append({
                    "query": query,
                    "titulo": resultado["titulo"],
                    "descripcion": resultado["descripcion"],
                    "url": resultado["url"],
                    "riesgo": riesgo,
                    "motivo": motivo,
                    "puntos": puntos
                })

    score = min(int(total_puntos / max(len(queries), 1)), 100)

    if score >= 60:
        nivel_global = "ALTO 🔴"
    elif score >= 30:
        nivel_global = "MEDIO 🟠"
    else:
        nivel_global = "BAJO 🟢"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Riesgo estimado", nivel_global)
    c2.metric("Score", f"{score}/100")
    c3.metric("Resultados revisados", total_resultados)
    c4.metric("Búsquedas ejecutadas", len(queries))

    st.progress(score / 100)

    st.caption(f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · Los datos no se almacenan.")

    st.divider()
    st.subheader("Resultados encontrados")

    tabs = st.tabs(["Todos", "Alto riesgo", "Medio/Bajo", "Búsquedas ejecutadas"])

    with tabs[0]:
        for item in resultados_globales:
            st.markdown(f"### {item['titulo']}")
            st.write(item["descripcion"])
            st.markdown(f"[Abrir resultado]({item['url']})")
            st.write(f"**Riesgo estimado:** {item['riesgo']}")
            st.write(f"**Motivo:** {item['motivo']}")
            st.caption(f"Búsqueda usada: {item['query']}")
            st.markdown("---")

    with tabs[1]:
        items_alto = [x for x in resultados_globales if "Alto" in x["riesgo"]]

        if not items_alto:
            st.info("No se han detectado resultados de alto riesgo en esta búsqueda.")
        else:
            for item in items_alto:
                st.markdown(f"### {item['titulo']}")
                st.write(item["descripcion"])
                st.markdown(f"[Abrir resultado]({item['url']})")
                st.write(f"**Motivo:** {item['motivo']}")
                st.markdown("---")

    with tabs[2]:
        for item in resultados_globales:
            if "Alto" not in item["riesgo"]:
                st.markdown(f"### {item['titulo']}")
                st.write(item["descripcion"])
                st.markdown(f"[Abrir resultado]({item['url']})")
                st.write(f"**Riesgo estimado:** {item['riesgo']}")
                st.markdown("---")

    with tabs[3]:
        for query in queries:
            st.code(query)

    st.divider()
    st.subheader("Recomendaciones iniciales")

    recomendaciones = [
        "Revisa manualmente los resultados de alto riesgo.",
        "Si aparece un PDF, CV o documento antiguo, solicita retirada al propietario de la web.",
        "Si aparece tu teléfono o email, prioriza su eliminación o sustitución por un canal profesional.",
        "Revisa la visibilidad pública de LinkedIn e Instagram.",
        "Repite la búsqueda cada cierto tiempo, especialmente después de cambiar de trabajo, publicar contenido o aparecer en eventos."
    ]

    for recomendacion in recomendaciones:
        st.markdown(f"- {recomendacion}")

else:
    st.caption("Introduce los datos, confirma el consentimiento y ejecuta el análisis.")