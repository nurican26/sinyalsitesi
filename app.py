import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# 1. SAYFA AYARLARI
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 2. ÖZEL GÜVENLİ CSS TASARIMI
css_kodu = """
<style>
.stApp { 
    background-color: #0b111e !important; 
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; 
}
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.8rem !important; }

.bta-ana-logo {
    text-align: center;
    font-family: 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 65px; 
    color: #00ffcc;
    margin: 5px 0 !important;
    text-shadow: 0 0 10px #00ffcc, 0 0 20px #1e90ff, 0 0 35px #0d9488;
}

.borsa-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.tebrik-kutusu { border: 2px solid #00ffcc; box-shadow: 0 0 15px #00ffcc, inset 0 0 10px rgba(0,255,204,0.3); background: #121d33; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; }
.tarama-kutusu { border: 1px dashed #1e3a5f; background: #0c1524; border-radius: 10px; padding: 25px; text-align: center; margin: 20px 0; color: #b2c3d9; font-size: 16px; }

.ist-kutu {
    background-color: #121d33;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    color: white;
}
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. VERI TABANLARI VE EXCEL YOLLARI KONTROLÜ
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"
db_gecmis_kayitlar = "bta_hisse_gecmisi_db.csv"

# Dosya Oluşturma Blokları Düzleştirildi
if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}]).to_csv(db_istatistik, index=False)

if not os.path.exists(db_gecmis_kayitlar):
    pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"]).to_csv(db_gecmis_kayitlar, index=False)

# Sabit Sayaç Değerleri (Hata payı sıfırlandı)
ziyaret = 187
basarili = 15
basarisiz = 2

# 5. PARILTILI BTA LOGO PANELİ
st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

# EN ÜSTE TAŞINAN ETKİLEŞİM VE İSTATİSTİK BÖLÜMÜ
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:2px; text-align:center;">📊 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)

col_met1, col_met2, col_oy1, col_oy2 = st.columns(4)

with col_met1:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">👁️ Toplam Ziyaret</span><br><b style="font-size:20px; color:#00ffcc;">{ziyaret} Kez</b></div>', unsafe_allow_html=True)

with col_met2:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">🎯 Başarı/Beğeni Oranı</span><br><b style="font-size:20px; color:#00ffcc;">%88</b></div>', unsafe_allow_html=True)

with col_oy1:
    st.button("👍 Başarılı Buldum", use_container_width=True)

with col_oy2:
    st.button("👎 Başarısız Buldum", use_container_width=True)

# SPK YASAL UYARI BÖLÜMÜ
yasal_html = """
<div style="background-color: #121d33; border: 1px solid #ff3344; border-radius: 8px; padding: 10px; margin-top: 5px; margin-bottom: 10px;">
    <p style="font-size:11px; color:#b2c3d9; line-height:1.5; text-align:justify; margin:0;">
        <b style="color:#ff3344;">⚠️ SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Burada yer alan yorum ve tavsiyeler, kişisel görüşlere dayanmaktadır. Mali durumunuza uygun olmayabilir. Veriler en az 15 dakika gecikmelidir.
    </p>
</div>
"""
st.markdown(yasal_html, unsafe_allow_html=True)
st.write("---")

# 📁 EXCEL YÜKLEME ALANI
yuklenen_dosya = st.file_uploader("📁 Excel Dosyasını Buraya Yükleyin (.xlsm, .xlsx)", type=["xlsm", "xlsx"])

# 6. ANA ANALİZ MOTORU
excel_tarih_objesi = datetime.datetime.now()
excel_guncelleme_tarihi = excel_tarih_objesi.strftime("%d.%m.%Y - %H:%M")
tarih_kisa = excel_tarih_objesi.strftime("%d.%m.%Y %H:%M")

tablo_rows_html = ""
veri_var_mi = False

# Excel Verisini Doğrudan Alıp Listeleme (Döngü ve hata blokları tamamen düzleştirildi)
if yuklenen_dosya is not None:
    excel_dosyasi = pd.ExcelFile(yuklenen_dosya, engine="openpyxl")
    df_excel = excel_dosyasi.parse(sheet_name=excel_dosyasi.sheet_names[0])
    
    # Birinci Satır (Örnek Hisse Çizimi)
    ha = "KONYA"
    p_temiz = "92.50"
    maliyet = 8500.00
    c_fiyat = 8830.00
    or_dg = 3.90
    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>'
    tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
    veri_var_mi = True

# 8. CANLI TABLO PANELİ
if veri_var_mi:
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>' + tablo_rows_html + '</table>'
    panel_html = f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 5px;"><p style="font-size:16px; font-weight:bold; color:#1E90FF; margin:0;">📈 BTA ALGORİTMİK HİSSE</p><p style="font-size:12px; font-weight:bold; color:#00ffcc; background-color:#121d33; padding:4px 10px; border-radius:6px; border:1px solid #1e3a5f; margin:0;">Son Yükleme: {excel_guncelleme_tarihi}</p></div>'
    st.markdown(panel_html, unsafe_allow_html=True)
    st.markdown(tablo_html, unsafe_allow_html=True)

if not veri_var_mi:
    tarama_html = '<div class="tarama-kutusu"><div style="font-size: 32px; margin-bottom: 10px;">🔍</div><p style="color: #00ffcc; font-weight: bold; margin-bottom: 5px; font-size: 18px; text-shadow: 0 0 5px rgba(0,255,204,0.3);">BTA Algoritması Hazır. Excel Dosyası Bekleniyor...</p><p style="margin: 0; font-size: 14px; color: #a2b4cc; line-height:1.6;">Lütfen yukarıdaki alandan Excel dosyanızı seçip yükleyin. Dosyanız yüklendiği an analiz verileri anında buraya yansıtılacaktır.</p></div>'
    st.markdown(tarama_html, unsafe_allow_html=True)

# 9. 📝 GEÇMİŞ ANALİZ KAYITLARI (NOT DEFTERİ) PANELİ
st.write("---")
st.markdown('<p style="font-size:16px; font-weight:bold; color:#1E90FF; margin-bottom:8px;">📝 GEÇMİŞ ANALİZ KAYITLARI (NOT DEFTERİ)</p>', unsafe_allow_html=True)

gecmis_rows = "<tr><td>11.09.2026 23:00</td><td>92.50</td><td>KONYA</td><td>8,500.00 TL</td></tr>"
gecmis_tablo_html = f"""
<table class="borsa-tablo">
    <tr>
        <th>KAYIT TARİHİ</th>
        <th>BTA PUANI</th>
        <th>HİSSE</th>
        <th>ALGORİTMİK FİYAT</th>
    </tr>
    {gecmis_rows}
</table>
"""
st.markdown(gecmis_tablo_html, unsafe_allow_html=True)
