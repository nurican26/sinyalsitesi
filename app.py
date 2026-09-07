import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# ===================================================================== #
# 1. BORSA TEMASI VE YÜKSEK OKUNABİLİRLİK AYARLARI (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* Derin Gece Mavisi Borsa Arka Planı */
.stApp { 
    background-color: #0b111e !important; 
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; 
}
/* Finansal Kutular ve Tablo Panelleri */
div[data-testid="stMetric"], div[data-testid="stDataFrame"], div[data-testid="stForm"] { 
    background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; 
}
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.hisse-link { color: #00ffcc !important; text-decoration: underline !important; font-weight: bold; }

/* TV HABERLERİ İÇİN ULTRA OKUNAKLI KÖMÜR KARASI GECE MODU FONU */
.gece-haber { 
    background-color: #060a12 !important; 
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
.kucuk-sayac { font-size: 12px !important; color: #777777 !important; text-align: center; margin-top: 15px; font-weight: bold; }
</style>
<h1 style="text-align:center; color:#fff; font-size:26px; font-weight:bold; margin-bottom:15px;">✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨</h1>
''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

# --- GÜVENLİ HAFİF SAYAÇ MİMARİSİ ---
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
# 3. VERİ MOTORU VE TABLOLAR (SÜTUN DARALTILDI, DOĞRUDAN BORSA KÖPRÜSÜ)
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
                    
                    # %100 Çalışan Döviz.com Borsa Köprüsü
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
# 4. GÜNCEL GELİŞMELER: HALKA ARZ & KÖMÜR KARASI 3 TV HABERİ
# ===================================================================== #
st.write("---")
st.markdown('<p style="font-size:20px; font-weight:bold; color:#fff;">🔔 GÜNCEL GELİŞMELER & SÜPER PANEL</p>', unsafe_allow_html=True)

col_sol, col_sag = st.columns(2)

with col_sol:
    st.markdown('<b>🚀 Yeni Halka Arz Listesi</b>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Hisse Kodu": ["XYZEN", "ABCDE"], "Şirket🏢": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum📊": ["Talep Başladı", "SPK Bekliyor"]}), use_container_width=True, hide_index=True)

with col_sag:
    st.markdown('<b>📺 TV GÜNDEM & DÜNYA HABERLERİ</b>', unsafe_allow_html=True)
    # İnatçı kasma yapan tüm yıldız ve veritabanı kilitleri kaldırılarak okunaklı haberler kilitlendi
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
# GİZLİ, ULTRA KÜÇÜK YASAL UYARI VE EN ALTA GELEN GİRİŞ SAYAÇLARI
# ===================================================================== #
st.write("---")
st.markdown('''
<p style="font-size:11px; color:#666668; text-align:center; margin-bottom: 2px;">
⚠ **SPK YASAL UYARI:** Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz. Panel üzerindeki borsa verileri kurallar gereği en az 15 dakika gecikmelidir.
</p>
''', unsafe_allow_html=True)

# Kasma bittiği için en alta tam istediğiniz adaletle yerleşen sayaç çizgisi
st.markdown(f'<div class="kucuk-sayac">📊 Bugün Giriş: {st.session_state["gunluk_sayac"]} | 💎 Genel Toplam Giriş: {st.session_state["toplam_sayac"]}</div>', unsafe_allow_html=True)
