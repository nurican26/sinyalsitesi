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

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}]).to_csv(db_istatistik, index=False)

if not os.path.exists(db_gecmis_kayitlar):
    pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"]).to_csv(db_gecmis_kayitlar, index=False)

# 4. ZIYARETCI SAYACINI TETIKLEME
ziyaret, basarili, basarisiz = 187, 15, 2
if os.path.exists(db_istatistik):
    try:
        df_ist = pd.read_csv(db_istatistik)
        if not df_ist.empty:
            if "ziyaret_sayildi" not in st.session_state:
                df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
                df_ist.to_csv(db_istatistik, index=False)
                st.session_state["ziyaret_sayildi"] = True
            ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
            basarili = int(df_ist.at[0, "basarili_oy"])
            basarisiz = int(df_ist.at[0, "basarisiz_oy"])
    except:
        pass

# 5. PARILTILI BTA LOGO PANELİ
st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

# EN ÜSTE TAŞINAN ETKİLEŞİM VE İSTATİSTİK BÖLÜMÜ
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:2px; text-align:center;">📊 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)

toplam_oy = basarili + basarisiz
begeni_orani = int((basarili / toplam_oy) * 100) if toplam_oy > 0 else 85

col_met1, col_met2, col_oy1, col_oy2 = st.columns(4)

with col_met1:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">👁️ Toplam Ziyaret</span><br><b style="font-size:20px; color:#00ffcc;">{ziyaret} Kez</b></div>', unsafe_allow_html=True)

with col_met2:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">🎯 Başarı/Beğeni Oranı</span><br><b style="font-size:20px; color:#00ffcc;">%{begeni_orani}</b></div>', unsafe_allow_html=True)

with col_oy1:
    if st.button("👍 Başarılı Buldum", use_container_width=True):
        try:
            df_ist = pd.read_csv(db_istatistik)
            df_ist.at[0, "basarili_oy"] = int(df_ist.at[0, "basarili_oy"]) + 1
            df_ist.to_csv(db_istatistik, index=False)
            st.toast("Oyunuz Kaydedildi! 👍")
        except:
            pass

with col_oy2:
    if st.button("👎 Başarısız Buldum", use_container_width=True):
        try:
            df_ist = pd.read_csv(db_istatistik)
            df_ist.at[0, "basarisiz_oy"] = int(df_ist.at[0, "basarisiz_oy"]) + 1
            df_ist.to_csv(db_istatistik, index=False)
            st.toast("Oyunuz Kaydedildi! 👎")
        except:
            pass

# SPK YASAL UYARI BÖLÜMÜ
yasal_html = """
<div style="background-color: #121d33; border: 1px solid #ff3344; border-radius: 8px; padding: 10px; margin-top: 5px; margin-bottom: 10px;">
    <p style="font-size:11px; color:#b2c3d9; line-height:1.5; text-align:justify; margin:0;">
        <b style="color:#ff3344;">⚠️ SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Burada yer alan yorum ve tavsiyeler, kişisel görüşlere dayanmaktadır. Mali durumunuz ile risk and getiri tercihlerinize uygun olmayabilir. Veriler en az 15 dakika gecikmelidir.
    </p>
</div>
"""
st.markdown(yasal_html, unsafe_allow_html=True)
st.write("---")

# 📁 EXCEL YÜKLEME ALANI
yuklenen_dosya = st.file_uploader("📁 Excel Dosyasını Buraya Yükleyin (.xlsm, .xlsx)", type=["xlsm", "xlsx"])

# 6. ANA ANALİZ MOTORU
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")
tarih_kisa = excel_tarih_objesi.strftime("%d.%m.%Y %H:%M")

tablo_rows_html = ""
veri_var_mi = False
basarili_hisseler = []

df_excel = pd.DataFrame()
df_gecmis = pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"])

# Excel Okuma Yapısı
if yuklenen_dosya is not None:
    try:
        excel_dosyasi = pd.ExcelFile(yuklenen_dosya, engine="openpyxl")
        mevcut_sayfalar = excel_dosyasi.sheet_names
        hedef_sayfa = mevcut_sayfalar[0]
        for sayfa in mevcut_sayfalar:
            if sayfa.strip().upper() == "WEB":
                hedef_sayfa = sayfa
        df_excel = excel_dosyasi.parse(sheet_name=hedef_sayfa)
    except:
        pass

if os.path.exists(db_gecmis_kayitlar):
    try:
        df_gecmis = pd.read_csv(db_gecmis_kayitlar)
    except:
        pass

yeni_kayitlar = []

# Sabit Sütun Düzenine Geri Dönüldü (Hata riskini sıfırlamak için)
hisse_col = 0
maliyet_col = 2
puan_col = 3

if not df_excel.empty:
    for idx in range(min(10, len(df_excel))):
        try:
            ha = str(df_excel.iloc[idx, hisse_col]).strip().upper() if pd.notna(df_excel.iloc[idx, hisse_col]) else ""
            alim_c = str(df_excel.iloc[idx, maliyet_col]).strip() if pd.notna(df_excel.iloc[idx, maliyet_col]) else ""
            puan_d = df_excel.iloc[idx, puan_col] if pd.notna(df_excel.iloc[idx, puan_col]) else ""
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG", "KOD"]:
                veri_var_mi = True
                p_temiz = "-"
                
                if pd.notna(puan_d) and str(puan_d).strip().lower() not in ["nan", "none", ""]:
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    
                c_fiyat = 0.0
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=3)
                    if len(h_veri) > 0:
                        c_fiyat = float(h_veri['Close'].iloc[-1])
                except:
                    c_fiyat = 0.0
                
                alim_c_temiz = alim_c.replace(",", ".").strip()
                maliyet = 0.0
                try:
                    if alim_c_temiz != "":
                        maliyet = float(alim_c_temiz)
                except:
                    maliyet = 0.0
                
                if maliyet > 0:
                    is_exist = False
                    if not df_gecmis.empty and 'Hisse' in df_gecmis.columns and 'Algoritmik Fiyat' in df_gecmis.columns:
                        is_exist = ((df_gecmis['Hisse'] == ha) & (df_gecmis['Algoritmik Fiyat'] == maliyet)).any()
                    
                    if not is_exist:
                        yeni_kayitlar.append({
                            "Tarih": tarih_kisa,
                            "BTA Puanı": p_temiz,
                            "Hisse": ha,
                            "Algoritmik Fiyat": maliyet
                        })

                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 9.0:
                        basarili_hisseler.append(ha)
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                elif maliyet > 0 and c_fiyat == 0.0:
                    kz_str = "<span style='color:#a2b4cc;'>Fiyat Çekilemedi</span>"
                else:
                    kz_str = "<span>-</span>"
                
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
        except:
            pass

if len(yeni_kayitlar) > 0:
    try:
        df_guncel_gecmis = pd.concat([df_gecmis, pd.DataFrame(yeni_kayitlar)], ignore_index=True)
        df_guncel_gecmis.to_csv(db_gecmis_kayitlar, index=False)
    except:
        pass

# 7. TEBRİK PANELİ GÖSTERİMİ
if len(basarili_hisseler) > 0:
