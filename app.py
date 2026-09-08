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

# Sitenin kotasını harcamadan ekranı 10 saniyede bir otomatik yenileyen motor
st_autorefresh(interval=10 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"

# ===================================================================== #
# 2. CANLI BORSA TABLOSU (SADECE "WEB" SAYFASI - B SÜTUNU GİZLİ)
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        # Nokta atışı olarak tam senin o yeşil "WEB" sekmesini içeri yüklüyoruz
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # B sütununu sildiğimiz için yeni başlıklarımız: BTA HİSSE, BTA ALIM FİYATI, BTA PUANI
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA HİSSE</th><th>BTA ALGORİTMİK FİYAT</th><th>BTA PUANI</th></tr>'
        veri_var_mi = False
        
        # Sizin "WEB" sayfanızın satırlarını baştan aşağıya tarıyoruz
        for idx in range(len(df)):
            try:
                # Sütun endeksleri (Python 0'dan başlar):
                # A sütunu (0): BTA HİSSE
                # B sütunu (1): BTA AL SAT ➡️ (GÖSTERMİYORUZ!)
                # C sütunu (2): BTA ALIM FİYATI
                # D sütunu (3): BTA PUANI
                
                hisse_adi = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_fiyati = df.iloc[idx, 2]
                bta_puani = df.iloc[idx, 3]
                
                # Başlıkları ve boş satırları süzüp sadece gerçek hisseyi alıyoruz
                if hisse_adi != "" and hisse_adi not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "HİSSE ADI", "HİSSE ADI "]:
                    veri_var_mi = True
                    
                    # Verileri ekranda pürüzsüz gösterecek metin nizamları
                    fiyat_temiz = f"{float(alim_fiyati):,.2f} TL" if isinstance(alim_fiyati, (int, float)) else str(alim_fiyati).strip()
                    puan_temiz = f"{float(bta_puani):.2f}" if isinstance(bta_puani, (int, float)) else str(bta_puani).strip()
                    
                    # Tablo satırına ekliyoruz (B sütunu olan BTA AL SAT tamamen dışarıda bırakıldı)
                    tablo_html += f'<tr><td>{hisse_adi}</td><td>{fiyat_temiz}</td><td>{puan_temiz}</td></tr>'
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
