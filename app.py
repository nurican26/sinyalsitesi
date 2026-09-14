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
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #00b0ff !important;
        box-shadow: 0 0 15px rgba(0, 176, 255, 0.3) !important;
        margin-bottom: 15px;
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
    
    /* SAĞDAN SOLA DOĞRU AĞIR YÜRÜYEN KURUMSAM BTA MİMARİSİ */
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
# 3. EXCEL E SÜTUNUNDAN HİSSELERİ OTOMATİK ÇEKME MOTORU
# ==========================================
hisse_listesi = ["KONYA"] # Excel okunamama durumunda yedek ana hisse

excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
if excel_dosyalari:
    hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
    secilen_excel = hedef_dosyalar if hedef_dosyalar else excel_dosyalari
    
    try:
        df_excel = pd.read_excel(secilen_excel, sheet_name=0, engine='openpyxl')
        df_excel.columns = df_excel.columns.astype(str).str.strip()
        
        # E sütunundaki (5. sütun) tüm hisse isimlerini çekiyoruz
        if len(df_excel.columns) >= 5:
            e_sutunu_verileri = df_excel.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            temiz_hisseler = [h for h in e_sutunu_verileri if h != "" and h != "NONE" and not h.replace('.','',1).isdigit()]
            if temiz_hisseler:
                hisse_listesi = sorted(list(set(temiz_hisseler)))
    except:
        pass

# ==========================================
# 4. 📋 SIFIR ARAMA KUTULU - BTA CANLI HİSSE PANELİ
# ==========================================
st.subheader("📊 BTA Canlı İzleme ve Portföy Paneli")
st.info("⏱️ Borsa İstanbul (BIST) verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** olarak yansımaktadır.")

# Arama motoru kutuları tamamen kaldırılmıştır. Tüm hisseler otomatik taranıp siber kartlar olarak basılır.
for hisse_adi in hisse_listesi:
    kurumsal_ticker = f"{hisse_adi}.IS"
    guncel_price = 0.0
    gunluk_change = 0.0
    veri_okundu = False
    
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
        # Renk koşullandırması (Artı ise yeşil, eksi ise kırmızı neon)
        border_color = "#089981" if gunluk_change >= 0 else "#da3637"
        text_color = "#089981" if gunluk_change >= 0 else "#da3637"
        isaret = "+" if gunluk_change >= 0 else ""
        
        if gunluk_change >= 9.85:
            st.balloons()
            
        st.markdown(f"""
        <div class="borsa-canli-kart" style="border-left: 6px solid {border_color};">
            <table style="width:100%; border-collapse:collapse; border:none;">
                <tr style="background:transparent; border:none;">
                    <td style="font-size:28px; font-weight:bold; color:#ffffff; border:none; width:30%; padding:0;">📈 {hisse_adi}</td>
                    <td style="font-size:26px; font-weight:bold; color:#ffffff; text-align:center; border:none; width:40%; padding:0;">Fiyat: {guncel_price:.2f} TL</td>
                    <td style="font-size:26px; font-weight:bold; color:{text_color}; text-align:right; border:none; width:30%; padding:0;">Değişim: {isaret}{gunluk_change:.2f}%</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
