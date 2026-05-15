import re
from datetime import datetime
import pandas as pd
import streamlit as st
from ddgs import DDGS

# -----------------------------------
# CONFIGURACIÓN
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
           resultados = list(ddgs.text(query, max_results=max_results))
       return resultados
   except Exception as error:
       return [{
           "title": "Error de búsqueda",
           "href": "",
           "body": str(error)
       }]

def limpiar_numero(valor):
   return re.sub(r"\D", "", valor or "")

def detectar_riesgo(texto, email, telefono):
   texto = texto or ""
   texto_lower = texto.lower()
   texto_numeros = limpiar_numero(texto)
   puntos = 0
   motivos = []
   # EMAIL
   if email and email.lower() in texto_lower:
       puntos += 35
       motivos.append("Email visible públicamente")
   # TELÉFONO
   telefono_limpio = limpiar_numero(telefono)
   if telefono_limpio and telefono_limpio in texto_numeros:
       puntos += 40
       motivos.append("Teléfono visible públicamente")
   # PALABRAS CLAVE ALTO RIESGO
   palabras_alto = [
       "dni",
       "dirección",
       "address",
       "cv",
       "curriculum",
       "currículum",
       "pdf",
       "boe",
       "teléfono",
       "phone"
   ]
   # PALABRAS CLAVE RIESGO MEDIO
   palabras_medio = [
       "linkedin",
       "instagram",
       "empresa",
       "trabajo",
       "perfil",
       "contacto",
       "email",
       "correo"
   ]
   if any(palabra in texto_lower for palabra in palabras_alto):
       puntos += 25
       motivos.append("Posible documento o dato sensible público")
   if any(palabra in texto_lower for palabra in palabras_medio):
       puntos += 10
       motivos.append("Exposición profesional o social")
   # NIVEL RIESGO
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
       queries.append(f'"{nombre_completo}"')
       queries.append(f'"{nombre_completo}" pdf')
       queries.append(f'"{nombre_completo}" CV OR curriculum')
       queries.append(f'"{nombre_completo}" email OR teléfono OR contacto')
       queries.append(f'"{nombre_completo}" site:linkedin.com/in')
       queries.append(f'"{nombre_completo}" site:instagram.com')
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
# INTERFAZ
# -----------------------------------
st.title("🛡️ Escáner de Huella Digital")
st.markdown("""
### Analiza tu exposición pública en internet
Esta herramienta beta busca información públicamente accesible relacionada contigo.
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
   if (
       not nombre
       and not apellidos
       and not email
       and not telefono
       and not linkedin
       and not instagram
   ):
       st.error("Introduce al menos un dato.")
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
           for resultado in resultados:
               titulo = resultado.get("title", "")
               url = resultado.get("href", "")
               descripcion = resultado.get("body", "")
               texto_completo = f"{titulo} {url} {descripcion}"
               riesgo, puntos, motivo = detectar_riesgo(
                   texto_completo,
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
                   "Descripción": descripcion
               })
   df = pd.DataFrame(todos_resultados)
   if df.empty:
       st.success(
           "No se han encontrado resultados públicos relevantes."
       )
       st.stop()
   # -----------------------------------
   # SCORE
   # -----------------------------------
   score = int(df["Puntos"].sum() / max(len(queries), 1))
   score = min(score, 100)
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
   col_a, col_b, col_c = st.columns(3)
   col_a.metric("Nivel de riesgo", nivel)
   col_b.metric("Score", f"{score}/100")
   col_c.metric("Resultados analizados", len(df))
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
   # ALTO RIESGO
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
           st.markdown(f"**Riesgo:** {row['Riesgo']}")
           st.markdown(f"**Motivo:** {row['Motivo']}")
           st.markdown(f"**URL:** {row['URL']}")
           st.markdown("---")
   # -----------------------------------
   # RECOMENDACIONES
   # -----------------------------------
   st.divider()
   st.subheader("Recomendaciones")
   recomendaciones = []
   if df["Motivo"].str.contains(
       "Email",
       case=False,
       na=False
   ).any():
       recomendaciones.append(
           "Tu email aparece en resultados públicos. Revisa dónde está publicado."
       )
   if df["Motivo"].str.contains(
       "Teléfono",
       case=False,
       na=False
   ).any():
       recomendaciones.append(
           "Tu teléfono aparece públicamente. Prioriza su retirada."
       )
   if df["Motivo"].str.contains(
       "documento",
       case=False,
       na=False
   ).any():
       recomendaciones.append(
           "Se han detectado posibles PDFs, CVs o documentos públicos."
       )
   recomendaciones.append(
       "Revisa la visibilidad pública de LinkedIn e Instagram."
   )
   recomendaciones.append(
       "Busca regularmente tu nombre completo entre comillas en Google."
   )
   recomendaciones.append(
       "Separa identidad profesional y personal cuando sea posible."
   )
   for recomendacion in recomendaciones:
       st.markdown(f"- {recomendacion}")
   # -----------------------------------
   # FOOTER
   # -----------------------------------
   st.divider()
   st.caption(
       f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
   )
   st.caption(
       "Beta experimental · No constituye asesoramiento legal ni garantía de eliminación de datos."
   )
else:
st.info(
       "Introduce los datos y pulsa 'Ejecutar análisis'."
   )
