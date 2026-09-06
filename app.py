import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import uuid
import re
from streamlit_autorefresh import st_autorefresh

# Sayfa yapılandırması ve 10 saniyede bir otomatik yenileyici
st.set_page_config(page_title="BTA Merkez", layout="wide")
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")

anim_id = int(time.time())
st.markdown(f'''
<style>
@keyframes btaPulse {{
    0% {{ transform: scale(1); filter: drop-shadow(0 0 5px rgba(30,58,138,0.3)); }}
    50% {{ transform: scale(1.03); filter: drop-shadow(0 0 15px rgba(30,58,138,0.6)); }}
    100% {{ transform: scale(1); filter: drop-shadow(0 0 5px rgba(30,58,138,0.3)); }}
}}
.bta-neon-title {{
    font-size: 65px;
    font-weight: 900;
    color: #1E3A8A;
    text-align: center;
    font-family: 'Arial Black', Gadget, sans-serif;
    letter-spacing: 5px;
    margin-top: 10px;
    margin-bottom: 5px;
    animation: btaPulse 3s infinite ease-in-out;
}}
</style>
''', unsafe_allow_html=True)

st.markdown(f'<div class="bta-neon-title">BTA</div>', unsafe_allow_html=True)

st.markdown('<p style="background-color:#FFF3CD; color:#856404; padding:12px; border-radius:8px; border-left:5px solid #FFC107; font-weight:bold; font-size:14px; margin-bottom:25px;">⚠ **SPK YASAL UYARI:** Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.</p>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

# Küfür ve argo kelime filtresi listesi
KUFUR_LISTESI = ["küfür1", "küfür2", "argo1", "piç", "siktir", "orospu", "pç", "sktr", "yarrak", "amk", "aq"]

def sohbet_temizle(metin):
    temiz_metin = metin
    for kelime in KUFUR_LISTESI:
        if kelime in temiz_metin.lower():
            sansur = "*" * len(kelime)
            insens_kelime = re.compile(re.escape(kelime), re.IGNORECASE)
            temiz_metin = insens_kelime.sub(sansur, temiz_metin)
    return temiz_metin

# Sunucu düzeyinde tek bir global hafıza havuzu oluşturur (Tüm kullanıcılar için ortaktır)
@st.cache_resource
def sunucu_canli_havuzunu_getir():
    return []

ortak_havuz = sunucu_canli_havuzunu_getir()

if "cihaz_id" not in st.session_state:
    st.session_state.cihaz_id = str(uuid.uuid4())

st.header("📊 BTA ALGORİTMİK HİSSE ")

# Sayıları TR formatına çevirme fonksiyonu
def formatla_tl(deger):
    try:
        f_deger = float(deger)
        ingiliz_stil = f"{f_deger:,.2f}"
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{tr_stil} TL"
    except:
        return str(deger)

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        # --- ÜST PANEL (BTA HİSSELERİ) ---
        tablo_bta = []
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                p_temiz = f"{float(puan_d):.2f}" if hasattr(puan_d, '__float__') or isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                try:
                    h_bta = yf.Ticker(f"{ha}.IS").history(period="1d")
                    if not h_bta.empty:
                        c_fiyat = float(h_bta['Close'].iloc[-1])
                except:
                    pass
                try:
                    maliyet = float(alim_c.replace(",", "."))
                except:
                    maliyet = 0.0
                kz_str = f"%{((c_fiyat - maliyet) / maliyet) * 100:+.2f}" if maliyet > 0 and c_fiyat > 0 else "-"
                tablo_bta.append({
                    "BTA PUAN 🔢": p_temiz,
                    "BTA HİSSE 📈": ha,
                    "BTA ALIM 📥": formatla_tl(maliyet) if maliyet > 0 else alim_c,
                    "GÜNCEL FİYAT 💥": formatla_tl(c_fiyat) if c_fiyat > 0 else "Yükleniyor...",
                    "KAR / ZARAR 📊": kz_str
                })
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#1E3A8A; margin-top:15px; margin-bottom:10px;">📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True)
        if len(tablo_bta) > 0:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
        st.write("")
        
        # --- ALT PANEL (GÜNLÜK AL SAT HİSSELERİ) ---
        tablo_alsat = []
        for idx in range(min(10, len(df))):
            hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            if hb != "" and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                as_fiyat = 0.0
                as_deg = 0.0
                try:
                    h_as = yf.Ticker(f"{hb}.IS").history(period="2d")
                    if not h_as.empty:
                        as_fiyat = float(h_as['Close'].iloc[-1])
                        as_prev = float(h_as['Close'].iloc[-2]) if len(h_as) >= 2 else as_fiyat
                        as_deg = ((as_fiyat - as_prev) / as_prev) * 100
                except:
                    pass
                tablo_alsat.append({
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": hb,
                    "ANLIK VERİ CANLI 📊": formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor...",
                    "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-"
                })
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#D97706; margin-top:15px; margin-bottom:10px;">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
        st.write("---")
        
        # --- BIST ANLIK ARAMA MOTORU ---
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#059669; margin-top:15px; margin-bottom:10px;">🔍 BIST ANLIK HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
            tum_hisseler.sort()
            if tum_hisseler:
                aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    with st.spinner(f"{aranan_hisse} verileri çekiliyor..."):
                        try:
                            h_detay = yf.Ticker(f"{aranan_hisse}.IS").history(period="2d")
                            if not h_detay.empty:
                                anlik_fiyat = float(h_detay['Close'].iloc[-1])
                                dunku_kapanis = float(h_detay['Close'].iloc[-2]) if len(h_detay) >= 2 else anlik_fiyat
                                gunluk_degisim = ((anlik_fiyat - dunku_kapanis) / dunku_kapanis) * 100
                                gunun_en_yuksek = float(h_detay['High'].iloc[-1])
                                gunun_en_dusuk = float(h_detay['Low'].iloc[-1])
                                
                                col1, col2, col3 = st.columns(3)
                                col1.metric(label="Anlık Canlı Fiyat 💥", value=formatla_tl(anlik_fiyat), delta=f"%{gunluk_degisim:+.2f}")
                                col2.metric(label="Gün içi En Yüksek 📈", value=formatla_tl(gunun_en_yuksek))
                                col3.metric(label="Gün içi En Düşük 📉", value=formatla_tl(gunun_en_dusuk))
                            else:
                                st.warning(f"{aranan_hisse} koduna ait anlık veri bulunamadı. Lütfen Excel'deki kodu kontrol edin (Örn: THYAO, EREGL).")
                        except Exception as e:
                            st.error("Borsa verisi çekilirken bir hata oluştu.")
            else:
                st.warning("Excel dosyasının E sütununda geçerli bir hisse listesi bulunamadı.")
        else:
            st.error("Excel dosyasında E sütunu bulunamadı!")
    except Exception as e:
        st.error("Excel veya Borsa verileri yüklenirken bir sorun oluştu.")
