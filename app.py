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
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. 5 SANİYEDE BİR YENİLEME MOTORU
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# 4. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"
db_kayit_defteri = "bta_kayit_defteri_db.csv"

# Hafıza kontrolü (Döngü kilitlenmesini engellemek için)
if "kaydedilen_hisseler" not in st.session_state:
    st.session_state["kaydedilen_hisseler"] = set()

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"]).to_csv(db_istatistik, index=False)

# Kayıt Defteri İlk Kurulum ve Güvenli Sıfırlama
if not os.path.exists(db_kayit_defteri):
    pd.DataFrame(columns=["Tarih", "Hisse", "Performans"]).to_csv(db_kayit_defteri, index=False)
else:
    try:
        # Eğer dosya bozulduysa veya yanlış veri dolduysa temizle
        df_check = pd.read_csv(db_kayit_defteri)
        if df_check.shape[1] != 3:
            pd.DataFrame(columns=["Tarih", "Hisse", "Performans"]).to_csv(db_kayit_defteri, index=False)
    except:
        pd.DataFrame(columns=["Tarih", "Hisse", "Performans"]).to_csv(db_kayit_defteri, index=False)

# 5. ZİYARETÇİ SAYACINI TETİKLEME
ziyaret, basarili, basarisiz = 0, 0, 0
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
        basarili = int(df_ist.at[0, "basarili_oy"])
        basarisiz = int(df_ist.at[0, "basarisiz_oy"])
    except:
        pass

# 6. KÖŞEDEN KÖŞEYE SÜREKLİ YÜRÜYEN BTA LOGOSU
st.markdown('<div class="logo-yurume-alani"><h1 class="yuruyen-bta-logo">BTA</h1></div>', unsafe_allow_html=True)

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
basarili_hisseler_kayit_verisi = []

# 🚀 TARİHİ KESİN OLARAK ŞU ANKİ ZAMANA EŞİTLİYORUZ
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")
kayit_defteri_tarihi = excel_tarih_objesi.strftime("%d.%m.%Y %H:%M")

# 7. EXCEL VERİLERİNİ OKUMA VE ANALİZ ETME
tablo_rows_html = ""
if os.path.exists(excel_yolu):
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
                    basarili_hisseler_kayit_verisi.append({"Hisse": basariliHisse_adi, "Performans": f"%{or_dg:.2f}"})
                kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
            else:
                kz_str = "<span>-</span>"
            
            tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'

# 8. OTOMATİK BAŞARI TEBRİK PANELİ VE GÜVENLİ KAYIT SİSTEMİ
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#00ffcc; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {hisseler_str} hedefine ulaşarak %9 ve üzeri performans göstermiştir. Tebrik ederiz!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)
    
    # 📌 MÜKERRER KAYIT ENGELLEYİCİ: Sadece bu oturumda kaydedilmeyenleri ekle
    try:
        df_kayit = pd.read_csv(db_kayit_defteri)
        yeni_kayitlar = []
        for veri in basarili_hisseler_kayit_verisi:
            hisse_anahtar = f"{veri['Hisse']}_{kayit_defteri_tarihi.split()[0]}" # Hisse ismi + Günlük Tarih
            
            # Eğer dosyanın içinde zaten yoksa VE oturum hafızasında işlenmediyse
            if hisse_anahtar not in st.session_state["kaydedilen_hisseler"]:
                if not ((df_kayit['Hisse'] == veri['Hisse']) & (df_kayit['Tarih'].str.startswith(kayit_defteri_tarihi.split()[0]))).any():
                    yeni_kayitlar.append({
                        "Tarih": kayit_defteri_tarihi,
                        "Hisse": veri['Hisse'],
                        "Performans": veri['Performans']
                    })
                st.session_state["kaydedilen_hisseler"].add(hisse_anahtar)
                
        if yeni_kayitlar:
            df_yeni = pd.DataFrame(yeni_kayitlar)
            df_son_kayit = pd.concat([df_kayit, df_yeni], ignore_index=True)
            df_son_kayit.to_csv(db_kayit_defteri, index=False)
    except:
        pass

# 9. TABLO VEYA ARAMA METNİ PANELİ
if veri_var_mi and tablo_rows_html != "":
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>' + tablo_rows_html + '</table>'
