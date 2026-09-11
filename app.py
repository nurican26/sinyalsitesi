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

# 4. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}]).to_csv(db_istatistik, index=False)

# Kilitlenmeyi önleyen önbellek hafızası
@st.cache_resource
def get_global_logged_signals():
    return set()

global_kayitlar = get_global_logged_signals()

# 5. ZİYARETÇİ SAYACINI TETİKLEME
ziyaret, basarili, basarisiz = 0, 0, 0
try:
    df_ist = pd.read_csv(db_istatistik)
    if df_ist.empty:
        df_ist = pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}])
    
    if "ziyaret_sayildi" not in st.session_state:
        df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state["ziyaret_sayildi"] = True
        
    ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
    basarili = int(df_ist.at[0, "basarili_oy"])
    basarisiz = int(df_ist.at[0, "basarisiz_oy"])
except:
    ziyaret, basarili, basarisiz = 1, 0, 0

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

# 🚀 TARİHİ KESİN OLARAK ŞU ANKİ ZAMANA EŞİTLİYORUZ
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")

# 7. EXCEL VERİLERİNİ OKUMA VE ANALİZ ETME
tablo_rows_html = ""
otomatik_eklenecekler = []

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 4].dropna().unique()
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() != ""])
            
        # 📌 KİLİTLENMEYİ ÖNLEYEN TOPLU FİYAT İNDİRME MEKANİZMASI (Süreyi saliselere indirir)
        indirilecek_hisseler = []
        for idx in range(min(10, len(df))):
            ha_kod = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            if ha_kod != "" and ha_kod not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                indirilecek_hisseler.append(f"{ha_kod}.IS")
        
        fiyat_sozlugu = {}
        if indirilecek_hisseler:
            try:
                # Tüm hisseleri tek bir komutla saniyeler içinde indiriyoruz
                toplu_veri = yf.download(indirilecek_hisseler, period="1d", group_by="ticker", auto_adjust=True, timeout=5, progress=False)
                for h_kod in indirilecek_hisseler:
                    try:
                        if len(indirilecek_hisseler) == 1:
                            fiyat_sozlugu[h_kod] = float(toplu_veri['Close'].iloc[-1])
                        else:
                            fiyat_sozlugu[h_kod] = float(toplu_veri[h_kod]['Close'].iloc[-1])
                    except:
                        fiyat_sozlugu[h_kod] = 0.0
            except:
                pass

        # HTML Tablosunu oluşturma süreci
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                
                # Hafızadan fiyatı anında çekiyoruz
                c_fiyat = fiyat_sozlugu.get(f"{ha}.IS", 0.0)
                
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
                
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'

                otomatik_eklenecekler.append({
                    "hisse": ha, "maliyet": maliyet, "c_fiyat": c_fiyat, "puan": p_temiz, "or_dg": or_dg
                })
    except:
        pass

# 🛠️ GÜVENLİ VE PERFORMANSLI OTOMATİK KAYIT SİSTEMİ
if otomatik_eklenecekler:
    try:
        df_notlar_mevcut = pd.read_csv(db_notlar)
        dosya_guncellendi = False
        
        for item in otomatik_eklenecekler:
            sinyal_anahtari = f"{item['hisse']}_{item['maliyet']}_{item['puan']}"
            
            if sinyal_anahtari not in global_kayitlar:
                zaten_var = False
                if not df_notlar_mevcut.empty:
                    kontrol = df_notlar_mevcut[(df_notlar_mevcut["hisse"] == item['hisse']) & 
                                               (df_notlar_mevcut["hedef_fiyat"] == f"{item['maliyet']:,.2f} TL")]
                    if not kontrol.empty:
                        zaten_var = True
                
                if not zaten_var:
                    yeni_id = int(df_notlar_mevcut["id"].max() + 1) if not df_notlar_mevcut.empty else 1
                    su_an = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                    oto_not = f"🤖 BTA Algoritması tarafından otomatik olarak sisteme işlendi. Anlık Fiyat: {item['c_fiyat']:,.2f} TL, K/Z Durumu: %{item['or_dg']:.2f}"
                    
                    yeni_satir = pd.DataFrame([{
                        "id": yeni_id,
                        "tarih": su_an,
                        "hisse": item['hisse'],
                        "not": oto_not,
                        "hedef_fiyat": f"{item['maliyet']:,.2f} TL"
                    }])
                    df_notlar_mevcut = pd.concat([df_notlar_mevcut, yeni_satir], ignore_index=True)
                    dosya_guncellendi = True
                
                global_kayitlar.add(sinyal_anahtari)
        
        if dosya_guncellendi:
            df_notlar_mevcut.to_csv(db_notlar, index=False)
    except:
        pass

