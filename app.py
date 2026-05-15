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
telefono = st.text_input("Teléfono")
linkedin = st.text_input("LinkedIn")
instagram = st.text_input("Instagram")
if st.button("Ejecutar análisis"):
   nombre_completo = f"{nombre} {apellidos}".strip()
   queries = []
   if nombre_completo:
       queries.append(f'"{nombre_completo}"')
       queries.append(f'"{nombre_completo}" pdf')
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
       st.error("Introduce al menos un dato para buscar.")
   else:
       st.success("Análisis iniciado correctamente.")
       for query in queries:
           st.subheader(f"Búsqueda: {query}")
           try:
               with DDGS() as ddgs:
                   resultados = list(ddgs.text(query, max_results=3))
               if not resultados:
st.info("Sin resultados.")
               for resultado in resultados:
                   titulo = resultado.get("title", "")
                   url = resultado.get("href", "")
                   descripcion = resultado.get("body", "")
                   st.markdown(f"**{titulo}**")
                   st.write(descripcion)
                   st.write(url)
                   st.markdown("---")
           except Exception as error:
               st.error(f"Error en la búsqueda: {error}")
