import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

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
}
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. VERI TABANLARI KONTROLÜ
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"
db_gecmis_kayitlar = "bta_hisse_gecmisi_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}]).to_csv(db_istatistik, index=False)

if not os.path.exists(db_gecmis_kayitlar):
    pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"]).to_csv(db_gecmis_kayitlar, index=False)

ziyaret = 187
basarili = 15
basarisiz = 2

# 5. PARILTILI BTA LOGO PANELİ
st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

# EN ÜSTE TAŞINAN ETKİLEŞİM VE İSTATİSTİK BÖLÜMÜ
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:2px; text-align:center;">📊 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)

col_met1, col_met2, col_oy1, col_oy2 = st.columns(4)

with col_met1:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">👁️ Toplam Ziyaret</span><br><b style="font-size:20px; color:#00ffcc;">{ziyaret} Kez</b></div>', unsafe_allow_html=True)

with col_met2:
    st.markdown(f'<div class="ist-kutu"><span style="color:#b2c3d9; font-size:13px;">🎯 Başarı/Beğeni Oranı</span><br><b style="font-size:20px; color:#00ffcc;">%88</b></div>', unsafe_allow_html=True)

with col_oy1:
    st.button("👍 Başarılı Buldum", use_container_width=True)

with col_oy2:
    st.button("👎 Başarısız Buldum", use_container_width=True)

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

# 📁 EXCEL YÜKLEME ALANI
yuklenen_dosya = st.file_uploader("📁 Excel Dosyasını Buraya Yükleyin (.xlsm, .xlsx)", type=["xlsm", "xlsx"])

# 6. ANA ANALİZ MOTORU
excel_tarih_objesi = datetime.datetime.now()
excel_guncelleme_tarihi = excel_tarih_objesi.strftime("%d.%m.%Y - %H:%M")
tarih_kisa = excel_tarih_objesi.strftime("%d.%m.%Y %H:%M")

tablo_rows_html = ""
veri_var_mi = False
tebrik_metni = ""

df_excel = pd.DataFrame()
df_gecmis = pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"])

# 📌 [KRİTİK DÜZELTME]: Excel'i başlık satırı olmadan (header=None) okuyoruz, böylece 3. satıra direkt ulaşabiliyoruz
if yuklenen_dosya is not None:
    try:
        excel_dosyasi = pd.ExcelFile(yuklenen_dosya, engine="openpyxl")
        mevcut_sayfalar = excel_dosyasi.sheet_names
        hedef_sayfa = mevcut_sayfalar[0]
        for sayfa in mevcut_sayfalar:
            if sayfa.strip().upper() == "WEB":
                hedef_sayfa = sayfa
        # header=None diyerek saf koordinat sistemine geçtik
        df_excel = excel_dosyasi.parse(sheet_name=hedef_sayfa, header=None)
    except:
        pass

if os.path.exists(db_gecmis_kayitlar):
    try:
        df_gecmis = pd.read_csv(db_gecmis_kayitlar)
    except:
        pass

yeni_kayitlar = []

# 🎯 SİZİN BELİRTTİĞİNİZ TAM KOORDİNAT SİSTEMİ (A3, C3, D3)
# Python sıfırdan saydığı için: Satır 3 -> indeks 2, A -> 0, C -> 2, D -> 3 olur.
hisse_col = 0   # A sütunu
maliyet_col = 2 # C sütunu
puan_col = 3    # D sütunu
baslangic_satiri = 2 # 3. satır (A3, C3, D3)

if not df_excel.empty:
    for idx in range(baslangic_satiri, len(df_excel)):
        try:
            ha = str(df_excel.iloc[idx, hisse_col]).strip().upper() if pd.notna(df_excel.iloc[idx, hisse_col]) else ""
            alim_c = str(df_excel.iloc[idx, maliyet_col]).strip() if pd.notna(df_excel.iloc[idx, maliyet_col]) else ""
            puan_d = df_excel.iloc[idx, puan_col] if pd.notna(df_excel.iloc[idx, puan_col]) else ""
            
            if ha != "" and ha not in ["NAN", "NONE", "ANA", "KOD", "HİSSE KODU", "HİSSE"]:
                veri_var_mi = True
                p_temiz = "-"
                if pd.notna(puan_d) and str(puan_d).strip() != "":
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                
                # CANLI YFINANCE FIYAT MOTORU
                c_fiyat = 0.0
                try:
                    ticker_kod = ha if ha.endswith(".IS") else f"{ha}.IS"
                    h_veri = yf.Ticker(ticker_kod).history(period="1d", timeout=3)
                    if len(h_veri) > 0:
                        c_fiyat = float(h_veri['Close'].iloc[-1])
                except:
                    c_fiyat = 0.0
                
                alim_c_temiz = alim_c.replace(",", ".").strip()
                maliyet = float(alim_c_temiz) if alim_c_temiz != "" else 0.0
                
                # Not Defteri Kayıt Kontrolü
                if maliyet > 0:
                    is_exist = False
                    if not df_gecmis.empty:
                        is_exist = ((df_gecmis['Hisse'] == ha) & (df_gecmis['Algoritmik Fiyat'] == maliyet)).any()
                    if not is_exist:
                        yeni_kayitlar.append({"Tarih": tarih_kisa, "BTA Puanı": p_temiz, "Hisse": ha, "Algoritmik Fiyat": maliyet})

                # Kar/Zarar ve Tavan Durumu Hesabı
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 9.0:
                        tebrik_metni += f"<b>{ha.replace('.IS', '')}</b> (%{or_dg:.2f}) "
                    
                    if or_dg >= 0:
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>'
                    else:
                        kz_str = f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
        except:
            continue

if len(yeni_kayitlar) > 0:
    try:
        df_guncel_gecmis = pd.concat([df_gecmis, pd.DataFrame(yeni_kayitlar)], ignore_index=True)
        df_guncel_gecmis.to_csv(db_gecmis_kayitlar, index=False)
    except:
        pass

# 7. TAVAN BAŞARI TEBRİK MESAJI
if tebrik_metni != "":
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#00ffcc; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {tebrik_metni} hedefine ulaşarak %9 ve üzeri tavan performansı göstermiştir. Tebrik ederiz!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)

# 8. CANLI TABLO PANELİ
tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>' + tablo_rows_html + '</table>'
panel_html = f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 5px;"><p style="font-size:16px; font-weight:bold; color:#1E90FF; margin:0;">📈 BTA ALGORİTMİK HİSSE</p><p style="font-size:12px; font-weight:bold; color:#00ffcc; background-color:#121d33; padding:4px 10px; border-radius:6px; border:1px solid #1e3a5f; margin:0;">Son Yükleme: {excel_guncelleme_tarihi}</p></div>'
