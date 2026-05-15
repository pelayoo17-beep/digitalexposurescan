import re
from datetime import datetime
import pandas as pd
import streamlit as st
from ddgs import DDGS

st.set_page_config(
   page_title="Escáner de Huella Digital",
   page_icon="🛡️",
   layout="wide"
)

def buscar_web(query, max_results=5):
   try:
       with DDGS() as ddgs:
           results = list(ddgs.text(query, max_results=max_results))
       return results
   except Exception as e:
       return [{"title": "Error de búsqueda", "href": "", "body": str(e)}]

def detectar_riesgo(texto, email, telefono):
   texto_lower = texto.lower()
   puntos = 0
   razones = []
   if email and email.lower() in texto_lower:
       puntos += 30
       razones.append("Email visible")
   if telefono and re.sub(r"\D", "", telefono) in re.sub(r"\D", "", texto):
       puntos += 35
       razones.append("Teléfono visible")
   palabras_alto = ["dni", "dirección", "address", "cv", "curriculum", "currículum", "pdf", "boe"]
   palabras_medio = ["linkedin", "instagram", "empresa", "trabajo", "perfil", "contacto"]
   if any(p in texto_lower for p in palabras_alto):
       puntos += 25
       razones.append("Posible dato sensible/documento público")
   if any(p in texto_lower for p in palabras_medio):
       puntos += 10
       razones.append("Exposición profesional/social")
   if puntos >= 45:
       riesgo = "Alto"
   elif puntos >= 20:
       riesgo = "Medio"
   else:
       riesgo = "Bajo"
   return riesgo, min(puntos, 100), ", ".join(razones) if razones else "Resultado público genérico"

def crear_queries(nombre, apellidos, email, telefono, linkedin, instagram):
   nombre_completo = f"{nombre} {apellidos}".strip()
   queries = []
   if nombre_completo:
       queries += [
           f'"{nombre_completo}"',
           f'"{nombre_completo}" pdf',
           f'"{nombre_completo}" CV OR curriculum',
           f'"{nombre_completo}" email OR teléfono OR contacto',
           f'"{nombre_completo}" site:linkedin.com/in',
           f'"{nombre_completo}" site:instagram.com',
       ]
   if email:
       queries.append(f'"{email}"')
   if telefono:
       queries.append(f'"{telefono}"')
   if linkedin:
       queries.append(f'"{linkedin}"')
   if instagram:
       queries.append(f'"{instagram}"')
   return queries

st.title("🛡️ Escáner de Huella Digital")
st.markdown("""
Esta beta busca exposición pública real en internet a partir de los datos que introduces.
No accede a cuentas privadas, no elimina datos y no hace hacking. Solo revisa resultados públicos indexados.
""")
st.warning("Usar solo con consentimiento de la persona analizada.")
with st.form("formulario"):
   col1, col2 = st.columns(2)
   with col1:
       nombre = st.text_input("Nombre")
       apellidos = st.text_input("Apellidos")
       email = st.text_input("Correo electrónico")
   with col2:
       telefono = st.text_input("Teléfono")
       linkedin = st.text_input("Perfil de LinkedIn")
       instagram = st.text_input("Perfil de Instagram")
   ejecutar = st.form_submit_button("Ejecutar análisis real")
if ejecutar:
   if not nombre and not apellidos and not email and not telefono:
       st.error("Introduce al menos nombre/apellidos, email o teléfono.")
       st.stop()
   queries = crear_queries(nombre, apellidos, email, telefono, linkedin, instagram)
   todos_resultados = []
   with st.spinner("Buscando exposición pública en web..."):
       for query in queries:
           resultados = buscar_web(query, max_results=5)
           for r in resultados:
               titulo = r.get("title", "")
               url = r.get("href", "")
               snippet = r.get("body", "")
               texto = f"{titulo} {snippet} {url}"
               riesgo, puntos, motivo = detectar_riesgo(texto, email, telefono)
               todos_resultados.append({
                   "Búsqueda": query,
                   "Riesgo": riesgo,
                   "Puntos": puntos,
                   "Motivo": motivo,
                   "Título": titulo,
                   "URL": url,
                   "Descripción": snippet
               })
   df = pd.DataFrame(todos_resultados)
   if df.empty:
       st.success("No se han encontrado resultados públicos relevantes.")
       st.stop()
   score = min(int(df["Puntos"].sum() / max(len(queries), 1)), 100)
   if score >= 60:
       nivel = "ALTO 🔴"
   elif score >= 30:
       nivel = "MEDIO 🟠"
   else:
       nivel = "BAJO 🟢"
   st.divider()
   st.subheader("Resumen")
   c1, c2, c3 = st.columns(3)
   c1.metric("Riesgo estimado", nivel)
   c2.metric("Score", f"{score}/100")
   c3.metric("Resultados revisados", len(df))
   st.progress(score / 100)
   st.divider()
   st.subheader("Resultados encontrados")
   st.dataframe(
       df[["Riesgo", "Motivo", "Título", "URL", "Búsqueda"]],
       use_container_width=True,
       hide_index=True
   )
   st.divider()
   st.subheader("Resultados de alto riesgo")
   altos = df[df["Riesgo"] == "Alto"]
   if altos.empty:
st.info("No se han detectado resultados de alto riesgo en esta búsqueda.")
   else:
       for _, row in altos.iterrows():
           st.markdown(f"**{row['Título']}**")
           st.markdown(f"- Riesgo: **{row['Riesgo']}**")
           st.markdown(f"- Motivo: {row['Motivo']}")
           st.markdown(f"- URL: {row['URL']}")
           st.markdown("---")
   st.divider()
   st.subheader("Recomendaciones")
   recomendaciones = []
   if any(df["Motivo"].str.contains("Email visible", case=False, na=False)):
       recomendaciones.append("El correo aparece en resultados públicos. Revisar dónde está publicado y solicitar retirada si no es necesario.")
   if any(df["Motivo"].str.contains("Teléfono visible", case=False, na=False)):
       recomendaciones.append("El teléfono aparece en resultados públicos. Priorizar retirada porque aumenta riesgo de spam, smishing y doxxing.")
   if any(df["Motivo"].str.contains("documento", case=False, na=False)):
       recomendaciones.append("Hay posibles PDFs/CVs/documentos indexados. Revisar si contienen datos personales o metadatos.")
   recomendaciones.append("Buscar también combinaciones con ciudad, empresa, universidad y usernames habituales.")
   recomendaciones.append("Revisar configuración pública de LinkedIn e Instagram.")
   for rec in recomendaciones:
       st.markdown(f"- {rec}")
   st.caption(f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
