import streamlit as st

st.set_page_config(page_title="ScaleDown Challenge", layout="centered")

st.title("🚀 ScaleDown Challenge App")

st.markdown("""
This app demonstrates the **ScaleDown pipeline**
in a simple and beginner-friendly way.
""")

st.header("📂 Project Overview")
st.write("""
ScaleDown is a modular Python project that shows
how optimization and compression can be structured
using a clean pipeline-based approach.
""")

st.header("⚙️ Pipeline Flow")
st.write("""
1. Input data enters the pipeline  
2. Optimization logic is applied  
3. Compression logic is applied  
4. Final output is produced  
""")

st.success("✅ Streamlit app is running successfully!")
