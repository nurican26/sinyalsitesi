import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# ===================================================================== #
# 1. TEMALANDIRMA VE STİLLER (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp {
    background-color: #0b111e !important;
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%), linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
}
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] {
    background-color: #121d33 !important; border: 1px solid #1e2e4d !important; border-radius: 12px !important; padding: 15px !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
}
input, textarea, select, div[data-baseweb="select"] { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #ffffff !important; border: 1px solid #00ffcc !important; border-radius: 8px !important; font-weight: bold !important; box-shadow: 0 0 10px rgba(0, 255, 204, 0.2) !important; }
.stButton>button:hover { background: linear-gradient(135deg, #0d9488 0%, #00ffcc 100%) !important; color: #0b111e !important; box-shadow: 0 0 20px rgba(0, 255, 204, 0.6) !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 18px; font-family: sans-serif; background-color: #121d33; border-radius: 12px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 14px 18px; }
.borsa-tablo td { padding: 14px 18px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.pozitif-degisim { color: #00ff66 !important; font-weight: bold; font-size: 19px; }
.negatif-degisim { color: #ff3344 !important; font-weight: bold; font-size: 19px; }
.finans-bandi { background: #121d33; border: 1px solid #1e2e4d; border-radius: 8px; padding: 10px; margin-bottom: 15px; font-weight: bold; font-size: 15px; color: #fff; text-align: center; }
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
# CANLI ALTIN VE BIST 100 PİYASA FIYAT BANDI
# ===================================================================== #
try:
    bist_v = yf.Ticker("XU100.IS").history(period="2d", timeout=2)
    ons_v = yf.Ticker("GC=F").history(period="2d", timeout=2)
    dolar_v = yf.Ticker("TRY=X").history(period="2d", timeout=2)
    
    bist_f = float(bist_v['Close'].iloc[-1]) if len(bist_v)>0 else 0.0
    bist_d = ((bist_f - float(bist_v['Close'].iloc[-2])) / float(bist_v['Close'].iloc[-2])) * 100 if len(bist_v)>=2 else 0.0
    
    ons_f = float(ons_v['Close'].iloc[-1]) if len(ons_v)>0 else 0.0
    usd_try = float(dolar_v['Close'].iloc[-1]) if len(dolar_v)>0 else 34.50
    
    # Gram Altın Hesaplama formülü: (Ons / 31.1034768) * Dolar Kuru
    gram_f = (ons_f / 31.1034768) * usd_try if ons_f>0 else 0.0
    ceyrek_f = gram_f * 1.63 if gram_f>0 else 0.0
    yarim_f = gram_f * 3.26 if gram_f>0 else 0.0
    tam_f = gram_f * 6.52 if gram_f>0 else 0.0
    
    bist_renk = "#00ff66" if bist_d >= 0 else "#ff3344"
    bist_isaret = "▲" if bist_d >= 0 else "▼"
    
    st.markdown(f'''
    <div class="finans-bandi">
        🌐 <b>BIST 100:</b> {bist_f:,.2f} <span style="color:{bist_renk};">{bist_isaret} %{bist_d:.2f}</span> | 
        🟡 <b>Ons Altın:</b> ${ons_f:,.2f} | 
        ✨ <b>Gram Altın:</b> {formatla_tl(gram_f)} | 
        🎯 <b>Çeyrek:</b> {formatla_tl(ceyrek_f)} | 
        📊 <b>Yarım:</b> {formatla_tl(yarim_f)} | 
        👑 <b>Tam Altın:</b> {formatla_tl(tam_f)}
    </div>
    ''', unsafe_allow_html=True)
except:
    st.markdown('<div class="finans-bandi">⏳ Finansal Veri Bandı Yükleniyor...</div>', unsafe_allow_html=True)

# ===================================================================== #
# 2. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUAN 🔢</th><th>BTA HİSSE 📈</th><th>BTA ALIM 📥</th><th>GÜNCEL FİYAT 💥</th><th>KAR / ZARAR 📊</th></tr>'
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
                        kz_str = f'<span class="pozitif-degisim">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span class="negatif-degisim">▼ %{or_dg:.2f}</span>'
                    else: kz_str = "<span>-</span>"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{formatla_tl(maliyet) if maliyet>0 else alim_c}</td><td>{formatla_tl(c_fiyat) if c_fiyat>0 else "Bağlanıyor..."}</td><td>{kz_str}</td></tr>'
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
# 3. HALKA ARZ VE HABER ALANI
# ===================================================================== #
st.write("---")
st.header("🔔 GÜNCEL HALKA ARZLAR VE ANLIK HABERLER")
c_arz, c_hbr = st.columns(2)
with c_arz:
    st.subheader("🚀 Yeni Halka Arz Listesi")
    st.dataframe(pd.DataFrame({"Hisse Kodu 📈": ["XYZEN", "ABCDE"], "Şirket🏢": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum📊": ["Talep Toplama Başladı", "SPK Onay Bekliyor"]}), use_container_width=True, hide_index=True)
with c_hbr:
    st.subheader("📰 Son Dakika Gelişmeler / KAP")
    st.info("🔴 [12:10] XYZEN halka arz sonuçları açıklandı! Hesap başı 15 lot dağıtıldı.")
    st.info("🔴 [11:45] SPK haftalık bülteni yayınlandı: 2 yeni halka arz onayı çıktı.")

st.markdown('<p style="font-size:20px; font-weight:bold; color:#00FF7F;">📈 BTA PANEL İSTATİSTİKLERİ</p>', unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
sc2.metric("📅 Günlük Giriş ", f"{st.session_state['gunluk_sayac']} Giriş")
