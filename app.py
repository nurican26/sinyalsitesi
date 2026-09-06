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

# --- GÜVENLİ VE HIZLI YARDIMCI FONKSİYONLAR (HATA RİSKSİZ) ---
def bst_en_cok_yukselenler():
    sonuclar = []
    for h in ["THYAO", "ASELS", "GARAN", "AKBNK", "EREGL", "TUPRS", "ISCTR", "KCHOL", "SAHOL", "YKBNK", "BIMAS", "SISE", "PGSUS", "EKGYO", "DOHOL", "PETKM", "ALARK", "ODAS"]:
        try:
            t = yf.Ticker(f"{h}.IS")
            hist = t.history(period="2d")
            if len(hist) >= 2:
                canli = float(hist['Close'].iloc[-1])
                onceki = float(hist['Close'].iloc[-2])
                degisim = ((canli - onceki) / onceki) * 100
                sonuclar.append({"HİSSE 🚀": h, "FİYAT 💰": f"{canli:.2f} TL", "DEĞİŞİM 📈": degisim})
        except:
            pass
    if sonuclar:
        df_yukselen = pd.DataFrame(sonuclar).sort_values(by="DEĞİŞİM 📈", ascending=False).head(5)
        df_yukselen["DEĞİŞİM 📈"] = df_yukselen["DEĞİŞİM 📈"].map(lambda x: f"%+{x:.2f}")
        return df_yukselen
    return pd.DataFrame()

def get_live_data(hisse_kodu, period="2d"):
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        hist = ticker.history(period=period)
        if not hist.empty:
            return hist
    except:
        pass
    return None

def mesajlari_yukle():
    if os.path.exists(sohbet_dosyası):
        try:
            with open(sohbet_dosyası, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def mesaj_kaydet(isim, mesaj):
    mevcut_mesajlar = mesajlari_yukle()
    yeni_mesaj = {"isim": isim, "mesaj": mesaj, "zaman": datetime.datetime.now().strftime("%H:%M:%S")}
    mevcut_mesajlar.append(yeni_mesaj)
    if len(mevcut_mesajlar) > 40:
        mevcut_mesajlar = mevcut_mesajlar[-40:]
    try:
        with open(sohbet_dosyası, "w", encoding="utf-8") as f:
            json.dump(mevcut_mesajlar, f, ensure_ascii=False, indent=4)
    except:
        pass

# ==================== BÖLÜM 1: BORSA PANELİ ====================
st.header("📊 CANLI BORSA TAKİP EKRANI")

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # Günün En Çok Yükselenleri
        st.markdown('<div class="yukselen-baslik">🔥 ARACI KURUM: GÜNÜN EN ÇOK YÜKSELEN HİSSELERİ (CANLI)</div>', unsafe_allow_html=True)
        yukselen_df = bst_en_cok_yukselenler()
        if not yukselen_df.empty:
            st.dataframe(yukselen_df, use_container_width=True, hide_index=True)
        
        # Arama Motoru
        st.write("")
        hisse_havuzu = []
        if len(df.columns) >= 5:
            e_sutunu_temiz = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            hisse_havuzu = sorted(list(set([h for h in e_sutunu_temiz if h not in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]])))
        
        secilen_hisse = st.selectbox("🔍 Canlı fiyatını görmek istediğiniz hisseyi havuzdan seçin:", ["Seçiniz..."] + hisse_havuzu)
        if secilen_hisse != "Seçiniz...":
            hist_ara = get_live_data(secilen_hisse, "2d")
            if hist_ara is not None:
                arama_canli_fiyat = float(hist_ara['Close'].iloc[-1])
                onceki_kap = float(hist_ara['Close'].iloc[-2]) if len(hist_ara) >= 2 else arama_canli_fiyat
                arama_degisim = ((arama_canli_fiyat - onceki_kap) / onceki_kap) * 100
                st.success(f"📈 **{secilen_hisse}** Anlık Fiyatı: **{arama_canli_fiyat:.2f} TL** | Günlük Değişim: **%{arama_degisim:+.2f}**")

        st.write("---")
        tablo_bta = []
        tablo_alsat = []
        sinir = min(10, len(df))
        
        for idx in range(sinir):
            # Üst Panel İşlemleri
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                puan_temiz = f"{float(puan_d):.2f}" if hasattr(puan_d, '__float__') or isinstance(puan_d, (int, float)) else str(puan_d).strip()
                canli_fiyat = 0.0
                hist_bta = get_live_data(hisse_a, "1d")
                if hist_bta is not None:
                    canli_fiyat = float(hist_bta['Close'].iloc[-1])
                
                maliyet = 0.0
                try:
                    maliyet = float(alim_c.replace(",", "."))
                except:
                    pass
                
                kz_oran_str = "-"
                if maliyet > 0 and canli_fiyat > 0:
                    kz_oran_str = f"%{((canli_fiyat - maliyet) / maliyet) * 100:+.2f}"
                
                tablo_bta.append({"BTA PUAN 🔢": puan_temiz, "BTA HİSSE 📈": hisse_a, "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c, "GÜNCEL FİYAT 💥": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor...", "KAR / ZARAR 📊": kz_oran_str})

            # Alt Panel İşlemleri
            alsat_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            if alsat_b and alsat_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                as_canli_fiyat = 0.0
                as_degisim = 0.0
                hist_as = get_live_data(alsat_b, "2d")
                if hist_as is not None:
                    as_canli_fiyat = float(hist_as['Close'].iloc[-1])
                    onceki_kap_as = float(hist_as['Close'].iloc[-2]) if len(hist_as) >= 2 else as_canli_fiyat
