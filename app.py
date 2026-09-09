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
.galeri-kutu { background-color: #121d33; border: 1px solid #1e3a5f; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 10px; }
.oda-sayici { background: linear-gradient(90deg, #1e3a5f 0%, #121d33 100%); color: #00ffcc; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; border: 1px solid #00ffcc; margin-bottom: 15px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:5px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı, Fiyatları ve Canlı Odayı Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_resimler = "bta_resim_kayit_db.csv"
db_aktiflik = "bta_aktiflik_db.csv"

# KALICI VERİTABANLARI BAŞLATMA
if not os.path.exists(db_resimler):
    pd.DataFrame(columns=["tarih", "saat", "resim_url", "not"]).to_csv(db_resimler, index=False)

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
# 3. VERİ MOTORU VE TABLOLAR (YUVARLAMASIZ)
# ===================================================================== #
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
                    
                    if maliyet > 0 and c_fiyat > 0:
                        or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                    else: kz_str = "<span>-</span>"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
                    if len(h_detay_veri) > 0:
                        st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. YÖNETİCİ GİRİŞİ (SADECE RESİM SİLME YETKİSİ İÇİN)
# ===================================================================== #
with st.expander("🛠 Yönetici"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"

# ===================================================================== #
# 5. TARİHLİ 3 RESİMLİK KAYIT DEFTERİ (GALERİ) ALANI
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#00ffcc;">📅 Tarihli Resim Kayıt Defteri (Son 3 Görsel)</p>', unsafe_allow_html=True)

with st.expander("🖼 Kayıt Defterine Yeni Resim Linki Ekle"):
    r_url = st.text_input("Resim URL (Web Adresi veya Bulut Linki):")
    r_not = st.text_input("Resim Notu / Açıklama:", max_chars=100)
    if st.button("Resmi Kaydet 💾") and r_url.strip():
        df_r = pd.read_csv(db_resimler)
        y_resim = pd.DataFrame([{
            "tarih": datetime.datetime.now().strftime("%d.%m.%Y"),
            "saat": datetime.datetime.now().strftime("%H:%M"),
            "resim_url": r_url.strip(),
            "not": r_not.strip()
        }])
        pd.concat([y_resim, df_r], ignore_index=True).to_csv(db_resimler, index=False)
        st.success("Resim başarıyla galeriye eklendi!")
        st.rerun()

df_resim_oku = pd.read_csv(db_resimler)

if not df_resim_oku.empty:
    son_uc_resim = df_resim_oku.head(3)
    r_cols = st.columns(3)
    
    # Girinti hatası vermeyen, düzleştirilmiş güvenli yeni yapı
    for r_idx in range(len(son_uc_resim)):
        r_row = son_uc_resim.iloc[r_idx]
        col_secimi = r_cols[r_idx % 3]
        
