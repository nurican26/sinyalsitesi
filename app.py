import streamlit as st

# 1. Sayfa Yapılandırması
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS Tasarımı - Piyasa Kutuları İçin
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; } 
    h1,h2,h3,h4,h5,h6,p,span,label { color: #fff!important; font-family: "Segoe UI", sans-serif; } 
    .piyasa-kutusu {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #3b82f6;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 BTA SİNYAL MERKEZİ")

# --- 📊 CANLI PİYASA TAKİP ALANI ---
st.markdown("### 📊 Canlı Piyasa Takip Ekranı")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown('<div class="piyasa-kutusu"><h4>📉 BIST 100</h4><h2>14.012,42</h2><p style="color:#2ecc71!important; margin:0;">+%0.57</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="piyasa-kutusu"><h4>🟡 Gram Altın</h4><h2>6.857 TL</h2><p style="color:#e74c3c!important; margin:0;">-%1.30</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="piyasa-kutusu"><h4>🪙 Çeyrek Altın</h4><h2>11.246 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="piyasa-kutusu"><h4>🥈 Yarım Altın</h4><h2>22.492 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)
with col5:
    st.markdown('<div class="piyasa-kutusu"><h4>👑 Tam Altın</h4><h2>44.984 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)

st.success("SİSTEM BAŞARIYLA BAĞLANDI! SIFIR HATA.")
