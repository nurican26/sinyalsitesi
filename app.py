import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# ===================================================================== #
# 1. TEMALANDIRMA VE STİLLER (GÖZ DOSTU & ULTRA OKUNAKLI)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* Deep Gece Mavisi Arka Plan */
.stApp {
    background-color: #0b111e !important;
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important;
}
/* Gözü Yormayan Büyük Veri Kartları */
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] {
    background-color: #121d33 !important; border: 2px solid #1e3a5f !important; border-radius: 12px !important; padding: 18px !important; box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5) !important;
}
input, textarea, select, div[data-baseweb="select"] { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; font-size: 16px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #ffffff !important; border: 1px solid #00ffcc !important; border-radius: 8px !important; font-weight: bold !important; font-size: 16px !important; }

/* TELEFONDA KAN KAN AKAN DÜZGÜN BORSA TABLOSU */
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 16px; background-color: #121d33; border-radius: 12px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 12px 10px; font-weight: bold; }
.borsa-tablo td { padding: 12px 10px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.pozitif-degisim { color: #00ff66 !important; font-weight: bold; }
.negatif-degisim { color: #ff3344 !important; font-weight: bold; }

/* ULTRA GÖRÜNÜR BÜYÜK FİNANS KARTLARI CSS */
.altin-kart { background: linear-gradient(135deg, #121d33 0%, #1a2e5c 100%); border: 2px solid #00ffcc; border-radius: 12px; padding: 15px; margin-bottom: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0, 255, 204, 0.1); }
.altin-baslik { font-size: 18px !important; color: #00ffcc !important; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
.altin-fiyat { font-size: 26px !important; color: #ffffff !important; font-weight: 900 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
</style>
<marquee scrollamount="8"><span style="font-size:45px; font-weight:bold; color:#fff; text-shadow: 0 0 10px #ff0055;">✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨</span></marquee>
''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

if "toplam_sayac" not in st.session_state: st.session_state["toplam_sayac"] = 1450
if "gunluk_sayac" not in st.session_state: st.session_state["gunluk_sayac"] = 120
st.session_state["toplam_sayac"] += 1
st.session_state["gunluk_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# CANLI ALTIN VE BIST 100 PİYASA FIYAT ALANI (BÜYÜK KART SİSTEMİ)
# ===================================================================== #
st.markdown('<p style="font-size:22px; font-weight:bold; color:#00ffcc;">📊 CANLI PİYASA ÖZETİ (GÖZ DOSTU)</p>', unsafe_allow_html=True)
try:
    bist_v = yf.Ticker("XU100.IS").history(period="2d", timeout=2)
    ons_v = yf.Ticker("GC=F").history(period="2d", timeout=2)
    dolar_v = yf.Ticker("TRY=X").history(period="2d", timeout=2)
    
    bist_f = float(bist_v['Close'].iloc[-1]) if len(bist_v)>0 else 0.0
    bist_d = ((bist_f - float(bist_v['Close'].iloc[-2])) / float(bist_v['Close'].iloc[-2])) * 100 if len(bist_v)>=2 else 0.0
    
    ons_f = float(ons_v['Close'].iloc[-1]) if len(ons_v)>0 else 0.0
    usd_try = float(dolar_v['Close'].iloc[-1]) if len(dolar_v)>0 else 34.50
    
    gram_f = (ons_f / 31.1034768) * usd_try if ons_f>0 else 0.0
    ceyrek_f = gram_f * 1.63 if gram_f>0 else 0.0
    yarim_f = gram_f * 3.26 if gram_f>0 else 0.0
    tam_f = gram_f * 6.52 if gram_f>0 else 0.0
    
    bist_renk = "#00ff66" if bist_d >= 0 else "#ff3344"
    bist_isaret = "▲" if bist_d >= 0 else "▼"
    
    # Telefonlarda alt alta devasa parlayan buton şeklinde kartlar diziyoruz
    st.markdown(f'''
    <div class="altin-kart" style="border-color:{bist_renk};">
        <div class="altin-baslik">🌐 BIST 100 ENDEKSİ</div>
        <div class="altin-fiyat">{bist_f:,.2f} <span style="color:{bist_renk}; font-size:20px;">{bist_isaret} %{bist_d:.2f}</span></div>
    </div>
    <div class="altin-kart">
        <div class="altin-baslik">✨ GRAM ALTIN</div>
        <div class="altin-fiyat">{formatla_tl(gram_f)}</div>
    </div>
    <div class="altin-kart">
        <div class="altin-baslik">🎯 ÇEYREK ALTIN</div>
        <div class="altin-fiyat">{formatla_tl(ceyrek_f)}</div>
    </div>
    <div class="altin-kart">
        <div class="altin-baslik">👑 TAM ALTIN</div>
        <div class="altin-fiyat">{formatla_tl(tam_f)}</div>
    </div>
    ''', unsafe_allow_html=True)
except:
    st.markdown('<div class="altin-kart">⏳ Fiyatlar Güncelleniyor...</div>', unsafe_allow_html=True)

# ===================================================================== #
# 2. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
st.write("")
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>PUAN</th><th>HİSSE</th><th>ALIM</th><th>FİYAT</th><th>K/Z</th></tr>'
        veri_var_mi = False
        
        for idx in range(min(10, len(df))):
            try:
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                    try: maliyet = float(alim_c.replace(",", "."))
                    except: maliyet = 0.0
                    
                    if maliyet > 0 and c_fiyat > 0:
                        or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                        kz_str = f'<span class="pozitif-degisim">▲ %{or_dg:.1f}</span>' if or_dg >= 0 else f'<span class="negatif-degisim">▼ %{or_dg:.1f}</span>'
                    else: kz_str = "<span>-</span>"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{formatla_tl(maliyet) if maliyet>0 else alim_c}</td><td>{formatla_tl(c_fiyat) if c_fiyat>0 else "..."}</td><td>{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU + GRAFİK + GÜNCEL HABERLER ---
        st.write("")
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin ", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="30d", timeout=3)
                    if len(h_detay_veri) > 0:
                        anlik_fiyat = float(h_detay_veri['Close'].iloc[-1])
                        dunku = float(h_detay_veri['Close'].iloc[-2]) if len(h_detay_veri) >= 2 else anlik_fiyat
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Fiyat 💥", formatla_tl(anlik_fiyat), f"%{((anlik_fiyat - dunku) / dunku) * 100:+.2f}")
                        col2.metric("En Yüksek 📈", formatla_tl(float(h_detay_veri['High'].iloc[-1])))
                        col3.metric("En Düşük 📉", formatla_tl(float(h_detay_veri['Low'].iloc[-1])))
                        st.line_chart(h_detay_veri['Close'], use_container_width=True)
                        try:
                            s_hbr = yf.Ticker(f"{aranan_hisse}.IS").news[:2]
                            if s_hbr: 
                                st.write("**Hisse Gelişmeleri:**")
                                for h in s_hbr: st.caption(f"🔗 [{h.get('title')}]({h.get('link')})")
                        except: pass
    except: st.error("Veriler yüklenirken sorun oluştu.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 3. HALKA ARZ VE HABER ALANI (2 ADET HABER TAM SÜRÜM)
# ===================================================================== #
st.write("---")
st.header("🔔 GÜNCEL HALKA ARZLAR VE ANLIK HABERLER")
c_arz, c_hbr = st.columns(2)
with c_arz:
    st.subheader("🚀 Yeni Halka Arz Listesi")
