import streamlit as st
import pandas as pd
import time

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="centered")

# ==========================================
# 🔑 GÜVENLİK VE ŞİFRE AYARLARI
# ==========================================
# Sitenizin giriş şifrelerini buradan istediğiniz gibi değiştirebilirsiniz
ADMIN_USERNAME = "nurican"
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
    col_title, col_logout = st.columns()
    with col_title:
        st.title("⚡ Sinyal Takip Merkezi")
    with col_logout:
        if st.button("Çıkış Yap 🔓"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.markdown("---")
    st.subheader("Sinyal Üretim Merkezi")
    
    # Klasörün içindeki Excel dosyanızın adı
    EXCEL_FILE_PATH = "nurican.xlsx" 

    # Sayfaya iki büyük buton yerleştiriyoruz
    col1, col2 = st.columns(2)
    
    with col1:
        al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
    with col2:
        al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

    # 🟡 1. BUTON: AL SAT SİNYALİ (T sütunundaki değerlere göre sıralı)
    if al_sat_butonu:
        with st.spinner("Veriler işleniyor..."):
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
                df.columns = df.columns.str.strip()
                
                # 0. Sütun = A (Hisse), 19. Sütun = T (AL_SAT)
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

    # 🟢 2. BUTON: AL SİNYALİ (W sütunundaki [AL] yazan veriler)
    if al_butonu:
        with st.spinner("Veriler işleniyor..."):
            try:
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="BTA")
                
                # W sütunu Excel'de 22. sütundur
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
