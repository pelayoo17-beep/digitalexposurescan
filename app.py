import streamlit as st
import pandas as pd
from datetime import datetime
st.set_page_config(
   page_title="Escáner de Huella Digital",
   page_icon="🛡️",
   layout="wide"
)
# -----------------------------
# Helpers
# -----------------------------
def risk_label(score):
   if score < 30:
       return "BAJO", "🟢"
   elif score < 65:
       return "MEDIO", "🟠"
   else:
       return "ALTO", "🔴"

def add_finding(findings, category, risk, finding, recommendation, points):
   findings.append({
       "Categoría": category,
       "Riesgo": risk,
       "Hallazgo": finding,
       "Recomendación": recommendation,
       "Puntos": points
   })

# -----------------------------
# Header
# -----------------------------
st.title("🛡️ Escáner de Huella Digital")
st.markdown("""
### Analiza tu exposición pública en internet
Esta beta identifica posibles riesgos de exposición digital a partir de la información facilitada por el usuario.
**Importante:** esta versión no elimina información ni accede a cuentas privadas. Solo genera una evaluación preliminar basada en indicadores de exposición pública.
""")
st.info("Beta privada: herramienta orientada a privacidad, RGPD y reducción de exposición digital.")
st.divider()
# -----------------------------
# Input form
# -----------------------------
with st.form("scan_form"):
   st.subheader("Datos para el análisis")
   col1, col2 = st.columns(2)
   with col1:
       nombre = st.text_input("Nombre completo *")
       ciudad = st.text_input("Ciudad")
       email = st.text_input("Email")
       telefono_visible = st.checkbox("Mi teléfono aparece públicamente en alguna web")
   with col2:
       linkedin = st.text_input("Perfil de LinkedIn")
       username = st.text_input("Username habitual")
       empresa = st.text_input("Empresa / sector")
       cv_publico = st.checkbox("Creo que puede haber CVs/PDFs míos publicados")
   st.caption("* Campos mínimos recomendados: nombre completo + email o username.")
   submitted = st.form_submit_button("Ejecutar análisis")
# -----------------------------
# Scan logic
# -----------------------------
if submitted:
   if not nombre:
       st.warning("Introduce al menos tu nombre completo para generar un análisis útil.")
       st.stop()
   findings = []
   score = 0
   # Base discoverability
   add_finding(
       findings,
       "Identidad pública",
       "Bajo",
       f"El nombre '{nombre}' puede ser utilizado para correlacionar resultados públicos.",
       "Revisar periódicamente resultados en buscadores usando nombre completo entre comillas.",
       10
   )
   score += 10
   if ciudad:
       add_finding(
           findings,
           "Correlación geográfica",
           "Medio",
           f"La ciudad '{ciudad}' reduce la ambigüedad y facilita identificar resultados asociados.",
           "Evitar combinar nombre completo + ciudad en perfiles no profesionales.",
           12
       )
       score += 12
   if email:
       add_finding(
           findings,
           "Email",
           "Alto",
           f"El email '{email}' puede estar asociado a brechas, registros o perfiles públicos.",
           "Comprobar exposición en bases de datos de brechas y activar MFA en servicios críticos.",
           25
       )
       score += 25
   if linkedin:
       add_finding(
           findings,
           "LinkedIn",
           "Medio",
           "El perfil profesional puede estar indexado y revelar cargo, empresa, red y trayectoria.",
           "Revisar visibilidad pública, actividad reciente y datos no necesarios del perfil.",
           15
       )
       score += 15
   if username:
       add_finding(
           findings,
           "Reutilización de username",
           "Medio",
           f"El username '{username}' puede permitir correlacionar cuentas entre plataformas.",
           "Evitar usar el mismo alias en plataformas personales, profesionales y foros.",
           18
       )
       score += 18
   if empresa:
       add_finding(
           findings,
           "Exposición profesional",
           "Medio",
           f"La asociación pública con '{empresa}' puede facilitar ingeniería social dirigida.",
           "Evitar publicar detalles internos, herramientas, proveedores, procesos o viajes laborales.",
           15
       )
       score += 15
   if telefono_visible:
       add_finding(
           findings,
           "Teléfono público",
           "Alto",
           "La exposición del teléfono incrementa riesgo de spam, phishing, smishing y doxxing.",
           "Solicitar retirada en webs públicas y limitar publicación del número personal.",
           30
       )
       score += 30
   if cv_publico:
       add_finding(
           findings,
           "Documentos públicos",
           "Alto",
           "CVs o PDFs antiguos pueden contener email, teléfono, dirección, metadatos o historial laboral.",
           "Buscar y retirar PDFs antiguos, especialmente CVs, listados, actas o documentos académicos.",
           25
       )
       score += 25
   score = min(score, 100)
   nivel, icono = risk_label(score)
   # -----------------------------
   # Results
   # -----------------------------
   st.divider()
   st.subheader("Resumen del análisis")
   colA, colB, colC, colD = st.columns(4)
   colA.metric("Riesgo global", f"{icono} {nivel}")
   colB.metric("Puntuación", f"{score}/100")
   colC.metric("Hallazgos", len(findings))
   colD.metric("Fecha", datetime.now().strftime("%d/%m/%Y"))
   st.progress(score / 100)
   if nivel == "ALTO":
       st.error("Tu exposición digital preliminar parece elevada. Conviene priorizar retirada de datos sensibles y revisión de perfiles públicos.")
   elif nivel == "MEDIO":
       st.warning("Tu exposición digital preliminar es moderada. Hay margen claro para reducir trazabilidad y riesgo.")
   else:
       st.success("Tu exposición digital preliminar parece baja, aunque conviene revisar periódicamente resultados públicos.")
   st.divider()
   st.subheader("Hallazgos detectados")
   df = pd.DataFrame(findings)
   st.dataframe(
       df[["Categoría", "Riesgo", "Hallazgo", "Recomendación"]],
       use_container_width=True,
       hide_index=True
   )
   st.divider()
   st.subheader("Plan de acción recomendado")
   high_risks = df[df["Riesgo"] == "Alto"]
   medium_risks = df[df["Riesgo"] == "Medio"]
   if not high_risks.empty:
       st.markdown("#### Prioridad alta")
       for _, row in high_risks.iterrows():
           st.markdown(f"- **{row['Categoría']}**: {row['Recomendación']}")
   if not medium_risks.empty:
       st.markdown("#### Prioridad media")
       for _, row in medium_risks.iterrows():
           st.markdown(f"- **{row['Categoría']}**: {row['Recomendación']}")
   st.markdown("#### Higiene digital general")
   st.markdown("""
- Buscar tu nombre completo entre comillas en Google/Bing.
- Revisar resultados con combinaciones de ciudad, empresa, email y username.
- Eliminar CVs antiguos, PDFs indexados y perfiles abandonados.
- Separar identidad profesional y personal cuando sea posible.
- Activar doble factor de autenticación en email, LinkedIn y servicios críticos.
""")
   st.divider()
   st.caption(
       "Disclaimer: análisis preliminar beta. No constituye asesoramiento legal, ciberseguridad forense ni garantía de eliminación de datos."
   )
else:
   st.markdown("""
#### Qué analiza esta beta
- Exposición de identidad pública  
- Riesgo asociado a email  
- Correlación por username  
- Exposición profesional  
- Posibles documentos públicos  
- Riesgo de teléfono visible  
Introduce tus datos y ejecuta el análisis para obtener una primera puntuación de exposición.
""")
