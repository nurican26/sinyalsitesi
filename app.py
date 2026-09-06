import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import uuid
import re

# Sayfa yapılandırması
st.set_page_config(page_title="BTA Merkez", layout="wide")

# Sayfa yenileme animasyon id'si
anim_id = int(time.time())

st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .arama-baslik {{background: linear-gradient(90deg, #3b82f6 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:10px; margin-bottom:20px;}}
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px;}}
    .cember-animasyon-{anim_id} {{width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden; animation: gokkusagiCember 4s linear infinite;}}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));}}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
</style>
''', unsafe_allow_html=True)

st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)
st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.</div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

def formatla_tl(deger):
    try:
        f_deger = float(deger)
        ingiliz_stil = f"{f_deger:,.2f}"
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{tr_stil} TL"
    except:
        return str(deger)

# --- SOHBET / GİRİŞ ALANI ---
# Global havuz yerine Streamlit session_state kullanarak kullanıcı girişini güvenli hale getiriyoruz
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = ""

if not st.session_state.giris_yapildi:
    st.subheader("🌐 Topluluk Sohbet Odasına Giriş")
    kullanici_input = st.text_input("Kullanıcı adınız:", value=st.session_state.kullanici_adi, placeholder="Bir rumuz girin...")
    
    if st.button("Odaya Gir"):
        if kullanici_input.strip() != "":
            # Türkçe karakter ve argo kontrolü buraya eklenebilir
            st.session_state.kullanici_adi = kullanici_input.strip()
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Lütfen geçerli bir kullanıcı adı girin!")
else:
    st.sidebar.success(f"Giriş Başarılı: {st.session_state.kullanici_adi}")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.giris_yapildi = False
        st.rerun()

    # --- VERİ VE HİSSE PANELİ (Sadece giriş yapılınca görünür) ---
    st.header("📊 BTA ALGORİTMİK HİSSE ")

    if os.path.exists(excel_yolu):
        try:
            df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
            
            # Tüm sembolleri önceden listeleyip toplu fiyat çekmek performansı uçurur
            hisse_listesi = []
            for idx in range(min(10, len(df))):
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
                if ha and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE"]: hisse_listesi.append(f"{ha}.IS")
                if hb and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]: hisse_listesi.append(f"{hb}.IS")
            
            # Yahoo Finance'ten toplu veri çekme (Kilitlenmeyi önler)
            canli_veriler = {}
            if hisse_listesi:
                try:
                    canli_veriler = yf.download(hisse_listesi, period="2d", group_by='ticker', progress=False)
                except:
                    pass

            # --- ÜST PANEL ---
            tablo_bta = []
            for idx in range(min(10, len(df))):
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    c_fiyat = 0.0
                    
                    # Toplu çekilen veriden oku
                    ticker_str = f"{ha}.IS"
                    if ticker_str in canli_veriler and not canli_veriler[ticker_str].empty:
                        c_fiyat = float(canli_veriler[ticker_str]['Close'].iloc[-1])
                    
                    try: maliyet = float(alim_c.replace(",", "."))
                    except: maliyet = 0.0
                    
                    kz_str = f"%{((c_fiyat - maliyet) / maliyet) * 100:+.2f}" if maliyet > 0 and c_fiyat > 0 else "-"
                    
                    tablo_bta.append({
                        "BTA PUAN 🔢": p_temiz, 
                        "BTA HİSSE 📈": ha, 
                        "BTA ALIM 📥": formatla_tl(maliyet) if maliyet > 0 else alim_c, 
                        "GÜNCEL FİYAT 💥": formatla_tl(c_fiyat) if c_fiyat > 0 else "Yükleniyor...", 
                        "KAR / ZARAR 📊": kz_str
                    })
            
            st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
            if tablo_bta:
                st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)

            # --- ALT PANEL ---
            tablo_alsat = []
            for idx in range(min(10, len(df))):
                hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
                if hb != "" and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                    as_fiyat = 0.0
                    as_deg = 0.0
                    
                    ticker_str = f"{hb}.IS"
                    if ticker_str in canli_veriler and not canli_veriler[ticker_str].empty:
                        as_fiyat = float(canli_veriler[ticker_str]['Close'].iloc[-1])
                        as_prev = float(canli_veriler[ticker_str]['Close'].iloc[-2]) if len(canli_veriler[ticker_str]) >= 2 else as_fiyat
                        as_deg = ((as_fiyat - as_prev) / as_prev) * 100
                    
                    tablo_alsat.append({
                        "GÜNLÜK AL SAT HİSSELERİ ⚡": hb, 
                        "ANLIK VERİ CANLI 📊": formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor...", 
                        "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-"
                    })
            
            st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
            if tablo_alsat:
                st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)

            st.write("---")
            
            # --- BIST ANLIK ARAMA MOTORU ---
            st.markdown('<div class="arama-baslik">🔍 BIST ANLIK HİSSE ARAMA MOTORU</div>', unsafe_allow_html=True)
            
            if len(df.columns) >= 5:
                tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
                tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
                tum_hisseler.sort()
                
                if tum_hisseler:
                    aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler)
                    
                    if aranan_hisse != "Seçiniz...":
                        st.info(f"{aranan_hisse} seçildi. Analiz detayları buraya eklenebilir.")
        except Exception as e:
            st.error(f"Excel okunurken hata oluştu: {e}")
