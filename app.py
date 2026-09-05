import streamlit as st

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Neon CSS Tasarımı
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    .neon-text {
        color: #66fcf1;
        text-shadow: 0 0 10px #66fcf1, 0 0 20px #66fcf1;
        font-weight: bold;
    }
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

# Oturum Durumunu Başlatma
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- HERKESE AÇIK ALAN (Her Zaman En Üstte Görünür) ---
st.markdown("<h1 class='neon-text'>BTA Bilgi Platformu</h1>", unsafe_allow_html=True)
st.write("Bu alan **herkese açıktır**. Giriş yapmadan genel verileri görebilirsiniz.")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Aktif Kullanıcı", value="1,240", delta="+12%")
with col2:
    st.metric(label="Günlük İşlem", value="45,210", delta="-3%")

st.divider()


# --- GİRİŞ VE İÇERİK KONTROLÜ ---
# Eğer giriş YAPILMAMIŞSA sadece giriş formunu göster
if not st.session_state.logged_in:
    st.subheader("🔒 Üye Paneline Giriş Yapın")
    
    username = st.text_input("Kullanıcı Adı", key="user_input")
    password = st.text_input("Şifre", type="password", key="pass_input")
    
    if st.button("Giriş Yap"):
        if username == "admin" and password == "bta123":
            st.session_state.logged_in = True
            st.rerun()  # Sayfayı yenileyip aşağıdaki 'else' kodunu çalıştırır
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")

# Eğer giriş YAPILMIŞSA giriş formunu gizle ve ÖZEL PANELİ göster
else:
    st.markdown("<h2 class='neon-text'>🚀 BTA Özel Üye Paneli</h2>", unsafe_allow_html=True)
    st.success("Başarıyla giriş yaptınız!")
    st.write("Şu an gizli / özel içerikleri görüyorsunuz.")
    
    st.info("Bu mesajı sadece giriş yapan yetkili kişiler görebilir.")
    
    # Çıkış Butonu
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()
