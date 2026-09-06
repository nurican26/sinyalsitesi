import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import json
import time
import uuid
import re  

# st_autorefresh kütüphanesini en güvenli şekilde dahil ediyoruz
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Lütfen projenize 'streamlit-autorefresh' kütüphanesini yükleyin (requirements.txt dosyasına ekleyin).")

# Sayfa Yapılandırması ve Otomatik Yenileme (10 saniyede bir)
st.set_page_config(page_title="BTA Merkez", layout="wide")

try:
    st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")
except NameError:
    pass

anim_id = int(time.time())

# CSS Tasarımları
st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:20px;}}
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px;}}
    .cember-animasyon-{anim_id} {{width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden; animation: gokkusagiCember 4s linear infinite;}}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));}}
    .chat-kutusu {{background-color: #1e293b; border-radius: 10px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #3b82f6; position: relative;}}
    .chat-isim {{ font-weight: bold; color: #38bdf8 !important; font-size: 0.95rem; }}
    .chat-zaman {{ color: #94a3b8 !important; font-size: 0.75rem; float: right; margin-right: 10px; }}
    .chat-mesaj {{ color: #f1f5f9 !important; margin-top: 4px; font-size: 1rem; }}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
</style>
''', unsafe_allow_html=True)

# Logo Alanı
st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)

# Dosya Yolları Tanımlamaları
excel_yolu = "nurican.xls.xlsm"
sohbet_dosyası = "nurican_sohbet_gecmisi.json"

# Yasaklı Kelime Listesi (Küfür ve Argolar)
YASAKLI_KELIMELER = ["küfür1", "argo2", "hakaret3", "lan", "salak", "aptal"]

# Oturum Değişkenleri İlklendirme
if "cihaz_id" not in st.session_state:
    st.session_state.cihaz_id = str(uuid.uuid4())

if "sohbet_uyari_sayisi" not in st.session_state:
    st.session_state.sohbet_uyari_sayisi = 0

if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = ""

st.header("📊 BTA ALGORİTMİK HİSSE ")

# --- 1. PANEL: EXCEL VE YFINANCE VERİ TABLOLARI ---
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_bta = []
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                p_temiz = f"{float(puan_d):.2f}" if hasattr(puan_d, '__float__') or isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                try:
                    h_bta = yf.Ticker(f"{ha}.IS").history(period="1d")
                    if not h_bta.empty:
                        c_fiyat = float(h_bta['Close'].iloc[-1])
                except:
                    pass
                try:
                    maliyet = float(alim_c.replace(",", "."))
                except:
                    maliyet = 0.0
                kz_str = f"%{((c_fiyat - maliyet) / maliyet) * 100:+.2f}" if maliyet > 0 and c_fiyat > 0 else "-"
                tablo_bta.append({"BTA PUAN 🔢": p_temiz, "BTA HİSSE 📈": ha, "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c, "GÜNCEL FİYAT 💥": f"{c_fiyat:.2f} TL" if c_fiyat > 0 else "Yükleniyor...", "KAR / ZARAR 📊": kz_str})
        
        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_bta) > 0:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)

        st.write("")
        tablo_alsat = []
        for idx in range(min(10, len(df))):
            hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            if hb != "" and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                as_fiyat = 0.0
                as_deg = 0.0
                try:
                    h_as = yf.Ticker(f"{hb}.IS").history(period="2d")
                    if not h_as.empty:
                        as_fiyat = float(h_as['Close'].iloc[-1])
                        as_prev = float(h_as['Close'].iloc[-2]) if len(h_as) >= 2 else as_fiyat
                        as_deg = ((as_fiyat - as_prev) / as_prev) * 100
                except:
                    pass
                tablo_alsat.append({"GÜNLÜK AL SAT HİSSELERİ ⚡": hb, "ANLIK VERİ CANLI 📊": f"{as_fiyat:.2f} TL" if as_fiyat > 0 else "Yükleniyor...", "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-"})
        
        st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)

    except:
        st.error("Excel verileri yüklenirken bir sorun oluştu.")
else:
    st.error(f"'{excel_yolu}' dosyası sistemde bulunamadı!")


# --- 2. PANEL: CANLI SOHBET ODASI VE FİLTRELEME SİSTEMİ ---
st.write("---")
st.header("💬  CANLI SOHBET ODASI")

if not st.session_state.kullanici_adi:
    with st.form("giris_formu"):
        st.subheader("Sohbete Katılmak İçin Bir İsim Seçin")
        gecici_isim = st.text_input("Kullanıcı Adınız:", placeholder="Örn: Nuri Can")
        if st.form_submit_button("Odaya Bağlan"):
            if gecici_isim.strip():
                st.session_state.kullanici_adi = gecici_isim.strip()
                st.rerun()
else:
    st.write(f"👤 Profil: **@{st.session_state.kullanici_adi}**")
    
    # 3 İhlal Cezası Durumunda Formu Kilitle
    if st.session_state.sohbet_uyari_sayisi >= 3:
        st.error("🚫 **CEZA:** Topluluk kurallarını 3 kez ihlal ettiğiniz için bu oturumda mesaj göndermeniz ENGELLENMİŞTİR!")
    else:
        with st.form("mesaj_formu", clear_on_submit=True):
            yeni_mesaj_metni = st.text_input("Mesajınızı yazın...", placeholder="Buraya yazın...", key="chat_input_text")
            if st.form_submit_button("Gönder 🚀"):
                if yeni_mesaj_metni.strip():
                    
                    # Regex Tabanlı Filtreleme Algoritması
                    mesaj_temiz_kontrol = yeni_mesaj_metni.lower()
                    yasakli_bulundu = False
                    
                    for kelime in YASAKLI_KELIMELER:
                        if re.search(r'\b' + re.escape(kelime) + r'\b', mesaj_temiz_kontrol):
                            yasakli_bulundu = True
                            break
                    
                    if yasakli_bulundu:
                        # Uyarıyı bir artır ve durumu kaydet
                        st.session_state.sohbet_uyari_sayisi += 1
                        if st.session_state.sohbet_uyari_sayisi >= 3:
                            st.session_state["sohbet_hata_mesaji"] = "❌ 3. İhlal! Kurallara uymadığınız için sohbet odasından uzaklaştırıldınız."
                        else:
                            st.session_state["sohbet_hata_mesaji"] = f"⚠️ Yazdığınız mesaj argo/küfür içerdiği için engellendi! (Uyarı: {st.session_state.sohbet_uyari_sayisi}/3)"
                        st.rerun()
                    else:
                        # Temiz mesajı JSON'a kaydetme süreci
                        mevcut = []
                        if os.path.exists(sohbet_dosyası):
                            try:
                                with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                                    mevcut = json.load(f)
                            except:
                                pass
                        
                        # Yeni mesaj verisini hazırlıyoruz
                        yeni_veri = {
                            "mesaj_id": str(uuid.uuid4()),
                            "cihaz_id": st.session_state.cihaz_id,
                            "isim": st.session_state.kullanici_adi, 
                            "mesaj": yeni_mesaj_metni.strip(), 
                            "zaman": datetime.datetime.now().strftime("%H:%M:%S")
                        }
                        mevcut.append(yeni_veri)
                        
