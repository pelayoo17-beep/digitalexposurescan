import streamlit as st
import urllib.parse
import urllib.request
import re
from html import unescape

st.set_page_config(
    page_title="Escáner de Huella Digital",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Escáner de Huella Digital")

st.write("Busca exposición pública real en internet usando resultados web indexados.")

nombre = st.text_input("Nombre")
apellidos = st.text_input("Apellidos")
email = st.text_input("Email")
telefono = st.text_input("Teléfono")
linkedin = st.text_input("Perfil de LinkedIn")
instagram = st.text_input("Perfil de Instagram")


def buscar_duckduckgo(query):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
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

    if "pdf" in texto or "cv" in texto or "curriculum" in texto:
        puntos += 30
        motivos.append("Posible documento público")

    if "linkedin" in texto:
        puntos += 15
        motivos.append("Exposición profesional")

    if "instagram" in texto:
        puntos += 15
        motivos.append("Exposición social")

    if "email" in texto or "correo" in texto or "contacto" in texto:
        puntos += 20
        motivos.append("Posible dato de contacto")

    if "teléfono" in texto or "phone" in texto:
        puntos += 25
        motivos.append("Posible teléfono visible")

    if puntos >= 40:
        riesgo = "Alto"
    elif puntos >= 20:
        riesgo = "Medio"
    else:
        riesgo = "Bajo"

    if not motivos:
        motivos.append("Resultado público general")

    return riesgo, ", ".join(motivos)


if st.button("Ejecutar análisis real"):

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

    if not queries:
        st.error("Introduce al menos un dato.")
        st.stop()

    st.success("Búsqueda real iniciada.")

    total_resultados = 0

    for query in queries:

        st.subheader(f"🔎 Búsqueda: {query}")

        resultados = buscar_duckduckgo(query)

        if not resultados:
            st.info("No se encontraron resultados.")
            continue

        for resultado in resultados:
            total_resultados += 1

            texto = resultado["titulo"] + " " + resultado["descripcion"] + " " + resultado["url"]
            riesgo, motivo = calcular_riesgo(texto)

            st.markdown(f"### {resultado['titulo']}")
            st.write(resultado["descripcion"])
            st.write(resultado["url"])
            st.write(f"**Riesgo estimado:** {riesgo}")
            st.write(f"**Motivo:** {motivo}")
            st.markdown("---")

    st.info(f"Resultados analizados: {total_resultados}")