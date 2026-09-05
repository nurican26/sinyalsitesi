import streamlit as st

st.set_page_config(page_title="BTA Sinyal Odası", page_icon="📈", layout="wide")

# SİZİN HAZIRLADIĞINIZ GOOGLE E-TABLO BURAYA BAĞLANIYOR
st.components.v1.iframe("https://google.com", height=800, scrolling=True)
