import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. KOTASIZ SABİT ÇİZGİLİ MATRİKS TEMASI VE STİLLER (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* İnternet kotası harcamayan, statik ince çizgili Matriks arka planı */
.stApp { 
    background-color: #040805 !important;
    background-image: 
        linear-gradient(to right, rgba(0, 255, 102, 0.04) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 255, 102, 0.04) 1px, transparent 1px) !important;
    background-size: 25px 25px !important;
}

/* Matriks yeşili paneller ve kutular */
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] { 
    background-color: #09100b !important; 
    border: 1px solid #00aa44 !important; 
    border-radius: 6px !important; 
    padding: 12px !important; 
}

/* Girdiler ve Seçim Alanları */
input, textarea, select { 
    background-color: #020503 !important; 
    color: #00ff66 !important; 
    border: 1px solid #00aa44 !important; 
    border-radius: 4px !important; 
}

/* Matriks Yeşili Butonlar */
.stButton>button { 
    background: linear-gradient(135deg, #050f08 0%, #006622 100%) !important; 
    color: #00ff66 !important; 
    border: 1px solid #00ff66 !important; 
    border-radius: 4px !important; 
    font-weight: bold !important; 
}

/* Borsa Tablosu */
.borsa-tablo { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 10px 0; 
    font-size: 15px; 
    background-color: #09100b; 
    border-radius: 6px; 
    overflow: hidden; 
    border: 1px solid #00aa44;
}
.borsa-tablo th { background-color: #0e1a12; color: #00ff66; text-align: left; padding: 10px 8px; border-bottom: 1px solid #00aa44; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #0e1a12; font-weight: bold; }

.kucuk-sayac { font-size: 14px !important; color: #00ff66 !important; text-align: center; margin-top: 15px; font-weight: bold; }
.kucuk-baslik { font-size: 15px !important; color: #00ff66 !important; font-weight: bold; margin-bottom: 5px; }
</style>

<!-- BTA BAŞLIĞI KAYAN YAZI -->
<marquee behavior="scroll" direction="left" scrollamount="7">
    <h1 style="color:#00ff66; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:15px; display:inline;">BTA</h1>
</marquee>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı ve Fiyatları Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_sohbet_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"

# KALICI SOHBET VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if "topham_sayac" not in st.session_state: st.session_state["topham_sayac"] = 1450
st.session_state["topham_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# 2. CANLI BIST 100 PİYASA ALANI (KUTU BOYUTU KISALTILDI)
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    
    # 4 sütun oluşturup sadece ilkini kullanarak BIST kutusunun uzamasını engelledik
    col_bist, _, _, _ = st.columns(4)
    col_bist.metric("BIST 100", f"{bist_f:,.1f}")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
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
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.1f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.1f}</span>'
                    else: kz_str = "<span>-</span>"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.1f} TL</td><td>{c_fiyat:,.1f} TL</td><td>{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#00ff66;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
                    if len(h_detay_veri) > 0:
                        st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. HALKA ARZLAR (KALDIRILDI)
# ===================================================================== #

# ===================================================================== #
# 5. ORİJİNAL GÜVENLİ SOHBET FORMU
# ===================================================================== #
st.write("---")
st.markdown('<div class="kucuk-baslik">Sohbet</div>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

with st.form(key="s_frm", clear_on_submit=True):
    y_is = st.text_input("Adınız:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=80)
    if st.form_submit_button("Mesajı Yayınla 📨", use_container_width=True) and y_is.strip() and y_me.strip():
        m_kucuk = y_me.lower().replace(" ", "").replace("@", "a").replace("0", "o")
        i_kucuk = y_is.lower().replace(" ", "")
        
        if not any(z in m_kucuk or z in i_kucuk for z in yasakli):
            df_s = pd.read_csv(db_sohbet)
            y_satir = pd.DataFrame([{"isim": y_is.strip(), "saat": datetime.datetime.now().strftime("%H:%M"), "yorum": y_me.strip()}])
            pd.concat([y_satir, df_s], ignore_index=True).to_csv(db_sohbet, index=False)
            st.rerun()
        else:
            st.error("⚠ Argo/Küfür içerikli kelimeler engellendi!")

with st.expander("🛠 Yönetici"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"

# MESAJ LİSTELEME
df_sohbet_oku = pd.read_csv(db_sohbet)
for s in range(len(df_sohbet_oku)):
    sh = df_sohbet_oku.iloc[s]
    st.markdown(f'<div style="background-color: #09100b; padding: 10px; border-radius: 8px; margin-bottom: 6px; border-left: 5px solid #00ff66; border: 1px solid #00aa44;"><b>👤 {sh["isim"]}</b> <span style="font-size:11px; color:#aaa; float:right;">⏱ {sh["saat"]}</span><p style="margin-top:4px; color:#fff;">{sh["yorum"]}</p></div>', unsafe_allow_html=True)
    if adm_mod and st.button(f"Sil ❌ (Sıra: {s+1})", key=f"sl_{s}"):
        df_sl = pd.read_csv(db_sohbet)
        df_sl.drop(s).reset_index(drop=True).to_csv(db_sohbet, index=False)
        st.rerun()

# ===================================================================== #
# SADECE ODADAKİ TOPLAM GİRİŞ SAYISI
# ===================================================================== #
st.write("---")
st.markdown(f'<div class="kucuk-sayac">💎 Odadaki Toplam Giriş Sayısı: {st.session_state["topham_sayac"]}</div>', unsafe_allow_html=True)
