
import datetime
import os
import time
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. KOTA DOSTU SADE TASARIM VE KUTULU SOHBET AYARLARI (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 16px; background-color: #121d33; border-radius: 8px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 12px 10px; font-weight: bold; }
.borsa-tablo td { padding: 12px 10px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.kucuk-baslik { font-size: 20px !important; color: #ffffff !important; font-weight: bold; margin-bottom: 5px; margin-top: 20px; }
div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; }

/* 📦 SOHBETİ KUTU İÇİNE HAPSEDEN VE KAYDIRAN ÖZEL AYAR */
.sohbet-kaydirma-kutusu {
    max-height: 400px;
    overflow-y: auto;
    background-color: #090f1a;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}
.mesaj-balonu {
    background-color: #121d33; 
    padding: 10px; 
    border-radius: 8px; 
    margin-bottom: 8px; 
    border-left: 5px solid #00ffcc;
}
</style>
<h1 style="text-align:center; color:#00ffcc; font-family:sans-serif; font-size:40px; margin-bottom:15px;">BTA ANALİZ MERKEZİ</h1>
''', unsafe_allow_html=True)

# Ekranı ve internet fiyatlarını 10 saniyede bir tazeleyen motor
st_autorefresh(interval=10 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_db.csv"
db_sayac = "bta_sayac_db.csv"

# VERİTABANLARINI BAŞLATMA
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

if not os.path.exists(db_sayac):
    pd.DataFrame(columns=["session_id", "son_aksiyon"]).to_csv(db_sayac, index=False)

# 👥 %100 GERÇEK CANLI SAYAÇ MOTORU
now_time = time.time()
if "user_session" not in st.session_state:
    st.session_state["user_session"] = str(now_time)

try:
    df_sayac_oku = pd.read_csv(db_sayac)
    df_sayac_oku = df_sayac_oku[df_sayac_oku["son_aksiyon"] > (now_time - 30)]
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

# ===================================================================== #
# 2. CANLI INTERNET DESTEKLİ BORSA TABLOSU (TAM NURİCAN USTA NİZAMI)
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        # Tam istediğiniz o yeşil sekmeli "WEB" sayfasını içeri yüklüyoruz
        df_web = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA HİSSE</th><th>BTA PUANI</th><th>ANLIK CANLI FİYAT</th><th>YÜKSELİŞ / DÜŞÜŞ %</th></tr>'
        veri_var_mi = False
        
        for idx in range(len(df_web)):
            try:
                # Sadece A sütununda (BTA HİSSE) veri varsa işlem yap, diğerlerini görme!
                hisse_adi = str(df_web.iloc[idx, 0]).strip().upper() if pd.notna(df_web.iloc[idx, 0]) else ""
                
                if hisse_adi != "" and hisse_adi not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "HİSSE ADI", "BTA AL SAT"]:
                    
                    # D sütunundaki (3. endeks) BTA PUANI verisini çekiyoruz
                    bta_puani = df_web.iloc[idx, 3]
                    puan_str = f"{float(bta_puani):.2f}" if isinstance(bta_puani, (int, float)) else str(bta_puani).strip()
                    
                    veri_var_mi = True
                    canli_fiyati = 0.0
                    degisim_orani = 0.0
                    
                    # 🌐 İNTERNETTEN ANLIK CANLI VERİYİ ÇEKME MOTORU (yfinance)
                    try:
                        ticker_meta = yf.Ticker(f"{hisse_adi}.IS")
                        h_veri = ticker_meta.history(period="1d", timeout=3)
                        
                        if len(h_veri) > 0:
                            canli_fiyati = float(h_veri['Close'].iloc[-1])
                            # Dünkü kapanış fiyatına bakarak yüzde kaç yükseldi/düştü anlık hesaplar
                            dunki_kapanis = float(ticker_meta.info.get('previousClose', canli_fiyati))
                            if dunki_kapanis > 0:
                                degisim_orani = ((canli_fiyati - dunki_kapanis) / dunki_kapanis) * 100
                    except:
                        pass
                    
                    canli_str = f"{canli_fiyati:,.2f} TL" if canli_fiyati > 0 else "⏳ Yükleniyor..."
                    
                    # Yüzde kaç yükselmiş düşmüş ok simgeli tasarım nizamı
                    if degisim_orani >= 0:
                        kz_str = f'<span style="color:#00ff66;">▲ %{degisim_orani:.2f}</span>'
                    else:
                        kz_str = f'<span style="color:#ff3344;">▼ %{abs(degisim_orani):.2f}</span>'
                    
                    tablo_html += f'<tr><td>{hisse_adi}</td><td>{puan_str}</td><td>{canli_str}</td><td>{kz_str}</td></tr>'
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
# 3. YÖNETİCİ GİRİŞ ALANI (Sadece Sana Özel Butonları Açar)
# ===================================================================== #
st.write("---")
with st.expander("🛠 Sadece Nurican Usta Yönetici Girişi"):
    adm_mod = st.text_input("Yönetici Şifrenizi Girin:", type="password", key="adm_key") == "bta123"
    if adm_mod:
        st.success("🛡 Yönetici Yetkileri Aktif. Artık Temizlik Yapabilirsiniz.")

# ===================================================================== #
# 4. BAŞLIK VE CANLI ODA SAYACI ALANI
# ===================================================================== #
col_baslik, col_sayac = st.columns(2)
col_baslik.markdown('<div class="kucuk-baslik">Canlı Borsa Sohbet Odası 💬</div>', unsafe_allow_html=True)
col_sayac.markdown(f'<div style="text-align:right; color:#00ffcc; font-weight:bold; margin-top:25px; font-size:18px;">👥 Gerçek Canlı: {gercek_canli_kisi} Kişi</div>', unsafe_allow_html=True)

# İsim Kaydı
rumuz = st.text_input("Sohbetteki Adınız:", max_chars=30, value="Ziyaretçi", key="bta_rumuz_alani")

# ===================================================================== #
# 5. KUTU İÇİNDE KAYAN MESAJ LİSTELEME MOTORU (SCROLL BOX)
# ===================================================================== #
df_sohbet_oku = pd.read_csv(db_sohbet)

if "son_mesaj_sayisi" not in st.session_state:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

if len(df_sohbet_oku) > st.session_state["son_mesaj_sayisi"]:
    st.components.v1.html(garantili_bip_html, height=0, width=0)
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)
elif len(df_sohbet_oku) < st.session_state["son_mesaj_sayisi"]:
    st.session_state["son_mesaj_sayisi"] = len(df_sohbet_oku)

html_sohbet_icerik = '<div class="sohbet-kaydirma-kutusu">'
for s in range(len(df_sohbet_oku)):
    sh = df_sohbet_oku.iloc[s]
    html_sohbet_icerik += f'<div class="mesaj-balonu"><b>👤 {sh["isim"]}</b> <span style="font-size:11px; color:#aaa; float:right;">⏱ {sh["saat"]}</span><p style="margin-top:4px; color:#fff; margin-bottom:0px; word-wrap: break-word;">{sh["yorum"]}</p></div>'
html_sohbet_icerik += '</div>'

st.markdown(html_sohbet_icerik, unsafe_allow_html=True)

if adm_mod and len(df_sohbet_oku) > 0:
    st.write("🗑 **Yönetici Silme Paneli:**")
    for s in range(len(df_sohbet_oku)):
        sh = df_sohbet_oku.iloc[s]
        if st.button(f"Sil ❌ - {sh['isim']}: {sh['yorum'][:20]}...", key=f"sl_{s}"):
            df_sl = pd.read_csv(db_sohbet)
            df_sl.drop(s).reset_index(drop=True).to_csv(db_sohbet, index=False)
            st.session_state["son_mesaj_sayisi"] = len(df_sl) - 1
            st.rerun()

# ===================================================================== #
# 6. EN ALTTA SABİT WHATSAPP TARZI GİRİŞ ÇUBUĞU (LİMİT 5000 HARF)
