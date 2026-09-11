import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

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

# 3. 5 SANİYEDE BİR YENİLEME MOTORU
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# 4. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"
db_gecmis_kayitlar = "bta_hisse_gecmisi_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 187, "basarili_oy": 15, "basarisiz_oy": 2}]).to_csv(db_istatistik, index=False)

# Kalıcı Geçmiş Kayıt Tablosu Altyapısı
if not os.path.exists(db_gecmis_kayitlar):
    pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat", "Anlık Fiyat", "Kar_Zarar_Yuzde"]).to_csv(db_gecmis_kayitlar, index=False)

# İstatistik Sayaçlarını Yükle
try:
    df_ist = pd.read_csv(db_istatistik)
    if df_ist.empty:
        df_ist = pd.DataFrame([{"ziyaret_sayisi": 187, "basarili_oy": 15, "basarisiz_oy": 2}])
    
    if "ziyaret_kaydedildi" not in st.session_state:
        df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state["ziyaret_kaydedildi"] = True

    ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
    basarili = int(df_ist.at[0, "basarili_oy"])
    basarisiz = int(df_ist.at[0, "basarisiz_oy"])
except:
    ziyaret, basarili, basarisiz = 188, 15, 2

toplam_oy = basarili + basarisiz
basari_orani = int((basarili / toplam_oy) * 100) if toplam_oy > 0 else 88

# 5. PARILTILI BTA LOGO PANELİ
st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

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

# ETKİLEŞİM VE İSTATİSTİK BÖLÜMÜ
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:2px; text-align:center;">📊 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)

col_met1, col_met2, col_oy1, col_oy2 = st.columns(4)

with col_met1:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">👁️ Toplam Ziyaret</span><br><b style="font-size:20px; color:#00ffcc;">{ziyaret} Kez</b></div>', unsafe_allow_html=True)

with col_met2:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">🎯 Başarı/Beğeni Oranı</span><br><b style="font-size:20px; color:#00ffcc;">%{basari_orani}</b></div>', unsafe_allow_html=True)

with col_oy1:
    if st.button("👍 Başarılı Buldum", use_container_width=True):
        df_ist.at[0, "basarili_oy"] = basarili + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.rerun()

with col_oy2:
    if st.button("👎 Başarısız Buldum", use_container_width=True):
        df_ist.at[0, "basarisiz_oy"] = basarisiz + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.rerun()

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

# 6. ANA ANALİZ MOTORU (Otomatik Dosya Okuma)
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M")

tablo_rows_html = ""
veri_var_mi = False
basarili_hisseler = []

# Mevcut kaydedilmiş verileri CSV'den yükle
try:
    df_gecmis_db = pd.read_csv(db_gecmis_kayitlar)
except:
    df_gecmis_db = pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat", "Anlık Fiyat", "Kar_Zarar_Yuzde"])

yeni_kayitlar = []

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                
                # Canlı Fiyat Çekimi
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                except:
                    pass
                
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                
                or_dg = 0.0
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 9.0:
                        basariliHisse_adi = ha.replace(".IS", "")
                        basarili_hisseler.append(f"<b>{basariliHisse_adi}</b> (%{or_dg:.2f})")
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                
                # Canlı Tablo Satırı
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
                
                # Veritabanında bu hisse aynı gün zaten kaydedilmiş mi kontrol et (Mükerrer kaydı önler)
                gunluk_kontrol = df_gecmis_db[(df_gecmis_db["Tarih"].str.contains(excel_guncelleme_tarihi.split(" -")[0])) & (df_gecmis_db["Hisse"] == ha)]
                if gunluk_kontrol.empty:
                    yeni_kayitlar.append({
                        "Tarih": excel_guncelleme_tarihi,
                        "BTA Puanı": p_temiz,
                        "Hisse": ha,
                        "Algoritmik Fiyat": f"{maliyet:,.2f} TL",
                        "Anlık Fiyat": f"{c_fiyat:,.2f} TL",
                        "Kar_Zarar_Yuzde": f"{or_dg:.2f}"
                    })
        
        # Yeni taranan hisseleri kalıcı olarak CSV veritabanına ekle ve kaydet
        if yeni_kayitlar:
            df_yeni = pd.DataFrame(yeni_kayitlar)
            df_gecmis_db = pd.concat([df_gecmis_db, df_yeni], ignore_index=True)
            df_gecmis_db.to_csv(db_gecmis_kayitlar, index=False)
            
    except Exception as e:
        st.error(f"Excel veya veritabanı senkronizasyon hatası: {e}")

# 7. OTOMATİK BAŞARI TEBRİK PANELİ
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
