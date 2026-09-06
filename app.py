 import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import json
import time
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması
st.set_page_config(page_title="BTA Borsa & Canlı Sohbet Odası", layout="wide")

# 🔄 CANLI YENİLEYİCİ: Sayfa her 10 saniyede bir otomatik yenilenir
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")
anim_id = int(time.time())

# Şık Tasarım CSS Kodları
st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .yukselen-baslik {{background: linear-gradient(90deg, #2563eb 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem; margin-top:20px;}}
    .logo-konteyner {{display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px;}}
    .cember-animasyon-{anim_id} {{width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden; animation: gokkusagiCember 4s linear infinite, yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;}}
    .bta-yazi-{anim_id} {{font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2; background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3)); animation: soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;}}
    .chat-kutusu {{background-color: #1e293b; border-radius: 10px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #3b82f6;}}
    .chat-isim {{ font-weight: bold; color: #38bdf8 !important; font-size: 0.95rem; }}
    .chat-zaman {{ color: #94a3b8 !important; font-size: 0.75rem; float: right; }}
    .chat-mesaj {{ color: #f1f5f9 !important; margin-top: 4px; font-size: 1rem; }}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        14% {{ border-color: #ff7f00; box-shadow: 0 0 15px #ff7f00, inset 0 0 15px #ff7f00; }}
        28% {{ border-color: #ffff00; box-shadow: 0 0 15px #ffff00, inset 0 0 15px #ffff00; }}
        42% {{ border-color: #00ff00; box-shadow: 0 0 15px #00ff00, inset 0 0 15px #00ff00; }}
        56% {{ border-color: #00ffff; box-shadow: 0 0 15px #00ffff, inset 0 0 15px #00ffff; }}
        70% {{ border-color: #0000ff; box-shadow: 0 0 15px #0000ff, inset 0 0 15px #0000ff; }}
        84% {{ border-color: #8b00ff; box-shadow: 0 0 15px #8b00ff, inset 0 0 15px #8b00ff; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
    @keyframes yukardanDus {{ 0% {{ transform: translateY(-200px) scale(0.3); opacity: 0; }} 70% {{ transform: translateY(10px) scale(1.05); opacity: 1; }} 100% {{ transform: translateY(0) scale(1); opacity: 1; }} }}
    @keyframes soldanYavascaKay {{ 0% {{ transform: translateX(-140px); opacity: 0; }} 30% {{ opacity: 0.5; }} 100% {{ transform: translateX(0); opacity: 1; }} }}
</style>
''', unsafe_allow_html=True)

# 🌈 BTA LOGO ALANI
st.markdown(f'<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #cbd5e1; font-weight: bold; margin-bottom: 20px;">📈 Canlı Piyasa & 💬 Ortak Sohbet Merkezi</div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
sohbet_dosyası = "nurican_sohbet_gecmisi.json"

# --- TEMİZ VE GÜVENLİ FİYAT MOTORU ---
def veri_motoru(hisse_adi, periyot="2d"):
    if not hisse_adi or hisse_adi in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]:
        return None
    try:
        t = yf.Ticker(f"{hisse_adi}.IS")
        hist = t.history(period=periyot)
        if not hist.empty:
            return hist
    except:
        pass
    return None

def bst_en_cok_yukselenler():
    sonuclar = []
    havuz = ["THYAO", "ASELS", "GARAN", "AKBNK", "EREGL", "TUPRS", "ISCTR", "KCHOL", "SAHOL", "YKBNK", "BIMAS", "SISE", "PGSUS", "EKGYO", "DOHOL", "PETKM", "ALARK", "ODAS"]
    for h in havuz:
        hist = veri_motoru(h, "2d")
        if hist is not None and len(hist) >= 2:
            canli = float(hist['Close'].iloc[-1])
            onceki = float(hist['Close'].iloc[-2])
            degisim = ((canli - onceki) / onceki) * 100
            sonuclar.append({"HİSSE 🚀": h, "FİYAT 💰": f"{canli:.2f} TL", "DEĞİŞİM 📈": degisim})
    if sonuclar:
        df_y = pd.DataFrame(sonuclar).sort_values(by="DEĞİŞİM 📈", ascending=False).head(5)
        df_y["DEĞİŞİM 📈"] = df_y["DEĞİŞİM 📈"].map(lambda x: f"%+{x:.2f}")
        return df_y
    return pd.DataFrame()

def mesajlari_yukle():
    if os.path.exists(sohbet_dosyası):
        try:
            with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def mesaj_kaydet(isim, mesaj):
    mevcut = mesajlari_yukle()
    mevcut.append({"isim": isim, "mesaj": mesaj, "zaman": datetime.datetime.now().strftime("%H:%M:%S")})
    if len(mevcut) > 40:
        mevcut = mevcut[-40:]
    try:
        with open(sohbet_dosyası, "w", encoding="utf-8") as f:
            json.dump(mevcut, f, ensure_ascii=False, indent=4)
    except:
        pass

# ==================== BORSA PANELİ ====================
st.header("📊 CANLI BORSA TAKİP EKRANI")

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        st.markdown('<div class="yukselen-baslik">🔥 ARACI KURUM: GÜNÜN EN ÇOK YÜKSELEN HİSSELERİ (CANLI)</div>', unsafe_allow_html=True)
        yukselen_df = bst_en_cok_yukselenler()
        if not yukselen_df.empty:
            st.dataframe(yukselen_df, use_container_width=True, hide_index=True)
        
        st.write("")
        hisse_havuzu = []
        if len(df.columns) >= 5:
            e_sut = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            hisse_havuzu = sorted(list(set([h for h in e_sut if h not in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]])))
        
        secilen_hisse = st.selectbox("🔍 Canlı fiyatını görmek istediğiniz hisseyi havuzdan seçin:", ["Seçiniz..."] + hisse_havuzu)
        if secilen_hisse != "Seçiniz...":
            hist_ara = veri_motoru(secilen_hisse, "2d")
            if hist_ara is not None:
                f_canli = float(hist_ara['Close'].iloc[-1])
                f_once = float(hist_ara['Close'].iloc[-2]) if len(hist_ara) >= 2 else f_canli
                pct = ((f_canli - f_once) / f_once) * 100
                st.success(f"📈 **{secilen_hisse}** Anlık Fiyatı: **{f_canli:.2f} TL** | Günlük Değişim: **%{pct:+.2f}**")

        st.write("---")
        tablo_bta = []
        tablo_alsat = []
        sinir = min(10, len(df))
        
        for idx in range(sinir):
            # Üst Panel
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                p_temiz = f"{float(puan_d):.2f}" if hasattr(puan_d, '__float__') or isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                h_bta = veri_motoru(ha, "1d")
                if h_bta is not None:
                    c_fiyat = float(h_bta['Close'].iloc[-1])
                try: maliyet = float(alim_c.replace(",", "."))
                except: maliyet = 0.0
                kz_str = f"%{((c_fiyat - maliyet) / maliyet) * 100:+.2f}" if maliyet > 0 and c_fiyat > 0 else "-"
                tablo_bta.append({"BTA PUAN 🔢": p_temiz, "BTA HİSSE 📈": ha, "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c, "GÜNCEL FİYAT 💥": f"{c_fiyat:.2f} TL" if c_fiyat > 0 else "Yükleniyor...", "KAR / ZARAR 📊": kz_str})

            # Alt Panel
            hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            if hb and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                as_fiyat = 0.0
                as_deg = 0.0
                h_as = veri_motoru(hb, "2d")
                if h_as is not None:
                    as_fiyat = float(h_as['Close'].iloc[-1])
                    as_prev = float(h_as['Close'].iloc[-2]) if len(h_as) >= 2 else as_fiyat
                    as_deg = ((as_fiyat - as_prev) / as_prev) * 100
                tablo_alsat.append({"GÜNLÜK AL SAT HİSSELERİ ⚡": hb, "ANLIK VERİ CANLI 📊": f"{as_fiyat:.2f} TL" if as_fiyat > 0 else "Yükleniyor...", "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-"})

        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if tablo_bta: st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
        
        st.write("")
0,
