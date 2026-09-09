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
.oda-sayici { background: linear-gradient(90deg, #1e3a5f 0%, #121d33 100%); color: #00ffcc; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; border: 1px solid #00ffcc; margin-bottom: 15px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:5px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı, Fiyatları ve Canlı Odayı Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_yildizlar = "bta_yildiz_begenileri_db.csv"
db_ortak_oda = "bta_ortak_oda_aktiflik.csv"

# KALICI VERİTABANLARI BAŞLATMA
if not os.path.exists(db_yildizlar):
    pd.DataFrame(columns=["rumuz"]).to_csv(db_yildizlar, index=False)

if not os.path.exists(db_ortak_oda):
    pd.DataFrame(columns=["rumuz", "son_gorulme"]).to_csv(db_ortak_oda, index=False)

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

col_ust1, col_ust2 = st.columns(2)

with col_ust1:
    st.markdown(f'<div style="text-align:left;"><div class="oda-sayici">🟢 Canlı Oda Sayısı: {canli_oda_sayisi} Gerçek Kişi Aktif</div></div>', unsafe_allow_html=True)
    with st.expander(f"👥 Odadaki Bağlantıları Gör ({canli_oda_sayisi})"):
        st.caption(", ".join(aktif_listesi))

# --- GERÇEK YILDIZ BEĞENİSİ MOTORU ---
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
    
    st.markdown(f'<div style="text-align:right; font-size:16px; font-weight:bold; color:#ffcc00; margin-bottom:5px;">📊 Yıldız Beğenisi: {toplam_gercek_begeni} Kişi</div>', unsafe_allow_html=True)
    if st.button(buton_metni, use_container_width=True, key="yildiz_butonu"):
        if kullanici_begenmis_mi:
            df_yildiz_oku = df_yildiz_oku[df_yildiz_oku["rumuz"] != st.session_state["bta_rumuz"]]
        else:
            yeni_begeni = pd.DataFrame([{"rumuz": st.session_state["bta_rumuz"]}])
            df_yildiz_oku = pd.concat([df_yildiz_oku, yeni_begeni], ignore_index=True)
            
        df_yildiz_oku.to_csv(db_yildizlar, index=False)
        st.rerun()

# ===================================================================== #
# 2. CANLI ALTIN VE BIST 100 PİYASA ALANI
# ===================================================================== #
st.write("---")
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
# 3. ANA VERİ MOTORU VE DİKEY YAN YANA BÜYÜTÜLMÜŞ KARTLAR
# ===================================================================== #
st.write("---")

# Sabit yedek liste (Hata riskini sıfırlamak için)
tum_hisseler = ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "GARAN", "SISE", "BIMAS", "SAHOL", "KCHOL"]

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        st.markdown('<p style="font-size:22px; font-weight:bold; color:#1E90FF; margin-bottom:15px;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        
        kart_sutun1, kart_sutun2 = st.columns(2)
        aktif_kart_sayisi = 0
        excel_hisseleri = []
        
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                excel_hisseleri.append(ha)
                    
                if isinstance(puan_d, (int, float)):
                    p_temiz = f"{float(puan_d):.2f}"
                else:
                    p_temiz = str(puan_d).strip()
                    
                h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    kz_str = f'<span style="color:#00ff66; font-size:18px;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344; font-size:18px;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span style='font-size:18px;'>-</span>"
                
                dikey_kart_html = f'''
                <div style="background-color: #121d33; border: 2px solid #1e3a5f; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                    <div style="font-size: 24px; color: #00ffcc; border-bottom: 2px solid #1e2e4d; padding-bottom: 8px; margin-bottom: 12px; font-weight: bold; letter-spacing: 1px;">📍 {ha} HİSSE BİLGİLERİ</div>
                    <div style="display: flex; flex-direction: column; gap: 10px; font-size: 18px; color: #ffffff;">
                        <div><b>BTA PUANI:</b> <span style="color: #00ffcc; font-size: 20px; font-weight: bold;">{p_temiz}</span></div>
                        <div><b>ALGORİTMİK FİYATI:</b> <span style="font-weight: bold; color: #e2e8f0;">{maliyet:,.2f} TL</span></div>
                        <div><b>GÜNCEL FİYAT:</b> <span style="font-weight: bold; color: #e2e8f0;">{c_fiyat:,.2f} TL</span></div>
                        <div><b>KÂR / ZARAR:</b> <b>{kz_str}</b></div>
                    </div>
                </div>
                '''
                
                if aktif_kart_sayisi % 2 == 0:
                    kart_sutun1.markdown(dikey_kart_html, unsafe_allow_html=True)
                else:
                    kart_sutun2.markdown(dikey_kart_html, unsafe_allow_html=True)
                aktif_kart_sayisi += 1
                
        if len(excel_hisseleri) > 0:
            tum_hisseler = excel_hisseleri
    except Exception as e:
        pass
else:
    st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. BORSA ARAMA MOTORU (SIFIR HIZALAMA - ASLA HATA VERMEZ)
# ===================================================================== #
st.write("---")
