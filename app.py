import streamlit as st
import pandas as pd
import datetime
import os
import time
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
.oda-durum { font-size: 14px; font-weight: bold; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:40px; margin-bottom:15px;">BTA ANALİZ MERKEZİ</h1>
''', unsafe_allow_html=True)

# Ekranı 10 saniyede bir otomatik yenileyen hafif saat motoru
st_autorefresh(interval=10 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"
db_ayar = "bta_ayar_db.csv"
db_sayac = "bta_sayac_db.csv"

# VERİTABANLARINI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if not os.path.exists(db_ayar):
    pd.DataFrame([{"oda_kilitli": 0}]).to_csv(db_ayar, index=False)

if not os.path.exists(db_sayac):
    pd.DataFrame(columns=["session_id", "son_aksiyon"]).to_csv(db_sayac, index=False)

# 👥 KANDIRMAYAN %100 GERÇEK CANLI SAYAÇ MOTORU
now_time = time.time()
if "user_session" not in st.session_state:
    st.session_state["user_session"] = str(now_time)

try:
    df_sayac_oku = pd.read_csv(db_sayac)
    # 30 saniyedir sayfada hiçbir hareket yapmayan eski bağlantıları listeden siler
    df_sayac_oku = df_sayac_oku[df_sayac_oku["son_aksiyon"] > (now_time - 30)]
    
    # Mevcut kullanıcının durumunu günceller veya ekler
    if st.session_state["user_session"] in df_sayac_oku["session_id"].astype(str).values:
        df_sayac_oku.loc[df_sayac_oku["session_id"].astype(str) == st.session_state["user_session"], "son_aksiyon"] = now_time
    else:
        df_sayac_oku = pd.concat([df_sayac_oku, pd.DataFrame([{"session_id": st.session_state["user_session"], "son_aksiyon": now_time}])], ignore_index=True)
    
    df_sayac_oku.to_csv(db_sayac, index=False)
    gercek_canli_kisi = len(df_sayac_oku)
except:
    gercek_canli_kisi = 1

garantili_bip_html = """
<script>
    (function() {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        var gain = context.createGain();
        osc.connect(gain);
        gain.connect(context.destination);
        osc.type = 'sine';
        osc.frequency.value = 830;
        gain.gain.setValueAtTime(0.1, context.currentTime);
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, context.currentTime + 0.15);
        osc.stop(context.currentTime + 0.16);
    })();
</script>
"""

# Ayarları dosyadan oku
df_ayar_oku = pd.read_csv(db_ayar)
oda_su_an_kilitli = int(df_ayar_oku.iloc[0, 0])

# ===================================================================== #
# 2. CANLI BORSA TABLOSU (ÇAPRAZ EŞLEŞTİRME İLE GÜNCEL FİYAT VE K/Z)
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df_web = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        df_ana = pd.read_excel(excel_yolu, sheet_name="Sayfa1", engine="openpyxl")
        
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA HİSSE</th><th>BTA ALGORİTMİK FİYAT</th><th>GÜNCEL FİYAT</th><th>BTA PUANI</th><th>K/Z STATUS</th></tr>'
        veri_var_mi = False
        
        for idx in range(len(df_web)):
            try:
                hisse_adi = str(df_web.iloc[idx, 0]).strip().upper() if pd.notna(df_web.iloc[idx, 0]) else ""
                algo_fiyati = df_web.iloc[idx, 2]
                bta_puani = df_web.iloc[idx, 3]
                
                if hisse_adi != "" and hisse_adi not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "HİSSE ADI"]:
                    veri_var_mi = True
                    
                    canli_fiyati = 0.0
                    hisse_satiri = df_ana[df_ana.iloc[:, 0].astype(str).str.strip().str.upper() == hisse_adi]
                    if not hisse_satiri.empty:
                        canli_fiyati = hisse_satiri.iloc[0, 4]
                    
                    try:
                        maliyet = float(algo_fiyati)
                        g_fiyat = float(canli_fiyati)
                        if maliyet > 0 and g_fiyat > 0:
                            or_dg = ((g_fiyat - maliyet) / maliyet) * 100
                            kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.1f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.1f}</span>'
                        else:
                            kz_str = "<span>-</span>"
                    except:
                        kz_str = "<span>-</span>"
                    
                    algo_str = f"{float(algo_fiyati):,.2f} TL" if isinstance(algo_fiyati, (int, float)) else str(algo_fiyati).strip()
                    canli_str = f"{float(canli_fiyati):,.2f} TL" if isinstance(canli_fiyati, (int, float)) else str(canli_fiyati).strip()
                    puan_str = f"{float(bta_puani):.2f}" if isinstance(bta_puani, (int, float)) else str(bta_puani).strip()
                    
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
# 3. ŞİFRELİ SOHBET FORMU VE SESLİ MESAJ KUTUSU
# ===================================================================== #
st.write("---")
col_baslik, col_sayac = st.columns(2)
col_baslik.markdown('<div class="kucuk-baslik">Sohbet Odası 💬</div>', unsafe_allow_html=True)
col_sayac.markdown(f'<div style="text-align:right; color:#00ffcc; font-weight:bold; margin-top:25px;">👥 Gerçek Canlı: {gercek_canli_kisi} Kişi</div>', unsafe_allow_html=True)

if oda_su_an_kilitli == 1:
    st.markdown('<div class="oda-durum" style="background-color:#ff3344; color:white;">🔒 ODA KİLİTLİ (Yayınlanması için Nurican ustanın verdiği şifre gereklidir)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="oda-durum" style="background-color:#00ff66; color:#0b111e;">🔓 ODA HERKESE AÇIK</div>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

with st.form(key="s_frm", clear_on_submit=True):
    y_is = st.text_input("Adınız:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=80)
    
    # Oda kilitliyken formun içine şifre kutusu ekliyoruz, böylece her halükarda form doldurulabiliyor
    girilen_oda_sifresi = ""
    if oda_su_an_kilitli == 1:
        girilen_oda_sifresi = st.text_input("🔑 Oda Şifresini Girin (Bilmeyenlerin mesajı yayınlanmaz):", type="password")
        
    if st.form_submit_button("Mesajı Yayınla 📨", use_container_width=True) and y_is.strip() and y_me.strip():
        m_kucuk = y_me.lower().replace(" ", "").replace("@", "a").replace("0", "o")
        i_kucuk = y_is.lower().replace(" ", "")
        
        if any(z in m_kucuk or z in i_kucuk for z in yasakli):
            st.error("⚠ Argo/Küfür içerikli kelimeler engellendi!")
        else:
            # Kilitleme kontrolü
            yayinla_izni = True
            if oda_su_an_kilitli == 1:
                if girilen_oda_sifresi == "bta123":
                    yayinla_izni = True
                else:
                    yayinla_izni = False
                    st.error("❌ Hatalı Oda Şifresi! Mesajınız Nurican ustaya ulaşmadı.")
            
            if yayinla_izni:
                df_s = pd.read_csv(db_sohbet)
                y_satir = pd.DataFrame([{"isim": y_is.strip(), "saat": datetime.datetime.now().strftime("%H:%M"), "yorum": y_me.strip()}])
                pd.concat([y_satir, df_s], ignore_index=True).to_csv(db_sohbet, index=False)
                st.rerun()

# ===================================================================== #
# 4. YÖNETİCİ PANELİ (KİLİT VE SİLME MOTORU)
# ===================================================================== #
with st.expander("🛠 Yönetici Kontrol Paneli"):
    adm_mod = st.text_input("Yönetici Şifresi:", type="password", key="adm") == "bta123"
    if adm_mod:
        st.success("🛡 Yönetici Girişi Başarılı.")
        st.write("### Oda Yönetim Seçenekleri")
        col_kilitle, col_ac = st.columns(2)
        if col_kilitle.button("🔒 Odayı Şifreli Yap"):
            pd.DataFrame([{"oda_kilitli": 1}]).to_csv(db_ayar, index=False)
            st.rerun()
        if col_ac.button("🔓 Odayı Herkese Aç"):
