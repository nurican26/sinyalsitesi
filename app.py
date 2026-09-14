import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os

# ==========================================
# 1. SAYFA VE KESİN SOL MENÜSÜZ AYARLAR
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik Finans Terminali",
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
        <div class='bta-neon-heavy'>BTA ALGORİTMİK İŞLEM VE TAKİP TERMİNALİ</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(spk_metni)
st.markdown("---")

# Varsayılan Excel Okuma Hafıza Listeleri
sabit_bta_listesi = [{"Hisse": "KONYA", "Maliyet": 4100.0, "Puan": "100"}]
e_sutunu_arama_listesi = ["KONYA"]

# ==========================================
# 3. ALGORİTMİK VERİ AYRIŞTIRMA MOTORU
# ==========================================
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
if excel_dosyalari:
    hedef_dosyalar = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm')) and ("bta" in f.lower() or "nurican" in f.lower())]
    secilen_excel = hedef_dosyalar[0] if hedef_dosyalar else excel_dosyalari[0]
    
    try:
        df_excel = pd.read_excel(secilen_excel, sheet_name=0, engine='openpyxl')
        df_excel.columns = df_excel.columns.astype(str).str.strip()
        
        # 📌 PANEL 1: A, C ve D sütunlarını güvenle al
        gerekli_bta_sutunlari = ["BTA HİSSE", "BTA ALIM FİYATI", "BTA PUAN"]
        if all(col in df_excel.columns for col in gerekli_bta_sutunlari):
            gecici_sabit_liste = []
            for idx, row in df_excel.iterrows():
                a_val = str(row["BTA HİSSE"]).strip().upper()
                c_val = row["BTA ALIM FİYATI"]
                d_val = row["BTA PUAN"]
                
                if a_val and a_val != "NAN" and a_val != "NONE" and not a_val.replace('.','',1).isdigit():
                    gecici_sabit_liste.append({
                        "Hisse": a_val,
                        "Maliyet": float(c_val) if pd.notna(c_val) else 0.0,
                        "Puan": str(d_val) if pd.notna(d_val) else "0"
                    })
            if gecici_sabit_liste:
                sabit_bta_listesi = gecici_sabit_liste

        # 📌 PANEL 2: E sütunundaki diğer tüm hisseleri arama motoru için ayır
        if len(df_excel.columns) >= 5:
            e_sutunu_ham = df_excel.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            temiz_e_hisseleri = [h for h in e_sutunu_ham if h != "" and h != "NONE" and h != "NAN" and not h.replace('.','',1).isdigit()]
            if temiz_e_hisseleri:
                e_sutunu_arama_listesi = sorted(list(set(temiz_e_hisseleri)))
    except:
        pass

# ==========================================
# PANEL 1: SABİT BTA PORTFÖY LİSTESİ (A - C - D Sütunları)
# ==========================================
st.header("📋 Sabit BTA Portföy Listesi (A - C - D Sütunları)")
for row_data in sabit_bta_listesi:
    st.markdown(f"""
    <div class="borsa-canli-kart" style="border-left: 6px solid #00b0ff; margin-bottom: 10px;">
        <span style="font-size: 24px; font-weight: bold; color: #ffffff;">📈 BTA HİSSE: {row_data['Hisse']}</span> | 
        <span style="font-size: 18px; color: #d1d4dc;">💰 BTA Alım Fiyatı (C): <b>{row_data['Maliyet']:.2f} TL</b></span> | 
        <span style="font-size: 18px; color: #d1d4dc;">🎯 BTA Puan (D): <b style="color:#ffeb3b;">{row_data['Puan']}</b></span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# PANEL 2: AYRI CANLI HİSSE ARAMA MOTORU (E SÜTUNU)
# ==========================================
st.header("🔍 E Sütunu Canlı Hisse Arama Motoru")
st.warning("⏱️ Arama motoru verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** yansımaktadır.")

secilen_arama_hissesi = st.selectbox(
    "Arama Motoru: Takip etmek istediğiniz E sütunu hissesini seçin veya yazın:",
    options=e_sutunu_arama_listesi,
    index=0
)

if secilen_arama_hissesi:
    kurumsal_ticker = f"{secilen_arama_hissesi}.IS"
    guncel_price = 0.0
    gunluk_change = 0.0
    veri_okundu = False
    tarihce_data = pd.DataFrame()
    
    try:
        hisse_data = yf.Ticker(kurumsal_ticker)
        tarihce_data = hisse_data.history(period="2d", interval="1d")
        if not tarihce_data.empty:
            guncel_price = tarihce_data['Close'].iloc[-1]
            gunluk_change = hisse_data.info.get('regularMarketChangePercent', 0.0)
            if gunluk_change == 0.0 and len(tarihce_data) > 1:
                onceki_kapanis = tarihce_data['Close'].iloc[-2]
                gunluk_change = ((guncel_price - onceki_kapanis) / onceki_kapanis) * 100
            veri_okundu = True
    except:
        pass
        
    if veri_okundu:
        # Tırnak hatası üreten karmaşık f-string yapısı kaldırılarak Streamlit native metrik kurgusuna geçildi
        if gunluk_change >= 9.85:
            st.balloons()
            st.success(f"🚀 **KUTLAMALAR BAŞLASIN! {secilen_arama_hissesi} HİSSESİ TAVAN OLDU!** 🥳🎉")
            
        st.subheader(f"🔎 Aranan Hisse: {secilen_arama_hissesi}")
        
        # Temiz ve kasmayan standart borsa kutuları
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Canlı İnternet Fiyatı", f"{guncel_price:.2f} TL")
        col_m2.metric("Günlük Değişim", f"{gunluk_change:+.2f}%")
        
        if not tarihce_data.empty:
            st.subheader(f"📊 {secilen_arama_hissesi} - Gün İçi Canlı Fiyat Grafik Trendi")
            st.line_chart(tarihce_data['Close'])
    else:
        st.error(f"⚠️ {secilen_arama_hissesi} kodu için veri çekilemedi. Lütfen seans saatlerini veya kod biçimini kontrol edin.")
