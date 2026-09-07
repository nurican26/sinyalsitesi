import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. PREMIUM BORSA TERMİNALİ TEMASI VE GÖRSEL STİLLER
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* Ana Ekran Arka Planı: Finans panellerine uygun derin gece mavisi ve borsa çizgisi gradyanı */
.stApp { 
    background-color: #060b13 !important; 
    background-image: 
        linear-gradient(rgba(0, 230, 118, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 176, 255, 0.02) 1px, transparent 1px),
        radial-gradient(at 0% 0%, rgba(13, 148, 136, 0.2) 0px, transparent 40%), 
        radial-gradient(at 100% 100%, rgba(11, 29, 58, 0.6) 0px, transparent 60%) !important;
    background-size: 40px 40px, 40px 40px, auto, auto !important;
}

/* Göstergeler, Formlar ve Genişleyen Paneller için Matrix Teması */
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] { 
    background-color: #0b1322 !important; 
    border: 1px solid #142847 !important; 
    border-radius: 8px !important; 
    padding: 14px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}

/* Giriş Alanları ve Seçim Kutuları */
input, textarea, select { 
    background-color: #040810 !important; 
    color: #00ffcc !important; 
    border: 1px solid #16325c !important; 
    border-radius: 6px !important; 
}

/* Borsa Terminali Gönderme Butonu */
.stButton>button { 
    background: linear-gradient(135deg, #09101d 0%, #11b782 100%) !important; 
    color: #fff !important; 
    border: 1px solid #00ffcc !important; 
    border-radius: 6px !important; 
    font-weight: bold !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 0 10px rgba(0, 255, 204, 0.2) !important;
}

/* BTA Özel Borsa Tablo Tasarımı */
.borsa-tablo { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 12px 0; 
    font-size: 15px; 
    background-color: #0b1322; 
    border-radius: 8px; 
    overflow: hidden; 
    border: 1px solid #142847;
}
.borsa-tablo th { 
    background-color: #0f1c30; 
    color: #00ffcc; 
    text-align: left; 
    padding: 12px 10px; 
    border-bottom: 2px solid #16325c;
    letter-spacing: 0.5px;
}
.borsa-tablo td { 
    padding: 12px 10px; 
    color: #ffffff; 
    border-bottom: 1px solid #142847; 
    font-weight: bold; 
}

/* Alt Sayaç ve Başlıklar */
.kucuk-sayac { font-size: 14px !important; color: #00ffcc !important; text-align: center; margin-top: 20px; font-weight: bold; letter-spacing: 0.5px; }
.kucuk-baslik { font-size: 16px !important; color: #00b0ff !important; font-weight: bold; margin-bottom: 8px; border-left: 3px solid #00b0ff; padding-left: 8px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:55px; margin-bottom:20px; text-shadow: 0 0 15px rgba(0, 255, 204, 0.4);">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı ve Fiyatları Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_sohbet_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"

# KALICI SOHBET VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if "topham_sayac" not in st.session_state: st.session_state["topham_sayac"] = 1450
st.session_state["topham_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# CANLI HALKA ARZ VERİSİ ÇEKME FONKSİYONU (GÜVENLİ VE YEDEKLİ HALE GETİRİLDİ 🛠)
@st.cache_data(ttl=3600)
def canli_halka_arz_getir():
    # İnternet kesilirse veya web sitesinin kod yapısı değişirse tablonun boş kalmaması için güncel yedek veriler
    yedek_veri = pd.DataFrame({
        "Hisse Kodu": ["NETGL", "INTET", "BKGRY"],
        "Şirket Adı 🏢": ["Net Global Endüstriyel Yatırımlar A.Ş.", "İntetra Teknoloji ve Bilişim Hizmetleri A.Ş.", "Bakırcı Gayrimenkul Yatırım Ortaklığı A.Ş."],
        "Arz Fiyatı 💰": ["25,52 TL", "53,60 TL", "12,93 TL"],
        "Durum / Tarih 📊": ["Talep Toplamayı Bekliyor (9-11 Eylül)", "Tamamlandı (BIST İşlem Bekliyor)", "Tamamlandı"]
    })
    
    try:
        url = "https://halkarz.com"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=4)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Değişen HTML sınıflarına karşı esnek element taraması yapılıyor
            arz_kutulari = soup.find_all('div', class_=lambda x: x and ('bulten' in x or 'item' in x or 'halka-arz' in x))
            
            if not arz_kutulari:
                return yedek_veri
                
            kodlar, isimler, fiyatlar, durumlar = [], [], [], []
            for kutu in arz_kutulari[:4]:
                try:
                    kod = kutu.find(lambda tag: tag.name == 'span' and 'kod' in str(tag.get('class', ''))).text.strip()
                    isim = kutu.find(lambda tag: tag.name in ['h3', 'div'] and 'isim' in str(tag.get('class', ''))).text.strip()
                    fiyat = kutu.find(lambda tag: 'fiyat' in str(tag.get('class', ''))).text.strip()
                    durum = kutu.find(lambda tag: 'durum' in str(tag.get('class', ''))).text.strip()
                    
                    if kod and isim:
                        kodlar.append(kod)
                        isimler.append(isim)
                        fiyatlar.append(fiyat if fiyat else "Bilinmiyor")
                        durumlar.append(durum if durum else "Aktif")
                except:
                    continue
            
            if len(kodlar) > 0:
                return pd.DataFrame({"Hisse Kodu": kodlar, "Şirket Adı 🏢": isimler, "Arz Fiyatı 💰": fiyatlar, "Durum / Tarih 📊": durumlar})
    except:
        return yedek_veri
        
    return yedek_veri

# ===================================================================== #
# 2. CANLI BIST 100 PİYASA ALANI
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    
    col_bist, _, _, _ = st.columns(4)
    col_bist.metric("BIST 100", f"{bist_f:,.1f}")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>PUAN</th><th>HİSSE</th><th>ALIM</th><th>FİYAT</th><th>K/Z</th></tr>'
        veri_var_mi = False
        
        for idx in range(min(10, len(df))):
            try:
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                    try: maliyet = float(alim_c.replace(",", "."))
                    except: maliyet = 0.0
                    
                    if maliyet > 0 and c_fiyat > 0:
                        or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.1f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.1f}</span>'
                    else: kz_str = "<span>-</span>"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.1f} TL</td><td>{c_fiyat:,.1f} TL</td><td>{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
                    if len(h_detay_veri) > 0:
                        st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
                        
                        st.write("")
                        st.markdown('<b>🏛️ CANLI EKONOMİK GÖSTERGELER PANELİ</b>', unsafe_allow_html=True)
                        f_col1, f_col2 = st.columns(2)
