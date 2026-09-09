import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.oda-sayici { background: linear-gradient(90deg, #1e3a5f 0%, #121d33 100%); color: #00ffcc; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; border: 1px solid #00ffcc; margin-bottom: 15px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:'Brush Script MT', cursive, sans-serif; font-size:50px; margin-bottom:5px;">BTA</h1>
''', unsafe_allow_html=True)

st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=2)['Close'].iloc[-1])
usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
gram_f = (ons_f / 31.1034768) * usd_f

pk1, pk2, pk3, col_bist, col_eur = st.columns(5)
pk1.metric("GRAM ALTIN", f"{gram_f:,.2f} TL")
pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.2f} TL")
pk3.metric("YARIM ALTIN", f"{gram_f * 3.26:,.2f} TL")
col_bist.metric("BIST 100", f"{bist_f:,.2f}")
col_eur.metric("EURO", f"{eur_f:,.2f} TL")

st.write("---")
tum_hisseler = [] 
veri_var_mi = False

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: 
            st.markdown(tablo_html, unsafe_allow_html=True)
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 4].dropna().unique()
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() != ""])
    except:
        pass
else:
    st.error("Excel bulunamadı.")

st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
if len(tum_hisseler) > 0:
    aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler, key="arama_motoru_select")
    if aranan_hisse != "Seçiniz...":
        try:
            h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
            if len(h_detay_veri) > 0:
                st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
        except:
            pass

st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#00ffcc;">🗒️Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti, aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır.Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir </p>', unsafe_allow_html=True)
col_not1, col_not2 = st.columns(2)

with col_not1:
    st.markdown('<p style="font-size:14px; font-weight:bold; color:#fff;">Yeni Not Ekle</p>', unsafe_allow_html=True)
    not_hisse_secim = st.selectbox("Not Alınacak Hisse", ["Manuel Gir..."] + tum_hisseler if tum_hisseler else ["Manuel Gir..."], key="not_hisse_v_sec")
    if not_hisse_secim == "Manuel Gir...":
        not_hisse = st.text_input("Hisse Kodu (Örn: THYAO):", max_chars=10, key="not_manuel_hisse_kod").strip().upper()
    else:
        not_hisse = not_hisse_secim
    not_hedef_fiyat = st.number_input("Hedef Fiyat (TL - Alarm için):", min_value=0.0, value=0.0, step=1.0, key="not_hedef_fiyat_input")
    hisse_notu = st.text_area("Hisse Hakkındaki Notunuz:", max_chars=500, placeholder="Stratejinizi yazın...", key="hisse_notu_metni")
    if st.button("Notu Kaydet 💾", use_container_width=True, key="notu_kaydet_butonu"):
        if not_hisse and hisse_notu.strip():
            try:
                df_notlar = pd.read_csv(db_notlar)
                yeni_id = str(int(time.time() * 1000))
                su_an_tarih = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                yeni_not_veri = pd.DataFrame([[yeni_id, su_an_tarih, str(not_hisse), str(hisse_notu.strip()), float(not_hedef_fiyat)]], columns=["id", "tarih", "hisse", "not", "hedef_fiyat"])
                df_notlar = pd.concat([df_notlar, yeni_not_veri], ignore_index=True)
                df_notlar.to_csv(db_notlar, index=False)
                st.success(f"Not kaydedildi! ({not_hisse})")
                time.sleep(0.5)
                st.rerun()
            except:
                pass

with col_not2:
    st.markdown('<div style="color:#fff; font-size:14px; font-weight:bold;">Odadaki Tüm Kayıtlı Notlar</div>', unsafe_allow_html=True)
    
    admin_yetkisi = False
    admin_paneli = st.checkbox("Yönetici Modu (Not Silme)")
    if admin_paneli:
        sifre_kontrol = st.text_input("Yönetici Şifresi:", type="password", key="admin_master_sifre")
        if sifre_kontrol == "bta123":
            admin_yetkisi = True
            st.success("Silme yetkisi aktif!")
        elif sifre_kontrol != "":
            st.error("Hatalı Şifre!")

    if os.path.exists(db_notlar):
        try:
            df_notlar_oku = pd.read_csv(db_notlar)
            if not df_notlar_oku.empty:
                df_notlar_oku = df_notlar_oku.iloc[::-1]
                for index, row in df_notlar_oku.iterrows():
                    not_id = str(row["id"])
                    hisse_adi = str(row["hisse"])
                    hedef_f = float(row["hedef_fiyat"]) if "hedef_fiyat" in row and pd.notna(row["hedef_fiyat"]) else 0.0
                    try:
                        canli_h_veri = yf.Ticker(f"{hisse_adi}.IS").history(period="1d", timeout=1)
                        not_anlik_fiyat = float(canli_h_veri['Close'].iloc[-1]) if len(canli_h_veri) > 0 else 0.0
                    except:
                        not_anlik_fiyat = 0.0
                    
                    alarm_durumu = ""
                    if hedef_f > 0.0 and not_anlik_fiyat > 0.0:
                        if not_anlik_fiyat >= hedef_f:
                            alarm_durumu = " 🟢 HEDEF GÖRÜLDÜ"
                        else:
                            alarm_durumu = f" ⏳ Hedef Bekleniyor ({hedef_f:.2f} TL)"
                    
                    fiyat_metni = f" | Anlık: {not_anlik_fiyat:.2f} TL" if not_anlik_fiyat > 0 else ""
                    baslik = f"📌 {hisse_adi}{fiyat_metni}{alarm_durumu}"
                    
                    with st.expander(baslik):
                        st.info(row["not"])
                        if admin_yetkisi:
