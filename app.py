import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

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
</style>
<marquee scrollamount="6"><span style="font-size:35px; font-weight:bold; color:#fff; text-shadow: 0 0 10px #ff0055;">✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨</span></marquee>
''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"
db_yildiz = "bta_yildiz_db.csv"

# KALICI SOHBET VE YILDIZ VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)
if not os.path.exists(db_yildiz):
    pd.DataFrame([{"s5": 124, "s4": 18, "s3": 5}]).to_csv(db_yildiz, index=False)

if "toplam_sayac" not in st.session_state: st.session_state["toplam_sayac"] = 1450
if "gunluk_sayac" not in st.session_state: st.session_state["gunluk_sayac"] = 120
st.session_state["toplam_sayac"] += 1
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
    gram_f = (ons_f / 31.1034768) * usd_f
    
    pk1, pk2, col_bist = st.columns(3)
    pk1.metric("✨ GRAM ALTIN", f"{gram_f:,.1f} TL")
    pk2.metric("🎯 ÇEYREK ALTIN", f"{gram_f * 1.63:,.1f} TL")
    col_bist.metric("🌐 BIST 100", f"{bist_f:,.1f}")
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
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="30d", timeout=2)
                    if len(h_detay_veri) > 0:
                        st.metric("Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
                        st.line_chart(h_detay_veri['Close'], use_container_width=True)
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. HALKA ARZLAR VE HABERLER
# ===================================================================== #
st.write("---")
st.header("🔔 GÜNCEL HALKA ARZLAR VE ANLIK HABERLER")
st.dataframe(pd.DataFrame({"Hisse Kodu": ["XYZEN", "ABCDE"], "Şirket🏢": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum📊": ["Talep Toplama Başladı", "SPK Onay Bekliyor"]}), use_container_width=True, hide_index=True)

st.subheader("📰 Son Dakika Gelişmeler / KAP")
st.info("🔴 [12:10] XYZEN halka arz sonuçları açıklandı! Hesap başı 15 lot dağıtıldı.")
st.info("🔴 [11:45] SPK haftalık bülteni yayınlandı: 2 yeni halka arz onayı çıktı.")

st.write("---")
st.markdown('<p style="font-size:22px; font-weight:bold; color:#FF69B4;">💬 KULLANICI YORUMLARI VE CANLI SOHBET</p>', unsafe_allow_html=True)

# GÜNCEL YILDIZ VERİSİNİ OKUMA VE GÜNCELLEME
df_y = pd.read_csv(db_yildiz)
st.write("**Paneli Puanlayın:**")
b1, b2, b3 = st.columns(3)
if b1.button(f"🤩 5 Yıldız ({df_y.loc[0, 's5']})", key="b5"):
    df_y.loc[0, "s5"] += 1
    df_y.to_csv(db_yildiz, index=False)
    st.rerun()
if b2.button(f"🙂 4 Yıldız ({df_y.loc[0, 's4']})", key="b4"):
    df_y.loc[0, "s4"] += 1
    df_y.to_csv(db_yildiz, index=False)
    st.rerun()
if b3.button(f"😐 3 Yıldız ({df_y.loc[0, 's3']})", key="b3"):
    df_y.loc[0, "s3"] += 1
    df_y.to_csv(db_yildiz, index=False)
    st.rerun()

st.write("---")

# GENİŞLETİLMİŞ ARGO VE KÜFÜR ENGELLEME LİSTESİ
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
            st.error("⚠ Argo/Küfür içerikli kelimeler topluluk kuralları gereği engellendi!")

with st.expander("🛠 Yönetici"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"

# MESAJLARI KALICI VERİTABANINDAN ÇEKİP LİSTELEME
df_sohbet_oku = pd.read_csv(db_sohbet)
for s in range(len(df_sohbet_oku)):
    sh = df_sohbet_oku.iloc[s]
    st.markdown(f'<div style="background-color: #121d33; padding: 10px; border-radius: 8px; margin-bottom: 6px; border-left: 5px solid #FF69B4;"><b>👤 {sh["isim"]}</b> <span style="font-size:11px; color:#aaa; float:right;">⏱ {sh["saat"]}</span><p style="margin-top:4px; color:#fff;">{sh["yorum"]}</p></div>', unsafe_allow_html=True)
    if adm_mod and st.button(f"Sil ❌ (Sıra: {s+1})", key=f"sl_{s}"):
        df_sl = pd.read_csv(db_sohbet)
        df_sl.drop(s).reset_index(drop=True).to_csv(db_sohbet, index=False)
        st.rerun()
