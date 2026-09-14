import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os

# ==========================================
# 1. SAYFA VE KESİN SOL MENÜSÜZ AYARLAR
# ==========================================
st.set_page_config(
    page_title="BTA Çoklu Hisse Takip Terminali",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Arka planda 5 saniyede bir otomatik yenileme tetikleyici
st_autorefresh(interval=5000, key="bta_terminal_refresh")

# SPK RESMİ YASAL UYARI METNİ
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 🌌 EN ARKA PANEL VE SAĞDAN SOLA AĞIR YÜRÜYEN BTA CSS
# ==========================================
st.markdown("""
<style>
    /* Sol menüyü tamamen yok etme */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], button[title="View sidebar"] {
        display: none !important;
        width: 0px !important;
    }
    
    /* EN ARKA PANEL: Siber yeşil ve borsa mavisi geçişli gradient duvar kağıdı */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container, [data-testid="stMainBlockContainer"] {
        background: linear-gradient(135deg, #0e3029 0%, #113052 50%, #291740 100%) !important;
        background-attachment: fixed !important;
        background-color: transparent !important;
        color: #ffffff !important;
    }
    
    [data-testid="stHeader"], [data-testid="stLayoutWidgetOnMainBlock"] {
        background-color: transparent !important;
    }

    /* Borsa Canlı Kart Tasarımları */
    .borsa-canli-kart {
        background: rgba(15, 32, 67, 0.85) !important;
        padding: 22px !important;
        border-radius: 14px !important;
        border: 2px solid #00b0ff !important;
        box-shadow: 0 0 20px rgba(0, 176, 255, 0.4) !important;
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }

    /* 🧠 LOGO PANELİ KUTUSU */
    .bta-logo-box {
        overflow: hidden;
        padding: 20px 0;
        margin-bottom: 20px;
        background: rgba(10, 20, 40, 0.75);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }

    /* Sabit Kurumsal Beyin Amblemi */
    .bta-brain-fixed {
        font-size: 55px;
        margin-left: 30px;
        margin-right: 20px;
        display: inline-block;
        z-index: 10;
    }
    
    /* SAĞDAN SOLA DOĞRU AĞIR YÜRÜYEN KURUMSAL BTA MİMARİSİ */
    .bta-yuruyen-alan {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
    }
    .bta-neon-heavy {
        font-family: 'Orbitron', sans-serif;
        font-size: 70px;
        font-weight: 900;
        letter-spacing: 15px;
        color: #00e676;
        display: inline-block;
        padding-left: 100%;
        animation: agirYuruBta 25s linear infinite;
        filter: drop-shadow(0 0 12px rgba(0, 230, 118, 0.8)) 
                drop-shadow(0 0 25px rgba(0, 176, 255, 0.6));
    }
    
    @keyframes agirYuruBta {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-100%); }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 🧠 HAREKETLİ ÜST BANT PANELİ
# ==========================================
st.markdown("""
<div class='bta-logo-box'>
    <span class='bta-brain-fixed'>🧠</span>
    <div class='bta-yuruyen-alan'>
        <div class='bta-neon-heavy'>BTA ALGORİTMİK PORTFÖY TAKİP TERMİNALİ</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(spk_metni)
st.markdown("---")

# ==========================================
# 3. EXCEL VERİLERİNİ BAĞLAMA VE EŞLEŞTİRME MOTORU
# ==========================================
# Excel okunamama ihtimaline karşı KONYA için sistem yedek havuzu
hisse_verileri_havuzu = [
    {"Hisse": "KONYA", "Alim_Fiyati": 4100.0, "Puan": "100"}
]

excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
if excel_dosyalari:
    hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
    secilen_excel = hedef_dosyalar[0] if hedef_dosyalar else excel_dosyalari[0]
    
    try:
        df_excel = pd.read_excel(secilen_excel, sheet_name=0, engine='openpyxl')
        # Sütun isimlerinin etrafındaki boşlukları temizliyoruz
        df_excel.columns = df_excel.columns.astype(str).str.strip()
        
        # Talep Edilen Sütunların Excel'de var olup olmadığını doğrula
        gerekli_sutunlar = ["BTA HİSSE", "BTA ALIM FİYATI", "BTA PUAN"]
        if all(col in df_excel.columns for col in gerekli_sutunlar) and len(df_excel.columns) >= 5:
            gecici_havuz = []
            
            # Satır satır tarayıp verileri birbirine bağlıyoruz
            for idx, row in df_excel.iterrows():
                # E sütunundan (5. sütun) hisse kodunu çekiyoruz
                hisse_kodu = str(row.iloc[4]).strip().upper()
                
                # Geçersiz satırları ve boş hücreleri eliyoruz
                if hisse_kodu and hisse_kodu != "NAN" and hisse_kodu != "NONE" and not hisse_kodu.replace('.','',1).isdigit():
                    alim_maliyeti = row["BTA ALIM FİYATI"]
                    bta_puan_degeri = row["BTA PUAN"]
                    
                    # Veriler boş değilse listeye mühürle
                    if pd.notna(alim_maliyeti) and pd.notna(bta_puan_degeri):
                        gecici_havuz.append({
                            "Hisse": hisse_kodu,
                            "Alim_Fiyati": float(alim_maliyeti),
                            "Puan": str(bta_puan_degeri)
                        })
            
            if gecici_havuz:
                hisse_verileri_havuzu = gecici_havuz
    except:
        pass

# ==========================================
# 4. 📋 CANLI İZLEME VE KÂR/ZARAR DEFTERİ PANELİ
# ==========================================
st.subheader("📊 BTA Canlı İzleme ve Portföy Paneli")
st.info("⏱️ Borsa İstanbul (BIST) verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** olarak yansımaktadır.")

# Eşleşen tüm hisseleri alt alta borsa kartı formatında listeliyoruz
for veri in hisse_verileri_havuzu:
    hisse_adi = veri["Hisse"]
    referans_maliyet = veri["Alim_Fiyati"]
    algoritma_puani = veri["Puan"]
    
    kurumsal_ticker = f"{hisse_adi}.IS"
    guncel_price = referans_maliyet
    gunluk_change = 0.0
    veri_okundu = False
    
    # Canlı internet fiyatı çekme katmanı
    try:
        hisse_data = yf.Ticker(kurumsal_ticker)
        tarihce_data = hisse_data.history(period="1d", interval="1d")
        if not tarihce_data.empty:
            guncel_price = tarihce_data['Close'].iloc[-1]
            gunluk_change = hisse_data.info.get('regularMarketChangePercent', 0.0)
            veri_okundu = True
    except:
        pass
        
    if veri_okundu:
        # Algoritmik Canlı Kâr / Zarar Hesaplama Dengesi
        net_tl_farki = guncel_price - referans_maliyet
        net_yuzde_farki = (net_tl_farki / referans_maliyet) * 100
        
        # Renklerin koşullandırılması (Kârda yeşil neon, zararda kırmızı neon hat çeker)
        border_color = "#089981" if net_tl_farki >= 0 else "#da3637"
        tl_renk = "#089981" if net_tl_farki >= 0 else "#da3637"
        isaret = "+" if net_tl_farki >= 0 else ""
        
        # Borsa tavan yaptığında kutlama balonları patlar
        if gunluk_change >= 9.85:
            st.balloons()
            
        # 🚀 REKOR GÜNCELLEME: Tüm BTA Alım Fiyatları, Puanları ve Canlı Hesaplar Tek Kartta!
        st.markdown(f"""
        <div class="borsa-canli-kart" style="border-left: 6px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 32px; font-weight: bold; color: #ffffff;">📈 {hisse_adi}</span>
                <span style="font-size: 28px; font-weight: bold; color: #ffffff;">Anlık Canlı: {guncel_price:.2f} TL ({gunluk_change:+.2f}% Günlük)</span>
            </div>
            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.15); margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <span style="font-size: 20px; color: #d1d4dc;">💰 Sizin Alım Maliyetiniz: <b style="color:#ffffff; font-size:22px;">{referans_maliyet:.2f} TL</b></span>
                <span style="font-size: 20px; color: #d1d4dc;">🎯 BTA Algoritma Puanı: <b style="color:#ffeb3b; font-size:22px;">{algoritma_puani}</b></span>
                <span style="font-size: 20px; color: #d1d4dc;">📊 Net Kâr/Zarar Durumu: <b style="color:{tl_renk}; font-size:24px;">{isaret}{net_tl_farki:.2f} TL ({isaret}{net_yuzde_farki:.2f}%)</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
