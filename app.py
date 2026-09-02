
import streamlit as st
import pandas as pd
import datetime
import pytz
import yfinance as yf

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

# Türkiye Saat Dilimi Ayarı (Sunucuda saatin şaşmaması için)
turkey_tz = pytz.timezone('Europe/Istanbul')
su_an_tr = datetime.datetime.now(turkey_tz)
guncel_tarih_saat = su_an_tr.strftime("%d.%m.%Y - %H:%M:%S")

# Sohbet geçmişi için kalıcı hafıza oluşturuyoruz
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# 📊 YFINANCE CANLI FIYAT VE KAR/ZARAR FONKSİYONU
# ==========================================
def canli_durum_hesapla(hisse_adi, giris_fiyati):
    """
    Excel'den gelen hisse adını alıp Yahoo Finance üzerinden canlı fiyatını çeker
    ve sinyal fiyatına göre yüzde kaç kazandırdığını hesaplar.
    """
    try:
        # Hisse adını temizle ve Borsa İstanbul formatına çevir (Örn: THYAO -> THYAO.IS)
        temiz_hisse = str(hisse_adi).strip().upper()
        if not temiz_hisse.endswith(".IS"):
            ticker_kod = f"{temiz_hisse}.IS"
        else:
            ticker_kod = temiz_hisse

        # İnternetten anlık hisse verisini çek
        hisse = yf.Ticker(ticker_kod)
        # En son kapanış veya anlık fiyatı al
        df_live = hisse.history(period="1d")
        if not df_live.empty:
            anlik_fiyat = df_live['Close'].iloc[-1]
            # Kar / Zarar Yüzdesi Hesaplama
            yuzde_fark = ((anlik_fiyat - giris_fiyati) / giris_fiyati) * 100
            
            # Görsel renkli formatlama
            if yuzde_fark >= 0:
                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandırdı"
            else:
                durum_str = f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                
            return f"{anlik_fiyat:.2f} TL", durum_str
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
    # Sayfa her yenilendiğinde Türkiye saatiyle tam zamanı gösterir
    st.metric(label="🕒 Son Güncelleme", value=su_an_tr.strftime("%H:%M:%S"))

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

# 🟡 1. BUTON: AL SAT SİNYALİ (CANLI KAR/ZARAR ENTEGRELİ)
if al_sat_butonu:
    with st.spinner("Excel verileri okunuyor ve Yahoo Finance üzerinden canlı kâr/zarar hesaplanıyor..."):
        try:
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
            df.columns = df.columns.str.strip()
            
            # Excel'inizdeki 1. sütun Hisse adı, 20. sütun (index 19) ise girdiğiniz sinyal fiyatı
            hisse_verisi = df.iloc[:, 0]
            al_sat_verisi = pd.to_numeric(df.iloc[:, 19], errors='coerce')
            
            temp_df = pd.DataFrame({"Hisse": hisse_verisi, "Sinyal_Fiyati": al_sat_verisi})
            # Girdiğiniz fiyat 0'dan büyük olan geçerli hisseleri filtrele
            df_filtered = temp_df[temp_df["Sinyal_Fiyati"] > 0.01].copy()
            
            if not df_filtered.empty:
                tablo_verisi = []
                
                # Her bir hisse için döngü başlatıp internetten canlı fiyat topluyoruz
                for idx, row in df_filtered.iterrows():
                    hisse_ismi = row['Hisse']
                    giris_fiy = row['Sinyal_Fiyati']
                    
                    # Canlı fiyat ve kar oranını yfinance fonksiyonundan çek
                    anlik_fiy, canli_durum = canli_durum_hesapla(hisse_ismi, giris_fiy)
                    
                    tablo_verisi.append({
                        "Hisse Kodu": hisse_ismi,
                        "Sinyal Fiyatı (Giriş)": f"{giris_fiy:.2f} TL",
                        "Anlık Canlı Fiyat": anlik_fiy,
                        "Canlı Durum / Değişim": canli_durum
                    })
                    
                st.success("AL SAT Sinyalleri ve Canlı Kar/Zarar Durumları Listelendi!")
                result_df = pd.DataFrame(tablo_verisi)
                st.dataframe(result_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Geçerli sinyal fiyatı içeren hisse bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# 🟢 2. BUTON: AL SİNYALİ
if al_butonu:
    with st.spinner("Veriler işleniyor..."):
        try:
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
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
        su_an_mesaj = datetime.datetime.now(turkey_tz).strftime("%H:%M")
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
