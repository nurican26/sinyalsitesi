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
.mesaj-kutusu { background-color: #090f1a; border: 1px solid #1e3a5f; padding: 8px; border-radius: 6px; max-height: 180px; overflow-y: auto; font-family: monospace; font-size: 12px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:5px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı, Fiyatları ve Canlı Odayı Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_ortak_oda = "bta_ortak_oda_aktiflik.csv"
db_mesajlar = "bta_hafif_mesaj_panosu.csv"

# KALICI VERİTABANLARI BAŞLATMA
if not os.path.exists(db_ortak_oda):
    pd.DataFrame(columns=["rumuz", "son_gorulme"]).to_csv(db_ortak_oda, index=False)

if not os.path.exists(db_mesajlar):
    pd.DataFrame(columns=["zaman", "rumuz", "mesaj"]).to_csv(db_mesajlar, index=False)

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

# --- DÜŞÜK KOTALI CANLI MESAJ PANAROMASI ---
with col_ust2:
    st.markdown('<p style="font-size:14px; font-weight:bold; color:#00ffcc; margin-bottom:2px; margin-top:-5px;">💬 Oda İçi Hafif Mesaj Paneli</p>', unsafe_allow_html=True)
    
    # Mesaj Oku ve Göster
    try:
        df_msg = pd.read_csv(db_mesajlar)
        msg_lines = []
        for _, row in df_msg.tail(15).iterrows():  # Sadece son 15 mesaj (Kota dostu)
            msg_lines.append(f"<span style='color:#0d9488;'>[{row['zaman']}]</span> <b style='color:#ffcc00;'>{row['rumuz']}:</b> <span style='color:#fff;'>{row['mesaj']}</span>")
        
        mesaj_govde = "<br>".join(msg_lines) if msg_lines else "<span style='color:#666;'>Henüz mesaj yok...</span>"
        st.markdown(f'<div class="mesaj-kutusu">{mesaj_govde}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="mesaj-kutusu"><span style="color:#ff3344;">Mesajlar yüklenemedi.</span></div>', unsafe_allow_html=True)
    
    # Mesaj Gönderme Formu (Tek satırda sıkışık düzen)
    col_msg_in, col_msg_btn = st.columns([4, 1])
    with col_msg_in:
        yeni_mesaj = st.text_input("", max_chars=100, placeholder="Mesaj yazın...", label_visibility="collapsed", key="msg_input_field")
    with col_msg_btn:
        if st.button("Gönder", use_container_width=True, key="msg_send_btn") and yeni_mesaj.strip():
            saat_str = datetime.datetime.now().strftime("%H:%M")
            df_yeni_msg = pd.DataFrame([{"zaman": saat_str, "rumuz": st.session_state["bta_rumuz"], "mesaj": yeni_mesaj.strip()}])
            try:
                df_eski_msg = pd.read_csv(db_mesajlar)
                df_toplam_msg = pd.concat([df_eski_msg, df_yeni_msg], ignore_index=True).tail(30) # Dosya boyutunu hep küçük tutar
                df_toplam_msg.to_csv(db_mesajlar, index=False)
            except:
                df_yeni_msg.to_csv(db_mesajlar, index=False)
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
# 3. ANA VERİ MOTORU VE TABLOLAR
# ===================================================================== #
st.write("---")
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
                    
                h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                if len(h_veri) > 0:
                    c_fiyat = float(h_veri['Close'].iloc[-1])
                else:
                    c_fiyat = 0.0
                
                alim_c_temiz = alim_c.replace(",", ".")
                if alim_c_temiz.replace(".", "", 1).isdigit():
                    maliyet = float(alim_c_temiz)
                else:
                    maliyet = 0.0
                
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 0:
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>'
                    else:
                        kz_str = f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                
                tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: 
            st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
