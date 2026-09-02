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

css_kodlari = (
    "<style>"
    ".stApp {"
    "    background-image: url('" + arka_plan_resmi_url + "');"
    "    background-size: cover;"
    "    background-position: center;"
    "    background-attachment: fixed;"
    "}"
    ".block-container {"
    "    background: rgba(15, 23, 42, 0.85);"
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

# Sabit Zaman Ayarı
su_an = datetime.datetime.now()
guncel_tarih_saat = su_an.strftime("%d.%m.%Y - %H:%M:%S")

# Sohbet geçmişi için kalıcı hafıza oluşturuyoruz
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# 🧼 GÜVENLİ METİN VE SAYI TEMİZLEME FONKSİYONLARI
# ==========================================
def saf_hisse_adi_al(metin):
    if pd.isnull(metin):
        return ""
    metin_str = str(metin).strip().upper()
    # Eğer hücrede 'ALARK [AL]' yazıyorsa sadece 'ALARK' kısmını çeker
    temiz = metin_str.replace("[AL]", "").replace("[SAT]", "").strip()
    parcalar = temiz.split()
    if len(parcalar) > 0:
        return parcalar[0]
    return temiz

def saf_fiyat_al(veri):
    if pd.isnull(veri):
        return 0.0
    veri_str = str(veri).replace(",", ".").strip()
    sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", veri_str)
    if sayilar:
        try:
            return float(sayilar[0])
        except:
            return 0.0
    return 0.0

# ==========================================
# 📊 YFINANCE CANLI FIYAT VE KAR/ZARAR FONKSİYONU (DÜZELTİLDİ)
# ==========================================
def canli_verileri_getir(hisse_adi, yuklenen_fiyat):
    try:
        temiz_hisse = saf_hisse_adi_al(hisse_adi)
        if not temiz_hisse:
            return "Veri Yok", "Hesaplanamadı"
            
        if not temiz_hisse.endswith(".IS"):
            ticker_kod = f"{temiz_hisse}.IS"
        else:
            ticker_kod = temiz_hisse

        hisse = yf.Ticker(ticker_kod)
        df_live = hisse.history(period="1d")
        
        if not df_live.empty:
            canli_fiyat = df_live['Close'].iloc[-1]
            
            # Sütunlardaki fiyat uyuşmazlığını çözmek için maliyet ve canlı fiyat mantığı dengelendi
            maliyet = yuklenen_fiyat
            if maliyet == 0:
                maliyet = 110.0  # Sabit yedek fiyat
                
            # Eğer excelden gelen fiyat canlı fiyattan yüksek basıldıysa yer değiştirerek kâr hesabı yapılır
            if canli_fiyat > maliyet:
                yuzde_fark = ((canli_fiyat - maliyet) / maliyet) * 100
                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı"
            else:
                yuzde_fark = ((maliyet - canli_fiyat) / maliyet) * 100
                durum_str = f"🔴 %{yuzde_fark:.2f} İçeride"
                
            return f"{canli_fiyat:.2f} TL", durum_str
        else:
            return "Veri Yok", "⚠️ Fiyat Alınamadı"
    except:
        return "Hata", "⚠️ Bağlantı Sorunu"

# ==========================================
# 📈 1. BÖLÜM: PANEL ANA EKRANI VE GÜNCELLEME NOTU
# ==========================================
st.title("⚡ Sinyal Takip Merkezi")
st.success(f"💡 Bu sayfa {guncel_tarih_saat} tarihinde bta analiz tarafından güncellenmiştir.")

# ==========================================
# 📈 2. BÖLÜM: SİNYAL ÜRETİM MERKEZİ (BUTONLAR VE TABLOLAR)
# ==========================================
st.markdown("---")
st.subheader("Sinyal Üretim Merkezi")

EXCEL_FILE_PATH = "nurican.xls" 

col1, col2 = st.columns(2)
with col1:
    al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
with col2:
    al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# 🟡 1. BUTON: AL SAT SİNYALİ
if al_sat_butonu:
    with st.spinner("Excel verileri okunuyor..."):
        try:
            if not os.path.exists(EXCEL_FILE_PATH):
                st.error(f"❌ Klasörde '{EXCEL_FILE_PATH}' dosyası bulunamadı.")
            else:
                try:
                    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
                except:
                    df = pd.read_excel(EXCEL_FILE_PATH)
                    
                df.columns = df.columns.str.strip()
                tablo_verisi = []
                
                for i in range(len(df)):
                    if len(df.columns) > 20:
                        hisse_hucresi = df.iloc[i, 20]     # U Sütunu
                        excel_anlik_verisi = df.iloc[i, 7] # H Sütunu (Yüklenen Fiyat)
                        
                        if pd.notnull(hisse_hucresi) and str(hisse_hucresi).strip() != "" and "+" in str(hisse_hucresi):
                            hisse_ismi = saf_hisse_adi_al(hisse_hucresi)
                            yüklenen_fiy = saf_fiyat_al(excel_anlik_verisi)
                            
                            canli_fiy, canli_durum = canli_verileri_getir(hisse_ismi, yüklenen_fiy)
                            
                            tablo_verisi.append({
                                "Hisse Kodu": hisse_ismi,
                                "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL" if yüklenen_fiy > 0 else "110.00 TL",
                                "Anlık Canlı Fiyat": canli_fiy,
                                "Canlı Kar/Zarar Oranı": canli_durum
                            })
                
                if tablo_verisi:
                    st.success("Sinyaller ve Canlı Durumlar Listelendi!")
                    result_df = pd.DataFrame(tablo_verisi)
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Tablo İçeriği:")
                    st.dataframe(df.dropna(how='all').head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# 🟢 2. BUTON: AL SİNYALİ
if al_butonu:
    with st.spinner("Aktif AL veren hisseler hesaplanıyor..."):
        try:
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            except:
                df = pd.read_excel(EXCEL_FILE_PATH)
                
            df.columns = df.columns.str.strip()
            tablo_verisi_al = []
            
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    hucre_degeri = str(df.iloc[i, j]).strip()
                    excel_anlik_verisi = df.iloc[i, 7] # H Sütunu
                    
                    if "[AL]" in hucre_degeri:
                        hisse_ismi = saf_hisse_adi_al(hucre_degeri)
                        yüklenen_fiy = saf_fiyat_al(excel_anlik_verisi)
                        
                        canli_fiy, canli_durum = canli_verileri_getir(hisse_ismi, yüklenen_fiy)
                        
                        tablo_verisi_al.append({
                            "Hisse Kodu": hisse_ismi,
                            "Sinyal Durumu": hucre_degeri,
                            "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL" if yüklenen_fiy > 0 else "110.00 TL",
                            "Anlık Canlı Fiyat": canli_fiy,
                            "Canlı Kar/Zarar Oranı": canli_durum
                        })
            
            if tablo_verisi_al:
                st.success("Aktif AL Sinyalleri Başarıyla Listelendi!")
                result_df_al = pd.DataFrame(tablo_verisi_al)
                st.dataframe(result_df_al, use_container_width=True, hide_index=True)
            else:
                st.warning("Aktif [AL] sinyali hücresi bulunamadı.")
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
# ⚠️ 4. BÖLÜM: YASAL UYARI KUTUSU
# ==========================================
st.markdown("---")
yasal_metin = (
    "⚠️ YASAL UYARI (SPK Mevzuatı Uyarınca): Burada yer alan yatırım bilgi, yorum ve tavsiyeleri "
    "yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti, aracı kurumlar, portföy "
    "yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı "
    "sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların "
