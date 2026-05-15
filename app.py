import streamlit as st
import pandas as pd
from datetime import datetime
st.set_page_config(
   page_title="Escáner de Huella Digital",
   page_icon="🛡️",
   layout="wide"
)
st.title("🛡️ Escáner de Huella Digital")
st.markdown("""
### Reduce tu exposición digital profesional y personal
Esta herramienta beta analiza riesgos de exposición pública en internet.
#### Comprobaciones actuales:
- Visibilidad en buscadores
- Exposición profesional
- Riesgo de email expuesto
- Reutilización de usernames
- Correlación de identidad digital
""")
st.divider()
col1, col2 = st.columns(2)
with col1:
   nombre = st.text_input("Nombre completo")
   ciudad = st.text_input("Ciudad")
   email = st.text_input("Email")
with col2:
   linkedin = st.text_input("LinkedIn")
   username = st.text_input("Username")
   empresa = st.text_input("Empresa")
run_scan = st.button("Ejecutar análisis")
if run_scan:
   hallazgos = []
   riesgo_total = 0
   # LinkedIn
   if linkedin:
       hallazgos.append({
           "Categoría": "LinkedIn",
           "Riesgo": "Medio",
           "Hallazgo": "Perfil profesional públicamente accesible e indexable"
       })
       riesgo_total += 15
   # Email
   if email:
       hallazgos.append({
           "Categoría": "Email",
           "Riesgo": "Alto",
           "Hallazgo": f"El email '{email}' debería comprobarse frente a brechas públicas"
       })
       riesgo_total += 35
   # Username
   if username:
       hallazgos.append({
           "Categoría": "Username",
           "Riesgo": "Medio",
           "Hallazgo": f"El username '{username}' podría reutilizarse en múltiples plataformas"
       })
       riesgo_total += 20
   # Empresa
   if empresa:
       hallazgos.append({
           "Categoría": "Exposición Profesional",
           "Riesgo": "Bajo",
           "Hallazgo": f"La asociación pública con '{empresa}' incrementa la exposición profesional"
       })
       riesgo_total += 10
   # Buscadores
   hallazgos.append({
       "Categoría": "Buscadores",
       "Riesgo": "Bajo",
       "Hallazgo": "La identidad parece ser localizable en motores de búsqueda"
   })
   riesgo_total += 10
   # Nivel riesgo
   if riesgo_total < 30:
       riesgo_global = "BAJO"
       color = "🟢"
   elif riesgo_total < 60:
       riesgo_global = "MEDIO"
       color = "🟠"
   else:
       riesgo_global = "ALTO"
       color = "🔴"
   st.divider()
   st.subheader("Resumen de Exposición")
   colA, colB, colC = st.columns(3)
   colA.metric("Riesgo Global", f"{color} {riesgo_global}")
   colB.metric("Puntuación", f"{riesgo_total}/100")
   colC.metric("Hallazgos", len(hallazgos))
   st.divider()
   st.subheader("Hallazgos Detectados")
   df = pd.DataFrame(hallazgos)
   st.dataframe(
       df,
       use_container_width=True,
       hide_index=True
   )
   st.divider()
   st.subheader("Recomendaciones")
   recomendaciones = [
       "Revisar la visibilidad pública de perfiles",
       "Eliminar PDFs o CVs antiguos públicos",
       "Evitar reutilizar usernames",
       "Monitorizar brechas de seguridad públicas",
       "Reducir oversharing profesional innecesario"
   ]
   for rec in recomendaciones:
       st.markdown(f"- {rec}")
   st.divider()
   st.caption(
       f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
   )
