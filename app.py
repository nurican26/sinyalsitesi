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
.oda-durum { font-size: 14px; font-weight: bold; padding: 6px 12px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; }
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:40px; margin-bottom:15px;">BTA ANALİZ MERKEZİ</h1>
''', unsafe_allow_html=True)

# Ekranı 10 saniyede bir yenileyen hafif borsa motoru (Isınma yapmaz)
st_autorefresh(interval=10 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"

# VERİTABANI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

# KİLİT MEKANİZMASINI BELLEKTE TUTMA (Sunucu trafiğini ve CPU'yu yormaz)
if "oda_kilidi_durumu" not in st.session_state:
    st.session_state["oda_kilidi_durumu"] = False  # Varsayılan: Herkese Açık

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

# ===================================================================== #
# 2. CANLI BORSA TABLOSU (Sayfa1 ve WEB Çapraz Eşleştirme - Kota %0)
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
                        canli_fiyati = hisse_satiri.iloc[0, 4] # Sayfa1'deki E Sütunu Anlık Fiyat
                    
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
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
        else: st.info("⏳ WEB Sayfasında Gösterilecek Hisse Verisi Bulunamadı...")
    except Exception as e:
        st.error(f"Veri okunurken bir hata oluştu: {e}")
else:
    st.error("Excel veritabanı bulunamadı. Lütfen nurican.xls.xlsm dosyasını yükleyin.")

# ===================================================================== #
# 3. YÖNETİCİ GİZLİ ŞALTER ODASI (Sadece Sende Açılır)
# ===================================================================== #
st.write("---")
with st.expander("🛠 Sadece Nurican Usta Yönetim Paneli"):
    adm_mod = st.text_input("Şifrenizi Girin:", type="password", key="adm_key") == "bta123"
    if adm_mod:
        st.success("🛡 Giriş Başarılı. Oda Şalterini Buradan Kontrol Edin:")
        col_k1, col_ac1 = st.columns(2)
        if col_k1.button("🔒 SOHBET ODASINI DIŞARIYA KAPAT"):
            st.session_state["oda_kilidi_durumu"] = True
            st.rerun()
        if col_ac1.button("🔓 SOHBET ODASINI HERKESE AÇ"):
            st.session_state["oda_kilidi_durumu"] = False
            st.rerun()

# ===================================================================== #
# 4. YENİ TELEGRAM MODU CANLI SOHBET ALANI
# ===================================================================== #
st.markdown('<div class="kucuk-baslik">Canlı Borsa Sohbet Odası 💬</div>', unsafe_allow_html=True)

if st.session_state["oda_kilidi_durumu"]:
    st.markdown('<div class="oda-durum" style="background-color:#ff3344; color:white;">🔒 SOHBET KİLİTLİ: Oda şu an Nurican Usta tarafından dış dünyaya kapatıldı.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="oda-durum" style="background-color:#00ff66; color:#0b111e;">🔓 SOHBET AKTİF: Herkes serbestçe yazabilir ve silebilir.</div>', unsafe_allow_html=True)

# İsim Kaydı
rumuz = st.text_input("Sohbetteki Adınız:", max_chars=20, value="Ziyaretçi", key="bta_rumuz_alani")

# KİLİT KONTROLÜ: Oda kilitliyse yazma çubuğunu tamamen gizler
if not st.session_state["oda_kilidi_durumu"]:
    # WhatsApp/Telegram tarzı ince chat giriş çubuğu (Donma, kasma yapmaz)
    mesaj_girdisi = st.chat_input("Mesajınızı buraya yazın ve Enter'a basın...")
    
    if mesaj_girdisi:
        m_temiz = mesaj_girdisi.lower().replace(" ", "")
        if not any(z in m_temiz for z in ["amk", "oç", "orospu", "siktir", "piç"]):
            df_s = pd.read_csv(db_sohbet)
            y_satir = pd.DataFrame([{"isim": rumuz.strip(), "saat": datetime.datetime.now().strftime("%H:%M"), "yorum": mesaj_girdisi.strip()}])
            pd.concat([y_satir, df_s], ignore_index=True).to_csv(db_sohbet, index=False)
            st.rerun()
        else:
            st.error("⚠ Argo kelime tespit edildi, mesaj engellendi!")
else:
    st.warning("🔒 Oda şu an kapalı olduğu için mesaj gönderim alanı geçici olarak devre dışıdır.")

# MESAJ LİSTELEME VE SES MOTORU
df_sohbet_oku = pd.read_csv(db_sohbet)

if "son_mesaj_sayisi" not in st.session_state:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

if len(df_sohbet_oku) > st.session_state["son_mesaj_sayisi"]:
    st.components.v1.html(garantili_bip_html, height=0, width=0)
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)
elif len(df_sohbet_oku) < st.session_state["son_mesaj_sayisi"]:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

# Mesajları Telegram tarzı balonlarla listeler
for s in range(len(df_sohbet_oku)):
    sh = df_sohbet_oku.iloc[s]
    with st.chat_message("user"):
        st.write(f"**👤 {sh['isim']}** | ⏱ {sh['saat']}")
        st.write(sh['yorum'])
        
        # Herkesin basıp silebileceği bağımsız buton
        if st.button(f"Sil ❌", key=f"sl_{s}"):
            df_sl = pd.read_csv(db_sohbet)
            df_sl.drop(s).reset_index(drop=True).to_csv(db_sohbet, index=False)
            st.session_state["son_mesaj_sayisi"] = len(df_sl) - 1
            st.rerun()
