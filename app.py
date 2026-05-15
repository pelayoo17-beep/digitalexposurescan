import re
from datetime import datetime
import pandas as pd
import streamlit as st
from ddgs import DDGS
# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(
   page_title="Escáner de Huella Digital",
   page_icon="🛡️",
   layout="wide"
)
# -----------------------------------
# FUNCIONES
# -----------------------------------
def buscar_web(query, max_results=5):
   try:
       with DDGS() as ddgs:
           results = list(ddgs.text(query, max_results=max_results))
       return results
   except Exception as e:
       return [{
           "title": "Error de búsqueda",
           "href": "",
           "body": str(e)
       }]

def detectar_riesgo(texto, email, telefono):
   texto_lower = texto.lower()
   puntos = 0
   motivos = []
   # Email
   if email and email.lower() in texto_lower:
       puntos += 30
       motivos.append("Email visible públicamente")
   # Teléfono
   telefono_limpio = re.sub(r"\D", "", telefono) if telefono else ""
   if telefono and telefono_limpio in re.sub(r"\D", "", texto):
       puntos += 35
       motivos.append("Teléfono visible públicamente")
   # Keywords sensibles
   palabras_alto = [
       "dni",
       "dirección",
       "address",
       "cv",
       "curriculum",
       "currículum",
       "pdf",
       "boe"
   ]
   palabras_medio = [
       "linkedin",
       "instagram",
       "empresa",
       "trabajo",
       "perfil",
       "contacto"
   ]
   if any(p in texto_lower for p in palabras_alto):
       puntos += 25
       motivos.append("Posible documento sensible público")
   if any(p in texto_lower for p in palabras_medio):
       puntos += 10
       motivos.append("Exposición profesional/social")
   # Riesgo
   if puntos >= 45:
       riesgo = "Alto"
   elif puntos >= 20:
       riesgo = "Medio"
   else:
       riesgo = "Bajo"
   if not motivos:
       motivos.append("Resultado público genérico")
   return riesgo, min(puntos, 100), ", ".join(motivos)

def crear_queries(
   nombre,
   apellidos,
   email,
   telefono,
   linkedin,
   instagram
):
   nombre_completo = f"{nombre} {apellidos}".strip()
   queries = []
   if nombre_completo:
       queries.extend([
           f'"{nombre_completo}"',
           f'"{nombre_completo}" pdf',
           f'"{nombre_completo}" CV OR curriculum',
           f'"{nombre_completo}" email OR teléfono OR contacto',
           f'"{nombre_completo}" site:linkedin.com/in',
           f'"{nombre_completo}" site:instagram.com',
       ])
   if email:
       queries.append(f'"{email}"')
   if telefono:
       queries.append(f'"{telefono}"')
   if linkedin:
       queries.append(f'"{linkedin}"')
   if instagram:
       queries.append(f'"{instagram}"')
   return queries

# -----------------------------------
# UI
# -----------------------------------
st.title("🛡️ Escáner de Huella Digital")
st.markdown("""
### Analiza tu exposición pública en internet
Esta beta busca información públicamente accesible relacionada contigo.
#### Qué analiza:
- Resultados indexados en buscadores
- Exposición de email y teléfono
- PDFs y CVs públicos
- LinkedIn e Instagram
- Correlación de identidad digital
⚠️ Esta herramienta NO accede a cuentas privadas ni elimina información.
""")
st.warning(
   "Utiliza esta herramienta únicamente con consentimiento de la persona analizada."
)
st.divider()
# -----------------------------------
# FORMULARIO
# -----------------------------------
with st.form("scan_form"):
   st.subheader("Datos para el análisis")
   col1, col2 = st.columns(2)
   with col1:
       nombre = st.text_input("Nombre")
       apellidos = st.text_input("Apellidos")
       email = st.text_input("Correo electrónico")
   with col2:
       telefono = st.text_input("Teléfono")
       linkedin = st.text_input("Perfil de LinkedIn")
       instagram = st.text_input("Perfil de Instagram")
   submitted = st.form_submit_button("Ejecutar análisis")
# -----------------------------------
# EJECUCIÓN
# -----------------------------------
if submitted:
   if not nombre and not apellidos and not email and not telefono:
       st.error(
           "Introduce al menos nombre/apellidos, email o teléfono."
       )
       st.stop()
   queries = crear_queries(
       nombre,
       apellidos,
       email,
       telefono,
       linkedin,
       instagram
   )
   todos_resultados = []
   with st.spinner("Buscando exposición pública en internet..."):
       for query in queries:
           resultados = buscar_web(query, max_results=5)
           for r in resultados:
               titulo = r.get("title", "")
               url = r.get("href", "")
               snippet = r.get("body", "")
               texto = f"{titulo} {snippet} {url}"
               riesgo, puntos, motivo = detectar_riesgo(
                   texto,
                   email,
                   telefono
               )
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
       st.success(
           "No se han encontrado resultados públicos relevantes."
       )
       st.stop()
   # -----------------------------------
   # SCORE GLOBAL
   # -----------------------------------
   score = min(
       int(df["Puntos"].sum() / max(len(queries), 1)),
       100
   )
   if score >= 60:
       nivel = "ALTO 🔴"
   elif score >= 30:
       nivel = "MEDIO 🟠"
   else:
       nivel = "BAJO 🟢"
   # -----------------------------------
   # RESUMEN
   # -----------------------------------
   st.divider()
   st.subheader("Resumen del análisis")
   c1, c2, c3 = st.columns(3)
   c1.metric("Nivel de riesgo", nivel)
   c2.metric("Score", f"{score}/100")
   c3.metric("Resultados analizados", len(df))
   st.progress(score / 100)
   # -----------------------------------
   # RESULTADOS
   # -----------------------------------
   st.divider()
   st.subheader("Resultados encontrados")
   st.dataframe(
       df[
           [
               "Riesgo",
               "Motivo",
               "Título",
               "URL",
               "Búsqueda"
           ]
       ],
       use_container_width=True,
       hide_index=True
   )
   # -----------------------------------
   # RESULTADOS ALTO RIESGO
   # -----------------------------------
   st.divider()
   st.subheader("Resultados de alto riesgo")
   altos = df[df["Riesgo"] == "Alto"]
   if altos.empty:
st.info(
           "No se han detectado resultados de alto riesgo en esta búsqueda."
       )
   else:
       for _, row in altos.iterrows():
           st.markdown(f"### {row['Título']}")
           st.markdown(
               f"**Riesgo:** {row['Riesgo']}"
           )
           st.markdown(
               f"**Motivo:** {row['Motivo']}"
           )
           st.markdown(
               f"**URL:** {row['URL']}"
           )
           st.markdown("---")
   # -----------------------------------
   # RECOMENDACIONES
   # -----------------------------------
   st.divider()
   st.subheader("Recomendaciones")
   recomendaciones = []
   if any(
       df["Motivo"].str.contains(
           "Email",
           case=False,
           na=False
       )
   ):
       recomendaciones.append(
           "Tu email aparece en resultados públicos. Revisa dónde está publicado."
       )
   if any(
       df["Motivo"].str.contains(
           "Teléfono",
           case=False,
           na=False
       )
   ):
       recomendaciones.append(
           "Tu teléfono aparece públicamente. Prioriza su retirada."
       )
   if any(
       df["Motivo"].str.contains(
           "documento",
           case=False,
           na=False
       )
   ):
       recomendaciones.append(
           "Se han detectado posibles PDFs/CVs públicos."
       )
   recomendaciones.append(
       "Revisa la visibilidad pública de LinkedIn e Instagram."
   )
   recomendaciones.append(
       "Busca regularmente tu nombre completo entre comillas en Google."
   )
   for rec in recomendaciones:
       st.markdown(f"- {rec}")
   st.divider()
   st.caption(
       f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
   )
   st.caption(
       "Beta experimental · No constituye asesoramiento legal ni garantía de eliminación de datos."
   )
