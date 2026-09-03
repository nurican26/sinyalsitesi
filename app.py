import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("<style>.stApp{background:rgba(15,23,42,0.95)!important;padding:2rem;} h1,h2,h3,h4,h5,h6,p,span,label{color:#fff!important;} input{color:#000!important;background-color:#fff!important;}</style>", unsafe_allow_html=True)

for k in ["chat_history", "kisitli_liste"]:
    if k not in st.session_state: st.session_state[k] = []
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
for key in ["ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if key not in st.session_state: st.session_state[key] = 0

st.session_state["ziyaret_sayaci"] += 1
st.title("⚡ Sinyal Takip Merkezi")

puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
c1, c2 = st.columns(2)
c1.metric("🔥 Toplam Panel Beğenisi (Oy)", f"{st.session_state['topham_oy_sayisi']} Kişi")
c2.metric("⭐ Topluluk Puan Ortalaması", f"{puan:.2f} / 5.0")

st.success(f"💡 Sistem Aktif. Son Yenilenme: {datetime.datetime.now().strftime('%d.%m.%Y - %H:%M:%S')}")
st.markdown("<div style='background-color:rgba(220,38,38,0.15);border-left:5px solid #dc2626;padding:10px;border-radius:5px;margin-bottom:15px;'><p style='margin:0;font-weight:bold;color:#f87171!important;'>⚠️ SPK YASAL UYARI: Yatırım tavsiyesi değildir.</p></div>", unsafe_allow_html=True)

st.markdown("### 📁 Güncel Excel Dosyası Yükleme")
yuklenen_dosya = st.file_uploader("Excel dosyasını seçin (.xlsx, .xlsm)", type=["xlsx", "xlsm"])
df_kaynak = None
if yuklenen_dosya is not None:
    try:
        df_kaynak = pd.read_excel(yuklenen_dosya, sheet_name=0, header=None)
        st.info("🔒 Excel dosyası güvenli bellek üzerinde işlendi.")
    except Exception as e: st.error(f"Dosya okuma hatası: {e}")
elif os.path.exists("nurican.xls.xlsm"):
    try: df_kaynak = pd.read_excel("nurican.xls.xlsm", header=None)
    except: pass

BORSA_HISSELERI = ["RAYSG", "SONME", "ZEDUR", "DOCO", "LYDYE", "MRSHL", "CMBTN", "UFUK", "GUNDG", "MAALT", "VERUS", "ALCAR", "AYCES", "ALKLC", "KAPLM", "INGRM", "FORTE", "PKENT", "DUNYH"]

# ⚡ CANLI BORSA KÖŞESİ
st.subheader("🎯 Canlı Takip")
st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
canli_borsa_listesi = []

if df_kaynak is not None:
    for i in range(2, len(df_kaynak)):
        try:
            if len(df_kaynak.columns) > 20:
                rv = df_kaynak.iloc[i, 20]
                if pd.isna(rv): continue
                uv = str(rv).strip().upper()
                h_adi = next((h for h in BORSA_HISSELERI if h in uv), None)
                if h_adi:
                    f_str = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if len(df_kaynak.columns) > 7 else "0"
                    sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", f_str)
                    excel_fiyat = float(sayilar) if sayilar else 0.0
                    if excel_fiyat > 0:
                        canli_borsa_listesi.append({"Hisse Kodu": h_adi, "Excel Fiyatı": f"{excel_fiyat:.2f} TL", "Durum": "🔄 Aktif Listede"})
        except: pass

# Excel boşsa kullanıcı paneli boş görmesin diye test verisi basıyoruz
if not canli_borsa_listesi:
    canli_borsa_listesi = [
        {"Hisse Kodu": "RAYSG", "Excel Fiyatı": "150.50 TL", "Durum": "⚙️ Test Modu (Aktif)"},
        {"Hisse Kodu": "ZEDUR", "Excel Fiyatı": "85.20 TL", "Durum": "⚙️ Test Modu (Aktif)"},
        {"Hisse Kodu": "DOCO", "Excel Fiyatı": "4200.00 TL", "Durum": "⚙️ Test Modu (Aktif)"}
    ]

df_liste = pd.DataFrame(canli_borsa_listesi).drop_duplicates(subset=['Hisse Kodu'])
st.dataframe(df_liste, use_container_width=True, hide_index=True, height=250)

st.divider()

st.subheader("📈 Sinyal Üretim Merkezi")
b1, b2 = st.columns(2)
al_sat_butonu = b1.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
al_butonu = b2.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

if al_sat_butonu:
    tablo_verisi = []
    if df_kaynak is not None:
        for i in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 20:
                    rv = df_kaynak.iloc[i, 20]
                    if pd.isna(rv): continue
                    uv = str(rv).strip().upper()
                    if "SONME" in uv or "ALKLC" in uv: continue
                    h_adi = next((h for h in BORSA_HISSELERI if h in uv), None)
                    if h_adi:
                        f_str = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if len(df_kaynak.columns) > 7 else "0"
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", f_str)
                        yfiy = float(sayilar) if sayilar else 0.0
                        tablo_verisi.append({"Hisse Kodu": h_adi, "Sinyal Metni": uv, "Excel Fiyatı": f"{yfiy:.2f} TL", "Durum Oranı": "🟡 Sinyal Aktif"})
            except: pass
    if not tablo_verisi: # Excel boşsa örnek simülasyon verisi bas
        tablo_verisi = [
            {"Hisse Kodu": "RAYSG", "Sinyal Metni": "RAYSG DİRENÇ KIRILIMI AL SAT", "Excel Fiyatı": "150.50 TL", "Durum Oranı": "🟡 Test Sinyali"},
            {"Hisse Kodu": "DOCO", "Sinyal Metni": "DOCO HEDEF BÖLGESİ AL SAT", "Excel Fiyatı": "4200.00 TL", "Durum Oranı": "🟡 Test Sinyali"}
        ]
    st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)

if al_butonu:
    tablo_verisi_al = []
    if df_kaynak is not None:
        for i in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    rw = df_kaynak.iloc[i, 22]
                    if pd.isna(rw): continue
                    wv = str(rw).strip().upper()
                    h_adi = next((h for h in BORSA_HISSELERI if h in wv), None)
                    if h_adi:
                        f_str = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if len(df_kaynak.columns) > 7 else "0"
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", f_str)
                        cfiy = float(sayilar) if sayilar else 0.0
                        st.session_state["ozel_takip_kutusu"][h_adi] = {"kayit_fiyati": cfiy, "kayit_zamani": datetime.datetime.now().strftime("%H:%M")}
                        tablo_verisi_al.append({"Hisse Kodu": h_adi, "Sinyal": wv, "Excel Fiyatı": f"{cfiy:.2f} TL", "Durum Oranı": "🟢 Başladı"})
            except: pass
    if not tablo_verisi_al: # Excel boşsa örnek simülasyon verisi bas
        st.session_state["ozel_takip_kutusu"]["ZEDUR"] = {"kayit_fiyati": 85.20, "kayit_zamani": "02:15"}
        tablo_verisi_al = [{"Hisse Kodu": "ZEDUR", "Sinyal": "ZEDUR NET AL", "Excel Fiyatı": "85.20 TL", "Durum Oranı": "🟢 Test Sinyali"}]
    st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)

st.divider()

st.markdown("#### 🌟 Sinyal Havuzuna Alınan Hisseler")
if st.session_state["ozel_takip_kutusu"]:
    thavuz = []
    for hisse, bilgi in list(st.session_state["ozel_takip_kutusu"].items()):
        thavuz.append({"Hisse Kodu": hisse, "Giriş Fiyatı": f"{bilgi['kayit_fiyati']:.2f} TL", "Kayıt Zamanı": bilgi["kayit_zamani"]})
    if thavuz:
        st.dataframe(pd.DataFrame(thavuz), use_container_width=True, hide_index=True)
        if st.button("🗑️ Takip Listesini Temizle", use_container_width=True):
            st.session_state["ozel_takip_kutusu"] = {}; st.rerun()
else: st.info("Henüz takibe alınan dinamik bir hisse bulunmuyor.")

st.divider()

st.subheader("💬 Topluluk Sohbet Odası")
with st.form("mesaj_formu", clear_on_submit=True):
    msg_input = st.text_input("Mesajınızı yazın:", placeholder="Buraya yazın...")
    if st.form_submit_button("Gönder", use_container_width=True) and msg_input:
        st.session_state["chat_history"].insert(0, f"[{datetime.datetime.now().strftime('%H:%M')}] Kullanıcı: {msg_input}")
        st.rerun()
for msg in st.session_state["chat_history"]: st.write(msg)

st.divider()

st.markdown("#### 🗳️ Paneli Değerlendir")
with st.form("oylama_formu", clear_on_submit=True):
    puan_slider = st.slider("Panele Yıldız Verin (1-5):", 1, 5, 5, 1)
    if st.form_submit_button("Beğen ve Gönder", use_container_width=True):
        st.session_state["topham_oy_sayisi"] += 1
        st.session_state["topham_yildiz_puani"] += puan_slider
        st.success("Beğeniniz kaydedildi!"); st.rerun()
