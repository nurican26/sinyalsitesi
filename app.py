import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

# ==========================================
# 🎨 BORSA TEMALI ARKA PLAN VE BOYAMA CSS AYARLARI
# ==========================================
arka_plan_resmi_url = "https://unsplash.com"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{arka_plan_resmi_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .block-container {{
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(10px);
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}
    .custom-update-box {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-left: 6px solid #eab308;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(234, 179, 8, 0.15);
        margin-top: 10px;
        margin-bottom: 20px;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sabit Zaman Ayarı
su_an = datetime.datetime.now()
guncel_tarih_saat = su_an.strftime("%d.%m.%Y - %H:%M:%S")

# Sohbet geçmişi için kalıcı hafıza oluşturuyoruz
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# 📊 YFINANCE CANLI FIYAT VE KAR/ZARAR FONKSİYONU
# ==========================================
def canli_verileri_getir(hisse_adi, yuklenen_fiyat):
    try:
        temiz_hisse = str(hisse_adi).strip().upper()
        if not temiz_hisse.endswith(".IS"):
            ticker_kod = f"{temiz_hisse}.IS"
        else:
            ticker_kod = temiz_hisse

        hisse = yf.Ticker(ticker_kod)
        df_live = hisse.history(period="1d")
        
        if not df_live.empty:
            canli_fiyat = df_live['Close'].iloc[-1]
            
            if yuklenen_fiyat > 0:
                yuzde_fark = ((canli_fiyat - yuklenen_fiyat) / yuklenen_fiyat) * 100
                if yuzde_fark >= 0:
                    durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı"
                else:
                    durum_str = f"🔴 %{abs(yuzde_fark):.2f} İçeride"
            else:
                durum_str = " Hesaplamaya Uygun Değil"
                
            return f"{canli_fiyat:.2f} TL", durum_str
        else:
            return "Veri Yok", "⚠️ Canlı Fiyat Çekilemedi"
    except:
        return "Hata", "⚠️ Bağlantı Sorunu"

# ==========================================
# 📈 1. BÖLÜM: PANEL ANA EKRANI VE GÜNCELLEME NOTU
# ==========================================
st.title("⚡ Sinyal Takip Merkezi")

st.markdown(
    f"""
    <div class="custom-update-box">
        <span style="font-size: 16px; font-weight: bold; color: #f8fafc !important;">
            💡 Bu sayfa {guncel_tarih_saat} tarihinde bta analiz tarafından güncellenmiştir.
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==========================================
# 📈 2. BÖLÜM: SİNYAL ÜRETİM MERKEZİ (BUTONLAR VE TABLOLAR)
# ==========================================
st.subheader("Sinyal Üretim Merkezi")

# Excel dosyanızın adı sol menüde 'nurican.xlsx' göründüğü için burayı sabitledik
EXCEL_FILE_PATH = "nurican.xlsx" 

col1, col2 = st.columns(2)
with col1:
    al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
with col2:
    al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# 🟡 1. BUTON: AL SAT SİNYALİ
if al_sat_butonu:
    with st.spinner("Excel verileri okunuyor ve canlı borsa takibi yapılıyor..."):
        try:
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            except:
                df = pd.read_excel(EXCEL_FILE_PATH)
                
            df.columns = df.columns.str.strip()
            
            hisse_verisi = df.iloc[:, 0]          
            excel_anlik_verisi = df.iloc[:, 7]    
            bta_verisi = pd.to_numeric(df.iloc[:, 16], errors='coerce') 
            
            temp_df = pd.DataFrame({
                "Hisse": hisse_verisi, 
                "Yuklenen_Fiyat": pd.to_numeric(excel_anlik_verisi, errors='coerce'), 
                "BTA_Deger": bta_verisi
            })
            
            df_filtered = temp_df[temp_df["BTA_Deger"] >= 0.01].copy()
            
            if not df_filtered.empty:
                df_sorted = df_filtered.sort_values(by="BTA_Deger", ascending=False)
                tablo_verisi = []
                
                for idx, row in df_sorted.iterrows():
                    hisse_ismi = row['Hisse']
                    yüklenen_fiy = row['Yuklenen_Fiyat']
                    
                    canli_fiy, canli_durum = canli_verileri_getir(hisse_ismi, yüklenen_fiy)
                    
                    tablo_verisi.append({
                        "Hisse Kodu": hisse_ismi,
                        "BTA Sinyal Skoru": f"{row['BTA_Deger']:.2f}",
                        "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL" if pd.notnull(yüklenen_fiy) else "Veri Yok",
                        "Anlık Canlı Fiyat": canli_fiy,
                        "Canlı Kar/Zarar Oranı": canli_durum
                    })
                    
                st.success("Sinyaller Büyükten Küçüğe Listelendi!")
                result_df = pd.DataFrame(tablo_verisi)
                st.dataframe(result_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Pozitif BTA sinyali bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# 🟢 2. BUTON: AL SİNYALİ
if al_butonu:
    with st.spinner("Aktif AL veren hisseler canlı borsa verileriyle hesaplanıyor..."):
        try:
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            except:
                df = pd.read_excel(EXCEL_FILE_PATH)
                
            df.columns = df.columns.str.strip()
            
            hisse_verisi = df.iloc[:, 0]          
            excel_anlik_verisi = df.iloc[:, 7]    
            w_sutun_verisi = df.iloc[:, 22].astype(str) 
            
            tablo_verisi_al = []
            kayit_tarihi = datetime.datetime.now().strftime("%d.%m.%Y")
            kayit_saati = datetime.datetime.now().strftime("%H:%M:%S")
            
            for i in range(len(df)):
                durum_metni = w_sutun_verisi.iloc[i]
                hisse_ismi = hisse_verisi.iloc[i]
                
                if "[AL]" in durum_metni and pd.notnull(hisse_ismi) and str(hisse_ismi).strip() != "":
                    yüklenen_fiy = pd.to_numeric(excel_anlik_verisi.iloc[i], errors='coerce')
                    canli_fiy, canli_durum = canli_verileri_getir(hisse_ismi, yüklenen_fiy)
                    
                    tablo_verisi_al.append({
                        "Sorgulama_Tarihi": kayit_tarihi,
                        "Sorgulama_Saati": kayit_saati,
                        "Hisse Kodu": hisse_ismi,
                        "Sinyal Durumu": "🟢 [AL]",
                        "Paylaştığınız Fiyat": f"{yüklenen_fiy:.2f} TL" if pd.notnull(yüklenen_fiy) else "Veri Yok",
                        "Anlık Canlı Fiyat": canli_fiy,
                        "Canlı Kar/Zarar Oranı": canli_durum
                    })
            
            if tablo_verisi_al:
                st.success("Aktif AL Sinyalleri Hesaplandı!")
                result_df_al = pd.DataFrame(tablo_verisi_al)
                st.dataframe(result_df_al, use_container_width=True, hide_index=True)
                
                gecmis_dosya = "nurican_sinyal_gecmisi.csv"
                if os.path.exists(gecmis_dosya):
                    eski_gecmis = pd.read_csv(gecmis_dosya)
                    yeni_gecmis = pd.concat([eski_gecmis, result_df_al], ignore_index=True)
                    yeni_gecmis.to_csv(gecmis_dosya, index=False)
                else:
                    result_df_al.to_csv(gecmis_dosya, index=False)
            else:
                st.warning("Aktif [AL] sinyali veren hisse bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# ==========================================
# 💬 3. BÖLÜM: BTA SOHBET ODASI
# ==========================================
st.markdown("---")
st.subheader("💬 BTA SOHBET ODASI")

sohbet_adi = st.text_input("👤 Sohbet Takma Adınız:", value="Nurican", key="chat_name")
yeni_mesaj = st.text_input("✍️ Mesajınızı yazın:", placeholder="Örn: Hisseler bugün çok iyi gidiyor... 🚀📈", key="chat_msg")

if st.button("Mesajı Gönder 🚀", use_container_width=True):
    if yeni_mesaj.strip() != "":
        su_an_mesaj = datetime.datetime.now().strftime("%H:%M")
        st.session_state["chat_history"].append(f"[{su_an_mesaj}] 👤 {sohbet_adi}: {yeni_mesaj}")
        st.rerun()

st.markdown("##### 📜 Mesaj Geçmişi")
if st.session_state["chat_history"]:
    for mesaj in reversed(st.session_state["chat_history"]):
        st.markdown(f"*{mesaj}*")
else:
    st.info("Henüz mesaj yazılmamış. İlk mesajı siz yazın! 👇")

# ==========================================
# ⚠️ 4. BÖLÜM: YASAL UYARI KUTUSU (Eksiksiz Tam Metin)
# ==========================================
st.markdown("---")
st.error("""
⚠️ **YASAL UYARI (SPK Mevzuatı Uyarınca):**
