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

    /* Borsa Hesaplama Kutuları */
    div[data-testid="stMetric"] {
        background: rgba(15, 32, 67, 0.85) !important;
        padding: 22px !important;
        border-radius: 14px !important;
        border: 2px solid #00b0ff !important;
        box-shadow: 0 0 20px rgba(0, 176, 255, 0.4) !important;
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
        <div class='bta-neon-heavy'>BTA ALGORİTMİK MULTİ-HİSSE TAKİP TERMİNALİ</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(spk_metni)
st.markdown("---")

# ==========================================
# 3. EXCEL E SÜTUNUNDAN HİSSELERİ OTOMATİK ÇEKME MOTORU
# ==========================================
hisse_listesi = ["KONYA"] # Excel yoksa varsayılan yedek

excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
if excel_dosyalari:
    hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
    secilen_excel = hedef_dosyalar[0] if hedef_dosyalar else excel_dosyalari[0]
    
    try:
        # Excel dosyasını hızlıca oku
        df_excel = pd.read_excel(secilen_excel, sheet_name=0, engine='openpyxl')
        
        # 🚀 5. sütun (E sütunu - indeks 4) mevcutsa hisse isimlerini ayıkla
        if len(df_excel.columns) >= 5:
            e_sutunu_verileri = df_excel.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            # Geçersiz, boş veya sayısal olmayan satırları temizle
            temiz_hisseler = [h for h in e_sutunu_verileri if h != "" and h != "NONE" and not h.replace('.','',1).isdigit()]
            if temiz_hisseler:
                # Benzersiz kodları sıralı liste yap
                hisse_listesi = sorted(list(set(temiz_hisseler)))
    except:
        pass

# ==========================================
# 4. 🔍 DİNAMIK HİSSE ARAMA MOTORU ARAYÜZÜ
# ==========================================
st.subheader("🔍 Algoritmik Hisse Arama ve Takip Motoru")
secilen_hisse_kodu = st.selectbox(
    "Excel E Sütunundan Çekilen Hisseler Listesi (Takip Etmek İstediğinizi Seçin):",
    options=hisse_listesi,
    index=0
)

# Yfinance taraması için hisse sonuna .IS ekliyoruz
kurumsal_ticker = f"{secilen_hisse_kodu}.IS"

# Canlı veri çekim katmanı
guncel_fta_fiyati = 0.0
gunluk_degisim_yuzde = 0.0
borsa_verisi_tamam = False
tarihce = pd.DataFrame()

try:
    hisse_motoru = yf.Ticker(kurumsal_ticker)
    tarihce = hisse_motoru.history(period="2d", interval="1d")
    if not tarihce.empty:
        guncel_fta_fiyati = tarihce['Close'].iloc[-1]
        gunluk_degisim_yuzde = hisse_motoru.info.get('regularMarketChangePercent', 0.0)
        if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
            onceki_kapanis = tarihce['Close'].iloc[-2]
            gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
        borsa_verisi_tamam = True
except:
    pass

# ==========================================
# 5. CANLI VERİ VE GRAFİK EKRANI
# ==========================================
if borsa_verisi_tamam:
    st.markdown("---")
    st.header(f"📊 {secilen_hisse_kodu} Canlı Analiz Paneli")
    st.warning("⏱️ Borsa İstanbul (BIST) verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** olarak yansımaktadır.")
    
    # Seçilen hissenin canlı borsa değerleri kartları
    c1, c2 = st.columns(2)
    c1.metric(f"Anlık Canlı {secilen_hisse_kodu} Fiyatı", f"{guncel_fta_fiyati:.2f} TL")
    c2.metric("Günlük Değişim Oranı", f"{gunluk_degisim_yuzde:.2f}%")
    
    # Tavan / tavan yakınlığı durumunda ödül konfetileri tetiklenir
    if gunluk_degisim_yuzde >= 9.85:
        st.balloons()
        st.success(f"🚀 **KUTLAMALAR BAŞLASIN! {secilen_hisse_kodu} HİSSESİ ANLIK OLARAK TAVAN OLDU!** 🥳🎉")
        
    st.markdown("---")
    st.subheader(f"📈 {secilen_hisse_kodu} - Gün İçi Canlı Fiyat Grafik Trendi")
    st.line_chart(tarihce['Close'])
else:
    st.error(f"⚠️ {secilen_hisse_kodu} hissesine ait canlı veriler Borsa İstanbul sunucularından çekilemedi. Kodun doğruluğunu veya internet bağlantısını kontrol edin.")
