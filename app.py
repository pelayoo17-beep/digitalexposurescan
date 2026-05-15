import streamlit as st
from ddgs import DDGS

st.set_page_config(
    page_title="Escáner de Huella Digital",
    page_icon="🛡️"
)

st.title("🛡️ Escáner de Huella Digital")
st.write("Beta de análisis de exposición pública en internet.")

nombre = st.text_input("Nombre")
apellidos = st.text_input("Apellidos")
email = st.text_input("Email")
linkedin = st.text_input("LinkedIn")
instagram = st.text_input("Instagram")


def buscar(query):
    resultados_limpios = []

    try:
        with DDGS() as ddgs:
            resultados = ddgs.text(query, max_results=5)

            for r in resultados:
                resultados_limpios.append({
                    "Título": r.get("title", ""),
                    "URL": r.get("href", ""),
                    "Descripción": r.get("body", "")
                })

    except Exception as e:
        resultados_limpios.append({
            "Título": "Error",
            "URL": "",
            "Descripción": str(e)
        })

    return resultados_limpios


if st.button("Ejecutar análisis"):
    nombre_completo = f"{nombre} {apellidos}".strip()

    if not nombre_completo and not email and not linkedin and not instagram:
        st.error("Introduce al menos un dato para analizar.")
    else:
        queries = []

        if nombre_completo:
            queries.append(f'"{nombre_completo}"')
            queries.append(f'"{nombre_completo}" pdf')
            queries.append(f'"{nombre_completo}" CV OR curriculum')

        if email:
            queries.append(f'"{email}"')

        if linkedin:
            queries.append(f'"{linkedin}"')

        if instagram:
            queries.append(f'"{instagram}"')

        for query in queries:
            st.info(f"Buscando: {query}")

            resultados = buscar(query)

            st.success(f"Resultados encontrados: {len(resultados)}")

            for resultado in resultados:
                st.subheader(resultado["Título"])
                st.write(resultado["Descripción"])
                st.write(resultado["URL"])
                st.markdown("---")
