import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# Sayfa yapılandırması ve 10 saniyede bir otomatik yenileyici
st.set_page_config(page_title="BTA Merkez", layout="wide")
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")
anim_id = int(time.time())

st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .arama-baslik {{background: linear-gradient(90deg, #3b82f6 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .sayac-baslik {{background: linear-gradient(90deg, #ec4899 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}}
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:10px; margin-bottom:20px;}}
    
    /* BTA LOGO - Yukarıdan Düşüş ve 30 Saniyede Bir Alev Efekti */
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px; position: relative;}}
    .cember-animasyon-{anim_id} {{
        width: 120px; height: 120px; 
        border: 4px solid #fff; border-radius: 50%; 
        display: flex; justify-content: center; align-items: center; 
        background: transparent; position: relative; overflow: hidden;
        animation: yukaridanDus-{anim_id} 1.5s ease-out forwards, atesPatla-{anim_id} 30s infinite;
    }}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));}}
    
    @keyframes yukaridanDus-{anim_id} {{
        0% {{ transform: translateY(-200px); opacity: 0; }}
        60% {{ transform: translateY(20px); opacity: 1; }}
        80% {{ transform: translateY(-10px); }}
        100% {{ transform: translateY(0); }}
    }}
    @keyframes atesPatla-{anim_id} {{
        0%, 95%, 100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        100% {{ border-color: #ff5500; box-shadow: 0 0 35px 15px #ff3300, inset 0 0 25px 10px #ff7700; transform: scale(1.1); }}
    }}
</style>
''', unsafe_allow_html=True)

st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.</div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

# --- BULUT UYUMLU GÜVENLİ SAYAÇ SİSTEMİ ---
@st.cache_resource
def sunucu_sayacini_getir():
    return {
        "toplam_giris": 0,
        "gunluk_giris": 0,
        "son_gun": datetime.date.today().strftime("%Y-%m-%d")
    }

sayac_verisi = sunucu_sayacini_getir()
bugun = datetime.date.today().strftime("%Y-%m-%d")

# Gün değiştiyse günlük girişi otomatik sıfırlama kontrolü
if sayac_verisi["son_gun"] != bugun:
    sayac_verisi["gunluk_giris"] = 0
    sayac_verisi["son_gun"] = bugun

# Sadece yeni gelen tekil oturumları listeye dahil et
if "ziyaret_kaydi_tamam" not in st.session_state:
    sayac_verisi["toplam_giris"] += 1
    sayac_verisi["gunluk_giris"] += 1
    st.session_state["ziyaret_kaydi_tamam"] = True

st.header("📊 BTA ALGORİTMİK HİSSE ")

def formatla_tl(deger):
    try:
        f_deger = float(deger)
        ingiliz_stil = f"{f_deger:,.2f}"
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{tr_stil} TL"
    except:
        return str(deger)

# Hisseler ve Arama Motoru Listesi İçin Hafıza Ataması
tum_hisseler = []

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # --- ÜST PANEL (BTA HİSSELERİ) ---
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
                
                tablo_bta.append({
                    "BTA PUAN 🔢": p_temiz, 
                    "BTA HİSSE 📈": ha, 
                    "BTA ALIM 📥": formatla_tl(maliyet) if maliyet > 0 else alim_c, 
                    "GÜNCEL FİYAT 💥": formatla_tl(c_fiyat) if c_fiyat > 0 else "Yükleniyor...", 
                    "KAR / ZARAR 📊": kz_str
                })
        
        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_bta) > 0:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)

        st.write("")
        
        # --- ALT PANEL (GÜNLÜK AL SAT HİSSELERİ) ---
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
                
                tablo_alsat.append({
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": hb, 
                    "ANLIK VERİ CANLI 📊": formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor...", 
                    "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-"
                })
        
        st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)

        # Excel'deki E sütunundaki (WEB sayfası) tüm hisseleri alıyoruz
        if len(df.columns) >= 5:
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
            tum_hisseler.sort()

    except Exception as e:
        st.error("Excel verileri okunurken teknik bir sorun oluştu.")
else:
    st.error(f"'{excel_yolu}' dosyası sistemde bulunamadı!")

# --- BIST ANLIK ARAMA MOTORU PANELİ ---
st.write("---")
st.markdown('<div class="arama-baslik">🔍 BIST ANLIK HİSSE ARAMA MOTORU (SADECE WEB SAYFASI)</div>', unsafe_allow_html=True)

if tum_hisseler:
    aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler)
    if aranan_hisse != "Seçiniz...":
        with st.spinner(f"{aranan_hisse} verileri çekiliyor..."):
            try:
                h_detay = yf.Ticker(f"{aranan_hisse}.IS").history(period="2d")
                if not h_detay.empty:
                    anlik_fiyat = float(h_detay['Close'].iloc[-1])
                    dunku_kapanis = float(h_detay['Close'].iloc[-2]) if len(h_detay) >= 2 else anlik_fiyat
                    gunluk_degisim = ((anlik_fiyat - dunku_kapanis) / dunku_kapanis) * 100
                    gunun_en_yuksek = float(h_detay['High'].iloc[-1])
                    gunun_en_dusuk = float(h_detay['Low'].iloc[-1])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Anlık Canlı Fiyat 💥", value=formatla_tl(anlik_fiyat), delta=f"%{gunluk_degisim:+.2f}")
                    with col2:
                        st.metric(label="Gün içi En Yüksek 📈", value=formatla_tl(gunun_en_yuksek))
                    with col3:
                        st.metric(label="Gün içi En Düşük 📉", value=formatla_tl(gunun_en_dusuk))
                else:
                    st.warning(f"{aranan_hisse} koduna ait anlık veri bulunamadı.")
            except:
