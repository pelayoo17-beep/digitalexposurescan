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
st.caption("Beta privada · Análisis preliminar de exposición pública")

st.info("Beta: los resultados pueden ser incompletos. Esta herramienta solo revisa información pública.")
st.success("RGPD: los datos introducidos no se almacenan. Solo se usan durante esta sesión.")

with st.expander("ℹ️ Aviso importante"):
    st.write("""
- No accede a cuentas privadas.
- No elimina información.
- No garantiza encontrar todos los resultados.
- Usa esta herramienta solo con consentimiento.
    """)

st.divider()

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre")
    apellidos = st.text_input("Apellidos")
    email = st.text_input("Email")

with col2:
    telefono = st.text_input("Teléfono")
    linkedin = st.text_input("LinkedIn")
    instagram = st.text_input("Instagram")

consentimiento = st.checkbox("Confirmo que tengo consentimiento para ejecutar este análisis.")


def buscar_duckduckgo(query):
    url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=6) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return [{
            "titulo": "No se pudo extraer automáticamente",
            "url": "https://www.google.com/search?q=" + urllib.parse.quote(query),
            "descripcion": "Abre este enlace para revisar la búsqueda manualmente."
        }]

    bloques = re.findall(
        r'<a[^>]*class="result__a"[^>]*href="(.*?)"[^>]*>(.*?)</a>',
        html,
        re.DOTALL
    )

    resultados = []

    for enlace, titulo in bloques[:3]:
        titulo_limpio = re.sub("<.*?>", "", titulo)
        titulo_limpio = unescape(titulo_limpio).strip()
        enlace = unescape(enlace).strip()

        resultados.append({
            "titulo": titulo_limpio,
            "url": enlace,
            "descripcion": "Resultado público encontrado."
        })

    if not resultados:
        resultados.append({
            "titulo": "No se pudieron extraer resultados automáticamente",
            "url": "https://www.google.com/search?q=" + urllib.parse.quote(query),
            "descripcion": "Abre este enlace para revisar resultados manualmente."
        })

    return resultados


def calcular_riesgo(texto):
    texto = texto.lower()
    puntos = 0
    motivos = []

    if "pdf" in texto or "cv" in texto or "curriculum" in texto:
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

    if puntos >= 40:
        riesgo = "Alto 🔴"
    elif puntos >= 20:
        riesgo = "Medio 🟠"
    else:
        riesgo = "Bajo 🟢"

    if not motivos:
        motivos.append("resultado público general")

    return riesgo, ", ".join(motivos)


def crear_queries():
    nombre_completo = f"{nombre} {apellidos}".strip()
    queries = []

    if nombre_completo:
        queries.append(f'"{nombre_completo}"')
        queries.append(f'"{nombre_completo}" pdf')
        queries.append(f'"{nombre_completo}" linkedin OR instagram')

    if email:
        queries.append(f'"{email}"')

    if telefono:
        queries.append(f'"{telefono}"')

    return queries[:5]


if st.button("🔎 Ejecutar análisis", type="primary"):

    if not consentimiento:
        st.error("Debes confirmar el consentimiento.")
        st.stop()

    queries = crear_queries()

    if not queries:
        st.error("Introduce al menos nombre, email o teléfono.")
        st.stop()

    resultados_globales = []

    progress = st.progress(0)
    status = st.empty()

    for i, query in enumerate(queries):
        status.write(f"Buscando: {query}")
        resultados = buscar_duckduckgo(query)

        for r in resultados:
            texto = r["titulo"] + " " + r["url"] + " " + r["descripcion"]
            riesgo, motivo = calcular_riesgo(texto)

            resultados_globales.append({
                "query": query,
                "titulo": r["titulo"],
                "url": r["url"],
                "descripcion": r["descripcion"],
                "riesgo": riesgo,
                "motivo": motivo
            })

        progress.progress((i + 1) / len(queries))

    status.write("Análisis completado.")

    st.divider()
    st.subheader("Resumen")

    c1, c2, c3 = st.columns(3)
    c1.metric("Búsquedas ejecutadas", len(queries))
    c2.metric("Resultados revisados", len(resultados_globales))
    c3.metric("Fecha", datetime.now().strftime("%d/%m/%Y"))

    st.divider()
    st.subheader("Resultados encontrados")

    for item in resultados_globales:
        st.markdown(f"### {item['titulo']}")
        st.write(item["descripcion"])
        st.markdown(f"[Abrir resultado]({item['url']})")
        st.write(f"**Riesgo:** {item['riesgo']}")
        st.write(f"**Motivo:** {item['motivo']}")
        st.caption(f"Búsqueda usada: {item['query']}")
        st.markdown("---")

    st.subheader("Recomendaciones")
    st.markdown("- Revisa manualmente los resultados encontrados.")
    st.markdown("- Si aparece un PDF/CV antiguo, solicita retirada.")
    st.markdown("- Si aparece email o teléfono, prioriza su eliminación.")
    st.markdown("- Revisa visibilidad pública de LinkedIn e Instagram.")

else:
    st.caption("Introduce los datos, confirma consentimiento y ejecuta el análisis.")