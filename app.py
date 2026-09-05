import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# 1. SAYFA AYARLARI VE TELEFON UYUMLU NEON TASARIM
st.set_page_config(page_title="BTA Piyasalar", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    @keyframes rainbowNeon {
        0% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f; }
        50% { color: #00f2fe !important; text-shadow: 0 0 15px #00f2fe; }
        100% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f; }
    }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
    } 
    h1, h2, h3, p, span, label {
        color: #fff !important; 
        font-family: "Segoe UI", sans-serif;
    } 
    input {
        color: #000 !important; 
        background-color: #fff !important;
    }
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
        padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 10px;
    } 
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
        padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 10px;
    } 
    .bta-logo-konteyner {
        width: 100%; overflow: hidden; white-space: nowrap;
        margin: 15px 0; padding: 10px 0; background: rgba(255, 255, 255, 0.02); border-radius: 8px;
    } 
    .bta-logo {
        display: inline-block; font-family: 'Segoe UI', sans-serif; font-style: italic;
        font-weight: bold; font-size: 4rem; padding-left: 100%; 
        animation: marquee 20s infinite linear, rainbowNeon 6s infinite linear; 
    } 
    .spk-kutusu {
        background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444;
        padding: 15px; border-radius: 8px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

if "oda_kilitli_mi" not in st.session_state:
    st.session_state["oda_kilitli_mi"] = False
if "sohbet_gecmisi" not in st.session_state:
    st.session_state["sohbet_gecmisi"] = []

# LOGO VE SPK UYARISI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA TRADING</div></div>', unsafe_allow_html=True)
st.markdown("""
<div class="spk-kutusu">
    <h4 style="color:#ef4444 !important; margin-top:0;">⚠️ SPK YASAL UYARI</h4>
    <p style="font-size:0.9rem; color:#cbd5e1 !important; margin-bottom:0;">
        Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
        Burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir.
    </p>
</div>
""", unsafe_allow_html=True)

# YÖNETİCİ PANELİ (SOL YAN MENÜ)
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    if st.sidebar.button("🔓 Odadaki Kilidi Kaldır / Kilitle", use_container_width=True):
        st.session_state["oda_kilitli_mi"] = not st.session_state["oda_kilitli_mi"]
        st.rerun()

# KİLİT KONTROLÜ
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div style="background:rgba(255,255,255,0.05); border-left:4px solid #ca8a04; padding:15px; border-radius:6px;">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Sistem verileri güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
    st.stop()

# ÜST PANEL SEKMELERİ
sekme_arama, sekme_altin, sekme_sohbet = st.tabs(["🔎 BIST Arama Motoru", "🪙 Canlı Altın Takibi", "💬 Sohbet & Not Alanı"])

with sekme_arama:
    st.markdown("### 🔎 BIST Hisse Arama Filtresi")
    arama_kelimesi = st.text_input("Filtrelemek istediğiniz hisse kodunu yazın (Örn: THYAO):", "").strip().upper()

with sekme_altin:
    st.markdown("### 🪙 Canlı Altın Piyasası Takibi")
    altin_df_data = pd.DataFrame({"Altın Türü": ["Veri Alınamadı"], "Fiyat (TL)": ["0.00"]})
    try:
        altin_download = yf.download(["GC=F", "TRY=X"], period="1d", progress=False)
        ons_v = float(altin_download['Close']['GC=F'].dropna().iloc[-1])
        usd_v = float(altin_download['Close']['TRY=X'].dropna().iloc[-1])
        g_altin = (ons_v / 31.1034768) * usd_v
        altin_df_data = pd.DataFrame({
            "Altın Türü 🪙": ["Gram Altın", "Çeyrek Altın", "Yarım Altın", "Tam Altın"],
            "Fiyat (TL) 💰": [f"{g_altin:,.2f}", f"{g_altin*1.75:,.2f}", f"{g_altin*3.5:,.2f}", f"{g_altin*7.01:,.2f}"]
        })
    except:
        pass
    st.table(altin_df_data)

with sekme_sohbet:
    st.markdown("### 💬 Bilgi Paylaşım & Analiz Notları")
    s_isim = st.text_input("Kullanıcı Adınız:", value="Yatırımcı")
    s_mesaj = st.text_input("Mesaj içeriği:", placeholder="Notunuzu buraya ekleyin...")
    if st.button("✉️ Mesajı İlet") and s_mesaj.strip():
        saat = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state["sohbet_gecmisi"].insert(0, f"[{saat}] **{s_isim}**: {s_mesaj}")
        st.toast("Not kaydedildi!", icon="💬")
    for msg in st.session_state["sohbet_gecmisi"][:8]:
        st.markdown(msg)

st.markdown("---")

# =========================================================================
# %100 GARANTİLİ VE HIZLI EXCEL LİSTELEME MOTORU (SIFIR HATA RİSKİ)
# =========================================================================
excel_adi = "nurican.xls.xlsm"

if os.path.exists(excel_adi):
    df_excel = pd.read_excel(excel_adi, header=None, engine="openpyxl")
    
    t_alsat_list = []
    t_al_list = []
    
    # Excel verisini listelere doğrudan doldurma (Hata payı sıfır)
    if len(df_excel.columns) > 22:
        for satir_idx in range(2, len(df_excel)):
            u_cell = str(df_excel.iloc[satir_idx, 20]).strip().upper() if not pd.isna(df_excel.iloc[satir_idx, 20]) else ""
            w_cell = str(df_excel.iloc[satir_idx, 22]).strip().upper() if not pd.isna(df_excel.iloc[satir_idx, 22]) else ""
            t_cell = str(df_excel.iloc[satir_idx, 19]).strip().upper() if not pd.isna(df_excel.iloc[satir_idx, 19]) else "0.0"
            
            # U Sütunu Filtreleme (Dönsmsel Al/Sat)
            if u_cell and u_cell not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                if arama_kelimesi == "" or arama_kelimesi in u_cell:
                    t_alsat_list.append({"Hisse Kodu 📈": u_cell, "BTA Puan": t_cell})
            
            # W Sütunu Filtreleme (Sadece Al)
            if w_cell and w_cell not in ["NAN", "NONE", "W_SÜTUNU"]:
                if arama_kelimesi == "" or arama_kelimesi in w_cell:
                    t_al_list.append({"Hisse Kodu 📈": w_cell})

    # EKRANA VERİLERİ YAN YANA BASMA ALANI
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL/SAT SİNYALLERİ</div>', unsafe_allow_html=True)
        if len(t_alsat_list) > 0:
            st.dataframe(pd.DataFrame(t_alsat_list), use_container_width=True)
        else:
            st.info("Listelenecek veri bulunamadı.")
            
    with c2:
        st.markdown('<div class="al-baslik">🟢 SADECE AL SİNYALLERİ (W)</div>', unsafe_allow_html=True)
        if len(t_al_list) > 0:
            st.dataframe(pd.DataFrame(t_al_list), use_container_width=True)
        else:
            st.info("Listelenecek veri bulunamadı.")
else:
    st.error("⚠️ 'nurican.xls.xlsm' veri tabanı dosyası ana dizinde bulunamadı!")
