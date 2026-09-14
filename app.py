import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. SAYFA AYARLARI
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 2. ÖZEL CSS TASARIMI
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
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
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

.chat-box {
    background-color: #121d33;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 15px;
    height: 300px;
    overflow-y: scroll;
    margin-bottom: 10px;
}
.chat-mesaj {
    padding: 6px 10px;
    border-radius: 5px;
    margin-bottom: 6px;
    font-size: 14px;
}
.chat-admin { background-color: rgba(255, 51, 68, 0.15); border-left: 4px solid #ff3344; color: #ff99a8; }
.chat-user { background-color: rgba(0, 255, 204, 0.08); border-left: 4px solid #00ffcc; color: #e2fcf7; }
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. 5 SANİYEDE BİR YENİLEME MOTORU
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# 4. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"
db_sohbet = "bta_canli_sohbet_db.csv"
db_hisse_yildiz = "bta_hisse_yildiz_db.csv"

# Güvenli veri tabanı başlatma adımları
if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}]).to_csv(db_istatistik, index=False)

if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["tarih", "kullanici", "mesaj", "rol"]).to_csv(db_sohbet, index=False)

if not os.path.exists(db_hisse_yildiz):
    pd.DataFrame(columns=["hisse", "begeniler", "yildizlar"]).to_csv(db_hisse_yildiz, index=False)

# 5. ZİYARETÇİ SAYACINI TETİKLEME
ziyaret, basarili, basarisiz = 0, 0, 0
try:
    df_ist = pd.read_csv(db_istatistik)
    if df_ist.empty or len(df_ist) == 0:
        df_ist = pd.DataFrame([{"ziyaret_sayisi": 1, "basarili_oy": 0, "basarisiz_oy": 0}])
    
    if "ziyaret_sayildi" not in st.session_state:
        df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state["ziyaret_sayildi"] = True
        
    ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
    basarili = int(df_ist.at[0, "basarili_oy"])
    basarisiz = int(df_ist.at[0, "basarisiz_oy"])
except:
    pass

# KULLANICI / YÖNETİCİ DURUMLARI
if "kullanici_adi" not in st.session_state:
    st.session_state["kullanici_adi"] = "Ziyaretci_" + str(int(time.time()) % 1000)
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Sidebar Paneli
with st.sidebar:
    st.markdown("### 🔐 Kullanıcı Profili")
    yeni_nick = st.text_input("Sohbet Takma Adınız (Nick):", st.session_state["kullanici_adi"])
    if yeni_nick:
        st.session_state["kullanici_adi"] = yeni_nick
    
    st.markdown("---")
    st.markdown("### 👑 Yönetici Girişi")
    admin_sifre = st.text_input("Yönetici Şifresi:", type="password")
    if admin_sifre == "admin123":
        st.session_state["is_admin"] = True
        st.success("Yönetici Yetkisi Aktif!")
    else:
        st.session_state["is_admin"] = False

# 6. LOGO VE TRADINGVIEW MODÜLLERİ
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

tum_hisseler = [] 
veri_var_mi = False
basarili_hisseler = []

excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")

# 7. GÜVENLİ EXCEL ANALİZİ
tablo_rows_html = ""
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 4].dropna().unique()
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() != ""])
            
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                except:
                    pass
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 9.0:
                        basariliHisse_adi = ha.replace(".IS", "")
                        basarili_hisseler.append(f"<b>{basariliHisse_adi}</b> (%{or_dg:.2f})")
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                
                # SÖZLÜK/HATA VEREN ALAN TAMAMEN GÜVENLİ HALE GETİRİLDİ
                df_yildiz = pd.read_csv(db_hisse_yildiz)
                hisse_kayit = df_yildiz[df_yildiz["hisse"] == ha]
                if hisse_kayit.empty:
                    begeniler = 0
                    yildizlar = 0.0
                else:
                    begeniler = int(hisse_kayit["begeniler"].values[0])
                    yildizlar = float(hisse_kayit["yildizlar"].values[0])
                
                yildiz_str = "⭐" * int(round(yildizlar)) if yildizlar > 0 else "---"
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td><td>👍 {begeniler} | {yildiz_str}</td></tr>'
    except Exception as e:
        pass

# 8. PANEL ÇIKTILARI
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#00ffcc; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {hisseler_str} hedefine ulaşarak %9 ve üzeri performans göstermiştir. Tebrik ederiz!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)

if veri_var_mi and tablo_rows_html != "":
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th><th>KAYIT DEFTERİ (BEĞENİ/YILDIZ)</th></tr>' + tablo_rows_html + '</table>'

