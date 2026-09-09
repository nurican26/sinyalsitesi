import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; font-size: 14px !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

# Başlık
st.markdown('<h1 style="text-align:center; color:#00ffcc; font-family:\'Brush Script MT\', cursive, sans-serif; font-size:42px; margin-top:5px; margin-bottom:5px;">BTA</h1>', unsafe_allow_html=True)

st.write("---")
tum_hisseler = [] 
veri_var_mi = False

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                except:
                    pass
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE <span style="font-size:12px; color:#ff3344; font-weight:normal; margin-left:10px;">⚠️ Veriler en az 15 dk gecikmelidir.</span></p>', unsafe_allow_html=True)
        if veri_var_mi: 
            st.markdown(tablo_html, unsafe_allow_html=True)
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 4].dropna().unique()
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() != ""])
    except:
        pass
else:
    st.error("Excel bulunamadı.")

# SPK YASAL UYARI BÖLÜMÜ
st.markdown('''
<div style="background-color: #121d33; border: 1px solid #ff3344; border-radius: 8px; padding: 15px; margin-top: 15px; margin-bottom: 15px;">
    <p style="font-size:13px; font-weight:bold; color:#ff3344; margin-bottom:8px; text-transform: uppercase; letter-spacing: 0.5px;">
        ⚠️ ÖNEMLİ YASAL UYARI (15 DAKİKA GECİKMELİ VERİ)
    </p>
    <p style="font-size:12px; color:#b2c3d9; line-height:1.6; text-align:justify; margin:0;">
        Bu tabloda ve platform genelinde yer alan tüm fiyatlar, K/Z oranları ve algoritmik hesaplamalar en az <b>15 dakika gecikmeli</b> veriler kullanılarak otomatik olarak üretilmektedir. 
        Sitemiz tamamen ücretsiz, herkese açık ve genel bilgilendirme amacıyla yayın yapan bağımsız bir platform olup; burada yer alan 'BTA Puanı', 'Algoritmik Fiyat' veya diğer hiçbir veri, formül ve grafik çıktısı yatırım danışmanlığı, yatırım tavsiyesi, hedef fiyat öngörüsü veya al/sat/tut yönlendirmesi niteliği taşımamaktadır.
    </p>
</div>
''', unsafe_allow_html=True)

st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
if len(tum_hisseler) > 0:
    aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler, key="arama_motoru_select")
    if aranan_hisse != "Seçiniz...":
        try:
            h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
            if len(h_detay_veri) > 0:
                st.metric("Güncel Fiyat (15 Dk Gecikmeli)", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
        except:
            pass

st.write("---")
col_not1, col_not2 = st.columns(2)

with col_not1:
    st.markdown('<p style="font-size:14px; font-weight:bold; color:#fff;">Yeni Not Ekle</p>', unsafe_allow_html=True)
    not_hisse_secim = st.selectbox("Not Alınacak Hisse", ["Manuel Gir..."] + tum_hisseler if tum_hisseler else ["Manuel Gir..."], key="not_hisse_v_sec")
    
    if not_hisse_secim == "Manuel Gir...":
        not_hisse = st.text_input("Hisse Kodu (Örn: THYAO):", max_chars=10, key="not_manuel_hisse_kod").strip().upper()
    else:
        not_hisse = not_hisse_secim
        
    not_hedef_fiyat = st.number_input("Hedef Fiyat (TL):", min_value=0.0, value=0.0, step=1.0, key="not_hedef_fiyat_input")
    hisse_notu = st.text_area("Hisse Hakkındaki Notunuz:", max_chars=500, placeholder="Stratejinizi yazın...", key="hisse_notu_metni")
    
    if st.button("Notu Kaydet 💾", use_container_width=True, key="notu_kaydet_butonu"):
        if not_hisse and hisse_notu.strip():
            try:
                df_notlar = pd.read_csv(db_notlar)
                yeni_id = str(int(time.time() * 1000))
                su_an_tarih = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                yeni_not_veri = pd.DataFrame([[yeni_id, su_an_tarih, str(not_hisse), str(hisse_notu.strip()), float(not_hedef_fiyat)]], columns=["id", "tarih", "hisse", "not", "hedef_fiyat"])
                df_notlar = pd.concat([df_notlar, yeni_not_veri], ignore_index=True)
                df_notlar.to_csv(db_notlar, index=False)
                st.success("Not kaydedildi!")
                time.sleep(0.5)
                st.rerun()
            except:
                pass

with col_not2:
    st.markdown('<div style="color:#fff; font-size:14px; font-weight:bold; margin-bottom:10px;">🔒 Yönetici Not Paneli</div>', unsafe_allow_html=True)
    
    # Giriş şifresi kutusu (Varsayılan olarak "1905" ayarladım, aşağıdan değiştirebilirsiniz)
    admin_sifre = st.text_input("Görmek ve silmek için Yönetici Şifresini girin:", type="password", key="not_paneli_giris_sifresi")
    
    if admin_sifre == "1905":  # <--- ŞİFRENİZ BURADA
        st.success("Yönetici girişi başarılı. Notlar listeleniyor.")
        if os.path.exists(db_notlar):
            df_notlar_oku = pd.read_csv(db_notlar)
            if not df_notlar_oku.empty:
                df_notlar_oku = df_notlar_oku.iloc[::-1]
                for i, row in df_notlar_oku.iterrows():
                    with st.expander(f"📌 {row['hisse']} - {row['tarih']}"):
                        st.write(f"**Not:** {row['not']}")
                        st.write(f"**Hedef Fiyat:** {row['hedef_fiyat']} TL")
                        
                        # Her nota özel Kırmızı Silme Butonu
                        if st.button(f"Bu Notu Kalıcı Olarak Sil ❌", key=f"sil_btn_{row['id']}", use_container_width=True):
                            try:
                                # Güncel CSV'yi tekrar oku ve ilgili ID'yi uçur
                                df_guncel = pd.read_csv(db_notlar)
                                df_guncel = df_guncel[df_guncel['id'].astype(str) != str(row['id'])]
                                df_guncel.to_csv(db_notlar, index=False)
                                st.error("Not silindi! Sayfa yenileniyor...")
                                time.sleep(0.8)
                                st.rerun()
                            except:
                                pass
            else:
                st.info("Kayıtlı hiçbir not bulunamadı.")
    elif admin_sifre != "":
        st.error("Hatalı yönetici şifresi! Erişim engellendi.")
