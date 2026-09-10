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
st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; font-size: 14px !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
/* Işıklı Ve Parıltılı Yeni Neon Tebrik Paneli Stili */
.tebrik-kutusu { border: 2px solid #00ffcc; box-shadow: 0 0 15px #00ffcc, inset 0 0 10px rgba(0,255,204,0.3); background: #121d33; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 20px; }
</style>
''', unsafe_allow_html=True)

# 3. 5 SANİYEDE BİR YENİLEME MOTORU
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# 4. VERİ TABANLARI VE EXCEL YOLLARI
# 👇 BURADAKİ DOSYA ADINI YENİ OLUŞTURDUĞUMUZ EXCEL ADIYLA GÜNCELLEDİK
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"

# Not veri tabanı kontrolü
if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

# İstatistik veri tabanı kontrolü
if not os.path.exists(db_istatistik):
    pd.DataFrame([[0, 0, 0]], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"]).to_csv(db_istatistik, index=False)

# 5. ZİYARETÇİ SAYACINI TETİKLEME
ziyaret = 0
basarili = 0
basarisiz = 0

if os.path.exists(db_istatistik):
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

# LOGO VE BAŞLIK
st.markdown('<h1 style="text-align:center; color:#00ffcc; font-family:\'Brush Script MT\', cursive, sans-serif; font-size:42px; margin-top:5px; margin-bottom:5px;">BTA</h1>', unsafe_allow_html=True)

# YENİ ÖZELLİK: TRADINGVIEW CANLI BIST 100 MINI GRAFİK KARTI
bist_mini_widget = """
<div class="tradingview-widget-container" style="margin: auto; text-align: center; width: 100%; max-width: 450px;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://tradingview.com" async>
  {
  "symbol": "BIST:XU100",
  "width": "100%",
  "height": "110",
  "locale": "tr",
  "dateRange": "1D",
  "colorTheme": "dark",
  "isTransparent": true,
  "autosize": false,
  "largeChartUrl": ""
  }
  </script>
</div>
"""
components.html(bist_mini_widget, height=120)
st.write("---")

tum_hisseler = [] 
veri_var_mi = False
basarili_hisseler = []

# 🗓️ EXCEL DOSYASININ YÜKLENME TARİHİNİ BULMA MOTORU
excel_guncelleme_tarihi = "Bilinmiyor"
if os.path.exists(excel_yolu):
    try:
        dosya_zaman_damgasi = os.path.getmtime(excel_yolu)
        excel_tarih_objesi = datetime.datetime.fromtimestamp(dosya_zaman_damgasi)
        gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        gun_adi = gunler_tr[excel_tarih_objesi.weekday()]
        excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gun_adi}")
    except:
        pass

# 6. EXCEL VERİLERİNİ OKUMA VE ANALİZ ETME
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
                
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
    except:
        pass

# 7. OTOMATİK NEON IŞIKLI TEBRİK PANELI
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'''
    <div class="tebrik-kutusu">
        <h3 style="color:#00ffcc; margin:0 0 8px 0; font-size:22px; text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc; font-weight: bold; letter-spacing: 1px;">
            ⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡
        </h3>
        <p style="color:#ffffff; font-size:16px; margin:0; line-height: 1.5;">
            Sistemimizde takip edilen {hisseler_str} algoritmik hedefine ulaşarak <b style="color:#00ffcc; text-shadow: 0 0 5px #00ffcc;">%9 ve üzeri</b> performans göstermiştir. Tebrik ederiz!
        </p>
    </div>
    '''
    st.markdown(tebrik_html, unsafe_allow_html=True)

# 8. BORSA TABLOSU PANELİ (YÜKLEME TARİHİ SAĞ ÜSTTE SABİT)
if veri_var_mi and tablo_rows_html != "":
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>' + tablo_rows_html + '</table>'
    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 10px;">
        <p style="font-size:18px; font-weight:bold; color:#1E90FF; margin:0;">📈 BTA ALGORİTMİK HİSSE <span style="font-size:12px; color:#ff3344; font-weight:normal; margin-left:10px;">⚠️ Veriler en az 15 dk gecikmelidir.</span></p>
        <p style="font-size:14px; font-weight:bold; color:#00ffcc; background-color:#121d33; padding:6px 15px; border-radius:8px; border:1px solid #1e3a5f; margin:0; text-shadow: 0 0 5px rgba(0,255,204,0.5);">🔄 Son Yükleme: {excel_guncelleme_tarihi}</p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown(tablo_html, unsafe_allow_html=True)
elif not os.path.exists(excel_yolu):
    st.error("Excel bulunamadı.")

# 9. YASAL UYARI BÖLÜMÜ
st.markdown('''
<div style="background-color: #121d33; border: 1px solid #ff3344; border-radius: 8px; padding: 15px; margin-top: 15px; margin-bottom: 15px;">
    <p style="font-size:13px; font-weight:bold; color:#ff3344; margin-bottom:8px; text-transform: uppercase; letter-spacing: 0.5px;">
        ⚠️ ÖNEMLİ YASAL UYARI (15 DAKİKA GECİKMELİ VERİ)
    </p>
    <p style="font-size:12px; color:#b2c3d9; line-height:1.6; text-align:justify; margin:0;">
        Bu tabloda ve platform genelinde yer alan tüm fiyatlar, K/Z oranları ve algoritmik hesaplamalar en az <b>15 dakika gecikmeli</b> veriler kullanılarak otomatik olarak üretilmektedir. 
        Sitemiz tamamen ücretsiz, herkese açık ve genel bilgilendirme amacıyla yayın yapan bağımsız bir platform olup; burada yer alan 'BTA Puanı', 'Algoritmik Fiyat' veya diğer hiçbir veri, formül ve grafik çıktısı yatırım danışmanlığı, yatırım tavsiyesi, hedef fiyat öngörüsü veya al/sat/tut yönlendirmesi niteliği taşımamaktadır.
    </p>
</div>
''', unsafe_allow_html=True)

# 10. ETKİLEŞİM VE BAŞARI ORANI ANKETİ
st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#00ffcc;">📊 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)

col_ist1, col_ist2, col_ist3 = st.columns(3)
with col_ist1:
    st.metric("👁️ Toplam Ziyaret Sayısı", f"{ziyaret} Kez")
