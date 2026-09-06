import streamlit as st
import pandas as pd
import datetime
import os
import json
import time
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması ve Tema (Karanlık Mod)
st.set_page_config(page_title="BTA Canlı Sohbet Odası", layout="centered")

# 🔄 CANLI CHAT YENİLEYİCİ: Sohbetin akması için sayfa her 5 saniyede bir otomatik yenilenir
st_autorefresh(interval=5 * 1000, key="sohbet_yenileyici")

# Özel CSS ile Şık Sohbet Arayüzü Tasarımı
st.markdown('''
<style>
    .stApp {background: #0f172a!important;} 
    h1, h2, h3, p, span {color: #fff!important;}
    .chat-kutusu {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #10b981;
    }
    .chat-isim {
        font-weight: bold;
        color: #38bdf8 !important;
        font-size: 0.95rem;
    }
    .chat-zaman {
        color: #94a3b8 !important;
        font-size: 0.75rem;
        float: right;
    }
    .chat-mesaj {
        color: #f1f5f9 !important;
        margin-top: 5px;
        font-size: 1.05rem;
    }
</style>
''', unsafe_allow_html=True)

st.title("💬 BTA Canlı Sohbet Odası")
st.caption("Sayfa her 5 saniyede bir yeni mesajlar için otomatik güncellenir.")
st.write("---")

# Sohbet geçmişinin tutulacağı JSON dosyasının adı
sohbet_dosyası = "nurican_sohbet_gecmisi.json"

# Mesajları yükleme fonksiyonu
def mesajlari_yukle():
    if os.path.exists(sohbet_dosyası):
        try:
            with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# Yeni mesaj kaydetme fonksiyonu
def mesaj_kaydet(isim, mesaj):
    mevcut_mesajlar = mesajlari_yukle()
    yeni_mesaj = {
        "isim": isim,
        "mesaj": mesaj,
        "zaman": datetime.datetime.now().strftime("%H:%M:%S")
    }
    mevcut_mesajlar.append(yeni_mesaj)
    
    # Sohbet odasında son 50 mesajı tutalım (Dosya şişmesin diye)
    if len(mevcut_mesajlar) > 50:
        mevcut_mesajlar = mevcut_mesajlar[-50:]
        
    with open(sohbet_dosyası, "w", encoding="utf-8") as f:
        json.dump(mevcut_mesajlar, f, ensure_ascii=False, indent=4)

# 👤 Kullanıcı Takma Adı (Session State kullanarak sayfada tutuyoruz)
if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = ""

if not st.session_state.kullanici_adi:
    with st.form("giris_formu"):
        st.subheader("Odaya Katılmak İçin Bir İsim Seçin")
        gecici_isim = st.text_input("Kullanıcı Adınız:", placeholder="Örn: Nuri Can")
        giris_butonu = st.form_submit_button("Odaya Gir")
        if giris_butonu and gecici_isim.strip():
            st.session_state.kullanici_adi = gecici_isim.strip()
            st.rerun()
else:
    # 📝 Mesaj Gönderme Alanı
    st.write(f"👤 Aktif Profil: **{st.session_state.kullanici_adi}**")
    
    with st.form("mesaj_formu", clear_on_submit=True):
        yeni_mesaj_metni = st.text_input("Mesajınızı yazın...", placeholder="Buraya yazın ve Gönder'e basın...")
        gonder_butonu = st.form_submit_button("Gönder 🚀")
        
        if gonder_butonu and yeni_mesaj_metni.strip():
            mesaj_kaydet(st.session_state.kullanici_adi, yeni_mesaj_metni.strip())
            st.rerun()

    st.write("### 📜 Sohbet Akışı")
    
    # 💬 Mesajları Ekranda Listeleme
    sohbet_gecmisi = mesajlari_yukle()
    
    if sohbet_gecmisi:
        # En yeni mesajı en üstte göstermek için listeyi ters çeviriyoruz
        for m in reversed(sohbet_gecmisi):
            st.markdown(f'''
            <div class="chat-kutusu">
                <span class="chat-isim">@{m['isim']}</span>
                <span class="chat-zaman">{m['zaman']}</span>
                <div class="chat-mesaj">{m['mesaj']}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("Sohbet odası henüz boş. İlk mesajı sen yaz!")
