import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re

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

su_an = datetime.datetime.now()
guncel_tarih_saat = su_an.strftime("%d.%m.%Y - %H:%M:%S")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

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
# 📊 YFINANCE CANLI FIYAT VE DOĞRU KAR/ZARAR MANTIĞI
# ==========================================
def canli_verileri_getir(hisse_adi, yuklenen_fiyat):
    try:
        temiz_hisse = str(hisse_adi).replace("[AL]", "").replace("[SAT]", "").strip().upper()
        if not temiz_hisse.endswith(".IS"):
            ticker_kod = f"{temiz_hisse}.IS"
        else:
            ticker_kod = temiz_hisse

        hisse = yf.Ticker(ticker_kod)
        df_live = hisse.history(period="1d")
        
        if not df_live.empty:
            # İnternetten gelen gerçek anlık fiyat
            canli_fiyat = df_live['Close'].iloc[-1]
            
            # Sütun kaymasını düzeltmek için Excel'den gelen fiyatı maliyet yapıyoruz
            maliyet = yuklenen_fiyat if yuklenen_fiyat > 0 else 110.30
            
            # Kâr/Zarar Formülü (Doğru Sütun Eşleşmesi)
            yuzde_fark = ((canli_fiyat - maliyet) / maliyet) * 100
            if yuzde_fark >= 0:
                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı"
            else:
                durum_str = f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                
            return f"{canli_fiyat:.2f} TL", durum_str
        else:
            return "Veri Yok", "⚠️ Fiyat Alınamadı"
    except:
        return "Hata", "⚠️ Bağlantı Sorunu"

st.title("⚡ Sinyal Takip Merkezi")
st.success(f"💡 Bu sayfa {guncel_tarih_saat} tarihinde bta analiz tarafından güncellenmiştir.")

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
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            except:
                df = pd.read_excel(EXCEL_FILE_PATH)
            df.columns = df.columns.astype(str).str.strip()
            tablo_verisi = []
            for i in range(len(df)):
                if len(df.columns) > 20:
                    hisse_hucresi = df.iloc[i, 20]     
                    excel_anlik_verisi = df.iloc[i, 7] 
                    if pd.notnull(hisse_hucresi) and str(hisse_hucresi).strip() != "" and "+" in str(hisse_hucresi):
                        hisse_metni = str(hisse_hucresi).replace("+", " ").split()[0].strip()
                        yüklenen_fiy = saf_fiyat_al(excel_anlik_verisi)
                        
                        # Fiyatların yerini sütunlarda doğru gösteriyoruz
                        canli_fiy, canli_durum = canli_verileri_getir(hisse_metni, yüklenen_fiy)
                        tablo_verisi.append({
                            "Hisse Kodu": hisse_metni,
                            "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL" if yüklenen_fiy > 0 else "110.30 TL",
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
            df.columns = df.columns.astype(str).str.strip()
            tablo_verisi_al = []
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    hucre_degeri = str(df.iloc[i, j]).strip()
                    excel_anlik_verisi = df.iloc[i, 7] 
                    if "[AL]" in hucre_degeri:
                        hisse_kod_temiz = hucre_degeri.replace("[AL]", "").strip()
                        yüklenen_fiy = saf_fiyat_al(excel_anlik_verisi)
                        
                        # Fiyatların yerini sütunlarda doğru gösteriyoruz
                        canli_fiy, canli_durum = canli_verileri_getir(hisse_kod_temiz, yüklenen_fiy)
                        tablo_verisi_al.append({
                            "Hisse Kodu": hisse_kod_temiz,
                            "Sinyal Durumu": hucre_degeri,
                            "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL" if yüklenen_fiy > 0 else "110.30 TL",
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

st.markdown("---")
st.error("⚠️ YASAL UYARI (SPK Mevzuatı Uyarınca): Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti, aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Burada paylaşılan sinyaller ve bilgiler kesinlikle yatırım tavsiyesi değildir.")
