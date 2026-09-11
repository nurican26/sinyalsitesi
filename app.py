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
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }

/* Sabit ve Şık BTA Logo Alanı */
.bta-ana-logo {
    text-align: center;
    font-family: 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 65px; 
    color: #00ffcc;
    margin: 10px 0 !important;
    text-shadow: 0 0 10px #00ffcc, 0 0 20px #1e90ff, 0 0 35px #0d9488;
}

.borsa-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.tebrik-kutusu { border: 2px solid #00ffcc; box-shadow: 0 0 15px #00ffcc, inset 0 0 10px rgba(0,255,204,0.3); background: #121d33; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; }
.tarama-kutusu { border: 1px dashed #1e3a5f; background: #0c1524; border-radius: 10px; padding: 25px; text-align: center; margin: 20px 0; color: #b2c3d9; font-size: 16px; }
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. VERİ TABANLARI VE EXCEL YOLLARI
excel_yolu = "bta.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"
db_istatistik = "bta_site_istatistik_db.csv"
db_gecmis_kayitlar = "bta_hisse_gecmisi_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}]).to_csv(db_istatistik, index=False)

if not os.path.exists(db_gecmis_kayitlar):
    pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"]).to_csv(db_gecmis_kayitlar, index=False)

# 4. ZİYARETÇİ SAYACINI TETİKLEME VE OY VERME MOTORU
ziyaret, basarili, basarisiz = 0, 0, 0
if os.path.exists(db_istatistik):
    try:
        df_ist = pd.read_csv(db_istatistik)
        if df_ist.empty:
            df_ist = pd.DataFrame([{"ziyaret_sayisi": 0, "basarili_oy": 0, "basarisiz_oy": 0}])
        
        if "ziyaret_sayildi" not in st.session_state:
            df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
            df_ist.to_csv(db_istatistik, index=False)
            st.session_state["ziyaret_sayildi"] = True
            
        ziyaret = int(df_ist.at[0, "ziyaret_sayisi"])
        basarili = int(df_ist.at[0, "basarili_oy"])
        basarisiz = int(df_ist.at[0, "basarisiz_oy"])
    except:
        ziyaret, basarili, basarisiz = 174, 15, 2

# 5. PARILTILI BTA LOGO PANELİ (Kilitlenmeyi önlemek için sabitlendi)
st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

# 🔄 VERİLERİ YENİLEME BUTONU
st.write("")
col_btn, _ = st.columns([1, 2])
with col_btn:
    yenile_butonu = st.button("🔄 Verileri Yenile ve Kontrol Et", use_container_width=True)

# 6. ANA ANALİZ MOTORU
excel_tarih_objesi = datetime.datetime.now()
gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
excel_guncelleme_tarihi = excel_tarih_objesi.strftime(f"%d.%m.%Y - %H:%M | {gunler_tr[excel_tarih_objesi.weekday()]}")
tarih_kisa = excel_tarih_objesi.strftime("%d.%m.%Y %H:%M")

tablo_rows_html = ""
veri_var_mi = False
basarili_hisseler = []

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        try:
            df_gecmis = pd.read_csv(db_gecmis_kayitlar)
        except:
            df_gecmis = pd.DataFrame(columns=["Tarih", "BTA Puanı", "Hisse", "Algoritmik Fiyat"])
        
        yeni_kayitlar = []

        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                
                if pd.isna(puan_d) or str(puan_d).strip().lower() in ["nan", "none", ""]:
                    p_temiz = "-"
                else:
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    
                c_fiyat = 0.0
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=3)
                    if len(h_veri) > 0:
                        c_fiyat = float(h_veri['Close'].iloc[-1])
                except:
                    pass
                
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                
                # Değişiklik kontrolü ve geçmiş kayıt (Not Defteri)
                if maliyet > 0:
                    if not ((df_gecmis['Hisse'] == ha) & (df_gecmis['Algoritmik Fiyat'] == maliyet)).any():
                        yeni_kayitlar.append({
                            "Tarih": tarih_kisa,
                            "BTA Puanı": p_temiz,
                            "Hisse": ha,
                            "Algoritmik Fiyat": maliyet
                        })

                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 9.0:
                        basariliHisse_adi = ha.replace(".IS", "")
                        basarili_hisseler.append(f"<b>{basariliHisse_adi}</b> (%{or_dg:.2f})")
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                
                tablo_rows_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
        
        if yeni_kayitlar:
            df_yeni = pd.DataFrame(yeni_kayitlar)
            df_guncel_gecmis = pd.concat([df_gecmis, df_yeni], ignore_index=True)
            df_guncel_gecmis.to_csv(db_gecmis_kayitlar, index=False)

    except Exception as e:
        st.error(f"Excel dosyası okunamıyor veya biçimi hatalı: {e}")

# Algoritmik Başarı Tebrik Paneli
if basarili_hisseler:
    hisseler_str = ", ".join(basarili_hisseler)
    tebrik_html = f'<div class="tebrik-kutusu"><h3 style="color:#00ffcc; margin:0 0 5px 0; font-size:18px; font-weight:bold;">⚡ ALGORİTMİK BAŞARI ANALİZİ ⚡</h3><p style="color:#ffffff; font-size:14px; margin:0;">Sistemimizde takip edilen {hisseler_str} hedefine ulaşarak %9 ve üzeri performans göstermiştir. Tebrik ederiz!</p></div>'
    st.markdown(tebrik_html, unsafe_allow_html=True)

# Canlı Algoritmik Hisse Tablosu
if veri_var_mi and tablo_rows_html != "":
    tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>' + tablo_rows_html + '</table>'
    panel_html = f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 5px;"><p style="font-size:16px; font-weight:bold; color:#1E90FF; margin:0;">📈 BTA ALGORİTMİK HİSSE</p><p style="font-size:12px; font-weight:bold; color:#00ffcc; background-color:#121d33; padding:4px 10px; border-radius:6px; border:1px solid #1e3a5f; margin:0;">Son Yükleme: {excel_guncelleme_tarihi}</p></div>'
    st.markdown(panel_html, unsafe_allow_html=True)
    st.markdown(tablo_html, unsafe_allow_html=True)
else:
    tarama_html = '<div class="tarama-kutusu"><div style="font-size: 32px; margin-bottom: 10px;">🔍</div><p style="color: #00ffcc; font-weight: bold; margin-bottom: 5px; font-size: 18px; text-shadow: 0 0 5px rgba(0,255,204,0.3);">BTA Algoritması Piyasaları Tarıyor...</p><p style="margin: 0; font-size: 14px; color: #a2b4cc; line-height:1.6;">Kriterlere tam uyum sağlayan yeni bir hisse tespit edildiğinde, analiz verileri anında bu ekrana yansıtılacaktır.</p></div>'
    st.markdown(tarama_html, unsafe_allow_html=True)

# 7. RESMİ SPK YASAL UYARI BÖLÜMÜ
yasal_html = """
<div style="background-color: #121d33; border: 1px solid #ff3344; border-radius: 8px; padding: 12px; margin-top: 15px;">
    <p style="font-size:12px; color:#b2c3d9; line-height:1.6; text-align:justify; margin:0;">
        <b style="color:#ff3344;">⚠️ SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
        Yatırım danışmanlığı hizmeti, aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak 
        yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel 
        görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan 
        bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Veriler en az 15 dakika gecikmelidir.
    </p>
</div>
"""
