import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Hisse Takip Programı", layout="wide")

# 🔄 CANLI FİYAT VE ANIMASYON KİLİDİ: Sayfa her 10 saniyede bir otomatik yenilenir
st_autorefresh(interval=10 * 1000, key="hisse_canli_yenileyici")

# Her yenilemede animasyonu baştan oynatmak için zaman damgası
anim_id = int(time.time())

# Şık Neon Tasarım, Gökkuşağı Çember, Yazı ve WhatsApp Tarzı Sohbet CSS Kodları
st.markdown(f'''
<style>
    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin-bottom: 20px;
    }}
    .rainbow-circle {{
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 5px solid transparent;
        border-top-color: #ff007f;
        border-right-color: #00f0ff;
        border-bottom-color: #7100ff;
        border-left-color: #00ff66;
        animation: spin 2s linear infinite;
    }}
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    .logo-text {{
        font-size: 42px;
        font-weight: bold;
        color: #fff;
        text-shadow: 0 0 10px #00f0ff, 0 0 20px #00f0ff, 0 0 40px #00f0ff;
        margin-top: 10px;
        font-family: 'Arial Black', Gadget, sans-serif;
    }}
    .time-text {{
        text-align: center;
        font-size: 18px;
        color: #888;
    }}
    .panel-title {{
        font-size: 24px;
        font-weight: bold;
        color: #ff007f;
        text-shadow: 0 0 5px #ff007f;
        border-bottom: 2px solid #ff007f;
        padding-bottom: 5px;
        margin-top: 25px;
        margin-bottom: 15px;
    }}
    .panel-title-blue {{
        font-size: 24px;
        font-weight: bold;
        color: #00f0ff;
        text-shadow: 0 0 5px #00f0ff;
        border-bottom: 2px solid #00f0ff;
        padding-bottom: 5px;
        margin-top: 25px;
        margin-bottom: 15px;
    }}
    .yasal-uyari {{
        text-align: center;
        font-size: 13px;
        color: #aaaaaa;
        background-color: rgba(255, 0, 0, 0.1);
        padding: 10px;
        border-radius: 5px;
        border: 1px solid rgba(255, 0, 0, 0.3);
        margin-top: 40px;
        font-weight: bold;
    }}
    
    /* WhatsApp Sohbet Tasarım Alanı */
    .chat-container {{
        background-color: #0b141a;
        background-image: url('https://githubusercontent.com');
        background-repeat: repeat;
        border-radius: 10px;
        padding: 15px;
        max-height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
        border: 1px solid #222e35;
        margin-bottom: 15px;
    }}
    .msg-box {{
        max-width: 65%;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 14px;
        position: relative;
        line-height: 1.4;
        color: #e9edef;
    }}
    .msg-user {{
        background-color: #005c4b;
        align-self: flex-end;
        border-top-right-radius: 0px;
    }}
    .msg-other {{
        background-color: #202c33;
        align-self: flex-start;
        border-top-left-radius: 0px;
    }}
    .msg-sender {{
        font-size: 11px;
        font-weight: bold;
        color: #00a884;
        margin-bottom: 3px;
    }}
    .msg-time {{
        font-size: 10px;
        color: rgba(233, 237, 239, 0.6);
        text-align: right;
        margin-top: 4px;
    }}
</style>
''', unsafe_allow_html=True)

# LOGO EKRAN ÇIKTISI
st.markdown(f'''
<div class="logo-container">
    <div class="rainbow-circle"></div>
    <div class="logo-text">BTA</div>
</div>
''', unsafe_allow_html=True)

# Saat Göstergesi
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div class="time-text">🕒 Son Güncelleme: {guncel_an} <br><small>(10sn de bir otomatik yenileniyor)</small></div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

if not os.path.exists(excel_yolu):
    st.error("Excel dosyası 'nurican.xls.xlsm' bulunamadı!")
else:
    try:
        # Doğrudan "WEB" isimli sayfayı okuyoruz
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # 🔍 KASMAYI ENGELLEYEN CANLI ARAMA MOTORU SİSTEMİ
        st.markdown("#### 🔍 BİST Canlı Fiyat Arama Motoru")
        
        # Excel'deki E sütunundaki (5. sütun) hisseleri alıyoruz
        hisse_havuzu = []
        if len(df.columns) >= 5:
            e_sutunu_temiz = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            hisse_havuzu = [h for h in e_sutunu_temiz if h not in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]]
            hisse_havuzu = sorted(list(set(hisse_havuzu))) # Benzersiz yap ve sırala
            
        # Kullanıcıya E sütunundan gelen temiz listeyi seçenek olarak sunuyoruz
        secilen_hisse = st.selectbox("Canlı verisini görmek istediğiniz hisseyi seçin:", ["Seçiniz..."] + hisse_havuzu)
        
        if secilen_hisse != "Seçiniz...":
            try:
                # Sadece seçilen hisse için internete gidilir (Kasma yapmaz)
                ticker_ara = yf.Ticker(f"{secilen_hisse}.IS")
                hist_ara = ticker_ara.history(period="2d")
                if not hist_ara.empty:
                    arama_canli_fiyat = float(hist_ara['Close'].iloc[-1])
                    onceki_kap = float(hist_ara['Close'].iloc[-2]) if len(hist_ara) >= 2 else arama_canli_fiyat
                    arama_degisim = ((arama_canli_fiyat - onceki_kap) / onceki_kap) * 100
                    st.success(f"📈 **{secilen_hisse}** Anlık Canlı Fiyatı: **{arama_canli_fiyat:.2f} TL** | Günlük Değişim: **%{arama_degisim:+.2f}**")
                else:
                    st.warning("Seçilen hisse için canlı veri şu an çekilemedi.")
            except:
                st.error("Veri motoru bağlantı hatası.")
                
        st.write("---")
        
        tablo_bta = []
        tablo_alsat = []
        sinir = min(10, len(df))
        
        for idx in range(sinir):
            # 1. ÜST PANEL VERİLERİ (A, C, D Sütunları)
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                try:
                    puan_temiz = f"{float(puan_d):.2f}"
                except:
                    puan_temiz = str(puan_d).strip() if pd.notna(puan_d) else ""
                    
                try:
                    ticker = yf.Ticker(f"{hisse_a}.IS")
                    hist = ticker.history(period="1d")
                    canli_fiyat = float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
                except:
                    canli_fiyat = 0.0
                    
                try:
                    maliyet = float(alim_c.replace(",", "."))
                except:
                    maliyet = 0.0
                    
                kz_oran_str = "-"
                if maliyet > 0 and canli_fiyat > 0:
                    kz = ((canli_fiyat - maliyet) / maliyet) * 100
                    kz_oran_str = f"%{kz:+.2f}"
                    
                tablo_bta.append({
                    "BTA PUAN 🔢": puan_temiz,
                    "BTA HİSSE 📈": hisse_a,
                    "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c,
                    "GÜNCEL FİYAT 💥": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor...",
                    "KAR / ZARAR 📊": kz_oran_str
                })
                
            # 2. ALT PANEL VERİLERİ (B Sütunu)
            alsat_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            if alsat_b and alsat_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                try:
                    ticker_as = yf.Ticker(f"{alsat_b}.IS")
                    hist_as = ticker_as.history(period="2d")
                    as_canli_fiyat = float(hist_as['Close'].iloc[-1]) if not hist_as.empty else 0.0
                    if len(hist_as) >= 2:
                        onceki_kapanis = float(hist_as['Close'].iloc[-2])
                        as_degisim = ((as_canli_fiyat - onceki_kapanis) / onceki_kapanis) * 100
                    else:
                        as_degisim = 0.0
                except:
                    as_canli_fiyat, as_degisim = 0.0, 0.0
                    
                tablo_alsat.append({
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": alsat_b,
                    "ANLIK VERİ CANLI 📊": f"{as_canli_fiyat:.2f} TL" if as_canli_fiyat > 0 else "Yükleniyor...",
                    "YÜKSELİŞ ORANI 📈": f"%{as_degisim:+.2f}" if as_canli_fiyat > 0 else "-"
                })
                
        # EKRANA BASMA İŞLEMLERİ
        st.markdown('<div class="panel-title">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if tablo_bta:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
        else:
            st.info("Üst panel için veri işleniyor...")
            
        st.write("")
        st.markdown('<div class="panel-title-blue">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if tablo_alsat:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
        else:
            st.info("Alt panel için veri işleniyor...")
            
        # 💬 WHATSAPP TARZI SOHBET VE NOT ALANI
        st.write("")
        st.markdown('<div class="panel-title-blue">💬 BTA SOHBET VE ANALİZ ODASI</div>', unsafe_allow_html=True)
        
