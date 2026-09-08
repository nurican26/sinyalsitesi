import streamlit as st
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. KOTA DOSTU SADE TASARIM VE RENK AYARLARI
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 16px; background-color: #121d33; border-radius: 8px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 12px 10px; font-weight: bold; }
.borsa-tablo td { padding: 12px 10px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:40px; margin-bottom:15px;">BTA ANALİZ MERKEZİ</h1>
''', unsafe_allow_html=True)

# Ekranı 10 saniyede bir yenileyen hafif saat motoru
st_autorefresh(interval=10 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"

# ===================================================================== #
# 2. CANLI BORSA TABLOSU (SADECE WEB SAYFASINDAKİ SÜZÜLMÜŞ HİSSELER)
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        veri_var_mi = False
        
        for idx in range(len(df)):
            try:
                puan_d = df.iloc[idx, 0]    # A Sütunu: BTA Puanı
                ha = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""  # B Sütunu: Hisse Adı
                algo_f = df.iloc[idx, 2]    # C Sütunu: Algoritmik Fiyat
                canli_f = df.iloc[idx, 3]   # D Sütunu: Canlı Fiyat
                kz_orani = df.iloc[idx, 4]  # E Sütunu: K/Z Oranı
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "HİSSE ADI", "HİSSE ADI "]:
                    veri_var_mi = True
                    
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    maliyet_str = f"{float(algo_f):,.1f} TL" if isinstance(algo_f, (int, float)) else str(algo_f).strip()
                    canli_str = f"{float(canli_f):,.1f} TL" if isinstance(canli_f, (int, float)) else str(canli_f).strip()
                    
                    kz_metin = str(kz_orani).strip()
                    if "▼" in kz_metin or "-" in kz_metin:
                        kz_str = f'<span style="color:#ff3344;">{kz_metin}</span>'
                    elif "▲" in kz_metin or "%" in kz_metin:
                        kz_str = f'<span style="color:#00ff66;">{kz_metin}</span>'
                    else:
                        kz_str = f'<span>{kz_metin}</span>'
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet_str}</td><td>{canli_str}</td><td>{kz_str}</td></tr>'
            except:
                continue
            
        tablo_html += '</table>'
        
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#1E90FF; margin-top:20px;">📈 BTA ALGORİTMİK HİSSE LİSTESİ</p>', unsafe_allow_html=True)
        if veri_var_mi: 
            st.markdown(tablo_html, unsafe_allow_html=True)
        else:
            st.info("⏳ WEB Sayfasında Gösterilecek Hisse Verisi Bulunamadı...")
            
    except Exception as e: 
        st.error(f"Veri okunurken bir hata oluştu: {e}")
else: 
    st.error("Excel veritabanı bulunamadı. Lütfen nurican.xls.xlsm dosyasını yükleyin.")
