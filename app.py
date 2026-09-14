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

# 2. ÖZEL CSS VE HAREKETLİ ŞİMŞEKLİ ARKA PLAN TASARIMI (KESİN ÇÖZÜM)
css_kodu = """
<style>
/* Streamlit'in tüm iç katmanlarını ezen kesin arka plan gradyanı */
html, body, [data-testid="stAppViewContainer"], .stApp { 
    background-color: #05070f !important; 
    background-image: 
        radial-gradient(at 20% 20%, rgba(0, 242, 254, 0.18) 0px, transparent 40%),
        radial-gradient(at 80% 40%, rgba(147, 51, 234, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 80%, rgba(0, 255, 204, 0.1) 0px, transparent 40%) !important; 
    background-attachment: fixed !important;
}

.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }

/* Şimşek Çizgili ve Parlak Neon Panel Kutuları */
div[data-testid="stMetric"], div[data-testid="stExpander"] { 
    background: linear-gradient(135deg, #0d1527 0%, #070a14 100%) !important; 
    border: 1px solid #00f2fe !important; 
    box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.2), inset 0px 0px 10px rgba(0, 242, 254, 0.1) !important;
    border-radius: 10px !important; 
    padding: 12px !important; 
}

/* Borsa Tablosu ve Şimşek Mavisi Çizgiler */
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #0d1527; border-radius: 10px; overflow: hidden; border: 1px solid #00f2fe; box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.15); }
.borsa-tablo th { background-color: #16223f; color: #00ffcc; text-align: left; padding: 10px 8px; border-bottom: 2px solid #00f2fe; text-shadow: 0 0 5px #00ffcc; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #16223f; font-weight: bold; }
.tebrik-kutusu { border: 2px solid #fffb00; box-shadow: 0 0 20px #fffb00, inset 0 0 10px rgba(255,251,0,0.3); background: #0d1527; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; }
.tarama-kutusu { border: 1px dashed #00f2fe; background: #070a14; border-radius: 10px; padding: 25px; text-align: center; margin: 20px 0; color: #b2c3d9; font-size: 16px; box-shadow: 0 0 15px rgba(0, 242, 254, 0.05); }

/* HTML Tabanlı Özel SPK Uyarı Kutusu */
.spk-kirmizi-kutu {
    background-color: rgba(255, 51, 68, 0.08) !important;
    border: 1px solid #ff3344 !important;
    box-shadow: 0px 0px 10px rgba(255, 51, 68, 0.2) !important;
    border-radius: 8px;
    padding: 12px;
    margin-top: 5px;
    margin-bottom: 15px;
}

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

/* Şık Kayan El Yazısı Fontu ve Voltajı Yüksek Şimşek Parlaması */
.yuruyen-bta-logo {
    font-family: 'Pacifico', 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 55px; 
    color: #fffb00;
    display: inline-block;
    animation: btaYoru 15s infinite linear;
    text-shadow: 0 0 12px #fffb00, 0 0 25px #ff6c00, 0 0 40px #00f2fe;
}
</style>
<link rel="preconnect" href="https://googleapis.com">
<link rel="preconnect" href="https://gstatic.com" crossorigin>
<link href="https://googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. 5 SANİYEDE BİR YENİLEME MOTORU
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# YASAL UYARI METNİ ŞABLONU
spk_metni_ham = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# 4. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"]).to_csv(db_istatistik, index=False)

# 5. ZİYARETÇİ SAYACINI TETİKLEME
ziyaret = 0
if os.path.exists(db_istatistik):
    try:
        df_ist = pd.read_csv(db_istatistik)
        if df_ist.empty:
            df_ist = pd.DataFrame([], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"])
        if "ziyaret_sayildi" not in st.session_state:
            df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
            df_ist.to_csv(db_istatistik, index=False)
            st.session_state["ziyaret_sayildi"] = True
        ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
    except:
        pass

# 6. KÖŞEDEN KÖŞEYE SÜREKLİ YÜRÜYEN EL YAZISI BTA LOGOSU
st.markdown('<div class="logo-yurume-alani"><h1 class="yuruyen-bta-logo">⚡ 🧠 BTA Algoritmik İşlem Portalı 🧠 ⚡</h1></div>', unsafe_allow_html=True)

# KESİN OLARAK EN ÜSTE SABİTLENEN KIRMZI SPK UYARI PANELİ
st.markdown(f'<div class="spk-kirmizi-kutu"><p style="font-size:12px; color:#f2f4f8; font-weight:bold; line-height:1.6; text-align:justify; margin:0;">{spk_metni_ham}</p></div>', unsafe_allow_html=True)

# TRADINGVIEW CANLI BIST 100 MINI GRAFİK KARTI
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

# TARİH ANALİZİ
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")

# 7. EXCEL VERİLERİNİ OKUMA VE ANALİZ ETME
tablo_rows_html = ""
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        df = df.fillna("")
        
        for idx in range(len(df)):
            ha = str(df.iloc[idx, 0]).strip().upper() if idx < len(df) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if idx < len(df) else ""
            puan_d = df.iloc[idx, 3] if idx < len(df) else ""
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG", "None", "NaN", "nan"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                p_temiz = "" if p_temiz in ["None", "NaN", "nan", "0.00"] else p_temiz
                
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
                
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
    except Exception as e:
        pass

# 8. OTOMATİK BAŞARI TEBRİK PANELİ
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#fffb00; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {hisseler_str} hedefine ulaşarak %9 ve üzeri performans göstermiştir. Tebrik ederiz!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)

# 9. TABLO VEYA ARAMA METNİ PANELİ
if veri_var_mi and tablo_rows_html != "":
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>ANLIK FİYAT</th><th>K/Z</th></tr>' + tablo_rows_html + '</table>'
