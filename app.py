import streamlit as st 
import pandas as pd 
import datetime 
import yfinance as yf 
import os 
import time 
import uuid 
import re 
from streamlit_autorefresh import st_autorefresh 

# Sayfa yapılandırması ve 10 saniyede bir otomatik yenileyici 
st.set_page_config(page_title="BTA Merkez", layout="wide") 
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici") 

# --- HAREKETLİ BTA LOGOSU VE STYLES ---
st.markdown('''
    <style>
    @keyframes float {
        0% { transform: translateY(0px) scale(1); filter: drop-shadow(0 5px 15px rgba(0,229,255,0.4)); }
        50% { transform: translateY(-10px) scale(1.02); filter: drop-shadow(0 15px 25px rgba(0,229,255,0.7)); }
        100% { transform: translateY(0px) scale(1); filter: drop-shadow(0 5px 15px rgba(0,229,255,0.4)); }
    }
    .bta-logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    .bta-animated-logo {
        font-size: 55px;
        font-weight: 900;
        letter-spacing: 5px;
        background: linear-gradient(45deg, #00E5FF, #00E676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: float 4s ease-in-out infinite;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .warning-banner {
        background-color: #fff3cd;
        color: #856404;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
        border: 1px solid #ffeeba;
    }
    </style>
    <div class="bta-logo-container">
        <div class="bta-animated-logo">BTA MERKEZ</div>
    </div>
''', unsafe_allow_html=True)

# --- 15 DAKİKA GECİKMELİ VERİ UYARISI VE YASAL UYARI ---
st.markdown('<div class="warning-banner">⚠️ Dikkat: Panel üzerindeki borsa verileri borsa kuralları gereği en az 15 dakika gecikmeli olarak yansıtılmaktadır.</div>', unsafe_allow_html=True)

st.markdown('''
<p style="color:#ff4b4b; font-size:13px; text-align:center;">
⚠ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.
</p>
''', unsafe_allow_html=True) 

excel_yolu = "nurican.xls.xlsm" 
sayac_dosyasi = "bta_sayac_verileri.txt"

# --- KALICI SAYAÇ YÖNETİMİ (KAYBOLMAYAN VERİLER) ---
@st.cache_resource
def sunucu_sayacini_getir():
    bugun = datetime.date.today().strftime("%Y-%m-%d")
    toplam_ziyaret = 0
    gunluk_ziyaret = 0
    son_tarih = bugun

    if os.path.exists(sayac_dosyasi):
        try:
            with open(sayac_dosyasi, "r") as f:
                satirlar = f.read().splitlines()
                if len(satirlar) >= 3:
                    toplam_ziyaret = int(satirlar[0])
                    gunluk_ziyaret = int(satirlar[1])
                    son_tarih = satirlar[2]
        except:
            pass

    if son_tarih != bugun:
        gunluk_ziyaret = 0
        son_tarih = bugun

    return {"toplam": toplam_ziyaret, "gunluk": gunluk_ziyaret, "tarih": son_tarih, "aktif_cihazlar": set()}

sayac_verisi = sunucu_sayacini_getir()

if "cihaz_id" not in st.session_state: 
    st.session_state.cihaz_id = str(uuid.uuid4()) 
    
    sayac_verisi["toplam"] += 1
    sayac_verisi["gunluk"] += 1
    
    try:
        with open(sayac_dosyasi, "w") as f:
            f.write(f"{sayac_verisi['toplam']}\n{sayac_verisi['gunluk']}\n{sayac_verisi['tarih']}")
    except:
        pass

sayac_verisi["aktif_cihazlar"].add(st.session_state.cihaz_id)
aktif_oda_sayisi = len(sayac_verisi["aktif_cihazlar"])

st.header("📊 BTA ALGORİTMİK HİSSE PANELİ") 

# Sayıları TR formatına çevirme fonksiyonu 
def formatla_tl(deger): 
    try: 
        f_deger = float(deger) 
        ingiliz_stil = f"{f_deger:,.2f}" 
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".") 
        return f"{tr_stil} TL" 
    except: 
        return str(deger) 

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
        
        st.markdown('<p style="font-weight:bold; font-size:18px; color:#00E5FF;">📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True) 
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
                    "GECİKMELİ VERİ 📊": formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor...", 
                    "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-" 
                }) 
        
        st.markdown('<p style="font-weight:bold; font-size:18px; color:#00E676;">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True) 
        if len(tablo_alsat) > 0: 
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True) 
        st.write("---") 
        
        # --- BIST ANLIK ARAMA MOTORU --- 
        st.markdown('<p style="font-weight:bold; font-size:18px; color:#FFA000;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True) 
        
        if len(df.columns) >= 5: 
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist() 
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]] 
            tum_hisseler.sort() 
            
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
                                col1.metric(label="Fiyat (Gecikmeli) 💥", value=formatla_tl(anlik_fiyat), delta=f"%{gunluk_degisim:+.2f}") 
                                col2.metric(label="Gün içi En Yüksek 📈", value=formatla_tl(gunun_en_yuksek)) 
                                col3.metric(label="Gün içi En Düşük 📉", value=formatla_tl(gunun_en_dusuk)) 
                            else: 
                                st.warning(f"{aranan_hisse} koduna ait veri bulunamadı. Excel'deki kodu kontrol edin (Örn: THYAO).") 
                        except Exception as e: 
                            st.error("Borsa verisi çekilirken bir hata oluştu.") 
            else: 
                st.warning("Excel dosyasının E sütununda geçerli bir hisse listesi bulunamadı.") 
        else: 
            st.error("Excel dosyasında E sütunu bulunamadı!") 
            
    except Exception as e: 
        st.error("Excel veya Borsa verileri yüklenirken bir sorun oluştu.") 
else: 
    st.error(f"Belirtilen Excel dosyası bulunamadı: {excel_yolu}")

st.write("---")

