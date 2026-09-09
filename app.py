import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. KOTA DOSTU TASARIM VE KORUNAKLI KARANLIK TEMA (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* Ön plan elemanlarını kapatmayan, göze hitap eden karanlık borsa teması */
.stApp { 
    background-color: #050b14 !important; 
    background-image: radial-gradient(at 0% 0%, rgba(0, 255, 204, 0.12) 0px, transparent 45%), 
                      radial-gradient(at 100% 0%, rgba(30, 144, 255, 0.1) 0px, transparent 40%) !important;
    background-attachment: fixed !important;
}

/* Kutu tasarımları ve görünürlük ayarları */
div[data-testid="stMetric"], div[data-testid="stExpander"] { 
    background-color: #0c1524 !important; 
    border: 1px solid #1e3a5f !important; 
    border-radius: 8px !important; 
    padding: 10px !important; 
}
input, textarea, select { 
    background-color: #060b12 !important; 
    color: #00ffcc !important; 
    border: 1px solid #1e3a5f !important; 
    border-radius: 6px !important; 
}
.stButton>button { 
    background: #0d9488 !important; 
    color: #fff !important; 
    border: 1px solid #00ffcc !important; 
    border-radius: 6px !important; 
    font-weight: bold !important; 
}

/* Borsa Tablosu Düzenlemeleri */
.borsa-tablo { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 10px 0; 
    font-size: 14px; 
    background-color: #0c1524; 
    border-radius: 8px; 
    overflow: hidden; 
    border: 1px solid #1e3a5f;
}
.borsa-tablo th { 
    background-color: #16243a; 
    color: #00ffcc; 
    text-align: left; padding: 8px; 
}
.borsa-tablo td { 
    padding: 8px; 
    color: #ffffff; 
    border-bottom: 1px solid #16243a; 
    font-weight: bold; 
}

/* Mesaj ve SPK Alanı */
.mesaj-kutusu { 
    background-color: #060b12; 
    border: 1px solid #1e3a5f; 
    padding: 8px; 
    border-radius: 6px; 
    max-height: 180px; 
    overflow-y: auto; 
    font-family: monospace; 
    font-size: 12px; 
    margin-bottom: 10px; 
}
.spk-uyari-alani { 
    background-color: rgba(255, 51, 68, 0.05); 
    border: 1px dashed #ff3344; 
    padding: 12px; 
    border-radius: 8px; 
    margin-top: 30px; 
    font-size: 11px; 
    color: #cccccc; 
    text-align: justify; 
    line-height: 1.4; 
    display: block !important; 
    clear: both !important; 
}

div[data-testid="stForm"] { border: none !important; padding: 0 !important; margin: 0 !important; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:36px; margin-bottom:10px;">BTA MERKEZ</h1>
''', unsafe_allow_html=True)

# Otomatik yenileme motoru (Kota tasarrufu için 30 saniye)
st_autorefresh(interval=30 * 1000, key="bta_kota_dostu_motor")

excel_yolu = "nurican.xls.xlsm"
db_mesajlar = "bta_hafif_mesaj_panosu.csv"

# Mesaj veritabanını başlat
if not os.path.exists(db_mesajlar):
    pd.DataFrame(columns=["zaman", "rumuz", "mesaj"]).to_csv(db_mesajlar, index=False)

# --- GELİŞMİŞ TÜRKÇE KARAKTER DUYARLI SANSÜR FONKSİYONU ---
def mesajı_sansurle(metin):
    kara_liste = [
        "serefsiz", "şerefsiz", "amk", "aq", "sik", "piç", "pic", "orospu", "göt", "got", 
        "yarrak", "amcık", "amcik", "siktir", "pezevenk", "kahpe", "yavşak", "yavsak"
    ]
    orijinal_metin = metin
    kucuk_metin = metin.replace('İ', 'i').replace('I', 'ı').replace('Ş', 'ş').replace('Ç', 'ç').replace('Ğ', 'ğ').replace('Ü', 'ü').replace('Ö', 'ö').lower()
    
    for kufur in kara_liste:
        if kufur in kucuk_metin:
            start_idx = 0
            while True:
                start_idx = kucuk_metin.find(kufur, start_idx)
                if start_idx == -1:
                    break
                uzunluk = len(kufur)
                orijinal_metin = orijinal_metin[:start_idx] + ("*" * uzunluk) + orijinal_metin[start_idx + uzunluk:]
                kucuk_metin = kucuk_metin[:start_idx] + ("*" * uzunluk) + kucuk_metin[start_idx + uzunluk:]
                start_idx += uzunluk
                
    return orijinal_metin

# ===================================================================== #
# RUMUZ GİRİŞ SİSTEMİ (ENTER DESTEKLİ FORM)
# ===================================================================== #
if "bta_rumuz" not in st.session_state:
    st.markdown("<h3 style='text-align:center; color:#fff;'>Giriş Yapın</h3>", unsafe_allow_html=True)
    with st.form("giris_formu", clear_on_submit=False):
        giriş_rumuz = st.text_input("Rumuz (Ad):", max_chars=15, key="rumuz_input")
        giriş_butonu = st.form_submit_button("Bağlan 🚀", use_container_width=True)
        if giriş_butonu and giriş_rumuz.strip():
            st.session_state["bta_rumuz"] = giriş_rumuz.strip().upper()
            st.rerun()
    st.stop()

# Üst Bilgi Satırı
st.write(f"👤 Aktif Kullanıcı: **{st.session_state['bta_rumuz']}** | 🕒 30sn Otomatik Yenileme Aktif")

# İki Kolonlu Ana Düzen
col_sol, col_sag = st.columns(2)

# ===================================================================== #
# SOL TARAF: HİSSELERİM VE ARAMA MOTORU
# ===================================================================== #
with col_sol:
    st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF; margin-bottom:2px;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
    
    if os.path.exists(excel_yolu):
        try:
            df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
            
            tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th></tr>'
            veri_var_mi = False
            
            for idx in range(min(15, len(df))):
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    fiyat_str = alim_c if "TL" in alim_c else f"{alim_c} TL"
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{fiyat_str}</td></tr>'
            
            tablo_html += '</table>'
            
            if veri_var_mi:
                st.markdown(tablo_html, unsafe_allow_html=True)
            else:
                st.info("Gösterilecek uygun hisse verisi bulunamadı.")
                
            # --- BORSA ARAMA MOTORU ---
            st.write("---")
            st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500; margin-bottom:2px;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
            
            if len(df.columns) >= 5:
                tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
                if tum_hisseler:
                    aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                    if aranan_hisse != "Seçiniz...":
                        h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=3)
                        if len(h_detay_veri) > 0:
                            guncel_fiyat = float(h_detay_veri['Close'].iloc[-1])
                            st.metric(label=f"{aranan_hisse} Güncel Fiyat", value=f"{guncel_fiyat:,.2f} TL")
                        else:
                            st.warning("Fiyat verisi alınamadı.")
        except Exception as e:
            st.error("Excel okunurken hata oluştu.")
    else:
        st.error("nurican.xls.xlsm dosyası bulunamadı.")

# ===================================================================== #
# SAĞ TARAF: MESAJ PANELI (YENİLENDİ)
# ===================================================================== #
with col_sag:
    st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:5px;">💬 Canlı Mesaj Paneli</p>', unsafe_allow_html=True)
    
    # Mesajları Oku
    try:
        df_msg = pd.read_csv(db_mesajlar)
        msg_lines = []
        for idx, row in df_msg.tail(10).iloc[::-1].iterrows():  
            msg_lines.append(f"<span style='color:#0d9488;'>[{row['zaman']}]</span> <b style='color:#ffcc00;'>{row['rumuz']}:</b> <span style='color:#fff;'>{row['mesaj']}</span>")
        
        mesaj_govde = "<br>".join(msg_lines) if msg_lines else "<span style='color:#666;'>Henüz mesaj yok...</span>"
        st.markdown(f'<div class="mesaj-kutusu">{mesaj_govde}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="mesaj-kutusu"><span style="color:#ff3344;">Mesajlar yüklenemedi.</span></div>', unsafe_allow_html=True)
    
    # Enter Tuşuyla Gönderim Sağlayan Form Yapısı
    with st.form("mesaj_formu", clear_on_submit=True):
        yeni_mesaj = st.text_input("Mesajınız:", max_chars=70, placeholder="Yazın ve Enter'a basın...", key="msg_input")
        gonder_butonu = st.form_submit_button("Gönder 📩", use_container_width=True)
        
        if gonder_butonu and yeni_mesaj.strip():
            filtrelenmis_mesaj = mesajı_sansurle(yeni_mesaj.strip())
            saat_str = datetime.datetime.now().strftime("%H:%M")
            df_yeni_msg = pd.DataFrame([{"zaman": saat_str, "rumuz": st.session_state["bta_rumuz"], "mesaj": filtrelenmis_mesaj}])
            try:
                df_eski_msg = pd.read_csv(db_mesajlar)
                df_toplam_msg = pd.concat([df_eski_msg, df_yeni_msg], ignore_index=True).tail(20)
                df_toplam_msg.to_csv(db_mesajlar, index=False)
            except:
