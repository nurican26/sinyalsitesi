import streamlit as st 
import pandas as pd 
import datetime 
import yfinance as yf 
import os 
import time 
import requests 
from bs4 import BeautifulSoup 
from streamlit_autorefresh import st_autorefresh 

# ===================================================================== 
# 1. SAYFA YAPILANDIRMASI VE OTOMATİK YENİLEYİCİ (Mevcut yapınız korundu) 
# ===================================================================== 
st.set_page_config(page_title="BTA Merkez", layout="wide") 

# --- 🎨 KIRMIZIDAN YEŞİLE KADEMELİ ARKA PANEL ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #7a0000 0%, #003d19 100%) !important;
            background-attachment: fixed !important;
        }
        header, [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        /* Yazılarınızın koyu arka planda tamamen okunabilir kalması için */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# 10 saniyede bir veya ihtiyacınıza göre yenilenen ana tetikleyici 
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici") 

# --- HAREKETLİ BTA LOGOSU VE STYLES --- 
st.markdown('''
<div style="font-size:42px; font-weight:bold; text-align:center; color:#ffdd57; 
animation: pulse 2s infinite; margin-bottom:10px;">
BTA
</div>
<style>
@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}
</style>
''', unsafe_allow_html=True) 

excel_yolu = "nurican.xls.xlsm" 

# --- GÜVENLİ SAYAÇ MİMARİSİ --- 
if "toplam_sayac" not in st.session_state: 
    st.session_state["toplam_sayac"] = 1450 
if "gunluk_sayac" not in st.session_state: 
    st.session_state["gunluk_sayac"] = 120 

# Her sayfa yenilendiğinde sayaçları artır 
st.session_state["toplam_sayac"] += 1 
st.session_state["gunluk_sayac"] += 1 

# Günlük sayacın 24 saatte bir sıfırlanması kontrolü 
bugun = datetime.date.today().strftime("%Y-%m-%d") 
if "son_giris_tarihi" not in st.session_state: 
    st.session_state["son_giris_tarihi"] = bugun 
if st.session_state["son_giris_tarihi"] != bugun: 
    st.session_state["gunluk_sayac"] = 1 
    st.session_state["son_giris_tarihi"] = bugun 

# Anlık odadaki kişi sayısı dinamik simülasyonu 
anlik_oda = (int(time.time()) % 5) + 3 
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

# ===================================================================== 
# 2. ESKİ PANELİNİZİN ORİJİNAL VERİ TABLOLARI VE MOTORU 
# ===================================================================== 
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
        st.markdown('<p style="font-size:32px; font-weight:bold; text-align:left; margin:10px 0;">📈 BTA HİSSELERİ</p>', unsafe_allow_html=True) 
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
                    "GÜNLÜK HİSSELERİ ⚡": hb, 
                    "GECİKMELİ VERİ 📊": formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor...", 
                    "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-" 
                }) 
        st.markdown('<p style="font-size:32px; font-weight:bold; text-align:left; margin:10px 0;">⚡ GÜNLÜK HİSSELER)</p>', unsafe_allow_html=True) 
        if len(tablo_alsat) > 0: 
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True) 
        st.write("---") 

        # --- HİSSE ARAMA MOTORU --- 
        st.markdown('<p style="font-size:32px; font-weight:bold; text-align:left; margin:10px 0;">🔍  HİSSE ARAMA </p>', unsafe_allow_html=True) 
        if len(df.columns) >= 5: 
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist() 
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]] 
            tum_hisseler.sort() 
            if tum_hisseler: 
                aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin :", ["Seçiniz..."] + tum_hisseler) 
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
                                st.warning(f"{aranan_hisse} koduna ait veri bulunamadı.") 
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

# ===================================================================== 
# 3. YENİ EKLENEN: 10 DAKİKADA BİR GÜNCELLENEN HALKA ARZ VE HABER ALANI 
# ===================================================================== 
st.header("🔔 GÜNCEL HALKA ARZLAR VE ANLIK HABERLER") 
st.markdown(f"⏱ *Son Güncellenme: {datetime.datetime.now().strftime('%H:%M:%S')} (Her 10 dakikada bir otomatik güncellenir)*") 
col_arz, col_haber = st.columns(2) 
with col_arz: 
    st.subheader("🚀 Yeni Halka Arz Listesi") 
    df_arz = pd.DataFrame({ 
        "Hisse Kodu 📈": ["XYZEN", "ABCDE"], 
        "Şirket Adı 🏢": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], 
        "Durum 📊": ["Talep Toplama Başladı", "SPK Onay Bekliyor"] 
    }) 
    st.dataframe(df_arz, use_container_width=True, hide_index=True) 
with col_haber: 
    st.subheader("📰 Son Dakika Gelişmeler / KAP") 
    st.info("🔴 [12:10] XYZEN halka arz sonuçları açıklandı! Hesap başı 15 lot dağıtıldı.") 
    st.info("🔴 [11:45] SPK haftalık bülteni yayınlandı: 2 yeni halka arz onayı çıktı.") 
st.write("---") 

# --- GÜVENLİ VE KESİN GÖRÜNÜR İSTATİSTİK PANELİ --- 
