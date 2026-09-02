
import streamlit as st
import pandas as pd
import datetime
import yfinance as yf

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

# Sabit Zaman Ayarı (Hata veren pytz kütüphanesi kaldırıldı)
su_an = datetime.datetime.now()
guncel_tarih_saat = su_an.strftime("%d.%m.%Y - %H:%M:%S")

# Sohbet geçmişi için kalıcı hafıza oluşturuyoruz
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# 📊 YFINANCE CANLI FIYAT VE KAR/ZARAR FONKSİYONU
# ==========================================
def canli_verileri_getir(hisse_adi, yuklenen_fiyat):
    """
    Excel'deki yüklenen fiyat ile internetteki canlı fiyatı karşılaştırır.
    """
    try:
        temiz_hisse = str(hisse_adi).strip().upper()
        if not temiz_hisse.endswith(".IS"):
            ticker_kod = f"{temiz_hisse}.IS"
        else:
            ticker_kod = temiz_hisse

        # İnternetten anlık canlı borsa fiyatını çekiyoruz
        hisse = yf.Ticker(ticker_kod)
        df_live = hisse.history(period="1d")
        
        if not df_live.empty:
            canli_fiyat = df_live['Close'].iloc[-1]
            
            # Eğer yüklediğiniz fiyat geçerliyse yüzde hesapla
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
# 📈 PANEL ANA EKRANI
# ==========================================
st.title("⚡ Sinyal Takip Merkezi")

# ==========================================
# 👥 ÇEVRİMİÇİ VE ZİYARETÇİ SAYACI
# ==========================================
st.markdown("---")
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric(label="🟢 Sitedeki Kişi Sayısı", value="Aktif")
with col_info2:
    st.metric(label="📊 Toplam Giriş Sayısı", value="1")
with col_info3:
    st.metric(label="🕒 Son Güncelleme", value=su_an.strftime("%H:%M:%S"))

# 💡 bta analiz Özel Güncelleme Notu (Tam istediğiniz formatta)
st.info(f"💡 Bu sayfa **{guncel_tarih_saat}** tarihinde **bta analiz** tarafından güncellenmiştir.")

st.markdown("---")
st.subheader("Sinyal Üretim Merkezi")

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
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            df.columns = df.columns.str.strip()
            
            # Sütunları görseldeki düzene göre tam indeksleriyle seçiyoruz:
            hisse_verisi = df.iloc[:, 0]          # A Sütunu - Hisse Adı
            excel_anlik_verisi = df.iloc[:, 7]    # H Sütunu - Excel'e yüklediğiniz andaki fiyat
            bta_verisi = pd.to_numeric(df.iloc[:, 16], errors='coerce') # Q Sütunu - BTA Değeri
            
            temp_df = pd.DataFrame({
                "Hisse": hisse_verisi, 
                "Yuklenen_Fiyat": pd.to_numeric(excel_anlik_verisi, errors='coerce'), 
                "BTA_Deger": bta_verisi
            })
            
            # BTA değeri 0.01 ve üzeri olan aktif sinyalleri filtrele
            df_filtered = temp_df[temp_df["BTA_Deger"] >= 0.01].copy()
            
            if not df_filtered.empty:
                # Büyükten küçüğe sırala
                df_sorted = df_filtered.sort_values(by="BTA_Deger", ascending=False)
                tablo_verisi = []
                
                for idx, row in df_sorted.iterrows():
                    hisse_ismi = row['Hisse']
                    yüklenen_fiy = row['Yuklenen_Fiyat']
                    
                    # İnternetten anlık canlı fiyatı ve yüzdeyi fonksiyonla çek
                    canli_fiy, canli_durum = canli_verileri_getir(hisse_ismi, yüklenen_fiy)
                    
                    tablo_verisi.append({
                        "Hisse Kodu": hisse_ismi,
                        "BTA Sinyal Skoru": f"{row['BTA_Deger']:.2f}",
                        "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL" if pd.notnull(yüklenen_fiy) else "Veri Yok",
                        "Anlık Canlı Fiyat": canli_fiy,
                        "Canlı Kar/Zarar Oranı": canli_durum
                    })
                    
                st.success("Sinyaller Büyükten Küçüğe Listelendi ve Canlı Verilerle Eşleştirildi!")
                result_df = pd.DataFrame(tablo_verisi)
                st.dataframe(result_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Pozitif BTA sinyali bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# 🟢 2. BUTON: AL SİNYALİ
if al_butonu:
    with st.spinner("Veriler işleniyor..."):
        try:
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            # W Sütunu (Index 22) [AL] durumunu kontrol eder
            w_sutun_verisi = df.iloc[:, 22].astype(str)
            aktif_aller = w_sutun_verisi[w_sutun_verisi.str.contains(r"\[AL\]", na=False)].tolist()
            
            if aktif_aller:
                st.success("Aktif [AL] Sinyali Veren Hisseler Listelendi!")
                result_df_al = pd.DataFrame(aktif_aller, columns=["Aktif AL Sinyalleri"])
                st.dataframe(result_df_al, use_container_width=True, hide_index=True)
            else:
                st.warning("Aktif [AL] sinyali veren hisse bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# ==========================================
# 💬 CANLI SOHBET ODASI BÖLÜMÜ
# ==========================================
st.markdown("---")
st.subheader("💬 Sinyal Odası Canlı Sohbet")

sohbet_adi = st.text_input("Sohbet Takma Adınız:", value="Nurican", key="chat_name")
yeni_mesaj = st.text_input("Mesajınızı yazın:", placeholder="Örn: Hisseler bugün çok iyi gidiyor...", key="chat_msg")

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
    st.info("Henüz mesaj yazılmamış. İlk mesajı siz yazın!")

# ==========================================
# ⚠️ SPK MEVZUATINA UYGUN YASAL UYARI KUTUSU
# ==========================================
st.markdown("---")
st.error("""
⚠️ **YASAL UYARI (SPK Mevzuatı Uyarınca):**
         
Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti, aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. 

Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. **Burada paylaşılan sinyaller ve bilgiler kesinlikle yatırım tavsiyesi değildir.**
""")
