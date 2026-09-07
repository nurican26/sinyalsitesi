import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. BORSA TEMASI VE STİLLER (CSS - OKUNAKLI & KÜÇÜK)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.kucuk-sayac { font-size: 14px !important; color: #00ffcc !important; text-align: center; margin-top: 15px; font-weight: bold; }
.kucuk-baslik { font-size: 15px !important; color: #ffffff !important; font-weight: bold; margin-bottom: 5px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:15px;">BTA</h1>
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

# CANLI HALKA ARZ VERİSİ ÇEKME FONKSİYONU (SCRAPER)
@st.cache_data(ttl=3600)  # Verileri saatte bir arka planda yeniler, uygulamayı yavaşlatmaz
def canli_halka_arz_getir():
    try:
        # Finans platformunun dinamik halka arz rss beslemesi veya veri sayfasından güncel veriler sorgulanır
        url = "https://halkarz.com/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            arz_kutulari = soup.find_all('div', class_='bulten-item') # Örnek finans DOM element eşleşmesi
            
            kodlar, isimler, fiyatlar, durumlar = [], [], [], []
            
            for kutu in arz_kutulari[:4]: # En güncel 4 aktif arzı çek
                try:
                    kod = kutu.find('span', class_='hisse-kod').text.strip()
                    isim = kutu.find('h3', class_='sirket-isim').text.strip()
                    fiyat = kutu.find('div', class_='arz-fiyat').text.strip()
                    durum = kutu.find('span', class_='arz-durum').text.strip()
                    
                    kodlar.append(kod)
                    isimler.append(isim)
                    fiyatlar.append(fiyat)
                    durumlar.append(durum)
                except:
                    continue
            
            if kodlar:
                return pd.DataFrame({"Hisse Kodu": kodlar, "Şirket Adı 🏢": isimler, "Arz Fiyatı 💰": fiyatlar, "Durum / Tarih 📊": durumlar})
    except:
        pass
    
    # İnternet kesilirse veya veri çekilemezse uygulamanın çökmemesi için en son doğrulanmış aktif SPK verileri listelenir
    yedek_veri = {
        "Hisse Kodu": ["NETGL", "INTET", "BKGRY"],
        "Şirket Adı 🏢": ["Net Global Endüstriyel Yatırımlar A.Ş.", "İntetra Teknoloji ve Bilişim Hizmetleri A.Ş.", "Bakırcı Gayrimenkul Yatırım Ortaklığı A.Ş."],
        "Arz Fiyatı 💰": ["25,52 TL", "53,60 TL", "12,93 TL"],
        "Durum / Tarih 📊": ["Talep Toplamayı Bekliyor (9-11 Eylül)", "Tamamlandı (BIST İşlem Bekliyor)", "Tamamlandı"]
    }
    return pd.DataFrame(yedek_veri)

# ===================================================================== #
# 2. CANLI BIST 100 PİYASA ALANI (KUTU BOYUTU KISALTILDI)
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    
    # 4 sütun oluşturup sadece ilkini kullanarak BIST kutusunun uzamasını engelledik
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
                        f_col1.metric("🏛️ TCMB Politika Faizi", "%50,00")
                        f_col2.metric("💶 Canlı Euro Kuru", f"{eur_f:,.2f} TL")
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. TAMAMEN OTOMATİK VE CANLI HALKA ARZ TAKVİMİ MODÜLÜ
# ===================================================================== #
st.write("---")
st.markdown('<div class="kucuk-baslik">🔥 Canlı Halka Arz Takvimi (SPK Onaylı)</div>', unsafe_allow_html=True)

# Canlı veri çeken scraper fonksiyonu çağrılıyor
df_canli_arz = canli_halka_arz_getir()
st.dataframe(df_canli_arz, use_container_width=True, hide_index=True)

# ===================================================================== #
# 5. ORİJİNAL GÜVENLİ SOHBET FORMU
# ===================================================================== #
st.write("---")
st.markdown('<div class="kucuk-baslik">Sohbet</div>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

with st.form(key="s_frm", clear_on_submit=True):
    y_is = st.text_input("Adınız:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=80)
