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

# 🔑 SABİT PARAMETRELER
YONETICI_SIFRESI = "bta2026"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state:
    st.session_state["oda_kilitli_mi"] = False
if "sohbet_gecmisi" not in st.session_state:
    st.session_state["sohbet_gecmisi"] = []

# GÖKKUŞAĞI BTA LOGOSU
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA TRADING</div></div>', unsafe_allow_html=True)

# --- SPK YASAL UYARI MADDESİ ---
st.markdown("""
<div class="spk-kutusu">
    <h4 style="color:#ef4444 !important; margin-top:0;">⚠️ SPK YASAL UYARI</h4>
    <p style="font-size:0.9rem; color:#cbd5e1 !important; margin-bottom:0;">
        Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
        Burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir.
    </p>
</div>
""", unsafe_allow_html=True)

# 🛠️ YÖNETİCİ PANELİ (SOL MENÜ)
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    durum_metni = "🔴 ODA KİLİTLİ" if st.session_state["oda_kilitli_mi"] else "🟢 HERKESE AÇIK"
    st.sidebar.markdown(f"Mevcut Durum: **{durum_metni}**")
    if st.sidebar.button("🔄 Durumu Değiştir (Kilitle/Aç)", use_container_width=True):
        st.session_state["oda_kilitli_mi"] = not st.session_state["oda_kilitli_mi"]
        st.rerun()

# --- 🏢 ERİŞİM KONTROLÜ VE İÇERİK AKTARIMI ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div style="background:rgba(255,255,255,0.05); border-left:4px solid #ca8a04; padding:15px; border-radius:6px;">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda kilitli fakat Yönetici olduğunuz için görüntülüyorsunuz.")

    # ETKİLEŞİM PANELİ SEKMELERİ
    sekme_arama, sekme_altin, sekme_sohbet = st.tabs(["🔎 BIST Arama Motoru", "🪙 Canlı Altın Takibi", "💬 Sohbet & Not Alanı"])
    
    with sekme_arama:
        st.markdown("### 🔎 BIST Hisse Arama Filtresi")
        arama_kelimesi = st.text_input("Filtrelemek istediğiniz hisse kodunu yazın (Örn: THYAO):", "").strip().upper()
        
    with sekme_altin:
        st.markdown("### 🪙 Canlı Altın Piyasası Takibi")
        if st.button("🔄 Altın Fiyatlarını Güncelle"):
            st.toast("Altın fiyatları yenileniyor...", icon="🪙")
            
        # Altın Hesaplama (Hata vermeyen güvenli doğrusal akış)
        altin_df_data = pd.DataFrame({"Durum": ["Veri çekilemedi"]})
        altin_download = yf.download(["GC=F", "TRY=X"], period="1d", progress=False)
        if not altin_download.empty:
            ons_v = float(altin_download['Close']['GC=F'].dropna().iloc[-1])
            usd_v = float(altin_download['Close']['TRY=X'].dropna().iloc[-1])
            g_altin = (ons_v / 31.1034768) * usd_v
            altin_df_data = pd.DataFrame({
                "Altın Türü 🪙": ["Gram Altın", "Çeyrek Altın", "Yarım Altın", "Tam Altın"],
                "Fiyat (TL) 💰": [f"{g_altin:,.2f}", f"{g_altin*1.75:,.2f}", f"{g_altin*3.5:,.2f}", f"{g_altin*7.01:,.2f}"]
            })
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
    # YENİ NESİL EXCEL İŞLEME VE TOPLU FİYAT MOTORU (BLOKSUZ VE SÜRATLİ)
    # =========================================================================
    excel_adi = "nurican.xls.xlsm"
    
    if os.path.exists(excel_adi):
        df_excel = pd.read_excel(excel_adi, header=None, engine="openpyxl")
        
        excel_listesi = []
        toplu_tickers = []
        
        # Sütun uzunluğunu kontrol ederek ham veriyi belleğe taşıma
        if len(df_excel.columns) > 22:
            for satir_idx in range(2, len(df_excel)):
                u_cell = str(df_excel.iloc[satir_idx, 20]).strip().upper() if not pd.isna(df_excel.iloc[satir_idx, 20]) else ""
                w_cell = str(df_excel.iloc[satir_idx, 22]).strip().upper() if not pd.isna(df_excel.iloc[satir_idx, 22]) else ""
                t_cell = str(df_excel.iloc[satir_idx, 19]).strip().upper() if not pd.isna(df_excel.iloc[satir_idx, 19]) else "0.0"
                
                if u_cell and u_cell not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    toplu_tickers.append(f"{u_cell}.IS")
                if w_cell and w_cell not in ["NAN", "NONE", "W_SÜTUNU"]:
                    toplu_tickers.append(f"{w_cell}.IS")
                    
                excel_listesi.append({"u": u_cell, "w": w_cell, "puan": t_cell})

        # Benzersiz hisselerin fiyatlarını internetten tek hamlede topluca indir
        toplu_tickers = list(set(toplu_tickers))
        fiyat_sozlugu = {}
        
        if toplu_tickers:
            download_data = yf.download(toplu_tickers, period="1d", progress=False)
            if not download_data.empty and 'Close' in download_data.columns:
                close_df = download_data['Close']
                for t_kod in toplu_tickers:
                    s_kod = t_kod.replace(".IS", "")
                    if isinstance(close_df, pd.DataFrame) and t_kod in close_df.columns:
                        valid_series = close_df[t_kod].dropna()
                        fiyat_sozlugu[s_kod] = float(valid_series.iloc[-1]) if not valid_series.empty else 0.0
                    elif isinstance(close_df, pd.Series):
                        fiyat_sozlugu[s_kod] = float(close_df.dropna().iloc[-1]) if not close_df.dropna().empty else 0.0

        # Filtreleme ve Tablo Ayrıştırma Adımları
        t_alsat_list = []
        t_al_list = []
        
        for veri in excel_listesi:
            # U Sütunu Filtresi
            if veri["u"] and veri["u"] not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                if arama_kelimesi == "" or arama_kelimesi in veri["u"]:
                    t_alsat_list.append({
                        "Hisse Kodu 📈": veri["u"],
                        "BTA Puan": veri["puan"],
                        "💥 Canlı Fiyat": fiyat_sozlugu.get(veri["u"], 0.0)
                    })
            
            # W Sütunu Filtresi
            if veri["w"] and veri["w"] not in ["NAN", "NONE", "W_SÜTUNU"]:
                if arama_kelimesi == "" or arama_kelimesi in veri["w"]:
                    t_al_list.append({
                        "Hisse Kodu 📈": veri["w"],
                        "💥 Canlı Fiyat": fiyat_sozlugu.get(veri["w"], 0.0)
                    })

        # EKRANA YAN YANA TABLOLARI ÇIKARTMA
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL/SAT SİNYALLERİ</div>', unsafe_allow_html=True)
            if t_alsat_list:
                st.dataframe(pd.DataFrame(t_alsat_list), use_container_width=True)
            else:
                st.info("Kriterlere uygun veri bulunamadı.")
                
        with c2:
            st.markdown('<div class="al-baslik">🟢 SADECE AL SİNYALLERİ (W)</div>', unsafe_allow_html=True)
            if t_al_list:
