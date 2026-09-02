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

DEFAULT_EXCEL_PATH = "nurican.xls.xlsm"

# Hafıza Başlatmaları (Session State)
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "ozel_takip_kutusu" not in st.session_state:
    st.session_state["ozel_takip_kutusu"] = {}
if "kisitli_liste" not in st.session_state:
    st.session_state["kisitli_liste"] = []
if "engellenen_kelimeler" not in st.session_state:
    st.session_state["engellenen_kelimeler"] = ["salak", "aptal", "küfür1", "küfür2"]
if "oda_sayisi" not in st.session_state:
    st.session_state["oda_sayisi"] = 1
if "ziyaret_sayaci" not in st.session_state:
    st.session_state["ziyaret_sayaci"] = 0

st.session_state["ziyaret_sayaci"] += 1

st.title("⚡ Sinyal Takip Merkezi")
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Son Panel Yenilenme Zamanı: {guncel_an}")

st.markdown("<div style='background-color: rgba(220, 38, 38, 0.15); border-left: 5px solid #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><p style='margin: 0; font-weight: bold; color: #f87171 !important;'>⚠️ SPK YASAL UYARI: Burada yer alan yatırım bilgi ve yorumları yatırım danışmanlığı kapsamında değildir. YATIRIM TAVSİYESİ KESİNLİKLE DEĞİLDİR.</p></div>", unsafe_allow_html=True)

# ==========================================
# 📂 EXCEL DOSYA YÜKLEME ALANI (GİZLİLİK KORUMALI)
# ==========================================
st.markdown("### 📁 Güncel Excel Dosyası Yükleme")
yuklenen_dosya = st.file_uploader("Güncel sinyal verilerinizi içeren Excel dosyasını seçin veya sürükleyin (.xlsx, .xlsm)", type=["xlsx", "xlsm"])

df_kaynak = None
if yuklenen_dosya is not None:
    try:
        excel_obj = pd.ExcelFile(yuklenen_dosya)
        sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names
        df_kaynak = pd.read_excel(yuklenen_dosya, sheet_name=sheet, header=None)
        st.info("🔒 Güncel Excel dosyası güvenli bellek üzerinde işlendi. Dış erişime tamamen kapatıldı.")
    except Exception as e:
        st.error(f"Yüklenen dosya okunurken hata oluştu: {e}")
elif os.path.exists(DEFAULT_EXCEL_PATH):
    try:
        excel_obj = pd.ExcelFile(DEFAULT_EXCEL_PATH)
        sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names
        df_kaynak = pd.read_excel(DEFAULT_EXCEL_PATH, sheet_name=sheet, header=None)
    except Exception as e:
        st.error(f"Varsayılan Excel okunurken hata oluştu: {e}")

BORSA_HISSELERI = ["RAYSG", "SONME", "ZEDUR", "DOCO", "LYDYE", "MRSHL", "CMBTN", "UFUK", "GUNDG", "MAALT", "VERUS", "ALCAR", "AYCES", "ALKLC", "KAPLM", "INGRM"]

# ==========================================
# 📊 YAN YANA PANEL DÜZENI
# ==========================================
sol_taraf, sag_taraf = st.columns([1.1, 0.9])

with sol_taraf:
    st.subheader("📈 Sinyal Üretim Merkezi")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
    with col_btn2:
        al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)
        
    # 🟡 1. ADIM: AL SAT SİNYAL GÖSTERİMİ (U SÜTUNU -> 20. İNDEKS)
    if al_sat_butonu and df_kaynak is not None:
        with st.spinner("Excel verileri işleniyor..."):
            tablo_verisi = []
            for i in range(len(df_kaynak)):
                try:
                    if df_kaynak.shape > 20:
                        u_hücre_degeri = str(df_kaynak.iloc[i, 20]).strip().upper() 
                        hisse_ham = str(df_kaynak.iloc[i, 0]).strip().upper()      
                        
                        hisse_temiz = None
                        for hisse in BORSA_HISSELERI:
                            if hisse in hisse_ham or hisse in u_hücre_degeri:
                                hisse_temiz = hisse
                                break
                        
                        # 🎯 KRİTİK GÜNCELLEME: SONME hissesinin AL-SAT (Sarı buton) altında görünmesini tamamen engelliyoruz
                        if hisse_temiz == "SONME":
                            continue
                            
                        if hisse_temiz and u_hücre_degeri and u_hücre_degeri != "NAN":
                            if "+" in u_hücre_degeri or "AL" in u_hücre_degeri or "SAT" in u_hücre_degeri:
                                excel_anlik_verisi = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if df_kaynak.shape > 7 else "0"
                                sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                                yüklenen_fiy = float(sayilar) if sayilar else 0.0
                                
                                ticker_kod = f"{hisse_temiz}.IS"
                                hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                                if not hisse_data.empty:
                                    canli_fiyat = hisse_data['Close'].iloc[-1]
                                    yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                                    durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                                    tablo_verisi.append({"Hisse Kodu": hisse_temiz, "Sinyal Metni": u_hücre_degeri, "Yüklenen Fiyat": f"{yüklenen_fiy:.2f} TL", "Canlı Fiyat": f"{canli_fiyat:.2f} TL", "Durum Oranı": durum_str})
                except:
                    pass
            if tablo_verisi:
                st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
            else:
                st.warning("Excel şablonunda aktif [AL SAT] kriterine uyan veri bulunamadı.")

    # 🟢 2. ADIM: AL SİNYALİNİ ÖZEL KUTUYA KAYDETME (W SÜTUNU -> 22. İNDEKS)
    if al_butonu and df_kaynak is not None:
        with st.spinner("AL sinyalleri hesaplanıyor..."):
            tablo_verisi_al = []
            for i in range(len(df_kaynak)):
                try:
                    if df_kaynak.shape > 22:
                        w_hücre_degeri = str(df_kaynak.iloc[i, 22]).strip().upper() 
                        hisse_ham = str(df_kaynak.iloc[i, 0]).strip().upper()      
                        
                        hisse_temiz = None
                        for hisse in BORSA_HISSELERI:
                            if hisse in hisse_ham or hisse in w_hücre_degeri:
                                hisse_temiz = hisse
                                break
                        
                        if hisse_temiz and w_hücre_degeri and w_hücre_degeri != "NAN":
                            # 🎯 SÖNME sadece bu yeşil buton altında AL sinyali olarak tetiklenecek
                            if "AL" in w_hücre_degeri or "SONME" in w_hücre_degeri:
                                excel_anlik_verisi = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if df_kaynak.shape > 7 else "0"
                                sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                                yüklenen_fiy = float(sayilar) if sayilar else 0.0
                                    
                                ticker_kod = f"{hisse_temiz}.IS"
                                hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                                if not hisse_data.empty:
                                    canli_fiyat = hisse_data['Close'].iloc[-1]
                                    yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                                    durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                                    
                                    st.session_state["ozel_takip_kutusu"][hisse_temiz] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                                    tablo_verisi_al.append({"Hisse Kodu": hisse_temiz, "Sinyal": w_hücre_degeri, "Yüklenen Fiyat": f"{yüklenen_fiy:.2f} TL", "Canlı Fiyat": f"{canli_fiyat:.2f} TL", "Durum Oranı": durum_str})
                except:
                    pass
            if tablo_verisi_al:
                st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
            else:
                st.warning("Excel şablonunda aktif [AL] kriterine uyan veri bulunamadı.")

    # 📦 SADECE AL SİNYALİ GELEN HİSSELERİN TAKİP KUTUSU
    if st.session_state["ozel_takip_kutusu"]:
        st.markdown("---")
        st.subheader("📥 Kaydedilen AL Sinyali Takip Kutusu")
        kutu_tablo = []
        for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
            try:
