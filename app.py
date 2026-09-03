
import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

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
        background: rgba(15, 23, 42, 0.90);
        backdrop-filter: blur(10px);
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

EXCEL_FILE_PATH = "nurican.xls.xlsm"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# 📈 PANEL ANA EKRANI
# ==========================================
st.title("⚡ Sinyal Takip Merkezi")
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Son Panel Yenilenme Zamanı: {guncel_an}")

st.markdown("---")
st.subheader("Sinyal Üretim Merkezi")

col1, col2 = st.columns(2)
with col1:
    al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
with col2:
    al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# 🟡 1. ADIM: AL SAT SİNYAL GÖSTERİMİ (U SÜTUNU - 20. İNDEKS)
if al_sat_butonu:
    with st.spinner("Excel verileri okunuyor..."):
        if os.path.exists(EXCEL_FILE_PATH):
            try:
                excel_obj = pd.ExcelFile(EXCEL_FILE_PATH)
                sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names[0]
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet)
                
                tablo_verisi = []
                for i in range(len(df)):
                    if i >= len(df):
                        break
                    
                    hisse_kodu_ham = str(df.iloc[i, 0]).strip().upper()
                    excel_anlik_verisi = str(df.iloc[i, 7]).replace(",", ".").strip()
                    
                    # U Sütununu kontrol et (20. indeks)
                    bta_sinyal_al_sat = str(df.iloc[i, 20]).strip().upper() if df.shape[1] > 20 else ""
                    
                    if not hisse_kodu_ham or hisse_kodu_ham == "NAN" or hisse_kodu_ham == "":
                        continue
                        
                    hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                    
                    # Sütunda artı işareti veya AL SAT yazısı arama
                    if "+" in bta_sinyal_al_sat or "AL" in bta_sinyal_al_sat:
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                        yüklenen_fiy = float(sayilar[0]) if sayilar else 0.0
                        
                        ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                        
                        if not hisse_data.empty:
                            canli_fiyat = hisse_data['Close'].iloc[-1]
                            yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                            durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                            
                            tablo_verisi.append({
                                "Hisse Kodu": hisse_temiz,
                                "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL",
                                "Anlık Canlı Fiyat": f"{canli_fiyat:.2f} TL",
                                "Canlı Kar/Zarar Oranı": durum_str
                            })
                
                if tablo_verisi:
                    st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
                else:
                    st.warning("U sütununda aktif Al-Sat sinyali bulunamadı.")
            except Exception as e:
                st.error(f"Veri işleme hatası: {e}")
        else:
            st.error("Excel dosyası bulunamadı!")

# 🟢 2. ADIM: AL SİNYAL GÖSTERİMİ (W SÜTUNU - 22. İNDEKS)
if al_butonu:
    with st.spinner("Aktif AL veren hisseler hesaplanıyor..."):
        if os.path.exists(EXCEL_FILE_PATH):
            try:
                excel_obj = pd.ExcelFile(EXCEL_FILE_PATH)
                sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names[0]
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet)
                
                tablo_verisi_al = []
                for i in range(len(df)):
                    if i >= len(df):
                        break
                        
                    hisse_kodu_ham = str(df.iloc[i, 0]).strip().upper()
                    excel_anlik_verisi = str(df.iloc[i, 7]).replace(",", ".").strip()
                    
                    # W Sütununu kontrol et (22. indeks)
                    w_sutun_verisi = str(df.iloc[i, 22]).strip().upper() if df.shape[1] > 22 else ""
                    
                    if not hisse_kodu_ham or hisse_kodu_ham == "NAN" or hisse_kodu_ham == "":
                        continue
                        
                    hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                    
                    # W sütununda [AL] ifadesi geçiyorsa listele
                    if "[AL]" in w_sutun_verisi or "AL" in w_sutun_verisi:
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                        yüklenen_fiy = float(sayilar[0]) if sayilar else 0.0
                        
                        ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                        
                        if not hisse_data.empty:
                            canli_fiyat = hisse_data['Close'].iloc[-1]
                            yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                            durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                            
                            tablo_verisi_al.append({
                                "Hisse Kodu": hisse_temiz,
                                "Sinyal Durumu": f"{hisse_temiz} [AL]",
                                "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL",
                                "Anlık Canlı Fiyat": f"{canli_fiyat:.2f} TL",
                                "Canlı Kar/Zarar Oranı": durum_str
                            })
                
                if tablo_verisi_al:
                    st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
                else:
                    st.warning("W sütununda aktif [AL] sinyali bulunamadı.")
            except Exception as e:
                st.error(f"Sinyal hesaplama hatası: {e}")
        else:
            st.error("Excel dosyası bulunamadı!")

# ==========================================
# 💬 3. BÖLÜM: BTA SOHBET ODASI
# ==========================================
st.markdown("---")
st.subheader("💬 BTA Sohbet Odası")

isat = st.text_input("Sohbet Takma Adınız:", value="Nurican")
mesaj = st.text_input("Mesajınızı yazın:", placeholder="Örn: Hisseler bugün çok iyi gidiyor...")

if st.button("Mesajı Gönder 🚀"):
    if mesaj:
        zaman = datetime.datetime.now().strftime("%H:%M")
        st.session_state["chat_history"].append(f"⏱️ {zaman} - **{isat}**: {mesaj}")
        st.rerun()

st.write("📜 **Mesaj Geçmişi**")
if st.session_state["chat_history"]:
    for m in reversed(st.session_state["chat_history"]):
        st.info(m)
else:
    st.caption("Henüz mesaj yazılmamış. İlk mesajı siz yazın! 👇")
