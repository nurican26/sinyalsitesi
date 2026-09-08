import streamlit as st
import pandas as pd
import datetime
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
.kucuk-baslik { font-size: 20px !important; color: #ffffff !important; font-weight: bold; margin-bottom: 5px; margin-top: 20px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:40px; margin-bottom:15px;">BTA ANALİZ MERKEZİ</h1>
''', unsafe_allow_html=True)

# Ekranı 10 saniyede bir otomatik yenileyen hafif saat motoru
st_autorefresh(interval=10 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"

# KALICI SOHBET VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

# İnternet gerektirmeyen, doğrudan tarayıcının kendi ürettiği Bip Sesi (Web Audio API)
garantili_bip_html = """
<script>
    (function() {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        var gain = context.createGain();
        osc.connect(gain);
        gain.connect(context.destination);
        osc.type = 'sine';
        osc.frequency.value = 830; // Sesin incelik ayarı (Hz)
        gain.gain.setValueAtTime(0.1, context.currentTime); // Ses seviyesi (0.1 ideal)
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, context.currentTime + 0.15); // 0.15 saniye sürer
        osc.stop(context.currentTime + 0.16);
    })();
</script>
"""

# ===================================================================== #
# 2. CANLI BORSA TABLOSU (EXCEL'DEN GÜNCEL FİYAT VE K/Z EKLENDİ)
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # Sütun başlıklarına GÜNCEL FİYAT ve K/Z alanlarını tam sırasıyla ekledik
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA HİSSE</th><th>BTA ALGORİTMİK FİYAT</th><th>GÜNCEL FİYAT</th><th>BTA PUANI</th><th>K/Z STATUS</th></tr>'
        veri_var_mi = False
        
        for idx in range(len(df)):
            try:
                # Sizin yeşil sekmeli WEB sayfanızın tam sütun nizamı:
                # A sütunu (0): BTA HİSSE
                # B sütunu (1): BTA AL SAT -> (GÖSTERMİYORUZ)
                # C sütunu (2): BTA ALIM FİYATI
                # D sütunu (3): BTA PUANI
                # E sütunu (4): GÜNCEL CANLI FİYAT (Excel'inizde hangi sütundaysa ona göre güncel fiyatı çeker)
                # F sütunu (5): K/Z ORANI
                
                hisse_adi = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                algo_fiyati = df.iloc[idx, 2]
                bta_puani = df.iloc[idx, 3]
                
                # Excel tablonuzdaki Güncel Fiyat ve K/Z verilerini çekiyoruz
                # Eğer Excel'de yerleri farklıysa sütun sayılarını (4 ve 5) ona göre eşleştiririz
                canli_fiyati = df.iloc[idx, 4] if len(df.columns) >= 5 else 0.0
                kz_orani = df.iloc[idx, 5] if len(df.columns) >= 6 else ""
                
                if hisse_adi != "" and hisse_adi not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "HİSSE ADI", "HİSSE ADI "]:
                    veri_var_mi = True
                    
                    # Sayısal nizamlar
                    algo_str = f"{float(algo_fiyati):,.2f} TL" if isinstance(algo_fiyati, (int, float)) else str(algo_fiyati).strip()
                    canli_str = f"{float(canli_fiyati):,.2f} TL" if isinstance(canli_fiyati, (int, float)) else str(canli_fiyati).strip()
                    puan_str = f"{float(bta_puani):.2f}" if isinstance(bta_puani, (int, float)) else str(bta_puani).strip()
                    
                    # K/Z Renklendirme motoru
                    kz_metin = str(kz_orani).strip()
                    if "▼" in kz_metin or "-" in kz_metin:
                        kz_str = f'<span style="color:#ff3344;">{kz_metin}</span>'
                    elif "▲" in kz_metin or "%" in kz_metin:
                        kz_str = f'<span style="color:#00ff66;">{kz_metin}</span>'
                    else:
                        kz_str = f'<span>{kz_metin}</span>'
                    
                    tablo_html += f'<tr><td>{hisse_adi}</td><td>{algo_str}</td><td>{canli_str}</td><td>{puan_str}</td><td>{kz_str}</td></tr>'
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

# ===================================================================== #
# 3. GÜVENLİ SOHBET FORMU VE SESLİ MESAJ KUTUSU
# ===================================================================== #
st.write("---")
st.markdown('<div class="kucuk-baslik">Sohbet Odası 💬</div>', unsafe_allow_html=True)

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
            st.error("⚠ Argo/Küfür içerikli kelimeler engellendi!")

with st.expander("🛠 Yönetici"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"

# MESAJ LİSTELEME VE SES KONTROL MOTORU
df_sohbet_oku = pd.read_csv(db_sohbet)

if "son_mesaj_sayisi" not in st.session_state:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

# Yeni mesaj geldiğinde sayfa yenilenirken yerel ses tetiklenir
if len(df_sohbet_oku) > st.session_state["son_mesaj_sayisi"]:
    st.components.v1.html(garantili_bip_html, height=0, width=0)
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)
elif len(df_sohbet_oku) < st.session_state["son_mesaj_sayisi"]:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

# Gelen mesajları ekrana nizamla dizer
for s in range(len(df_sohbet_oku)):
    sh = df_sohbet_oku.iloc[s]
    st.markdown(f'<div style="background-color: #121d33; padding: 10px; border-radius: 8px; margin-bottom: 6px; border-left: 5px solid #00ffcc;"><b>👤 {sh["isim"]}</b> <span style="font-size:11px; color:#aaa; float:right;">⏱ {sh["saat"]}</span><p style="margin-top:4px; color:#fff;">{sh["yorum"]}</p></div>', unsafe_allow_html=True)
    if adm_mod and st.button(f"Sil ❌ (Sıra: {s+1})", key=f"sl_{s}"):
        df_sl = pd.read_csv(db_sohbet)
        df_sl.drop(s).reset_index(drop=True).to_csv(db_sohbet, index=False)
        st.session_state["son_mesaj_sayisi"] = len(df_sl) - 1
        st.rerun()
