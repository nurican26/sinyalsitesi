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

/* Kayan Yazı Bant Tasarımı */
.kayan-yazi-bandi { background: #121d33; border-bottom: 2px solid #1e3a5f; padding: 8px 0; overflow: hidden; white-space: nowrap; font-family: monospace; font-size: 16px; font-weight: bold; }
.kayan-icerik { display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; }
@keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
.piyasa-yukselis { color: #00ff66; margin-right: 30px; }
.piyasa-dusis { color: #ff3344; margin-right: 30px; }
.piyasa-notr { color: #ffffff; margin-right: 30px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:5px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı, Fiyatları ve Canlı Odayı Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_yildizlar = "bta_yildiz_begenileri_db.csv"
db_ortak_oda = "bta_ortak_oda_aktiflik.csv"
db_notlar = "bta_ortak_notlar_db.csv"

# KALICI VERİTABANLARI BAŞLATMA
if not os.path.exists(db_yildizlar):
    pd.DataFrame(columns=["rumuz"]).to_csv(db_yildizlar, index=False)

if not os.path.exists(db_ortak_oda):
    pd.DataFrame(columns=["rumuz", "son_gorulme"]).to_csv(db_ortak_oda, index=False)

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["Tarih", "Yazan", "Hisse", "Hedef", "Not"]).to_csv(db_notlar, index=False)

# ===================================================================== #
# RUMUZ GİRİŞ SİSTEMİ İPTAL EDİLDİ - VARSAYILAN ATAMA YAPILDI
# ===================================================================== #
if "bta_rumuz" not in st.session_state:
    st.session_state["bta_rumuz"] = "ZİYARETÇİ"

# --- HERKESİN BİRBİRİNİ GÖRDÜĞÜ ORTAK DOSYA TABANLI CANLI ODA MOTORU ---
simdi = time.time()
try:
    df_oda = pd.read_csv(db_ortak_oda)
    df_oda = df_oda[df_oda["rumuz"] != st.session_state["bta_rumuz"]]
    yeni_sinyal = pd.DataFrame([{"rumuz": st.session_state["bta_rumuz"], "son_gorulme": simdi}])
    df_oda = pd.concat([df_oda, yeni_sinyal], ignore_index=True)
    df_oda = df_oda[df_oda["son_gorulme"] > (simdi - 15)]
    df_oda.to_csv(db_ortak_oda, index=False)
    
    aktif_listesi = df_oda["rumuz"].unique().tolist()
    canli_oda_sayisi = len(aktif_listesi)
except:
    canli_oda_sayisi = 1
    aktif_listesi = [st.session_state["bta_rumuz"]]

# ===================================================================== #
# CANLI PİYASA VERİ ÇEKİMİ VE YÜZDESEL DEĞİŞİM HESAPLAMA MOTORU
# ===================================================================== #
kayan_yazi_html = ""
try:
    # Verileri Çek
    bist_t = yf.Ticker("XU100.IS").history(period="2d", timeout=2)
    usd_t = yf.Ticker("TRY=X").history(period="2d", timeout=2)
    eur_t = yf.Ticker("EURTRY=X").history(period="2d", timeout=2)
    ons_t = yf.Ticker("GC=F").history(period="2d", timeout=2)

    def hesapla_degisim(df_ticker, is_gold=False, usd_df=None):
        if len(df_ticker) >= 2:
            guncel = float(df_ticker['Close'].iloc[-1])
            onceki = float(df_ticker['Close'].iloc[-2])
            
            if is_gold and usd_df is not None:
                guncel_usd = float(usd_df['Close'].iloc[-1])
                onceki_usd = float(usd_df['Close'].iloc[-2])
                guncel = (guncel / 31.1034768) * guncel_usd
                onceki = (onceki / 31.1034768) * onceki_usd
                
            yuzde = ((guncel - onceki) / onceki) * 100
            if yuzde > 0:
                return f"▲ %{yuzde:.2f}", "yukselis", guncel
            elif yuzde < 0:
                return f"▼ %{abs(yuzde):.2f}", "dusis", guncel
        return "• %0.00", "notr", float(df_ticker['Close'].iloc[-1]) if len(df_ticker)>0 else 0.0

    bist_ok, bist_durum, bist_f = hesapla_degisim(bist_t)
    usd_ok, usd_durum, usd_f = hesapla_degisim(usd_t)
    eur_ok, eur_durum, eur_f = hesapla_degisim(eur_t)
    gram_ok, gram_durum, gram_f = hesapla_degisim(ons_t, is_gold=True, usd_df=usd_t)

    # HTML Kayan yazı metnini inşa et
    kayan_yazi_html = f'''
    <div class="kayan-yazi-bandi">
        <div class="kayan-icerik">
            <span class="piyasa-{gram_durum}">GRAM ALTIN: {gram_f:,.2f} TL {gram_ok}</span>
            <span class="piyasa-{bist_durum}">BIST 100: {bist_f:,.2f} {bist_ok}</span>
            <span class="piyasa-{usd_durum}">DOLAR (USD): {usd_f:,.2f} TL {usd_ok}</span>
            <span class="piyasa-{eur_durum}">EURO (EUR): {eur_f:,.2f} TL {eur_ok}</span>
        </div>
    </div>
    '''
except Exception as e:
    kayan_yazi_html = '<div class="kayan-yazi-bandi"><div class="kayan-icerik"><span class="piyasa-notr">⏳ Canlı Finansal Veriler Güncelleniyor...</span></div></div>'

# Kayan Yazıyı En Üste Bas
st.markdown(kayan_yazi_html, unsafe_allow_html=True)
st.write("")

# Üst Bilgi Satırı
col_ust1, col_ust2 = st.columns(2)

with col_ust1:
    st.markdown(f'<div style="text-align:left;"><div class="oda-sayici">🟢 Canlı Oda Sayısı: {canli_oda_sayisi} Kişi Aktif</div></div>', unsafe_allow_html=True)
    with st.expander(f"👥 Odadaki Bağlantıları Gör ({canli_oda_sayisi})"):
        st.caption(", ".join(aktif_listesi))

with col_ust2:
    try:
        df_yildiz_oku = pd.read_csv(db_yildizlar)
        begenen_listesi = df_yildiz_oku["rumuz"].unique().tolist()
    except:
        begenen_listesi = []
        df_yildiz_oku = pd.DataFrame(columns=["rumuz"])
        
    toplam_gercek_begeni = len(begenen_listesi)
    kullanici_begenmis_mi = st.session_state["bta_rumuz"] in begenen_listesi
    buton_metni = "🌟 Sistem Favorilerimde! (Beğenildi)" if kullanici_begenmis_mi else "⭐ Panele Yıldız Bırak"
    
    st.markdown(f'<div style="text-align:right; font-size:16px; font-weight:bold; color:#ffcc00; margin-bottom:5px;">📊 Gerçek Yıldız Beğenisi: {toplam_gercek_begeni} Kişi</div>', unsafe_allow_html=True)
    if st.button(buton_metni, use_container_width=True, key="yildiz_butonu"):
        if kullanici_begenmis_mi:
            df_yildiz_oku = df_yildiz_oku[df_yildiz_oku["rumuz"] != st.session_state["bta_rumuz"]]
        else:
            yeni_begeni = pd.DataFrame([{"rumuz": st.session_state["bta_rumuz"]}])
            df_yildiz_oku = pd.concat([df_yildiz_oku, yeni_begeni], ignore_index=True)
            
        df_yildiz_oku.to_csv(db_yildizlar, index=False)
        st.rerun()

# ===================================================================== #
# 2. METRİK PANEL ALANI (STATİK YAN YANA GÖRÜNÜM)
# ===================================================================== #
st.write("---")
if 'gram_f' in locals():
    pk1, pk2, pk3, col_bist, col_eur = st.columns(5)
    pk1.metric("GRAM ALTIN", f"{gram_f:,.2f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.2f} TL")
    pk3.metric("YARIM ALTIN", f"{gram_f * 3.26:,.2f} TL")
    col_bist.metric("BIST 100", f"{bist_f:,.2f}")
    col_eur.metric("EURO", f"{eur_f:,.2f} TL")
else:
    st.info("⏳ Finansal Metrikler Yükleniyor...")

# ===================================================================== #
# 3. ANA VERİ MOTORU VE TABLOLAR
# ===================================================================== #
st.write("---")
df = None
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        veri_var_mi = False
        
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                if isinstance(puan_d, (int, float)):
                    p_temiz = f"{float(puan_d):.2f}"
                else:
                    p_temiz = str(puan_d).strip()
                    
