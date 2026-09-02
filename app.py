import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re
import time
import threading

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

# ==========================================
# 🎨 BORSA TEMALI ARKA PLAN VE CSS AYARLARI
# ==========================================
arka_plan_resmi_url = "https://unsplash.com"

css_kodlari = (
    "<style>"
    ".stApp {"
    "    background-image: url('" + arka_plan_resmi_url + "');"
    "    background-size: cover;"
    "    background-position: center;"
    "    background-attachment: fixed;"
    "}"
    ".block-container {"
    "    background: rgba(15, 23, 42, 0.90);"
    "    backdrop-filter: blur(10px);"
    "    padding: 3rem;"
    "    border-radius: 15px;"
    "    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);"
    "    border: 1px solid rgba(255, 255, 255, 0.1);"
    "    margin-top: 2rem;"
    "    margin-bottom: 2rem;"
    "}"
    "h1, h2, h3, h4, h5, h6, p, span, label {"
    "    color: #ffffff !important;"
    "}"
    "</style>"
)
st.markdown(css_kodlari, unsafe_allow_html=True)

# Dosya adı tanımı
EXCEL_FILE_PATH = "nurican.xls.xlsm"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# 🖲️ EXCEL MAKRO TETİKLEME MOTORU (BULUT UYUMLU GÜVENLİ MOD)
# ==========================================
def excel_makro_tetikle(buton_adi):
    """ Arka planda Excel'i açar, ilgili makro butonunu çalıştırır ve kaydeder """
    if os.name != 'nt':
        print(f"⚠️ Bulut ortamındasınız. Windows olmadığı için Excel Makrosu tetiklenemedi: {buton_adi}")
        return False
        
    try:
        import win32com.client
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False  
        excel.DisplayAlerts = False
        
        tam_yol = os.path.abspath(EXCEL_FILE_PATH)
        wb = excel.Workbooks.Open(tam_yol)
        
        makro_haritasi = {
            # ☀️ Gündüz Seans Butonları
            "ANLIK GÜNCELLEME": "AnlikGuncelle",
            "SIRALA": "Module21.TumSirala",
            "BTA": "BloklariBTAyaGoreSirala",
            "AL SAT SİNYALİ": "Module2.SadeceUyePozitifleriListele",
            
            # 🌙 Gece Yarısı Butonları
            "BİLANÇO": "BilancoGuncelle",       
            "KONTROL YENİLİK": "YenilikKontrol", 
            "KOPYA": "Q_Sutununu_S_Sutununa_Deger_Kopyalasi",             
            "ARZ HİSSELERİ": "HisseFiltreleSatir3"      
        }
        
        makro_ismi = makro_haritasi.get(buton_adi)
        if makro_ismi:
            excel.Application.Run(f"'{wb.Name}'!{makro_ismi}")
            wb.Save()
            print(f"✔️ Makro Başarılı: {buton_adi}")
        
        wb.Close()
        excel.Quit()
        return True
    except Exception as e:
        print(f"❌ Excel Otomasyon Hatası ({buton_adi}): {e}")
        return False

# ==========================================
# ⏱️ AKILLI SEANS VE GECE ZAMANLAYICI DÖNGÜSÜ
# ==========================================
def zamanlayici_dongusu():
    son_gunduz_dakikasi = -1
    gece_tetiklendi_mi = False

    while True:
        simdi = datetime.datetime.now()
        su_an_saat_dakika = simdi.strftime("%H:%M")
        
        # ☀️ 1. SENARYO: GÜNDÜZ SEANS DÖNGÜSÜ (10:10 - 18:10 | 15 DK PERİYOT)
        if "10:10" <= su_an_saat_dakika <= "18:10":
            if (simdi.minute - 10) % 15 == 0 and simdi.minute != son_gunduz_dakikasi:
                son_gunduz_dakikasi = simdi.minute
                print(f"⏰ Seans Döngüsü Başladı | Saat: {su_an_saat_dakika}")
                
                excel_makro_tetikle("ANLIK GÜNCELLEME")
                time.sleep(300) # 5 dakika güncelleme bekleme süresi
                
                excel_makro_tetikle("SIRALA")
                time.sleep(5)
                
                excel_makro_tetikle("BTA")
                time.sleep(5)
                
                excel_makro_tetikle("AL SAT SİNYALİ")
                time.sleep(5)
                print(f"✅ Seans Periyodu Tamamlandı | Saat: {datetime.datetime.now().strftime('%H:%M')}")

        # 🌙 2. SENARYO: GECE YARISI RUTİNİ (00:00 - SADECE 1 KERE)
        if simdi.hour == 0 and simdi.minute == 0:
            if not gece_tetiklendi_mi:
                gece_tetiklendi_mi = True  
                print(f"🌙 Gece Yarısı Veri Güncellemesi Başlatıldı | Saat: {su_an_saat_dakika}")
                
                excel_makro_tetikle("BİLANÇO")
                time.sleep(120) 
                
                excel_makro_tetikle("KONTROL YENİLİK")
                time.sleep(60)
                
                excel_makro_tetikle("KOPYA")
                time.sleep(60)
                
                excel_makro_tetikle("ARZ HİSSELERİ")
                time.sleep(120)
                print("✅ Gece Yarısı Rutini Başarıyla Sona Erdi.")
        else:
            gece_tetiklendi_mi = False

        time.sleep(1)

# Arka plan zamanlayıcı başlatma
if "dongu_aktif" not in st.session_state:
    st.session_state["dongu_aktif"] = True
    t = threading.Thread(target=zamanlayici_dongusu, daemon=True)
    t.start()

# ==========================================
# 🧼 GÜVENLİ SAYI VE METİN TEMİZLEME FONKSİYONLARI
# ==========================================
def saf_fiyat_al(veri):
    if pd.isnull(veri):
        return 0.0
    try:
        veri_str = str(veri).replace(",", ".").strip()
        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", veri_str)
        if sayilar:
            return float(sayilar[0])
    except Exception:
        return 0.0
    return 0.0

def saf_hisse_adi_al(metin):
    if pd.isnull(metin):
        return ""
    try:
        metin_str = str(metin).strip().upper()
        temiz = metin_str.replace("[AL]", "").replace("[SAT]", "").strip()
        parcalar = temiz.split()
        if len(parcalar) > 0:
            return parcalar[0]
    except Exception:
        return ""
    return ""

def canli_verileri_getir(hisse_adi, yuklenen_fiyat):
    try:
        temiz_hisse = saf_hisse_adi_al(hisse_adi)
        if not temiz_hisse:
            return None, None
            
        gecersiz_kelimeler = ["ANA", "PAZAR", "HİSSE", "DOLAŞIM", "PİYASA", "LOT", "ANLIK", "BTA", "UCUZ", "KOPYA", "AL", "SAT", "NAN", "ARZ"]
        if any(x in temiz_hisse for x in gecersiz_kelimeler) or len(temiz_hisse) < 2:
            return None, None

        ticker_kod = f"{temiz_hisse}.IS" if not temiz_hisse.endswith(".IS") else temiz_hisse
        hisse = yf.Ticker(ticker_kod)
        df_live = hisse.history(period="1d")
        
        if not df_live.empty:
            canli_fiyat = df_live['Close'].iloc[-1]
            maliyet = yuklenen_fiyat
            if maliyet <= 0:
                return f"{canli_fiyat:.2f} TL", "Maliyet Yok"
                
            yuzde_fark = ((canli_fiyat - maliyet) / maliyet) * 100
            if canli_fiyat >= maliyet:
                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı"
            else:
                durum_str = f"🔴 %{abs(yuzde_fark):.2f} İçeride"
            return f"{canli_fiyat:.2f} TL", durum_str
        return "Veri Yok", "⚠️ Fiyat Alınamadı"
    except Exception:
        return "Hata", "⚠️ Bağlantı Sorunu"

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

# 🟡 AL SAT SİNYAL GÖSTERİMİ
if al_sat_butonu:
    with st.spinner("Excel verileri okunuyor..."):
        try:
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA") if "BTA" in pd.ExcelFile(EXCEL_FILE_PATH).sheet_names else pd.read_excel(EXCEL_FILE_PATH)
            df.columns = df.columns.astype(str).str.strip()
            tablo_verisi = []
            
            for i in range(len(df)):
                hisse_kodu_ham = df.iloc[i, 0]      
                excel_anlik_verisi = df.iloc[i, 7] 
                bta_sinyal_al_sat = df.iloc[i, 20] 
                
                hisse_temiz = saf_hisse_adi_al(hisse_kodu_ham)
                if hisse_temiz and pd.notnull(bta_sinyal_al_sat) and "+" in str(bta_sinyal_al_sat):
                    yüklenen_fiy = saf_fiyat_al(excel_anlik_verisi)
                    canli_fiy, canli_durum = canli_verileri_getir(hisse_temiz, yüklenen_fiy)
                    if canli_fiy is not None:
                        tablo_verisi.append({"Hisse Kodu": hisse_temiz, "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL", "Anlık Canlı Fiyat": canli_fiy, "Canlı Kar/Zarar Oranı": canli_durum})
            
            if tablo_verisi:
                st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
            else:
                st.warning("Aktif Al-Sat sinyali bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# 🟢 AL SİNYAL GÖSTERİMİ
if al_butonu:
    with st.spinner("Aktif AL veren hisseler hesaplanıyor..."):
        try:
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA") if "BTA" in pd.ExcelFile(EXCEL_FILE_PATH).sheet_names else pd.read_excel(EXCEL_FILE_PATH)
            df.columns = df.columns.astype(str).str.strip()
            tablo_verisi_al = []
            
            for i in range(len(df)):
                satir_hisse_adi = saf_hisse_adi_al(df.iloc[i, 0])
                if satir_hisse_adi:
                    excel_anlik_verisi = df.iloc[i, 7]
