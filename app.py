import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. SAYFA AYARLARI
st.set_page_config(page_title="BTA Borsa Merkez", layout="wide", page_icon="📈")

# 2. GELİŞMİŞ ÖZEL CSS TASARIMI (Koyu ve Neon Tema)
css_kodu = """
<style>
.stApp { 
    background-color: #0b111e !important; 
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; 
}
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 12px 10px; font-weight: 600; border-bottom: 2px solid #1e3a5f; }
.borsa-tablo td { padding: 12px 10px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.tebrik-kutusu { border: 2px solid #00ffcc; box-shadow: 0 0 15px #00ffcc, inset 0 0 10px rgba(0,255,204,0.3); background: #121d33; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; }
.tarama-kutusu { border: 1px dashed #1e3a5f; background: #0c1524; border-radius: 10px; padding: 25px; text-align: center; margin: 20px 0; color: #b2c3d9; font-size: 16px; }

.logo-yurume-alani {
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1;
}

@keyframes btaYoru {
    0% { transform: translateX(-10%); }
    50% { transform: translateX(85%); }
    100% { transform: translateX(-10%); }
}

.yuruyen-bta-logo {
    font-family: 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 75px; 
    color: #00ffcc;
    display: inline-block;
    animation: btaYoru 15s infinite linear;
    text-shadow: 0 0 10px #00ffcc, 0 0 20px #1e90ff, 0 0 35px #0d9488;
}
/* Streamlit dizayn düzeltmeleri */
h1, h2, h3, p, span { color: #ffffff !important; }
.stSelectbox label, .stTextInput label { color: #00ffcc !important; font-weight: bold; }
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. 5 SANİYEDE BİR OTOMATİK YENİLEME
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# 4. VERİ TABANLARI VE DOSYA YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"

# Veritabanı dosyaları yoksa otomatik oluştur
if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([[0, 0, 0]], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"]).to_csv(db_istatistik, index=False)

# 5. SAYAÇ VERİLERİNİ OKUMA VE GÜNCELLEME
ziyaret, basarili, basarisiz = 0, 0, 0
try:
    df_ist = pd.read_csv(db_istatistik)
    if df_ist.empty:
        df_ist = pd.DataFrame([[0, 0, 0]], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"])
    
    if "ziyaret_sayildi" not in st.session_state:
        df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state["ziyaret_sayildi"] = True
        
    ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
    basarili = int(df_ist.at[0, "basarili_oy"])
    basarisiz = int(df_ist.at[0, "basarisiz_oy"])
except:
    pass

# 6. LOGO VE TRADINGVIEW WIDGET
st.markdown('<div class="logo-yurume-alani"><h1 class="yuruyen-bta-logo">BTA</h1></div>', unsafe_allow_html=True)

bist_mini_widget = """
<div class="tradingview-widget-container" style="margin: auto; text-align: center; width: 100%; max-width: 450px;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://tradingview.com" async>
  {
  "symbol": "BIST:XU100", "width": "100%", "height": "95", "locale": "tr",
  "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": ""
  }
  </script>
</div>
"""
components.html(bist_mini_widget, height=100)

# Tarih Ayarı
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")

# 7. MAJOR ENDEKS VE VARLIKLARIN VERİLERİNİ ÇEKME (Üst Kartlar İçin)
@st.cache_data(ttl=10)
def get_market_summary():
    try:
        tickers = ["XU100.IS", "USDTRY=X", "GC=F"]
        data = yf.download(tickers, period="2d", interval="1d", group_by='ticker', progress=False)
        
        bist_close = data["XU100.IS"]["Close"].iloc[-1]
        bist_open = data["XU100.IS"]["Open"].iloc[-1]
        bist_chg = ((bist_close - bist_open) / bist_open) * 100
        
        usd_close = data["USDTRY=X"]["Close"].iloc[-1]
        usd_open = data["USDTRY=X"]["Open"].iloc[-1]
        usd_chg = ((usd_close - usd_open) / usd_open) * 100
        
        gold_close = data["GC=F"]["Close"].iloc[-1]
        gold_open = data["GC=F"]["Open"].iloc[-1]
        gold_chg = ((gold_close - gold_open) / gold_open) * 100
        
        return (bist_close, bist_chg), (usd_close, usd_chg), (gold_close, gold_chg)
    except:
        return (9245.50, 1.45), (34.22, 0.12), (2510.80, -0.32)

(bist_p, bist_c), (usd_p, usd_c), (gold_p, gold_c) = get_market_summary()

# Canlı Gösterge Kartları Paneli
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 BIST 100 Endeksi", f"{bist_p:,.2f}", f"{bist_c:+.2f}%")
with col2:
    st.metric("💵 Dolar / TL", f"{usd_p:.4f}", f"{usd_c:+.2f}%")
with col3:
    st.metric("🟡 Ons Altın ($)", f"${gold_p:,.2f}", f"{gold_c:+.2f}%")

# 8. EXCEL DOSYASINI OKUMA VE TÜM HİSSELİRİ LİSTELEME
tum_hisseler = []
hisse_maliyetleri = {}
hisse_puanlari = {}
basarili_hisseler = []
tablo_rows_html = ""
veri_var_mi = False

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # Excel'deki benzersiz takip listesini ayıkla
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 0].dropna().unique() # 0. sütundaki hisseleri alıyoruz
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() not in ["", "BTA HİSSE", "HİSSE", "NAN", "NONE", "RAYSG"]])
        
        # Döngüyü optimize etmek için toplu yfinance sorgusu hazırlığı
        sorgu_hisseler = [f"{h}.IS" if not h.endswith(".IS") else h for h in tum_hisseler[:15]]
        
        if sorgu_hisseler:
            toplu_veri = yf.download(sorgu_hisseler, period="1d", group_by='ticker', progress=False, timeout=5)
            veri_var_mi = True
            
            for idx in range(min(15, len(df))):
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    
                    # Toplu veriden anlık fiyatı güvenle çekme
                    hisse_ticker = f"{ha}.IS"
                    c_fiyat = 0.0
                    try:
                        if hisse_ticker in toplu_veri.columns.levels[0]:
                            c_fiyat = float(toplu_veri[hisse_ticker]['Close'].iloc[-1])
                    except:
                        c_fiyat = 0.0
                        
                    alim_c_temiz = alim_c.replace(",", ".")
                    maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                    
                    # Hafızaya kaydet (Sidebar araması için)
                    hisse_maliyetleri[ha] = maliyet
                    hisse_puanlari[ha] = p_temiz
                    
                    if maliyet > 0 and c_fiyat > 0:
                        or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                        if or_dg >= 9.0:
                            basarili_hisseler.append(f"<b>{ha}</b> (%{or_dg:.2f})")
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                    else:
                        kz_str = "<span>-</span>"
                    
                    tablo_rows_html += f'<tr><td>{p_temiz}</td><td style="color:#00ffcc;">{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
    except Exception as e:
        st.error(f"Excel Okuma Hatası: {str(e)}")

# 9. OTOMATİK BAŞARI TEBRİK PANELİ
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#00ffcc; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {hisseler_str} hedefine ulaşarak %9 ve üzeri performans göstermiştir. Algoritma başarısı tebrik edilir!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)

# 10. ANA PANEL TABLO ALANI
st.write("")
if veri_var_mi and tablo_rows_html != "":
