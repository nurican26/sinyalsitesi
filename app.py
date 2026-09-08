import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import uuid
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. BORSA TEMASI VE STİLLER (CSS - OKUNAKLI & KÜÇÜK)
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
.kucuk-sayac { font-size: 14px !important; color: #00ffcc !important; text-align: center; margin-top: 15px; font-weight: bold; }
.kucuk-baslik { font-size: 15px !important; color: #ffffff !important; font-weight: bold; margin-bottom: 5px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:15px;">BTA</h1>
''', unsafe_allow_html=True)

# Otomatik Yenileme Motoru (5 Saniyede Bir Ekranı ve Fiyatları Tazeler)
st_autorefresh(interval=5 * 1000, key="bta_sohbet_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"
db_aktifler = "bta_aktif_kullanicilar.csv"

# KALICI SOHBET VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if "topham_sayac" not in st.session_state: st.session_state["topham_sayac"] = 1450
st.session_state["topham_sayac"] += 1

# ANLIK ODA KULLANICI TAKİP MOTORU
if "cihaz_id" not in st.session_state:
    st.session_state["cihaz_id"] = str(uuid.uuid4())

simdi = datetime.datetime.now()
try:
    if os.path.exists(db_aktifler):
        df_akt = pd.read_csv(db_aktifler)
        df_akt["zaman"] = pd.to_datetime(df_akt["zaman"])
        df_akt = df_akt[df_akt["zaman"] > (simdi - datetime.timedelta(seconds=15))]
    else:
        df_akt = pd.DataFrame(columns=["id", "zaman"])
except:
    df_akt = pd.DataFrame(columns=["id", "zaman"])

df_akt = df_akt[df_akt["id"] != st.session_state["cihaz_id"]]
yeni_aktif = pd.DataFrame([{"id": st.session_state["cihaz_id"], "zaman": simdi}])
df_akt = pd.concat([df_akt, yeni_aktif], ignore_index=True)
df_akt.to_csv(db_aktifler, index=False)

gercek_kisi_sayisi = len(df_akt)

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# 2. CANLI ALTIN VE BIST 100 PİYASA ALANI (SABİTLENMİŞ GÖSTERGELER)
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=2)['Close'].iloc[-1])
    usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    gram_f = (ons_f / 31.1034768) * usd_f
    
    pk1, pk2, pk3, col_bist, col_eur = st.columns(5)
    pk1.metric("GRAM ALTIN", f"{gram_f:,.1f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.1f} TL")
    pk3.metric("YARIM ALTIN", f"{gram_f * 3.26:,.1f} TL")
    col_bist.metric("BIST 100", f"{bist_f:,.1f}")
    col_eur.metric("EURO", f"{eur_f:,.2f} TL")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
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
# 4. GÜVENLİ SOHBET FORMU VE YEREL SES SİNYALİ (GARANTİLİ SES)
# ===================================================================== #
st.write("---")

st.markdown(f'<div class="kucuk-baslik">Sohbet (<span style="color:#00ffcc;">Odadaki Kişi: {gercek_kisi_sayisi}</span>)</div>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

garantili_bip_html = """
<script>
    (function() {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        var gain = context.createGain();
        osc.connect(gain);
        gain.connect(context.destination);
        osc.type = 'sine';
        osc.frequency.value = 830;
        gain.gain.setValueAtTime(0.1, context.currentTime);
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, context.currentTime + 0.15);
        osc.stop(context.currentTime + 0.16);
    })();
</script>
"""

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

# MESAJ LİSTELEME VE KONTROL MOTORU
df_sohbet_oku = pd.read_csv(db_sohbet)

if "son_mesaj_sayisi" not in st.session_state:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

if len(df_sohbet_oku) > st.session_state["son_mesaj_sayisi"]:
    st.components.v1.html(garantili_bip_html, height=0, width=0)
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)
