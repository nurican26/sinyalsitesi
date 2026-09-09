import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. KOTA DOSTU TASARIM VE CSS (HAFİF VE ŞIK)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

# Görselleri ve ağır efektleri kaldırıp düz renklerle kotayı koruyoruz
st.markdown('''
<style>
.stApp { background-color: #0b111e !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; padding: 10px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: #0d9488 !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 14px; background-color: #121d33; border-radius: 8px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 8px; }
.borsa-tablo td { padding: 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.mesaj-kutusu { background-color: #090f1a; border: 1px solid #1e3a5f; padding: 8px; border-radius: 6px; max-height: 150px; overflow-y: auto; font-family: monospace; font-size: 12px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:36px; margin-bottom:10px;">BTA MERKEZ</h1>
''', unsafe_allow_html=True)

# Otomatik yenilemeyi 30 saniyeye çektik (Kota tasarrufu için en kritik ayar)
st_autorefresh(interval=30 * 1000, key="bta_kota_dostu_motor")

excel_yolu = "nurican.xls.xlsm"
db_mesajlar = "bta_hafif_mesaj_panosu.csv"

# Mesaj veritabanını başlat
if not os.path.exists(db_mesajlar):
    pd.DataFrame(columns=["zaman", "rumuz", "mesaj"]).to_csv(db_mesajlar, index=False)

# ===================================================================== #
# RUMUZ GİRİŞ SİSTEMİ
# ===================================================================== #
if "bta_rumuz" not in st.session_state:
    st.markdown("<h3 style='text-align:center; color:#fff;'>Giriş Yapın</h3>", unsafe_allow_html=True)
    giriş_rumuz = st.text_input("Rumuz (Ad):", max_chars=15, key="rumuz_input")
    if st.button("Bağlan 🚀") and giriş_rumuz.strip():
        st.session_state["bta_rumuz"] = giriş_rumuz.strip().upper()
        st.rerun()
    st.stop()

# Üst Bilgi Satırı
st.write(f"👤 Aktif Kullanıcı: **{st.session_state['bta_rumuz']}** | 🕒 30sn Otomatik Yenileme Aktif")

# İki Kolonlu Ana Düzen
col_sol, col_sag = st.columns([2, 1])

# ===================================================================== #
# SOL TARAF: HİSSELERİM VE ARAMA MOTORU
# ===================================================================== #
with col_sol:
    st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF; margin-bottom:2px;">📈 HİSSELERİM (Excel Verisi)</p>', unsafe_allow_html=True)
    
    if os.path.exists(excel_yolu):
        try:
            df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
            
            # Kota aşımını önlemek için Excel tablosunu ham gösteriyoruz (yfinance sorgularını kaldırdık)
            tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYAT</th></tr>'
            veri_var_mi = False
            
            for idx in range(min(15, len(df))):
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{alim_c}</td></tr>'
            
            tablo_html += '</table>'
            
            if veri_var_mi:
                st.markdown(tablo_html, unsafe_allow_html=True)
            else:
                st.info("Gösterilecek uygun hisse verisi bulunamadı.")
                
            # --- BORSA ARAMA MOTORU (Yalnızca tıklandığında veri çeker - Tam kota dostu) ---
            st.write("---")
            st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500; margin-bottom:2px;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
            
            if len(df.columns) >= 5:
                tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
                if tum_hisseler:
                    aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                    if aranan_hisse != "Seçiniz...":
                        # Sadece tek bir hisse seçildiğinde internete bağlanır, hafızayı şişirmez
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
# SAĞ TARAF: KOTA DOSTU MESAJ PANELI
# ===================================================================== #
with col_sag:
    st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:5px;">💬 Canlı Mesaj Paneli</p>', unsafe_allow_html=True)
    
    # Mesajları Oku ve Listele
    try:
        df_msg = pd.read_csv(db_mesajlar)
        msg_lines = []
        # Sadece son 10 mesajı çekerek ağ trafiğini ve RAM'i sıfıra indiriyoruz
        for _, row in df_msg.tail(10).iterrows():  
            msg_lines.append(f"<span style='color:#0d9488;'>[{row['zaman']}]</span> <b style='color:#ffcc00;'>{row['rumuz']}:</b> <span style='color:#fff;'>{row['mesaj']}</span>")
        
        mesaj_govde = "<br>".join(msg_lines) if msg_lines else "<span style='color:#666;'>Henüz mesaj yok...</span>"
        st.markdown(f'<div class="mesaj-kutusu">{mesaj_govde}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="mesaj-kutusu"><span style="color:#ff3344;">Mesajlar yüklenemedi.</span></div>', unsafe_allow_html=True)
    
    # Mesaj Gönderme Formu
    yeni_mesaj = st.text_input("Mesajınız:", max_chars=70, placeholder="Yazın ve Gönder'e basın...", key="msg_input")
    if st.button("Gönder 📩", use_container_width=True) and yeni_mesaj.strip():
        saat_str = datetime.datetime.now().strftime("%H:%M")
        df_yeni_msg = pd.DataFrame([{"zaman": saat_str, "rumuz": st.session_state["bta_rumuz"], "mesaj": yeni_mesaj.strip()}])
        try:
            df_eski_msg = pd.read_csv(db_mesajlar)
            # Dosyanın satır sayısını her zaman 20'de sınırlandırarak disk kotasını koruyoruz
            df_toplam_msg = pd.concat([df_eski_msg, df_yeni_msg], ignore_index=True).tail(20)
            df_toplam_msg.to_csv(db_mesajlar, index=False)
        except:
            df_yeni_msg.to_csv(db_mesajlar, index=False)
        st.rerun()
