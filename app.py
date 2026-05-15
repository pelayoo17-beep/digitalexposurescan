import streamlit as st
st.set_page_config(
   page_title="Escáner de Huella Digital",
   page_icon="🛡️"
)
st.title("🛡️ Escáner de Huella Digital")
st.write("La app funciona correctamente.")
nombre = st.text_input("Nombre")
email = st.text_input("Email")
linkedin = st.text_input("LinkedIn")
instagram = st.text_input("Instagram")
if st.button("Ejecutar análisis"):
   st.success("Análisis ejecutado correctamente")
   resultados = []
   if nombre:
       resultados.append({
           "Tipo": "Nombre",
           "Resultado": f"Se detectó el nombre: {nombre}"
       })
   if email:
       resultados.append({
           "Tipo": "Email",
           "Resultado": f"Se analizará exposición del email: {email}"
       })
   if linkedin:
       resultados.append({
           "Tipo": "LinkedIn",
           "Resultado": "Perfil profesional detectado"
       })
   if instagram:
       resultados.append({
           "Tipo": "Instagram",
           "Resultado": "Perfil social detectado"
       })
   st.write(resultados)
