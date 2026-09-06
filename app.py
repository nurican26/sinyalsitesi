import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import json
import time
import uuid
from streamlit_autorefresh import st_autorefresh

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
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:20px;}}
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px;}}
    .cember-animasyon-{anim_id} {{width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden; animation: gokkusagiCember 4s linear infinite;}}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));}}
    .chat-kutusu {{background-color: #1e293b; border-radius: 10px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #3b82f6; position: relative;}}
    .chat-isim {{ font-weight: bold; color: #38bdf8 !important; font-size: 0.95rem; }}
    .chat-zaman {{ color: #94a3b8 !important; font-size: 0.75rem; float: right; margin-right: 10px; }}
    .chat-mesaj {{ color: #f1f5f9 !important; margin-top: 4px; font-size: 1rem; }}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
</style>
''', unsafe_allow_html=True)

st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
sohbet_dosyası = "nurican_sohbet_gecmisi.json"

if "cihaz_id" not in st.session_state:
    st.session_state.cihaz_id = str(uuid.uuid4())

st.header("📊 BTA ALGORİTMİK HİİSE ")

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
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
                tablo_bta.append({"BTA PUAN 🔢": p_temiz, "BTA HİSSE 📈": ha, "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c, "GÜNCEL FİYAT 💥": f"{c_fiyat:.2f} TL" if c_fiyat > 0 else "Yükleniyor...", "KAR / ZARAR 📊": kz_str})
        
        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_bta) > 0:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)

        st.write("")
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
                tablo_alsat.append({"GÜNLÜK AL SAT HİSSELERİ ⚡": hb, "ANLIK VERİ CANLI 📊": f"{as_fiyat:.2f} TL" if as_fiyat > 0 else "Yükleniyor...", "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-"})
        
        st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)

    except:
        st.error("Excel verileri yüklenirken bir sorun oluştu.")
else:
    st.error(f"'{excel_yolu}' dosyası sistemde bulunamadı!")

st.write("---")
st.header("💬  CANLI SOHBET ODASI")

if "kullanici_adi" not in st.session_state:
    st.session_state.kullanici_adi = ""

if not st.session_state.kullanici_adi:
    with st.form("giris_formu"):
        st.subheader("Sohbete Katılmak İçin Bir İsim Seçin")
        gecici_isim = st.text_input("Kullanıcı Adınız:", placeholder="Örn: Nuri Can")
        if st.form_submit_button("Odaya Bağlan"):
            if gecici_isim.strip():
                st.session_state.kullanici_adi = gecici_isim.strip()
                st.rerun()
else:
    st.write(f"👤 Profil: **@{st.session_state.kullanici_adi}**")
    with st.form("mesaj_formu", clear_on_submit=True):
        yeni_mesaj_metni = st.text_input("Mesajınızı yazın...", placeholder="Buraya yazın...")
        if st.form_submit_button("Gönder 🚀"):
            if yeni_mesaj_metni.strip():
                mevcut = []
                if os.path.exists(sohbet_dosyası):
                    try:
                        with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                            mevcut = json.load(f)
                    except:
                        pass
                mevcut.append({
                    "mesaj_id": str(uuid.uuid4()),
                    "cihaz_id": st.session_state.cihaz_id,
                    "isim": st.session_state.kullanici_adi, 
                    "mesaj": yeni_mesaj_metni.strip(), 
                    "zaman": datetime.datetime.now().strftime("%H:%M:%S")
                })
                if len(mevcut) > 40:
                    mevcut = mevcut[-40:]
                try:
                    with open(sohbet_dosyası, "w", encoding="utf-8") as f:
                        json.dump(mevcut, f, ensure_ascii=False, indent=4)
                except:
                    pass
                st.rerun()

    with st.expander("🛠️ Admin / Moderatör Paneli"):
        admin_sifre = st.text_input("Yönetici Şifresi:", type="password", placeholder="Şifreyi girin...")
        if admin_sifre == "3015":
            if st.button("🚨 Tüm Sohbet Geçmişini Sıfırla"):
                try:
                    with open(sohbet_dosyası, "w", encoding="utf-8") as f:
                        json.dump([], f)
                    st.success("Sohbet odası sıfırlandı!")
                    time.sleep(1)
                    st.rerun()
                except:
                    pass

    sohbet_gecmisi = []
    if os.path.exists(sohbet_dosyası):
        try:
            with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                sohbet_gecmisi = json.load(f)
        except:
            pass

    if sohbet_gecmisi:
        for m in reversed(sohbet_gecmisi):
            col_m, col_s = st.columns([0.85, 0.15])
            with col_m:
                st.markdown(f'''
                <div class="chat-kutusu">
                    <span class="chat-isim">@{m['isim']}</span>
                    <span class="chat-zaman">{m['zaman']}</span>
                    <div class="chat-mesaj">{m['mesaj']}</div>
                </div>
                ''', unsafe_allow_html=True)
            with col_s:
                if m.get("cihaz_id") == st.session_state.cihaz_id:
                    if st.button("❌ Sil", key=m.get("mesaj_id")):
                        try:
                            g_liste = [msg for msg in sohbet_gecmisi if msg.get("mesaj_id") != m.get("mesaj_id")]
                            with open(sohbet_dosyası, "w", encoding="utf-8") as f:
                                json.dump(g_liste, f, ensure_ascii=False, indent=4)
                            st.rerun()
                        except:
                            pass
    else:
        st.info("Sohbet odası şu an sessiz.")

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
