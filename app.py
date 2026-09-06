import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import json
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BTA Merkez", layout="wide")
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")
anim_id = int(time.time())

st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:20px;}}
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px;}}
    .cember-animasyon-{anim_id} {{width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden; animation: gokkusagiCember 4s linear infinite, yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;}}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3)); animation: soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;}}
    .chat-kutusu {{background-color: #1e293b; border-radius: 10px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #3b82f6;}}
    .chat-isim {{ font-weight: bold; color: #38bdf8 !important; font-size: 0.95rem; }}
    .chat-zaman {{ color: #94a3b8 !important; font-size: 0.75rem; float: right; }}
    .chat-mesaj {{ color: #f1f5f9 !important; margin-top: 4px; font-size: 1rem; }}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
</style>
''', unsafe_allow_html=True)

st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
sohbet_dosyası = "nurican_sohbet_gecmisi.json"

st.header("💬 BTA ORTAK CANLI SOHBET ODASI")

if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = ""

if not st.session_state.kullanici_adi:
    with st.form("giris_formu"):
        st.subheader("Sohbete Katılmak İçin Bir İsim Seçin")
        gecici_isim = st.text_input("Kullanıcı Adınız:", placeholder="Örn: Nuri Can")
        if st.form_submit_button("Odaya Bağlan"):
            if gecici_isim.strip():
                st.session_state.kullanici_adi = gecici_isim.strip()
                st.rerun()
else:
    st.write(f"👤 Aktif Profil: **@{st.session_state.kullanici_adi}**")
    
    with st.form("mesaj_formu", clear_on_submit=True):
        yeni_mesaj_metni = st.text_input("Mesajınızı yazın...", placeholder="Buraya yazın...")
        if st.form_submit_button("Gönder 🚀"):
            if yeni_mesaj_metni.strip():
                mevcut = []
                if os.path.exists(sohbet_dosyası):
                    try:
                        with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                            mevcut = json.load(f)
                    except:
                        pass
                mevcut.append({"isim": st.session_state.kullanici_adi, "mesaj": yeni_mesaj_metni.strip(), "zaman": datetime.datetime.now().strftime("%H:%M:%S")})
                if len(mevcut) > 40:
                    mevcut = mevcut[-40:]
                try:
                    with open(sohbet_dosyası, "w", encoding="utf-8") as f:
                        json.dump(mevcut, f, ensure_ascii=False, indent=4)
                except:
                    pass
                st.rerun()

    sohbet_gecmisi = []
    if os.path.exists(sohbet_dosyası):
        try:
            with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                sohbet_gecmisi = json.load(f)
        except:
            pass

    if sohbet_gecmisi:
        for m in reversed(sohbet_gecmisi):
            st.markdown(f'''
            <div class="chat-kutusu">
                <span class="chat-isim">@{m['isim']}</span>
                <span class="chat-zaman">{m['zaman']}</span>
                <div class="chat-mesaj">{m['mesaj']}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("Sohbet odası şu an sessiz.")

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
 
