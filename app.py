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
st.markdown(f''' ''', unsafe_allow_html=True) 
st.markdown(f'<p>BTA</p>', unsafe_allow_html=True) 
st.markdown('<p>⚠ **SPK YASAL UYARI:** Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.</p>', unsafe_allow_html=True) 

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
            puan_d = df.iloc[idx, 3] if hasattr(df.iloc[idx, 3], '__float__') or isinstance(df.iloc[idx, 3], (int, float)) else df.iloc[idx, 3]
            
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
        
        st.markdown('<p>📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True) 
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
        
        st.markdown('<p>⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True) 
        if len(tablo_alsat) > 0: 
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True) 
        st.write("---") 
        
        # --- BIST ANLIK ARAMA MOTORU --- 
        st.markdown('<p>🔍 BIST ANLIK HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True) 
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
                                st.warning(f"{aranan_hisse} koduna ait anlık veri bulunamadı. Lütfen Excel'deki kodu kontrol edin.") 
                        except: 
                            st.error("Borsa verisi çekilirken bir hata oluştu.") 
            else: 
                st.warning("Excel dosyasının E sütununda geçerli bir hisse listesi bulunamadı.") 
        else: 
            st.error("Excel dosyasında E sütunu bulunamadı!") 
    except Exception as e: 
        st.error("Excel veya Borsa verileri yüklenirken bir sorun oluştu.") 

# --- SİTE EN ALTI SOHBET ODASI ENTEGRASYONU --- 
st.markdown("---") 
st.subheader("💬 Topluluk Sohbet Odası") 

sohbet_html_kodu = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; }
        .chat-card { width: 100%; max-width: 450px; height: 550px; background: #fff; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; margin: 10px auto; }
        .header { background: #075e54; color: white; padding: 15px; text-align: center; font-size: 1.2rem; font-weight: bold; }
        .login-screen { padding: 30px; display: flex; flex-direction: column; justify-content: center; height: 100%; text-align: center; }
        .login-screen input { padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 1rem; outline: none; }
        .login-screen button { padding: 12px; background: #128c7e; color: white; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
        .chat-screen { display: none; flex-direction: column; height: 100%; }
        .messages-area { flex: 1; padding: 15px; overflow-y: auto; background: #efeae2; display: flex; flex-direction: column; gap: 10px; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 10px; font-size: 0.95rem; word-wrap: break-word; }
        .msg.incoming { background: white; align-self: flex-start; }
        .msg.outgoing { background: #d9fdd3; align-self: flex-end; }
        .msg .username { font-size: 0.75rem; color: #128c7e; font-weight: bold; display: block; }
        .input-area { padding: 10px; background: #f0f2f5; display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; border: none; border-radius: 20px; outline: none; }
        .input-area button { background: #128c7e; color: white; border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer; }
    </style>
    <script src="https://gstatic.com"></script>
