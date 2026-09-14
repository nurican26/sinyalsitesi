import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SAYFA, COĞRAFYA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik Finans Portalı",
    page_icon="⚡",
    layout="wide"
)

# 5 saniyede bir sayfayı canlı güncelleyen yenileme motoru
st_autorefresh(interval=5 * 1000, key="bta_global_refresh_motoru")

# ==========================================
# 2. ŞİMŞEKLİ, PARLAK NEON ARKA PLAN CSS TASARIMI
# ==========================================
css_tasarımı = """
<style>
/* Kesin ve sarsılmaz koyu neon radyal gradyan arka plan katmanı */
html, body, [data-testid="stAppViewContainer"], .stApp { 
    background-color: #05070f !important; 
    background-image: 
        radial-gradient(at 15% 15%, rgba(0, 242, 254, 0.2) 0px, transparent 45%),
        radial-gradient(at 85% 35%, rgba(147, 51, 234, 0.15) 0px, transparent 50%),
        radial-gradient(at 50% 85%, rgba(0, 255, 204, 0.12) 0px, transparent 45%) !important; 
    background-attachment: fixed !important;
    color: #ffffff !important;
}

/* Sayfa boşluklarını daraltma */
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }

/* Şimşek Mavisi ve Neon Parlamalı Metrik Kutuları */
div[data-testid="stMetric"], div[data-testid="stExpander"], .bta-card { 
    background: linear-gradient(135deg, #0d1527 0%, #070a14 100%) !important; 
    border: 1px solid #00f2fe !important; 
    box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.25), inset 0px 0px 10px rgba(0, 242, 254, 0.1) !important;
    border-radius: 10px !important; 
    padding: 15px !important; 
}

/* Siber Borsa Tablosu Tasarımı */
.borsa-tablo { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 15px 0; 
    font-size: 15px; 
    background-color: #0d1527; 
    border-radius: 10px; 
    overflow: hidden; 
    border: 1px solid #00f2fe; 
    box-shadow: 0px 0px 20px rgba(0, 242, 254, 0.2); 
}
.borsa-tablo th { 
    background-color: #16223f; 
    color: #00ffcc; 
    text-align: left; 
    padding: 12px 10px; 
    border-bottom: 2px solid #00f2fe; 
    text-shadow: 0 0 5px #00ffcc; 
    font-weight: bold;
}
.borsa-tablo td { 
    padding: 12px 10px; 
    color: #ffffff; 
    border-bottom: 1px solid #16223f; 
    font-weight: bold; 
}
.borsa-tablo tr:hover {
    background-color: rgba(0, 242, 254, 0.05);
}

/* Özel Şerit Tipi Kırmızı SPK Uyarı Kutusu */
.spk-neon-kutu {
    background-color: rgba(255, 51, 68, 0.07) !important;
    border: 1px solid #ff3344 !important;
    box-shadow: 0px 0px 12px rgba(255, 51, 68, 0.2) !important;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 20px;
}

/* Başlık Kayan Alan Genişliği */
.marquee-alan {
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    margin-bottom: 10px;
}

@keyframes marqueeBTA {
    0% { transform: translateX(-5%); }
    50% { transform: translateX(80%); }
    100% { transform: translateX(-5%); }
}

/* Şık Kayan El Yazısı Portal Logosu */
.marquee-bta-logo {
    font-family: 'Pacifico', 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 50px; 
    color: #fffb00;
    display: inline-block;
    animation: marqueeBTA 16s infinite linear;
    text-shadow: 0 0 12px #fffb00, 0 0 25px #ff6c00, 0 0 40px #00f2fe;
}
</style>
<link rel="preconnect" href="https://googleapis.com">
<link rel="preconnect" href="https://gstatic.com" crossorigin>
<link href="https://googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
"""
st.markdown(css_tasarımı, unsafe_allow_html=True)

# YASAL METİN ŞABLONU
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 3. ANA PANEL GÖRSEL ÖĞELERİ VE GRAFİKLER
# ==========================================
# Kayan şimşekli el yazısı logo başlığı
st.markdown('<div class="marquee-alan"><h1 class="marquee-bta-logo">⚡ 🧠 BTA Algoritmik Finans Portalı 🧠 ⚡</h1></div>', unsafe_allow_html=True)

# Kırmızı korumalı SPK yasal uyarısı
st.markdown(f'<div class="spk-neon-kutu"><p style="font-size:12px; color:#f2f4f8; font-weight:bold; line-height:1.6; text-align:justify; margin:0;">{spk_metni}</p></div>', unsafe_allow_html=True)

# TRADINGVIEW CANLI BIST 100 GRAFİK WIDGETI
bist_grafik_widget = """
<div class="tradingview-widget-container" style="margin: auto; text-align: center; width: 100%;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://tradingview.com" async>
  {
  "symbol": "BIST:XU100", "width": "100%", "height": "110", "locale": "tr",
  "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": ""
  }
  </script>
</div>
"""
components.html(bist_grafik_widget, height=115)

# Zaman Damgası Hesaplama
zaman_obj = datetime.datetime.now()
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
guncel_zaman_str = zaman_obj.strftime(f"%d.%m.%Y - %H:%M:%S | {gunler[zaman_obj.weekday()]}")

st.markdown(f'<p style="font-size:13px; font-weight:bold; color:#00ffcc; text-align:right; margin-bottom:5px;">🕒 Sistem Güncelleme Zamanı: {guncel_zaman_str}</p>', unsafe_allow_html=True)

# ==========================================
# 4. CANLI BORSA TAKİP VE VERİ MOTORU (YFINANCE)
# ==========================================
st.markdown('<p style="font-size:18px; font-weight:bold; color:#00f2fe; text-shadow: 0 0 5px #00f2fe; margin:0;">📈 CANLI BORSA TAKİP PANELİ</p>', unsafe_allow_html=True)

# Takip etmek istediğiniz ana endeks ve popüler hisseler (İleride buraya listenizi ekleriz)
ornek_hisseler = ["KONYA", "THYAO", "ASELS", "EREGL", "AKBNK"]
tablo_satirlari = ""

for hisse_kodu in ornek_hisseler:
    anlik_fiyat = 0.0
    gunluk_degisim = 0.0
    yuzde_str = "-"
    
    # Ultra güvenli, internet kopsa bile sayfayı kilitlemeyen yfinance motoru
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        veri = ticker.history(period="2d", interval="1d", timeout=1.5)
        if not veri.empty and len(veri) >= 1:
            anlik_fiyat = float(veri['Close'].iloc[-1])
            if len(veri) > 1:
                onceki_kapanis = float(veri['Close'].iloc[-2])
                gunluk_degisim = ((anlik_fiyat - onceki_kapanis) / onceki_kapanis) * 100
                
            if gunluk_degisim >= 0:
                yuzde_str = f'<span style="color:#00ff66;">▲ %{gunluk_degisim:.2f}</span>'
            else:
                yuzde_str = f'<span style="color:#ff3344;">▼ %{gunluk_degisim:.2f}</span>'
    except:
        anlik_fiyat = 0.0
        yuzde_str = '<span style="color:#8892b0;">Bağlantı Bekleniyor...</span>'

    fiyat_gosterim = f"{anlik_fiyat:.2f} TL" if anlik_fiyat > 0 else "0.00 TL"
    
    # Tablo satırlarını dinamik inşa ediyoruz
    tablo_satirlari += f"""
    <tr>
        <td>⚡ {hisse_kodu}</td>
        <td>{fiyat_gosterim}</td>
        <td>{yuzde_str}</td>
        <td>Borsa İstanbul (BIST)</td>
    </tr>
    """

# Tabloyu HTML formatında sayfaya basıyoruz
borsa_tablo_html = f"""
<table class="borsa-tablo">
    <tr>
        <th>HİSSE KODU</th>
        <th>ANLIK FİYAT</th>
        <th>GÜNLÜK DEĞİŞİM</th>
        <th>PİYASA BAĞLANTISI</th>
    </tr>
    {tablo_satirlari}
</table>
"""
st.markdown(borsa_tablo_html, unsafe_allow_html=True)

# ==========================================
# 5. ALT YASAL BİLGİLENDİRME PANELİ
# ==========================================
st.markdown(
    """
    <div style="background-color: #0d1527; border: 1px solid #ff3344; border-radius: 8px; padding: 12px; margin-top: 15px; box-shadow: 0 0 10px rgba(255,51,68,0.15);">
        <p style="font-size:11px; color:#b2c3d9; line-height:1.5; text-align:justify; margin:0;">
            <b style="color:#ff3344;">⚠️ ÖNEMLİ BİLGİLENDİRME:</b> Finansal piyasa verileri en az 15 dakika gecikmelidir. Sitemiz teknik altyapı ve kod denemeleri amacıyla kurulmuş olup, sistem üzerinde yansıtılan hiçbir veri, fiyat veya değişim oranı yatırım danışmanlığı, al-sat sinyali veya portföy yönetim yönlendirmesi niteliği taşımamaktadır.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
