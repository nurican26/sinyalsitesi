
import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re

# Sayfa TasarÄ±m AyarlarÄ±
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="ğŸ“ˆ", layout="centered")

# ==========================================
# ğŸ¨ BORSA TEMALI ARKA PLAN VE CSS AYARLARI
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
# ğŸ“ˆ PANEL ANA EKRANI
# ==========================================
st.title("âš¡ Sinyal Takip Merkezi")
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"ğŸ’¡ Sistem Aktif. Son Panel Yenilenme ZamanÄ±: {guncel_an}")

st.markdown("---")
st.subheader("Sinyal Ãœretim Merkezi")

col1, col2 = st.columns(2)
with col1:
    al_sat_butonu = st.button("ğŸŸ¡ AL SAT SÄ°NYALÄ°NÄ° GÃ–STER", use_container_width=True)
with col2:
    al_butonu = st.button("ğŸŸ¢ AL SÄ°NYALÄ°NÄ° GÃ–STER", use_container_width=True)

# ğŸŸ¡ 1. ADIM: AL SAT SÄ°NYAL GÃ–STERÄ°MÄ° (U SÃœTUNU - 20. Ä°NDEKS)
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
                    
                    # U SÃ¼tununu kontrol et (20. indeks)
                    bta_sinyal_al_sat = str(df.iloc[i, 20]).strip().upper() if df.shape[1] > 20 else ""
                    
                    if not hisse_kodu_ham or hisse_kodu_ham == "NAN" or hisse_kodu_ham == "":
                        continue
                        
                    hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                    
                    # SÃ¼tunda artÄ± iÅŸareti veya AL SAT yazÄ±sÄ± arama
                    if "+" in bta_sinyal_al_sat or "AL" in bta_sinyal_al_sat:
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                        yÃ¼klenen_fiy = float(sayilar[0]) if sayilar else 0.0
                        
                        ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                        
                        if not hisse_data.empty:
                            canli_fiyat = hisse_data['Close'].iloc[-1]
                            yuzde_fark = ((canli_fiyat - yÃ¼klenen_fiy) / yÃ¼klenen_fiy) * 100 if yÃ¼klenen_fiy > 0 else 0.0
                            durum_str = f"ğŸŸ¢ %{yuzde_fark:.2f} KazandÄ±" if canli_fiyat >= yÃ¼klenen_fiy else f"ğŸ”´ %{abs(yuzde_fark):.2f} Ä°Ã§eride"
                            
                            tablo_verisi.append({
                                "Hisse Kodu": hisse_temiz,
                                "YÃ¼klediÄŸiniz Fiyat": f"{yÃ¼klenen_fiy:.2f} TL",
                                "AnlÄ±k CanlÄ± Fiyat": f"{canli_fiyat:.2f} TL",
                                "CanlÄ± Kar/Zarar OranÄ±": durum_str
                            })
                
                if tablo_verisi:
                    st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
                else:
                    st.warning("U sÃ¼tununda aktif Al-Sat sinyali bulunamadÄ±.")
            except Exception as e:
                st.error(f"Veri iÅŸleme hatasÄ±: {e}")
        else:
            st.error("Excel dosyasÄ± bulunamadÄ±!")

# ğŸŸ¢ 2. ADIM: AL SÄ°NYAL GÃ–STERÄ°MÄ° (W SÃœTUNU - 22. Ä°NDEKS)
if al_butonu:
    with st.spinner("Aktif AL veren hisseler hesaplanÄ±yor..."):
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
                    
                    # W SÃ¼tununu kontrol et (22. indeks)
                    w_sutun_verisi = str(df.iloc[i, 22]).strip().upper() if df.shape[1] > 22 else ""
                    
                    if not hisse_kodu_ham or hisse_kodu_ham == "NAN" or hisse_kodu_ham == "":
                        continue
                        
                    hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                    
                    # W sÃ¼tununda [AL] ifadesi geÃ§iyorsa listele
                    if "[AL]" in w_sutun_verisi or "AL" in w_sutun_verisi:
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                        yÃ¼klenen_fiy = float(sayilar[0]) if sayilar else 0.0
                        
                        ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                        
                        if not hisse_data.empty:
                            canli_fiyat = hisse_data['Close'].iloc[-1]
                            yuzde_fark = ((canli_fiyat - yÃ¼klenen_fiy) / yÃ¼klenen_fiy) * 100 if yÃ¼klenen_fiy > 0 else 0.0
                            durum_str = f"ğŸŸ¢ %{yuzde_fark:.2f} KazandÄ±" if canli_fiyat >= yÃ¼klenen_fiy else f"ğŸ”´ %{abs(yuzde_fark):.2f} Ä°Ã§eride"
                            
                            tablo_verisi_al.append({
                                "Hisse Kodu": hisse_temiz,
                                "Sinyal Durumu": f"{hisse_temiz} [AL]",
                                "YÃ¼klediÄŸiniz Fiyat": f"{yÃ¼klenen_fiy:.2f} TL",
                                "AnlÄ±k CanlÄ± Fiyat": f"{canli_fiyat:.2f} TL",
                                "CanlÄ± Kar/Zarar OranÄ±": durum_str
                            })
                
                if tablo_verisi_al:
                    st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
                else:
                    st.warning("W sÃ¼tununda aktif [AL] sinyali bulunamadÄ±.")
            except Exception as e:
                st.error(f"Sinyal hesaplama hatasÄ±: {e}")
        else:
            st.error("Excel dosyasÄ± bulunamadÄ±!")

# ==========================================
# ğŸ’¬ 3. BÃ–LÃœM: BTA SOHBET ODASI
# ==========================================
st.markdown("---")
st.subheader("ğŸ’¬ BTA Sohbet OdasÄ±")

isat = st.text_input("Sohbet Takma AdÄ±nÄ±z:", value="Nurican")
mesaj = st.text_input("MesajÄ±nÄ±zÄ± yazÄ±n:", placeholder="Ã–rn: Hisseler bugÃ¼n Ã§ok iyi gidiyor...")

if st.button("MesajÄ± GÃ¶nder ğŸš€"):
    if mesaj:
        zaman = datetime.datetime.now().strftime("%H:%M")
        st.session_state["chat_history"].append(f"â±ï¸ {zaman} - **{isat}**: {mesaj}")
        st.rerun()

st.write("ğŸ“œ **Mesaj GeÃ§miÅŸi**")
if st.session_state["chat_history"]:
    for m in reversed(st.session_state["chat_history"]):
        st.info(m)
else:
    st.caption("HenÃ¼z mesaj yazÄ±lmamÄ±ÅŸ. Ä°lk mesajÄ± siz yazÄ±n! ğŸ‘‡")
