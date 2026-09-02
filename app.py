
import streamlit as st
import pandas as pd
import time
import datetime

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

# ==========================================
# 🔑 GÜVENLİK VE ŞİFRE AYARLARI
# ==========================================
ADMIN_USERNAME = "nurican26"
ADMIN_PASSWORD = "3015"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Giriş Ekranı Tasarımı
if not st.session_state["logged_in"]:
    st.markdown("<h2 style='text-align: center;'>🔒 Nurican Sinyal Sistemine Giriş</h2>", unsafe_allow_html=True)
    st.write("Lütfen giriş yapmak için bilgilerinizi yazın.")
    
    username = st.text_input("Kullanıcı Adı:")
    password = st.text_input("Şifre:", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state["logged_in"] = True
            st.success("Giriş Başarılı! Sistem yükleniyor...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Hatalı Kullanıcı Adı veya Şifre!")
            
# ==========================================
# 📈 PANEL ANA EKRANI (ŞİFRE DOĞRUYSA AÇILIR)
# ==========================================
else:
    # Sohbet geçmişi ve sayaçlar için kalıcı hafıza oluşturuyoruz
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    col_title, col_logout = st.columns(2)
    with col_title:
        st.title("⚡ Sinyal Takip Merkezi")
    with col_logout:
        if st.button("Çıkış Yap 🔓"):
            st.session_state["logged_in"] = False
            st.rerun()

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
        st.metric(label="🕒 Son Güncelleme", value=datetime.datetime.now().strftime("%H:%M:%S"))

    st.subheader("Sinyal Üretim Merkezi")
    
    EXCEL_FILE_PATH = "nurican.xlsx" 

    col1, col2 = st.columns(2)
    with col1:
        al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
    with col2:
        al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

    # 🟡 1. BUTON: AL SAT SİNYALİ
    if al_sat_butonu:
        with st.spinner("Veriler işleniyor..."):
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
                df.columns = df.columns.str.strip()
                hisse_verisi = df.iloc[:, 0]
                al_sat_verisi = pd.to_numeric(df.iloc[:, 19], errors='coerce')
                
                temp_df = pd.DataFrame({"Hisse": hisse_verisi, "Deger": al_sat_verisi})
                df_filtered = temp_df[temp_df["Deger"] >= 0.01].copy()
                
                if not df_filtered.empty:
                    df_sorted = df_filtered.sort_values(by="Deger", ascending=False)
                    sonuc = []
                    for idx, row in df_sorted.iterrows():
                        sonuc.append(f"🟨 {row['Hisse']} +{row['Deger']:.2f}")
                        
                    st.success("AL SAT Sinyalleri Büyükten Küçüğe Sıralandı!")
                    result_df = pd.DataFrame(sonuc, columns=["AL_SAT Sinyal Listesi"])
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Pozitif AL SAT sinyali bulunamadı.")
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
    
    # Kullanıcının adını girmesi veya otomatik Üye yazması için alan
    sohbet_adi = st.text_input("Sohbet Takma Adınız:", value="Nurican", key="chat_name")
    
    # Mesaj kutusu
    yeni_mesaj = st.text_input("Mesajınızı yazın:", placeholder="Örn: Hisseler bugün çok iyi gidiyor...", key="chat_msg")
    
    if st.button("Mesajı Gönder 🚀", use_container_width=True):
        if yeni_mesaj.strip() != "":
            su_an = datetime.datetime.now().strftime("%H:%M")
            # Geçmişe ekle
            st.session_state["chat_history"].append(f"[{su_an}] 👤 {sohbet_adi}: {yeni_mesaj}")
            st.rerun()

    # Mesaj Geçmişini Listeleme
    st.markdown("##### 📜 Mesaj Geçmişi")
    if st.session_state["chat_history"]:
        # Yeni mesajlar en üstte görünsün diye listeyi ters çevirip yazdırıyoruz
        for mesaj in reversed(st.session_state["chat_history"]):
            st.markdown(f"*{mesaj}*")
    else:
        st.info("Henüz mesaj yazılmamış. İlk mesajı siz yazın!")
