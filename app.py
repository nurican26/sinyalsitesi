import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. MİNİMALİST VE SADE BORSA TEMASI (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* Arka plan tamamen düz ve koyu yapıldı, geçişler kaldırıldı */
.stApp { 
    background-color: #0d1117 !important; 
}

/* Metrik kutuları ve form alanları sade, ince gri çerçeveli yapıldı */
div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] { 
    background-color: #161b22 !important; 
    border: 1px solid #30363d !important; 
    border-radius: 6px !important; 
    padding: 12px !important; 
}

/* Girdi alanları sadeleştirildi */
input, textarea, select { 
    background-color: #0d1117 !important; 
    color: #c9d1d9 !important; 
    border: 1px solid #30363d !important; 
    border-radius: 6px !important; 
}

/* Buton renkleri düz ve koyu tona çekildi, parlama kaldırıldı */
.stButton>button { 
    background: #21262d !important; 
    color: #c9d1d9 !important; 
    border: 1px solid #30363d !important; 
    border-radius: 6px !important; 
    font-weight: bold !important; 
}
.stButton>button:hover {
    border: 1px solid #58a6ff !important;
    color: #58a6ff !important;
}

/* Sade kurumsal borsa tablosu */
.borsa-tablo { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 10px 0; 
    font-size: 14px; 
    background-color: #161b22; 
    border-radius: 6px; 
    overflow: hidden; 
}
.borsa-tablo th { background-color: #21262d; color: #8b949e; text-align: left; padding: 10px 8px; border-bottom: 1px solid #30363d; }
.borsa-tablo td { padding: 10px 8px; color: #c9d1d9; border-bottom: 1px solid #30363d; font-weight: normal; }

.kucuk-sayac { font-size: 13px !important; color: #8b949e !important; text-align: center; margin-top: 15px; }
.kucuk-baslik { font-size: 15px !important; color: #c9d1d9 !important; font-weight: bold; margin-bottom: 5px; }
</style>

<!-- Kayan yazı kaldırıldı, yerine çok sade bir düz başlık eklendi -->
<h1 style="color:#c9d1d9; font-family:sans-serif; font-size:32px; font-weight:600; margin-bottom:20px; letter-spacing:1px;">BTA MERKEZ</h1>
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

# Arka planda diğer kullanıcılara ses çalabilmesi için mesaj takip sistemi
if "eski_mesaj_sayisi" not in st.session_state:
    try: 
        st.session_state["eski_mesaj_sayisi"] = len(pd.read_csv(db_sohbet))
    except: 
        st.session_state["eski_mesaj_sayisi"] = 0

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# 2. CANLI BIST 100 PİYASA ALANI
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    eur_f = float(yf.Ticker("EURTRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    
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
                        kz_str = f'<span style="color:#2ea043;">▲ %{or_dg:.1f}</span>' if or_dg >= 0 else f'<span style="color:#f85149;">▼ %{or_dg:.1f}</span>'
                    else: kz_str = "<span>-</span>"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.1f} TL</td><td>{c_fiyat:,.1f} TL</td><td>{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.markdown('<p style="font-size:16px; font-weight:bold; color:#c9d1d9;">📈 Algoritmik Hisse Listesi</p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:16px; font-weight:bold; color:#c9d1d9; margin-top:20px;">🔍 BIST Hisse Arama Motoru</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
                    if len(h_detay_veri) > 0:
                        st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
                        
                        st.write("")
                        st.markdown('<b style="color:#c9d1d9;">🏛️ Ekonomik Göstergeler</b>', unsafe_allow_html=True)
                        f_col1, f_col2 = st.columns(2)
                        f_col1.metric("TCMB Politika Faizi", "%50,00")
                        f_col2.metric("Euro Kuru", f"{eur_f:,.2f} TL")
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 5. SADE SOHBET FORMU VE BİP SES MOTORU
# ===================================================================== #
st.write("---")
st.markdown('<div class="kucuk-baslik">Sohbet</div>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

# Net ve kısa bildirim bip sesi linki
ses_url = "https://mixkit.co"

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
            
            # Mesajı gönderen kişi için sesi çal
            st.markdown(f'<audio autoplay><source src="{ses_url}" type="audio/wav"></audio>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error("⚠ Argo/Küfür içerikli kelimeler engellendi!")

with st.expander("🛠 Yönetici"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"

# MESAJ LİSTELEME VE SAYFADAKİ DİĞER KULLANICILAR İÇİN SES KONTROLÜ
try:
    df_sohbet_oku = pd.read_csv(db_sohbet)
    guncel_mesaj_sayisi = len(df_sohbet_oku)
    
    # 5 saniyelik otomatik yenilemede yeni bir mesaj geldiyse odadaki herkes için ses çalar
    if guncel_mesaj_sayisi > st.session_state["eski_mesaj_sayisi"]:
        st.markdown(f'<audio autoplay><source src="{ses_url}" type="audio/wav"></audio>', unsafe_allow_html=True)
        st.session_state["eski_mesaj_sayisi"] = guncel_mesaj_sayisi

    for s in range(guncel_mesaj_sayisi):
        sh = df_sohbet_oku.iloc[s]
        st.markdown(f'<div style="background-color: #161b22; padding: 10px; border-radius: 6px; margin-bottom: 6px; border: 1px solid #30363d; border-left: 4px solid #8b949e;"><b>👤 {sh["isim"]}</b> <span style="font-size:11px; color:#8b949e; float:right;">⏱ {sh["saat"]}</span><p style="margin-top:4px; color:#c9d1d9; font-weight:normal;">{sh["yorum"]}</p></div>', unsafe_allow_html=True)
        
        # Hatalı boşluk bırakılan if satırı ve altındaki işlemler düzeltildi
        if adm_mod and st.button(f"Sil ❌ (Sıra: {s+1})", key=f"sl_{s}"):
