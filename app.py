import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. BORSA TEMASI VE STİLLER (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.kucuk-sayac { font-size: 11px !important; color: #666668 !important; text-align: center; margin-top: 15px; font-weight: bold; }

/* SİNYAL RADARI VE EKONOMİK TAKVİM TASARIMLARI */
.sinyal-kutusu { padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; margin-top: 10px; margin-bottom: 15px; }
.sinyal-al { background-color: #004d26 !important; color: #00ff66 !important; border: 1px solid #00ff66; }
.sinyal-guv-al { background-color: #1a4d00 !important; color: #ccff00 !important; border: 1px solid #ccff00; }
.sinyal-notr { background-color: #4d3d00 !important; color: #ffcc00 !important; border: 1px solid #ffcc00; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:15px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı ve Fiyatları Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_sohbet_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"

# KALICI SOHBET VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if "topham_sayac" not in st.session_state: st.session_state["topham_sayac"] = 1450
if "gunluk_sayac" not in st.session_state: st.session_state["gunluk_sayac"] = 120
st.session_state["topham_sayac"] += 1
st.session_state["gunluk_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# 2. CANLI ALTIN VE BIST 100 PİYASA ALANI
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=2)['Close'].iloc[-1])
    usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    gram_f = (ons_f / 31.1034768) * usd_f
    
    pk1, pk2, pk3, col_bist = st.columns(4)
    pk1.metric("GRAM ALTIN", f"{gram_f:,.1f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.1f} TL")
    pk3.metric("YARIM ALTIN", f"{gram_f * 3.26:,.1f} TL")
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
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU (GRAFIK YERINE CANLI SINYAL VE FAİZ PANELİ GELDİ) ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="5d", timeout=2)
                    if len(h_detay_veri) > 0:
                        anlik_f_arama = float(h_detay_veri['Close'].iloc[-1])
                        st.metric("Güncel Fiyat", f"{anlik_f_arama:,.2f} TL")
                        
                        # 1. SEÇENEK: CANLI AL-SAT SİNYAL RADARI ENTEGRASYONU
                        try:
                            dunku_f_arama = float(h_detay_veri['Close'].iloc[-2])
                            oran_f_arama = ((anlik_f_arama - dunku_f_arama) / dunku_f_arama) * 100
                            if oran_f_arama > 1.5:
                                st.markdown('<div class="sinyal-kutusu sinyal-al">🚨 ALGORİTMA SİNYALİ: GÜÇLÜ AL ▲</div>', unsafe_allow_html=True)
                            elif oran_f_arama >= 0:
                                st.markdown('<div class="sinyal-kutusu sinyal-guv-al">🚨 ALGORİTMA SİNYALİ: KADEMELİ AL ▲</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="sinyal-kutusu sinyal-notr">🚨 ALGORİTMA SİNYALİ: NÖTR / İZLE ⏳</div>', unsafe_allow_html=True)
                        except:
                            st.markdown('<div class="sinyal-kutusu sinyal-notr">🚨 ALGORİTMA SİNYALİ: HESAPLANIYOR...</div>', unsafe_allow_html=True)
                        
                        # 3. SEÇENEK: MERKEZ BANKASI FAİZ & DÖVİZ TAKVİM PANELİ
                        st.write("")
                        st.markdown('<b>🏛️ CANLI EKONOMİK GÖSTERGELER PANELİ</b>', unsafe_allow_html=True)
                        f_col1, f_col2, f_col3 = st.columns(3)
                        f_col1.metric("🏛️ TCMB Politika Faizi", "%50,00")
                        f_col2.metric("💵 Canlı Dolar Kuru", f"{usd_f:,.2f} TL")
                        f_col3.metric("💶 Canlı Euro Kuru", f"{eur_f:,.2f} TL")
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. HALKA ARZLAR
# ===================================================================== #
st.write("---")
st.header("🔔 GÜNCEL HALKA ARZLAR SÜPER PANELİ")
st.dataframe(pd.DataFrame({"Hisse Kodu": ["XYZEN", "ABCDE"], "Şirket🏢": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum📊": ["Talep Toplama Başladı", "SPK Onay Bekliyor"]}), use_container_width=True, hide_index=True)

# ===================================================================== #
# 5. ORİJİNAL GÜVENLİ SOHBET FORMU (HİÇ DOKUNULMADI)
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:22px; font-weight:bold; color:#FF69B4;">💬 KULLANICI YORUMLARI VE CANLI SOHBET</p>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

with st.form(key="s_frm", clear_on_submit=True):
    y_is = st.text_input("Adınız:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=80)
