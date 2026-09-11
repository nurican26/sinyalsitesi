import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. SAYFA AYARLARI
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 2. ÖZEL GÜVENLİ CSS TASARIMI
css_kodu = """
<style>
.stApp { 
    background-color: #0b111e !important; 
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; 
}
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.8rem !important; }

.bta-ana-logo {
    text-align: center;
    font-family: 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 65px; 
    color: #00ffcc;
    margin: 5px 0 !important;
    text-shadow: 0 0 10px #00ffcc, 0 0 20px #1e90ff, 0 0 35px #0d9488;
}

.borsa-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.tebrik-kutusu { border: 2px solid #00ffcc; box-shadow: 0 0 15px #00ffcc, inset 0 0 10px rgba(0,255,204,0.3); background: #121d33; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; }
.tarama-kutusu { border: 1px dashed #1e3a5f; background: #0c1524; border-radius: 10px; padding: 25px; text-align: center; margin: 20px 0; color: #b2c3d9; font-size: 16px; }

.ist-kutu {
    background-color: #121d33;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    color: white;
    height: 100%;
}
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. 5 SANİYEDE BİR YENİLEME MOTORU
st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

# 4. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_istatistik = "bta_site_istatistik_db.csv"
db_gecmis_kayitlar = "bta_hisse_gecmisi_db.csv"

# Veritabanı dosyalarını güvenli başlatma veya eski dosyayı otomatik dönüştürme
if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 196, "toplam_yildiz": 5, "oy_sayisi": 1}]).to_csv(db_istatistik, index=False)
else:
    try:
        df_eski_kontrol = pd.read_csv(db_istatistik)
        if "toplam_yildiz" not in df_eski_kontrol.columns:
            df_eski_kontrol["toplam_yildiz"] = 5
            df_eski_kontrol["oy_sayisi"] = 1
            df_eski_kontrol.to_csv(db_istatistik, index=False)
    except:
        pass

if not os.path.exists(db_gecmis_kayitlar):
    pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat", "Anlık Fiyat", "Kâr/Zarar Durumu"]).to_csv(db_gecmis_kayitlar, index=False)

# İstatistikleri Yükle ve Ziyaretçiyi Artır
df_ist = pd.read_csv(db_istatistik)
if "ziyaret_artirildi" not in st.session_state:
    df_ist.loc[0, "ziyaret_sayisi"] += 1
    df_ist.to_csv(db_istatistik, index=False)
    st.session_state["ziyaret_artirildi"] = True

ziyaret = int(df_ist.loc[0, "ziyaret_sayisi"])
toplam_yildiz = float(df_ist.loc[0, "toplam_yildiz"])
oy_sayisi = int(df_ist.loc[0, "oy_sayisi"])
mevcut_puan = round(toplam_yildiz / oy_sayisi, 1) if oy_sayisi > 0 else 5.0

# 5. PARILTILI BTA LOGO PANELİ
st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

# TRADINGVIEW CANLI BIST 100 MINI GRAFİK KARTI
bist_mini_widget = """
<div class="tradingview-widget-container" style="margin: auto; text-align: center; width: 100%; max-width: 450px;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://tradingview.com" async>
  {
  "symbol": "BIST:XU100", "width": "100%", "height": "95", "locale": "tr",
  "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": ""
  }
  </script>
</div>
"""
components.html(bist_mini_widget, height=100)

# ETKİLEŞİM VE İSTATİSTİK BÖLÜMÜ
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:2px; text-align:center;">📊 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)

col_met1, col_met2, col_oy = st.columns(3)

with col_met1:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">👁️ Toplam Ziyaret</span><br><b style="font-size:20px; color:#00ffcc;">{ziyaret} Kez</b></div>', unsafe_allow_html=True)

with col_met2:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">⭐ Platform Puanı</span><br><b style="font-size:20px; color:#00ffcc;">{mevcut_puan} / 5</b></div>', unsafe_allow_html=True)

with col_oy:
    yildiz_secimi = st.feedback("stars", key="bta_yildiz_sistemi")
    if yildiz_secimi is not None and f"oylandi_{yildiz_secimi}" not in st.session_state:
        verilen_puan = yildiz_secimi + 1
        df_ist.loc[0, "toplam_yildiz"] += verilen_puan
        df_ist.loc[0, "oy_sayisi"] += 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state[f"oylandi_{yildiz_secimi}"] = True
        st.toast(f"🎉 {verilen_puan} Yıldız verdiniz. Teşekkürler!", icon="⭐")
        st.rerun()

# SPK YASAL UYARI BÖLÜMÜ
yasal_html = """
<div style="background-color: #121d33; border: 1px solid #ff3344; border-radius: 8px; padding: 10px; margin-top: 5px; margin-bottom: 10px;">
    <p style="font-size:11px; color:#b2c3d9; line-height:1.5; text-align:justify; margin:0;">
        <b style="color:#ff3344;">⚠️ SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Burada yer alan yorum ve tavsiyeler, kişisel görüşlere dayanmaktadır. Mali durumunuza uygun olmayabilir. Veriler en az 15 dakika gecikmelidir.
    </p>
</div>
"""
st.markdown(yasal_html, unsafe_allow_html=True)
st.write("---")

# 6. ANA ANALİZ MOTORU (Otomatik Dosya Okuma)
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")

tablo_rows_html = ""
veri_var_mi = False
basarili_hisseler = []

if os.path.exists(excel_yolu):
    try:
        # Excel dosyasını oku
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        df_gecmis_db = pd.read_csv(db_gecmis_kayitlar)
        yeni_kayitlar = []
        
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG", "HİSELER KAYIT DEFTERİ"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                
                # Canlı Fiyat Çekimi
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                except:
                    pass
                
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 9.0:
                        basariliHisse_adi = ha.replace(".IS", "")
                        basarili_hisseler.append(f"<b>{basariliHisse_adi}</b> (%{or_dg:.2f})")
                    kz_str = f'▲ %{or_dg:.2f}' if or_dg >= 0 else f'▼ %{or_dg:.2f}'
                    kz_html = f'<span style="color:#00ff66;">{kz_str}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">{kz_str}</span>'
                else:
                    kz_str = "-"
                    kz_html = "<span>-</span>"
                
                # Canlı Tablo Satırı Oluştur
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_html}</td></tr>'
                
                # MÜKERRER KAYIT KONTROLÜ: Son 1 saat içinde aynı fiyattan kaydedilmişse tekrar yazma
                zaman_eski_sinir = excel_tarih_objesi - datetime.timedelta(hours=1)
                
                # Geçmiş veritabanında bu hisseye ait kayıtları filtrele
                hisse_kayitlari = df_gecmis_db[df_gecmis_db["Hisse"] == ha]
                mukerrer = False
                
                for _, k_row in hisse_kayitlari.iterrows():
                    try:
                        # Kayıt tarihini ayrıştır
                        k_tarih_str = k_row["Tarih"].split(" | ")[0]
                        k_tarih = datetime.datetime.strptime(k_tarih_str, "%d.%m.%Y - %H:%M")
                        
                        # Eğer 1 saatten daha yeniyse ve fiyat aynıysa mükerrer kabul et
                        if k_tarih > zaman_eski_sinir and k_row["Anlık Fiyat"] == f"{c_fiyat:,.2f} TL":
                            mukerrer = True
                            break
                    except:
                        pass
                
                if not mukerrer and c_fiyat > 0:
                    yeni_kayitlar.append({
                        "Tarih": excel_guncelleme_tarihi,
                        "BTA Puanı": p_temiz,
                        "Hisse": ha,
                        "Algoritmik Fiyat": f"{maliyet:,.2f} TL",
                        "Anlık Fiyat": f"{c_fiyat:,.2f} TL",
