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
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .arama-baslik {{background: linear-gradient(90deg, #3b82f6 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:10px; margin-bottom:20px;}}
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px;}}
    .cember-animasyon-{anim_id} {{width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden; animation: gokkusagiCember 4s linear infinite;}}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));}}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
</style>
''', unsafe_allow_html=True)

st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
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
        
        st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)

        st.write("---")
        
        # --- BIST ANLIK ARAMA MOTORU (E SÜTUNU, E2 SATIRINDAN İTİBAREN) ---
        st.markdown('<div class="arama-baslik">🔍 BIST ANLIK HİSSE ARAMA MOTORU</div>', unsafe_allow_html=True)
        
        # Excel'deki E sütunundaki tüm benzersiz ve boş olmayan hisseleri okur
        if len(df.columns) >= 5: # E sütunu var mı kontrolü
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
            # Başlık satırını veya geçersiz verileri temizle
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
                                
                                # Arama Sonuçlarını Kart Düzeni Şeklinde Göster
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

import streamlit as st

# MEVCUT SİTE KODLARINIZIN EN ALTINA BU KISMI EKLEYİN
st.markdown("---")
st.subheader("💬 Topluluk Sohbet Odası")

sohbet_kodlari = """
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
    <script src="https://gstatic.com"></script>
</head>
<body>
<div class="chat-card">
    <div class="header">Topluluk Sohbet Odası</div>
    <div id="loginScreen" class="login-screen">
        <h3>Hoş Geldiniz</h3>
        <input type="text" id="usernameInput" placeholder="Kullanıcı adınız..." maxlength="15">
        <button onclick="girisYap()">Odaya Gir</button>
    </div>
    <div id="chatScreen" class="chat-screen">
        <div id="messagesArea" class="messages-area"></div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Mesajınızı yazın..." onkeypress="if(event.key === 'Enter') mesajGonder()">
            <button onclick="mesajGonder()">➤</button>
        </div>
    </div>
</div>
<script>
    const firebaseConfig = {
        apiKey: "AIzaSyATG7FEv2Stt2cUjdc2lW7V6LBWLSKRwJo",
        authDomain: "://firebaseapp.com",
        projectId: "sohbet-44d3f",
        storageBucket: "://appspot.com",
        messagingSenderId: "226504669806",
        appId: "1:226504669806:web:e99c57056dba758ac1847f"
    };
    firebase.initializeApp(firebaseConfig);
    const db = firebase.firestore();
    let aktifKullanici = "";
    function girisYap() {
        const input = document.getElementById("usernameInput").value.trim();
        if (input === "") return;
        aktifKullanici = input;
        document.getElementById("loginScreen").style.display = "none";
        document.getElementById("chatScreen").style.display = "flex";
        mesajlariYukle();
    }
    function mesajGonder() {
        const input = document.getElementById("messageInput");
        let mesajMetni = input.value.trim();
        if (mesajMetni === "") return;
        db.collection("mesajlar").add({
            kullanici: aktifKullanici,
            mesaj: mesajMetni,
            tarih: firebase.firestore.FieldValue.serverTimestamp()
        });
        input.value = "";
    }
    function mesajlariYukle() {
        const alan = document.getElementById("messagesArea");
        db.collection("mesajlar").orderBy("tarih", "asc").limitToLast(50).onSnapshot((snapshot) => {
            alan.innerHTML = "";
            snapshot.forEach((doc) => {
                const veri = doc.data();
                if(!veri.tarih) return;
                const tip = veri.kullanici === aktifKullanici ? "outgoing" : "incoming";
                const mesajDiv = document.createElement("div");
                mesajDiv.className = `msg ${tip}`;
                mesajDiv.innerHTML = `<span class="username">\${veri.kullanici}</span>\${veri.mesaj}`;
                alan.appendChild(mesajDiv);
            });
            alan.scrollTop = alan.scrollHeight;
        });
    }
</script>
</body>
</html>
"""

st.components.v1.html(sohbet_kodlari, height=580, scrolling=False)
