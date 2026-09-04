import streamlit as st

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Neon CSS Tasarımı
st.markdown("""
    <style>
    /* Karanlık arka plan ve neon yazı tipi */
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    /* Neon Başlıklar */
    .neon-text {
        color: #66fcf1;
        text-shadow: 0 0 10px #66fcf1, 0 0 20px #66fcf1;
        font-weight: bold;
    }
    /* Neon Butonlar */
    div.stButton > button {
        background-color: transparent;
        color: #45f3ff;
        border: 2px solid #45f3ff;
        box-shadow: 0 0 10px #45f3ff;
        border-radius: 8px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #45f3ff;
        color: #111;
        box-shadow: 0 0 20px #45f3ff, 0 0 40px #45f3ff;
    }
    </style>
""", unsafe_allow_html=True)

# Oturum Durumu (Session State) Başlatma
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- HERKESE AÇIK ALAN (Giriş Yapılmasa da Görünür) ---
st.markdown("<h1 class='neon-text'>BTA Bilgi Platformu</h1>", unsafe_allow_html=True)
st.write("Bu alan **herkese açıktır**. Giriş yapmadan genel verileri görebilirsiniz.")

# Örnek Herkese Açık İçerik
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Aktif Kullanıcı", value="1,240", delta="+12%")
with col2:
    st.metric(label="Günlük İşlem", value="45,210", delta="-3%")

st.divider()

# --- GİRİŞ KONTROLÜ VE ÖZEL ALAN ---
if not st.session_state.logged_in:
    st.subheader("🔒 Üye Paneline Giriş Yapın")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap"):
        # Buraya kendi kullanıcı adı ve şifreni yazabilirsin
        if username == "admin" and password == "bta123":
            st.session_state.logged_in = True
            st.success("Başarıyla giriş yapıldı!")
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")

else:
    # --- SADECE GİRİŞ YAPANLARIN GÖRECEĞİ ÖZEL ALAN ---
    st.markdown("<h2 class='neon-text'>🚀 BTA Özel Üye Paneli</h2>", unsafe_allow_html=True)
    st.write("Tebrikler! Giriş yaptınız ve şu an gizli / özel içerikleri görüyorsunuz.")
    
    # Özel araçlar, grafikler veya tablolar buraya gelecek
    st.info("Bu mesajı sadece giriş yapan yetkili kişiler görebilir.")
    
    # Çıkış Butonu
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()
