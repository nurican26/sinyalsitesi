import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# ===================================================================== #
# 1. BORSA TEMASI VE OKUNABİLİRLİK OPTİMİZASYONU (CSS)
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
.hisse-link { color: #00ffcc !important; text-decoration: underline !important; font-weight: bold; }
.kucuk-sayac { font-size: 12px !important; color: #888888 !important; text-align: center; margin-top: 15px; font-weight: bold; }

/* TELEFONDA ULTRA OKUNAKLI GECE MODU HABER KUTULARI */
.gece-haber { 
    background-color: #070c16 !important; 
    border-left: 5px solid #ff3344; 
    padding: 12px !important; 
    margin-bottom: 8px !important; 
    border-radius: 6px;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
}
.haber-metni { 
    color: #ffffff !important; 
    font-size: 15px !important; 
    font-weight: bold !important; 
    line-height: 1.5 !important;
}

/* YAN YANA PARLAYAN ŞIK YILDIZ BUTONLARI */
.yildiz-btn>button {
    background: transparent !important;
    border: none !important;
    font-size: 24px !important;
    padding: 0px !important;
    margin: 0px !important;
    box-shadow: none !important;
    transition: transform 0.2s;
}
.yildiz-btn>button:hover { transform: scale(1.3); }
</style>
<h1 style="text-align:center; color:#fff; font-size:26px; font-weight:bold; margin-bottom:15px;">✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨</h1>
''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"
db_yildiz = "bta_yildiz_db.csv"

if not os.path.exists(db_sohbet): pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)
if not os.path.exists(db_yildiz): pd.DataFrame([{"s5": 124, "s4": 18, "s3": 5}]).to_csv(db_yildiz, index=False)

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
    
    pk1, pk2, pk3, pk4 = st.columns(4)
    pk1.metric("✨ GRAM ALTIN", f"{gram_f:,.1f} TL")
    pk2.metric("🎯 ÇEYREK ALTIN", f"{gram_f * 1.63:,.1f} TL")
    pk3.metric("👑 TAM ALTIN", f"{gram_f * 6.52:,.1f} TL")
    pk4.metric("🌐 BIST 100", f"{bist_f:,.1f}")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>PUAN</th><th>HİSSE 🔗</th><th>ALIM</th><th>FİYAT</th><th>K/Z</th></tr>'
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
                    
                    link_url = f"https://doviz.com{ha.lower()}"
                    hisse_kopru = f'<a href="{link_url}" target="_blank" class="hisse-link">🔍 {ha}</a>'
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{hisse_kopru}</td><td>{maliyet:,.1f} TL</td><td>{c_fiyat:,.1f} TL</td><td>{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.write("")
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. GÜNCEL GELİŞMELER: HALKA ARZ & HIGH-CONTRAST OKUNAKLI HABERLER
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:20px; font-weight:bold; color:#fff;">🔔 GÜNCEL GELİŞMELER & SÜPER PANEL</p>', unsafe_allow_html=True)

col_sol, col_sag = st.columns(2)

with col_sol:
    st.markdown('<b>🚀 Yeni Halka Arz Listesi</b>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Hisse Kodu": ["XYZEN", "ABCDE"], "Şirket🏢": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum📊": ["Talep Başladı", "SPK Bekliyor"]}), use_container_width=True, hide_index=True)

with col_sag:
    st.markdown('<b>📺 TV GÜNDEM & DÜNYA HABERLERİ</b>', unsafe_allow_html=True)
    # Tam istediğiniz gibi arka fonu kömür karası, yazıları kalın ve okunaklı yüksek kontrastlı hale getirdim
    st.markdown('''
    <div class="gece-haber">
        <span class="haber-metni"><span style="color:#ff3344;">🔴 [SON DAKİKA]</span> Küresel piyasalarda altın ve döviz hareketliliği yakından takip ediliyor.</span>
    </div>
    <div class="gece-haber" style="border-left-color:#00ff66;">
        <span class="haber-metni"><span style="color:#00ff66;">🟢 [Gündem]</span> İç piyasada borsa endeksleri haftaya dengeli bir seyirle başladı.</span>
    </div>
    <div class="gece-haber" style="border-left-color:#00bfff;">
        <span class="haber-metni"><span style="color:#00bfff;">🔵 [Dünya]</span> Ekonomi yönetiminden makro ekonomik verilere dair yeni açıklamalar geldi.</span>
    </div>
    ''', unsafe_allow_html=True)

# ===================================================================== #
# 5. CANLI SOHBET KUTUSU (GÖRSEL SARI ALTIN YILDIZ ENTEGRESİ)
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:22px; font-weight:bold; color:#FF69B4;">💬 KULLANICI YORUMLARI VE CANLI SOHBET</p>', unsafe_allow_html=True)

df_y = pd.read_csv(db_yildiz)
st.write("**Paneli Puanlayın (Altın Yıldızlar):**")

# Yan yana dizilmiş 5 parıl parıl parlayan altın yıldız simgeleri
y_col1, y_col2, y_col3, y_col4, y_col5 = st.columns([1,1,1,1,1])
with y_col1:
    st.markdown('<div class="yildiz-btn">', unsafe_allow_html=True)
    if st.button(f"⭐ ({df_y.loc[0, 's5']})", key="star5"):
        df_y.loc[0, "s5"] += 1
        df_y.to_csv(db_yildiz, index=False)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with y_col2:
    st.markdown('<div class="yildiz-btn">', unsafe_allow_html=True)
    if st.button(f"⭐ ({df_y.loc[0, 's4']})", key="star4"):
        df_y.loc[0, "s4"] += 1
        df_y.to_csv(db_yildiz, index=False)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with y_col3:
    st.markdown('<div class="yildiz-btn">', unsafe_allow_html=True)
    if st.button(f"⭐ ({df_y.loc[0, 's3']})", key="star3"):
        df_y.loc[0, "s3"] += 1
        df_y.to_csv(db_yildiz, index=False)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with y_col4:
    st.markdown('<div class="yildiz-btn">', unsafe_allow_html=True)
    if st.button("⭐", key="star2"): st.toast("Geri bildiriminiz için teşekkürler!")
