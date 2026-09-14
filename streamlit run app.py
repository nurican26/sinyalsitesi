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

# 4. EXCEL VE BELLEK VERİ TABANI AYARLARI
excel_yolu = "bta.xls.xlsm"

# Çökmeyi önlemek için verileri geçici session_state hafızasında ve yedek dosyalarda tutuyoruz
if "ziyaret_sayisi" not in st.session_state:
    st.session_state["ziyaret_sayisi"] = 124  # Başlangıç örnek değeri
if "kullanici_adi" not in st.session_state:
    st.session_state["kullanici_adi"] = "Ziyaretci_" + str(int(time.time()) % 1000)
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "sohbet_gecmisi" not in st.session_state:
    st.session_state["sohbet_gecmisi"] = []
if "hisse_begenileri" not in st.session_state:
    st.session_state["hisse_begenileri"] = {}
if "hisse_yildizlari" not in st.session_state:
    st.session_state["hisse_yildizlari"] = {}

# Sol Menü (Sidebar) Paneli
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

# 7. ASLA ÇÖKMEYEN GARANTİLİ EXCEL ANALİZİ
tablo_rows_html = ""
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 4].dropna().unique()
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() != ""])
            
        for idx in range(min(10, len(df))):
            try:
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    c_fiyat = 0.0
                    try:
                        h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=1.5)
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
                    
                    # Güvenli Sözlük Altyapısı (Boş kalsa da hata fırlatmaz)
                    begeniler = st.session_state["hisse_begenileri"].get(ha, 0)
                    yildizlar = st.session_state["hisse_yildizlari"].get(ha, 0.0)
                    yildiz_str = "⭐" * int(round(yildizlar)) if yildizlar > 0 else "---"
                    
                    tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td><td>👍 {begeniler} | {yildiz_str}</td></tr>'
            except:
                pass
    except:
        pass

# 8. PANEL ÇIKTILARI
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#00ffcc; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {hisseler_str} hedefine ulaşarak %9 ve üzeri performans göstermiştir. Tebrik ederiz!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)

if veri_var_mi and tablo_rows_html != "":
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th><th>KAYIT DEFTERİ (BEĞENİ/YILDIZ)</th></tr>' + tablo_rows_html + '</table>'
    panel_html = f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 5px;"><p style="font-size:16px; font-weight:bold; color:#1E90FF; margin:0;">📈 BTA ALGORİTMİK HİSSE</p><p style="font-size:12px; font-weight:bold; color:#00ffcc; background-color:#121d33; padding:4px 10px; border-radius:6px; border:1px solid #1e3a5f; margin:0;">Son Yükleme: {excel_guncelleme_tarihi}</p></div>'
    st.markdown(panel_html, unsafe_allow_html=True)
    st.markdown(tablo_html, unsafe_allow_html=True)
else:
    tarama_html = '<div class="tarama-kutusu"><div style="font-size: 32px; margin-bottom: 10px;">🔍</div><p style="color: #00ffcc; font-weight: bold; margin-bottom: 5px; font-size: 18px; text-shadow: 0 0 5px rgba(0,255,204,0.3);">BTA Algoritması Piyasaları Tarıyor...</p><p style="margin: 0; font-size: 14px; color: #a2b4cc; line-height:1.6;">Kriterlere tam uyum sağlayan yeni bir hisse tespit edildiğinde, analiz verileri anında bu ekrana yansıtılacaktır.</p></div>'
    st.markdown(tarama_html, unsafe_allow_html=True)

# 9. HİSSE KAYIT DEFTERİ OYLAMA PANELİ
st.markdown("---")
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:8px;">📝 HİSSE KAYIT DEFTERİ DEĞERLENDİRME PANELİ</p>', unsafe_allow_html=True)

if len(tum_hisseler) > 0:
