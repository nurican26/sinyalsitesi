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

# Şık Neon Tasarım, Gökkuşağı Çember ve Yazı CSS Kodları
st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    
    /* 🌈 ANIMASYONLU GÖKKUŞAĞI ÇEMBER VE KAYAN BTA LOGO ALANI */
    .logo-konteyner {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px 0;
        margin-bottom: 10px;
    }}
    .cember-animasyon-{anim_id} {{
        width: 120px;
        height: 120px;
        border: 4px solid #fff;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: transparent;
        position: relative;
        overflow: hidden;
        animation: 
            gokkusagiCember 4s linear infinite,
            yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    .bta-yazi-{anim_id} {{
        font-family: 'Caveat', 'Segoe UI', cursive, sans-serif;
        font-size: 3.2rem;
        font-weight: bold;
        margin: 0;
        padding: 0;
        z-index: 2;
        background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));
        animation: soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}
    
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        14% {{ border-color: #ff7f00; box-shadow: 0 0 15px #ff7f00, inset 0 0 15px #ff7f00; }}
        28% {{ border-color: #ffff00; box-shadow: 0 0 15px #ffff00, inset 0 0 15px #ffff00; }}
        42% {{ border-color: #00ff00; box-shadow: 0 0 15px #00ff00, inset 0 0 15px #00ff00; }}
        56% {{ border-color: #00ffff; box-shadow: 0 0 15px #00ffff, inset 0 0 15px #00ffff; }}
        70% {{ border-color: #0000ff; box-shadow: 0 0 15px #0000ff, inset 0 0 15px #0000ff; }}
        84% {{ border-color: #8b00ff; box-shadow: 0 0 15px #8b00ff, inset 0 0 15px #8b00ff; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
    @keyframes yukardanDus {{ 0% {{ transform: translateY(-200px) scale(0.3); opacity: 0; }} 70% {{ transform: translateY(10px) scale(1.05); opacity: 1; }} 100% {{ transform: translateY(0) scale(1); opacity: 1; }} }}
    @keyframes soldanYavascaKay {{ 0% {{ transform: translateX(-140px); opacity: 0; }} 30% {{ opacity: 0.5; }} 100% {{ transform: translateX(0); opacity: 1; }} }}
</style>
''', unsafe_allow_html=True)

# LOGO EKRAN ÇIKTISI
st.markdown(f'''
<div class="logo-konteyner">
    <div class="cember-animasyon-{anim_id}">
        <span class="bta-yazi-{anim_id}">BTA</span>
    </div>
</div>
''', unsafe_allow_html=True)

# 🕒 CANLI SAAT GÖSTERGESİ (Sadece saat ve otomatik yenileme metni)
guncel_saat = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown(f'<div style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 15px; font-weight: bold; text-align: center;">🕒 Canlı Saat: {guncel_saat} <span style="color:#10b981; font-size:0.9rem;">(10 saniyede bir otomatik yenileniyor)</span></div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # 🔍 CANLI ARAMA MOTORU SİSTEMİ
        st.markdown("#### 🔍 BİST Canlı Fiyat Arama Motoru")
        hisse_havuzu = []
        if len(df.columns) >= 5:
            e_sutunu_temiz = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            hisse_havuzu = [h for h in e_sutunu_temiz if h not in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]]
            hisse_havuzu = sorted(list(set(hisse_havuzu)))
        
        secilen_hisse = st.selectbox("Canlı verisini görmek istediğiniz hisseyi seçin:", ["Seçiniz..."] + hisse_havuzu)
        
        if secilen_hisse != "Seçiniz...":
            try:
                hist_ara = yf.download(f"{secilen_hisse}.IS", period="2d", progress=False)
                if not hist_ara.empty:
                    arama_canli_fiyat = float(hist_ara['Close'].dropna().iloc[-1])
                    onceki_kap = float(hist_ara['Close'].dropna().iloc[-2]) if len(hist_ara) >= 2 else arama_canli_fiyat
                    arama_degisim = ((arama_canli_fiyat - onceki_kap) / onceki_kap) * 100
                    st.success(f"📈 **{secilen_hisse}** Anlık Canlı Fiyatı: {arama_canli_fiyat:.2f} TL | Günlük Değişim: %{arama_degisim:+.2f}")
            except:
                st.error("Arama motoru bağlantı hatası.")
        
        st.write("---")

        # ⚡ HAS GÜVENLİ VE HIZLI TOPLU VERİ İNDİRME ADIMI
        sinir = min(10, len(df))
        ust_kodlar, alt_kodlar = [], []
        
        for idx in range(sinir):
            h_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            h_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            if h_a and h_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                ust_kodlar.append(h_a)
            if h_b and h_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                alt_kodlar.append(h_b)
                
        tum_liste = list(set(ust_kodlar + alt_kodlar))
        canli_havuz = {}
        
        if tum_liste:
            try:
                indirme_metni = " ".join([f"{k}.IS" for k in tum_liste])
                toplu_data = yf.download(indirme_metni, period="2d", progress=False, group_by="ticker")
                for k in tum_liste:
                    is_kodu = f"{k}.IS"
                    if is_kodu in toplu_data:
                        sub_df = toplu_data[is_kodu].dropna()
                        if not sub_df.empty:
                            s_f = float(sub_df["Close"].iloc[-1])
                            o_f = float(sub_df["Close"].iloc[-2]) if len(sub_df) >= 2 else s_f
                            canli_havuz[k] = {"son": s_f, "onceki": o_f}
            except:
                pass

        tablo_bta = []
        tablo_alsat = []
        
        # Verileri tablolara hatasız ve hızlıca dağıtma
        for idx in range(sinir):
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alsat_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]

            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                puan_temiz = f"{float(puan_d):.2f}" if pd.notna(puan_d) and isinstance(puan_d, (int, float)) else str(puan_d).strip() if pd.notna(puan_d) else ""
                canli_fiyat = canli_havuz.get(hisse_a, {}).get("son", 0.0)
                
                kz_oran_str = "-"
                maliyet_num = 0.0
                if alim_c and alim_c != "-":
                    try:
                        maliyet_num = float(str(alim_c).replace(",", "."))
                    except:
                        pass
                
                if maliyet_num > 0 and canli_fiyat > 0:
                    kz = ((canli_fiyat - maliyet_num) / maliyet_num) * 100
                    kz_oran_str = f"%{kz:+.2f}"

                tablo_bta.append({
                    "BTA PUAN 🔢": puan_temiz,
                    "BTA HİSSE 📈": hisse_a,
                    "BTA ALIM 📥": alim_c if alim_c else "-",
                    "GÜNCEL FİYAT 💥": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor...",
                    "KAR / ZARAR 📊": kz_oran_str
                })

            if alsat_b and alsat_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                as_canli = canli_havuz.get(alsat_b, {}).get("son", 0.0)
                as_onceki = canli_havuz.get(alsat_b, {}).get("onceki", 0.0)
                as_degisim = 0.0
                if as_canli > 0 and as_onceki > 0:
                    as_degisim = ((as_canli - as_onceki) / as_onceki) * 100

                tablo_alsat.append({
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": alsat_b,
                    "ANLIK VERİ CANLI 📊": f"{as_canli:.2f} TL" if as_canli > 0 else "Yükleniyor...",
                    "YÜKSELİŞ ORANI 📈": f"%{as_degisim:+.2f}" if as_canli > 0 else "-"
                })

        # EKRANA BASMA İŞLEMLERİ
        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if tablo_bta:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
        else:
            st.info("Üst panel verisi işleniyor...")

        st.write("")

        st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if tablo_alsat:
