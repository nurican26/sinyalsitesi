import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re

# Sayfa Tasarım Ayarları (Geniş Ekran Düzeni)
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="wide")

# ==========================================
# 🎨 BORSA TEMALI ARKA PLAN VE CSS AYARLARI
# ==========================================
arka_plan_resmi_url = "https://unsplash.com"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('{arka_plan_resmi_url}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .block-container {{
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 1rem;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: #ffffff !important;
    }}
    input {{
        color: #000000 !important;
        background-color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

EXCEL_FILE_PATH = "nurican.xls.xlsm"

# Hafıza Başlatmaları (Session State)
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "ozel_takip_kutusu" not in st.session_state:
    st.session_state["ozel_takip_kutusu"] = {}
if "kisitli_liste" not in st.session_state:
    st.session_state["kisitli_liste"] = []
if "oda_sayisi" not in st.session_state:
    st.session_state["oda_sayisi"] = 1

# Otomatik Filtrelenecek Kelimeler
YASAKLI_KELIMELER = ["salak", "aptal", "küfür1", "küfür2"]

# Ana Başlıklar
st.title("⚡ Sinyal Takip Merkezi")
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Son Panel Yenilenme Zamanı: {guncel_an}")

# En Üstte Sabit SPK Yasal Uyarı Şeridi
st.markdown("<div style='background-color: rgba(220, 38, 38, 0.15); border-left: 5px solid #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><p style='margin: 0; font-weight: bold; color: #f87171 !important;'>⚠️ SPK YASAL UYARI: Burada yer alan yatırım bilgi ve yorumları yatırım danışmanlığı kapsamında değildir. YATIRIM TAVSİYESİ KESİNLİKLE DEĞİLDİR.</p></div>", unsafe_allow_html=True)

# ==========================================
# 📊 YAN YANA PANEL DÜZENİ (SOL: SİNYALLER | SAĞ: SOHBET)
# ==========================================
sol_taraf, sag_taraf = st.columns([1.1, 0.9])

with sol_taraf:
    st.subheader("📈 Sinyal Üretim Merkezi")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
    with col_btn2:
        al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)
        
    # 🟡 AL SAT Sinyal Tablosu
    if al_sat_butonu:
        with st.spinner("Excel verileri okunuyor..."):
            if os.path.exists(EXCEL_FILE_PATH):
                try:
                    excel_obj = pd.ExcelFile(EXCEL_FILE_PATH)
                    sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names
                    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet)
                    tablo_verisi = []
                    for i in range(len(df)):
                        hisse_kodu_ham = str(df.iloc[i, 0]).strip().upper()
                        excel_anlik_verisi = str(df.iloc[i, 7]).replace(",", ".").strip()
                        bta_sinyal_al_sat = str(df.iloc[i, 20]).strip().upper() if df.shape[1] > 20 else ""
                        if not hisse_kodu_ham or hisse_kodu_ham in ["NAN", ""]: continue
                        hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                        if "+" in bta_sinyal_al_sat or "AL" in bta_sinyal_al_sat:
                            sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                            yüklenen_fiy = float(sayilar) if sayilar else 0.0
                            ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                            hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                            if not hisse_data.empty:
                                canli_fiyat = hisse_data['Close'].iloc[-1]
                                yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                                tablo_verisi.append({"Hisse Kodu": hisse_temiz, "Yüklenen Fiyat": f"{yüklenen_fiy:.2f} TL", "Canlı Fiyat": f"{canli_fiyat:.2f} TL", "Durum Oranı": durum_str})
                    if tablo_verisi: st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
                except Exception as e: st.error(f"Hata: {e}")
            else: st.error("Excel bulunamadı!")

    # 🟢 AL Sinyali & Farklı Kutuya Kayıt
    if al_butonu:
        with st.spinner("AL sinyalleri hesaplanıyor..."):
            if os.path.exists(EXCEL_FILE_PATH):
                try:
                    excel_obj = pd.ExcelFile(EXCEL_FILE_PATH)
                    sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names
                    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet)
                    tablo_verisi_al = []
                    for i in range(len(df)):
                        hisse_kodu_ham = str(df.iloc[i, 0]).strip().upper()
                        excel_anlik_verisi = str(df.iloc[i, 7]).replace(",", ".").strip()
                        w_sutun_verisi = str(df.iloc[i, 22]).strip().upper() if df.shape > 22 else ""
                        if not hisse_kodu_ham or hisse_kodu_ham in ["NAN", ""]: continue
                        hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                        if "[AL]" in w_sutun_verisi or "AL" in w_sutun_verisi:
                            sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                            yüklenen_fiy = float(sayilar) if sayilar else 0.0
                            ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                            hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                            if not hisse_data.empty:
                                canli_fiyat = hisse_data['Close'].iloc[-1]
                                yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                                st.session_state["ozel_takip_kutusu"][hisse_temiz] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")}
                                tablo_verisi_al.append({"Hisse Kodu": hisse_temiz, "Sinyal": f"{hisse_temiz} [AL]", "Yüklenen Fiyat": f"{yüklenen_fiy:.2f} TL", "Canlı Fiyat": f"{canli_fiyat:.2f} TL", "Durum Oranı": durum_str})
                    if tablo_verisi_al: st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
                except Exception as e: st.error(f"Hata: {e}")

    # 📦 Yeni Sütunlu Özel Takip Kutusu
    if st.session_state["ozel_takip_kutusu"]:
        st.markdown("---")
        st.subheader("📥 Kaydedilen AL Sinyali Takip Kutusu")
        kutu_tablo = []
        for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
            hisse_data = yf.Ticker(f"{hisse}.IS").history(period="1d")
            if not hisse_data.empty:
                guncel_canli = hisse_data['Close'].iloc[-1]
                eski_fiyat = bilge["kayit_fiyati"]
                yuzde_fark = ((guncel_canli - eski_fiyat) / eski_fiyat) * 100 if eski_fiyat > 0 else 0.0
                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if guncel_canli >= eski_fiyat else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                kutu_tablo.append({"Hisse Kodu": hisse, "Kutuya Kayıt Fiyatı (O Anlık)": f"{eski_fiyat:.2f} TL", "Güncel Canlı Fiyat": f"{guncel_canli:.2f} TL", "Anlık Kar/Zarar Oranı": durum_str, "Kayıt Zamanı": bilge["kayit_zamani"]})
        if kutu_tablo:
            st.dataframe(pd.DataFrame(kutu_tablo), use_container_width=True, hide_index=True)
            if st.button("🗑️ Kutuyu Sıfırla"):
                st.session_state["ozel_takip_kutusu"] = {}
                st.rerun()

with sag_taraf:
    st.subheader("💬 BTA Sohbet Odası")
    isat = st.text_input("Sohbet Takma Adınız:", value="BTA Sohbet")
    
    # Python 3.14 için büyük-küçük esnek admin kontrol yapısı
    if isat.strip().lower() == "nurican":
        st.markdown(f"### 🚪 Oda Sayısı: {st.session_state['oda_sayisi']} | 👑 Yetkili Girişi")
        engellenecek = st.text_input("Kısıtlanacak Kullanıcı Adı:")
        if st.button("❌ Kullanıcıyı Kısıtla"):
            if engellenecek.strip():
                st.session_state["kisitli_liste"].append(engellenecek.strip())
                st.success(f"{engellenecek} kısıtlandı.")
        if st.button("🗑️ Tüm Mesajları Temizle"):
            st.session_state["chat_history"] = []
            st.rerun()
            
    mesaj = st.text_input("Mesajınızı yazın:")
    if st.button("Mesajı Gönder 🚀") and mesaj.strip():
        mesaj_kucuk = mesaj.strip().lower()
        iceriyor_mu = any(yasakli in mesaj_kucuk for yasakli in YASAKLI_KELIMELER)
        if isat.strip() in st.session_state["kisitli_liste"]:
            st.error("🚫 Bu odada mesaj yazma yetkiniz kısıtlanmıştır!")
        elif iceriyor_mu:
