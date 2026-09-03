import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Google Fonts'tan el yazısı fontu (Sacramento) yüklüyoruz ve stilleri tanımlıyoruz
st.markdown("""
<link rel="preconnect" href="https://googleapis.com">
<link rel="preconnect" href="https://gstatic.com" crossorigin>
<link href="https://googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<style>
    .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: 'Segoe UI', sans-serif;} 
    input, textarea {color: #000!important; background-color: #fff!important;}
    
    .stDataFrame {width: 100% !important; border: 1px solid #4338ca !important; border-radius: 8px;}
    div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;}
    
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    
    /* 🟢 BÜYÜK HARFLİ YEŞİL BTA LOGOSU */
    .bta-logo-konteyner {
        display: flex;
        align-items: center;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .bta-logo {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white !important;
        font-family: 'Sacramento', cursive, sans-serif !important;
        font-weight: bold;
        font-size: 3.2rem;
        padding: 2px 25px;
        border-radius: 16px;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        line-height: 1.2;
    }
    
    .mesaj-kutusu {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #10b981;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .spk-kutu-sol {
        background-color: rgba(220, 38, 38, 0.1);
        border-left: 4px solid #dc2626; 
        padding: 12px;
        border-radius: 6px; 
        margin-top: 30px; 
        margin-bottom: 20px;
        color: #fca5a5 !important; 
        font-size: 0.82rem; 
        text-align: justify;
        line-height: 1.4;
    }
    .alt-metrik-kutusu {
        background: rgba(255, 255, 255, 0.03);
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# 💾 ORTAK VERI TABANI DOSYALARI
MESAJ_DOSYASI = "ortak_mesajlar.csv"
PUAN_DOSYASI = "ortak_puanlar.csv"

def puanlari_yukle():
    if os.path.exists(PUAN_DOSYASI):
        try:
            df = pd.read_csv(PUAN_DOSYASI)
            toplam_oy = len(df)
            ortalama_puan = df["puan"].mean() if toplam_oy > 0 else 0.0
            return ortalama_puan, toplam_oy
        except:
            return 0.0, 0
    return 0.0, 0

def puan_kaydet(verilen_puan):
    yeni_puan = pd.DataFrame([{"puan": verilen_puan, "tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}])
    if os.path.exists(PUAN_DOSYASI):
        yeni_puan.to_csv(PUAN_DOSYASI, mode='a', header=False, index=False)
    else:
        yeni_puan.to_csv(PUAN_DOSYASI, mode='w', header=True, index=False)

# 🚫 KÜFÜR VE UYGUNSUZ KELİME FİLTRE MOTORU
YASAKLI_KELIMELER = ["küfür1", "küfür2", "argo1", "hakaret1", "salak", "aptal"] 

def sansurle(metin):
    temiz_metin = metin
    for kelime in YASAKLI_KELIMELER:
        pattern = re.compile(re.escape(kelime), re.IGNORECASE)
        temiz_metin = pattern.sub("*" * len(kelime), temiz_metin)
    return temiz_metin

def mesajlari_yukle():
    if os.path.exists(MESAJ_DOSYASI):
        try:
            return pd.read_csv(MESAJ_DOSYASI).to_dict(orient="records")
        except:
            return []
    return []

def mesaj_kaydet(isim, mesaj, saat):
    güvenli_isim = sansurle(isim)
    güvenli_mesaj = sansurle(mesaj)
    yeni_data = pd.DataFrame([{"isim": güvenli_isim, "mesaj": güvenli_mesaj, "saat": saat}])
    if os.path.exists(MESAJ_DOSYASI):
        yeni_data.to_csv(MESAJ_DOSYASI, mode='a', header=False, index=False)
    else:
        yeni_data.to_csv(MESAJ_DOSYASI, mode='w', header=True, index=False)

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "ziyaret_sayaci" not in st.session_state: st.session_state["ziyaret_sayaci"] = 1
else:
    if "sayac_arttirildi" not in st.session_state:
        st.session_state["ziyaret_sayaci"] += 1
        st.session_state["sayac_arttirildi"] = True

puan, toplam_oy_sayisi = puanlari_yukle()

# BÜYÜK HARFLİ YEŞİL BTA LOGOSU
st.markdown("""
<div class="bta-logo-konteyner">
    <div class="bta-logo">BTA</div>
</div>
""", unsafe_allow_html=True)

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel okuma hatası: {e}")

# 📌 OPTİMİZE EDİLMİŞ HIZLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300:
            return saved_price
            
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except:
        pass
    return 0.0

def temiz_metin_al(val):
    if pd.isna(val): return ""
    return str(val).strip().upper()

# 🌟 EXCEL VERİ AYIKLAMA VE TABLOLAMA MOTORU
tablo_alsat = []
tablo_al = []

if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            if len(df_kaynak.columns) > 22:
                uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
                t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])
                
                if uv_degeri and uv_degeri not in ["NAN", "NONE", "0", "0.0", "-", "AL_SAT SİNYALİ"]:
                    hisse_ara = re.findall(r'[A-Z]+', uv_degeri)
                    if hisse_ara:
                        hisse = hisse_ara[0]
                        canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                        puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                        bta_puan = puan_bul[0] if puan_bul else (t_degeri if t_degeri else uv_degeri)
                        
                        tablo_alsat.append({
                            "Hisse Kodu 📈": hisse, 
                            "BTA PUAN (T)": bta_puan,
                            "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."
                        })
                
                if wv_degeri and wv_degeri not in ["NAN", "NONE", "0", "0.0", "-", "AL", "AL SİNYALİ"]:
                    hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                    if hisse_ara:
                        hisse = hisse_ara[0]
                        canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                        puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                        bta_puan = puan_bul[0] if puan_bul else (t_degeri if t_degeri else uv_degeri)
                        
                        if hisse not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")}
                        
                        tablo_al.append({
                            "Hisse Kodu": hisse, 
                            "BTA PUAN (T)": bta_puan,
                            "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."
                        })
        except:
            pass

sol_kolon, sag_kolon = st.columns(2)

with sol_kolon:
    st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
    if tablo_alsat:
        st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else:
        st.write("🔒 Aktif AL SAT sinyali taranıyor...")

    st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
    if tablo_al:
        st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
    else:
        st.write("🔒 Aktif BTA sinyali taranıyor...")

    st.markdown("""
    <div class="spk-kutu-sol">
        <b>⚖️ YASAL UYARI (SPK):</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı 
        kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy şirketleri, 
        mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi 
        çerçevesinde sunulmaktadır. Veriler en az 15 dakika gecikmelidir.
    </div>
    """, unsafe_allow_html=True)

with sag_kolon:
    st.markdown("#### 🌟 Özel Takip Havuzu 💰")
    
    if st.session_state["ozel_takip_kutusu"]:
        tk_list = []
        for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
            cfiy = hızlı_canli_fiyat_bul(hisse)
            if cfiy == 0.0: 
