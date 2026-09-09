import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time  # Zaman takibi için eklendi
from streamlit_autorefresh import st_autorefresh
from streamlit.runtime.scriptrunner import get_script_run_ctx

# ===================================================================== #
# 1. BORSA TEMASI VE STİLLER (CSS - OKUNAKLI & KÜÇÜK)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.kucuk-sayac { font-size: 14px !important; color: #00ffcc !important; text-align: center; margin-top: 15px; font-weight: bold; }
.kucuk-baslik { font-size: 15px !important; color: #ffffff !important; font-weight: bold; margin-bottom: 5px; }
.online-kullanici { display: inline-block; background-color: #1a2e4c; color: #00ffcc; padding: 4px 10px; border-radius: 20px; font-size: 13px; margin: 3px; border: 1px solid #1e3a5f; }
.online-nokta { height: 10px; width: 10px; background-color: #00ff66; border-radius: 50%; display: inline-block; margin-right: 5px; animate: pulse 2s infinite; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:15px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı ve Fiyatları Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_sohbet_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"
db_arsiv = "bta_hisse_arsiv_db.csv"
db_aktif_kullanicilar = "bta_aktif_kullanicilar_db.csv"

# KALICI VERİTABANLARINI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if not os.path.exists(db_arsiv):
    pd.DataFrame(columns=["tarih_saat", "bta_puani", "hisse", "algoritmik_fiyat", "guncel_fiyat", "kz_orani"]).to_csv(db_arsiv, index=False)

if not os.path.exists(db_aktif_kullanicilar):
    pd.DataFrame(columns=["session_id", "isim", "son_aktiflik"]).to_csv(db_aktif_kullanicilar, index=False)

if "topham_sayac" not in st.session_state: st.session_state["topham_sayac"] = 1450
st.session_state["topham_sayac"] += 1

# KULLANICI RUMUZU VE OTURUM TAKİBİ
ctx = get_script_run_ctx()
session_id = ctx.session_id if ctx else "bilinmeyen_oturum"

if "kullanici_adi" not in st.session_state:
    st.session_state["kullanici_adi"] = f"Misafir_{session_id[:5].upper()}"

# AKTİFLİK GÜNCELLEME MOTORU (Syntax hatası düzeltildi)
try:
    su_an = int(time.time())
    df_aktif = pd.read_csv(db_aktif_kullanicilar)
    
    # Mevcut oturum kayıtlı mı kontrol et
    if session_id in df_aktif["session_id"].values:
        df_aktif.loc[df_aktif["session_id"] == session_id, "son_aktiflik"] = su_an
        df_aktif.loc[df_aktif["session_id"] == session_id, "isim"] = st.session_state["kullanici_adi"]
    else:
        yeni_user = pd.DataFrame([{"session_id": session_id, "isim": st.session_state["kullanici_adi"], "son_aktiflik": su_an}])
        df_aktif = pd.concat([df_aktif, yeni_user], ignore_index=True)
    
    # 20 saniyeden uzun süre ekranı yenilenmeyen (odadan çıkan) kullanıcıları temizle
    df_aktif = df_aktif[(su_an - df_aktif["son_aktiflik"]) < 20]
    df_aktif.to_csv(db_aktif_kullanicilar, index=False)
except:
    pass

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# CANLI ÇEVRİMİÇİ ÜYE PANELİ (ÜST ALAN)
# ===================================================================== #
try:
    df_online = pd.read_csv(db_aktif_kullanicilar)
    toplam_online = len(df_online)
    
    online_html = f'<div style="background-color:#121d33; padding:10px; border-radius:10px; border:1px solid #1e3a5f; margin-bottom:15px;">'
    online_html += f'<p style="color:#00ffcc; font-weight:bold; margin-bottom:5px; font-size:14px;"><span class="online-nokta"></span> CANLI ODADA {toplam_online} KİŞİ VAR</p>'
    
    for _, row in df_online.iterrows():
        online_html += f'<span class="online-kullanici">👤 {row["isim"]}</span>'
    
    online_html += '</div>'
    st.markdown(online_html, unsafe_allow_html=True)
except:
    pass

# ===================================================================== #
# 2. CANLI ALTIN VE BIST 100 PİYASA ALANI (SABİTLENMİŞ GÖSTERGELER)
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=2)['Close'].iloc[-1])
    usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    gram_f = (ons_f / 31.1034768) * usd_f
    
    pk1, pk2, pk3, col_bist, col_eur = st.columns(5)
    pk1.metric("GRAM ALTIN", f"{gram_f:,.1f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.1f} TL")
    pk3.metric("YARIM ALTIN", f"{gram_f * 3.26:,.1f} TL")
    col_bist.metric("BIST 100", f"{bist_f:,.1f}")
    col_eur.metric("EURO", f"{eur_f:,.2f} TL")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        veri_var_mi = False
        
        anlik_gelen_hisseler = []
        
        for idx in range(min(10, len(df))):
            try:
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                    try: maliyet = float(alim_c.replace(",", "."))
                    except: maliyet = 0.0
                    
                    if maliyet > 0 and c_fiyat > 0:
                        or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.1f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.1f}</span>'
                        kz_kayit_str = f"▲ %{or_dg:.1f}" if or_dg >= 0 else f"▼ %{or_dg:.1f}"
                    else: 
                        kz_str = "<span>-</span>"
                        kz_kayit_str = "-"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.1f} TL</td><td>{c_fiyat:,.1f} TL</td><td>{kz_str}</td></tr>'
                    
                    anlik_gelen_hisseler.append({
                        "tarih_saat": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                        "bta_puani": p_temiz,
                        "hisse": ha,
                        "algoritmik_fiyat": f"{maliyet:,.2f} TL",
                        "guncel_fiyat": f"{c_fiyat:,.2f} TL",
                        "kz_orani": kz_kayit_str
                    })
            except: continue
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: 
            st.markdown(tablo_html, unsafe_allow_html=True)
            
            try:
                df_arsiv_oku = pd.read_csv(db_arsiv)
                yeni_kayitlar = []
                
                for h_bilgi in anlik_gelen_hisseler:
                    hisse_eski_kayitlar = df_arsiv_oku[df_arsiv_oku["hisse"] == h_bilgi["hisse"]]
                    
                    if hisse_eski_kayitlar.empty:
                        yeni_kayitlar.append(h_bilgi)
                    else:
                        son_kayit = hisse_eski_kayitlar.iloc[-1]
                        if (str(son_kayit["algoritmik_fiyat"]) != str(h_bilgi["algoritmik_fiyat"])) or (str(son_kayit["bta_puani"]) != str(h_bilgi["bta_puani"])):
