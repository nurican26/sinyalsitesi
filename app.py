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
</style>
<marquee scrollamount="8"><span style="font-size:45px; font-weight:bold; color:#fff; text-shadow: 0 0 10px #ff0055;">✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨</span></marquee>
''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

# --- REFRESH VE SAYAÇ BAŞLANGICI ---
if "toplam_sayac" not in st.session_state: st.session_state["toplam_sayac"] = 1450
if "gunluk_sayac" not in st.session_state: st.session_state["gunluk_sayac"] = 120
st.session_state["toplam_sayac"] += 1
st.session_state["gunluk_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

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
sc3.metric("💎 Genel ", f"{st.session_state['toplam_sayac']} Giriş")

# ===================================================================== #
# 4. CANLI SOHBET KUTUSU
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:24px; font-weight:bold; color:#FF69B4;">💬 KULLANICI YORUMLARI VE CANLI SOHBET</p>', unsafe_allow_html=True)
if "sohbet_hafizasi" not in st.session_state: st.session_state["sohbet_hafizasi"] = [{"isim": "Ahmet Y.", "saat": "12:15", "yorum": "Algoritma puanlamaları harika."}]

with st.form(key="s_frm", clear_on_submit=True):
    y_is = st.text_input("Adınız:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=100)
    if st.form_submit_button("Mesajı Yayınla 📨", use_container_width=True) and y_is.strip() and y_me.strip():
        if not any(z in y_me.lower() or z in y_is.lower() for z in ["küfür1", "siktir", "piç", "salak"]):
            st.session_state["sohbet_hafizasi"].insert(0, {"isim": y_is.strip(), "saat": datetime.datetime.now().strftime("%H:%M"), "yorum": y_me.strip()})
            st.success("✅ Yayınlandı!")
            time.sleep(0.5)
            st.rerun()
        else: st.error("⚠ Argo kelime engellendi!")

with st.expander("🛠 Yönetici Girişi"):
    if st.text_input("Şifre:", type="password", key="adm") == "bta123": st.success("🔓 Silme yetkisi aktif!")

for s, sh in enumerate(st.session_state["sohbet_hafizasi"]):
    st.markdown(f'<div style="background-color: #121d33; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #FF69B4;"><b>👤 {sh["isim"]}</b> <span style="font-size:11px; color:#aaa; float:right;">⏱ {sh["saat"]}</span><p style="margin-top:6px; color:#fff;">{sh["yorum"]}</p></div>', unsafe_allow_html=True)
