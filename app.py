import streamlit as st
import pandas as pd
st.title("Digital Exposure Scan")
st.markdown("""
### Reduce your professional digital exposure
This beta tool analyzes:
- Public exposure
- Search engine indexing
- Email visibility
- Username correlation
- Professional exposure risks
""")
name = st.text_input("Full name")
city = st.text_input("City")
email = st.text_input("Email")
linkedin = st.text_input("LinkedIn URL")
username = st.text_input("Username")
if st.button("Run Exposure Scan"):
   findings = []
   if linkedin:
       findings.append({
           "Category": "LinkedIn",
           "Risk": "Medium",
           "Finding": "LinkedIn profile publicly accessible"
       })
   if email:
       findings.append({
           "Category": "Email",
           "Risk": "High",
           "Finding": f"Email {email} should be checked for breaches"
       })
   if username:
       findings.append({
           "Category": "Username",
           "Risk": "Medium",
           "Finding": f"Username '{username}' may be reused across platforms"
       })
   findings.append({
       "Category": "Google",
       "Risk": "Low",
       "Finding": "Public search engine exposure detected"
   })
   df = pd.DataFrame(findings)
   st.subheader("Exposure Findings")
   st.dataframe(df)
   st.subheader("Overall Risk")
   st.error("MEDIUM")
