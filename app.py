import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. BORSA TEMASI VE STİLLER (CSS - OKUNAKLI & KÜÇÜK)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.oda-sayici { background: linear-gradient(90deg, #1e3a5f 0%, #121d33 100%); color: #00ffcc; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; border: 1px solid #00ffcc; margin-bottom: 15px; }
.defter-kutu { background-color: #121d33; border-left: 5px solid #00ffcc; border-radius: 6px; padding: 10px; margin-bottom: 8px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:5px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı, Fiyatları ve Canlı Odayı Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_hisse_defteri = "bta_hisse_kayit_defteri_db.csv"
db_aktiflik = "bta_aktiflik_db.csv"

# KALICI VERİTABANLARI BAŞLATMA
if not os.path.exists(db_hisse_defteri):
    pd.DataFrame(columns=["tarih", "saat", "hisse", "bta_puani", "algoritmik_fiyat"]).to_csv(db_hisse_defteri, index=False)

if not os.path.exists(db_aktiflik):
    pd.DataFrame(columns=["rumuz", "son_gorulme"]).to_csv(db_aktiflik, index=False)

# ===================================================================== #
# RUMUZ GİRİŞ SİSTEMİ (GERÇEK KİŞİ DOĞRULAMA)
# ===================================================================== #
if "bta_rumuz" not in st.session_state:
    st.markdown("<h3 style='text-align:center; color:#fff;'>BTA Merkez Paneline Giriş</h3>", unsafe_allow_html=True)
    giriş_rumuz = st.text_input("Lütfen Panel için bir Rumuz (Ad) giriniz:", max_chars=20, key="rumuz_input")
    if st.button("Panele Bağlan 🚀") and giriş_rumuz.strip():
        st.session_state["bta_rumuz"] = giriş_rumuz.strip().upper()
        st.rerun()
    st.stop()

# --- ANLIK CANLI ODA SAYISI MOTORU (GERÇEK RUMUZ TABANLI) ---
simdi = time.time()
try:
    df_akt = pd.read_csv(db_aktiflik)
    df_akt = df_akt[df_akt["rumuz"] != st.session_state["bta_rumuz"]]
    yeni_akt = pd.DataFrame([{"rumuz": st.session_state["bta_rumuz"], "son_gorulme": simdi}])
    df_akt = pd.concat([df_akt, yeni_akt], ignore_index=True)
    df_akt = df_akt[df_akt["son_gorulme"] > (simdi - 12)]
    df_akt.to_csv(db_aktiflik, index=False)
    
    aktif_listesi = df_akt["rumuz"].unique().tolist()
    canli_oda_sayisi = len(aktif_listesi)
except:
    canli_oda_sayisi = 1
    aktif_listesi = [st.session_state["bta_rumuz"]]

st.markdown(f'<div style="text-align:center;"><div class="oda-sayici">🟢 Canlı Oda Sayısı: {canli_oda_sayisi} Gerçek Kişi Aktif</div></div>', unsafe_allow_html=True)

with st.expander(f"👥 Odadaki Bağlantıları Gör ({canli_oda_sayisi})"):
    st.caption(", ".join(aktif_listesi))

# ===================================================================== #
# 2. CANLI ALTIN VE BIST 100 PİYASA ALANI
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=2)['Close'].iloc[-1])
    usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    gram_f = (ons_f / 31.1034768) * usd_f
    
    pk1, pk2, pk3, col_bist, col_eur = st.columns(5)
    pk1.metric("GRAM ALTIN", f"{gram_f:,.2f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.2f} TL")
    pk3.metric("YARIM ALTIN", f"{gram_f * 3.26:,.2f} TL")
    col_bist.metric("BIST 100", f"{bist_f:,.2f}")
    col_eur.metric("EURO", f"{eur_f:,.2f} TL")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. YENİ YER: TARİHLİ OTOMATİK HİSSE KAYIT DEFTERİ (EN ÜSTTE)
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#00ffcc;">📅 Tarihli Otomatik Hisse Kayıt Defteri (Asla Silinmez Arşiv)</p>', unsafe_allow_html=True)

# Önce Excel verilerini arka planda okuyup yeni hisse var mı kontrol edelim ve kaydedelim
yeni_kayitlar_listesi = []
if os.path.exists(excel_yolu):
    try:
        df_excel_check = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        df_kayitli_defter_check = pd.read_csv(db_hisse_defteri)
        bugunun_tarihi_check = datetime.datetime.now().strftime("%d.%m.%Y")
        
        for idx_c in range(min(10, len(df_excel_check))):
            ha_c = str(df_excel_check.iloc[idx_c, 0]).strip().upper() if pd.notna(df_excel_check.iloc[idx_c, 0]) else ""
            alim_c_c = str(df_excel_check.iloc[idx_c, 2]).strip() if pd.notna(df_excel_check.iloc[idx_c, 2]) else ""
            puan_d_c = df_excel_check.iloc[idx_c, 3]
            
            if ha_c != "" and ha_c not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                p_temiz_c = f"{float(puan_d_c):.2f}" if isinstance(puan_d_c, (int, float)) else str(puan_d_c).strip()
                try: maliyet_c = float(alim_c_c.replace(",", "."))
                except: maliyet_c = 0.0
                
                zaten_var_mi = df_kayitli_defter_check[(df_kayitli_defter_check["hisse"] == ha_c) & (df_kayitli_defter_check["tarih"] == bugunun_tarihi_check)]
                if zaten_var_mi.empty:
                    yeni_satir = {
                        "tarih": bugunun_tarihi_check,
                        "saat": datetime.datetime.now().strftime("%H:%M"),
                        "hisse": ha_c,
                        "bta_puani": p_temiz_c,
                        "algoritmik_fiyat": f"{maliyet_c:,.2f} TL"
                    }
                    yeni_kayitlar_listesi.append(yeni_satir)
                    
        if yeni_kayitlar_listesi:
            df_yeni_eklemeler = pd.DataFrame(yeni_kayitlar_listesi)
            df_guncel_defter = pd.concat([df_yeni_eklemeler, df_kayitli_defter_check], ignore_index=True)
            df_guncel_defter.to_csv(db_hisse_defteri, index=False)
            st.rerun()
    except:
        pass

# Güncellenmiş arşivi ekrana basma alanı (En yeni hisse en üstte görünür)
df_gosterilecek_defter = pd.read_csv(db_hisse_defteri)
if not df_gosterilecek_defter.empty:
    for idx, row in df_gosterilecek_defter.iterrows():
        st.markdown(f'''
        <div class="defter-kutu">
            <span style="color:#aaa; font-size:12px;">⏱ {row["tarih"]} - {row["saat"]}</span> &nbsp;&nbsp;&nbsp; 
            <span style="color:#00ffcc; font-size:15px; font-weight:bold;">🔥 {row["hisse"]}</span> &nbsp;&nbsp;&nbsp; 
            <span style="color:#fff;">BTA Puanı: <b>{row["bta_puani"]}</b></span> &nbsp;&nbsp;&nbsp; 
            <span style="color:#fff;">Algoritmik Fiyat: <b style="color:#00ff66;">{row["algoritmik_fiyat"]}</b></span>
        </div>
        ''', unsafe_allow_html=True)
else:
    st.info("Sistem otomatik takibe başladı. Excel tablonuza yeni bir hisse düştüğü an burada tarihli olarak sonsuza dek kilitlenecektir.")

# ===================================================================== #
# 4. ANA VERİ MOTORU VE TABLOLAR
# ===================================================================== #
st.write("---")
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        veri_var_mi = False
        
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
