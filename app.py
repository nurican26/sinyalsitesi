import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re

# Sayfa Tasarım Ayarları
st.set_page_config(page_title="Nurican Sinyal Paneli", page_icon="📈", layout="wide")

# 🎨 Arka Plan Ayarları
st.markdown(
    """
    <style>
    .stApp {
        background: rgba(15, 23, 42, 0.95) !important;
        padding: 2rem;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }
    input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DEFAULT_EXCEL_PATH = "nurican.xls.xlsm"

# Hafıza Başlatmaları
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

st.markdown("<div style='background-color: rgba(220, 38, 38, 0.15); border-left: 5px solid #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><p style='margin: 0; font-weight: bold; color: #f87171 !important;'>⚠️ SPK YASAL UYARI: Yatırım tavsiyesi değildir.</p></div>", unsafe_allow_html=True)

# 📂 Excel Dosya Yükleme
st.markdown("### 📁 Güncel Excel Dosyası Yükleme")
yuklenen_dosya = st.file_uploader("Excel dosyasını seçin (.xlsx, .xlsm)", type=["xlsx", "xlsm"])

df_kaynak = None
if yuklenen_dosya is not None:
    try:
        df_kaynak = pd.read_excel(yuklenen_dosya, sheet_name=0, header=None)
        st.info("🔒 Excel dosyası belleğe yüklendi.")
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
elif os.path.exists(DEFAULT_EXCEL_PATH):
    try:
        df_kaynak = pd.read_excel(DEFAULT_EXCEL_PATH, header=None)
    except:
        pass

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
        
    # 🟡 1. ADIM: SARI BUTON (DOĞRUDAN U SÜTUNUNA BAKAR)
    if al_sat_butonu and df_kaynak is not None:
        tablo_verisi = []
        sutun_sayisi = len(df_kaynak.columns)
        for i in range(len(df_kaynak)):
            if sutun_sayisi > 20:
                u_val = str(df_kaynak.iloc[i, 20]).strip() # U Sütunu
                
                # Başlıkları veya boş hücreleri eliyoruz
                if not u_val or u_val.upper() in ["NAN", "AL SAT SİNYALİ", ""]:
                    continue
                
                # SÖNME ve ALKLC sadece yeşil butona ayrıldığı için sarıdan eliyoruz
                if "SONME" in u_val.upper() or "ALKLC" in u_val.upper():
                    continue
                    
                try:
                    fiyat_str = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if sutun_sayisi > 7 else "0"
                    sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", fiyat_str)
                    yuklenen_fiy = float(sayilar) if sayilar else 0.0
                    
                    # Hücrenin içindeki ilk kelimeyi (Hisse adını) ayıklıyoruz (Örn: FORTE +2,45 -> FORTE)
                    hisse_adi = u_val.split()[0].upper().replace("[AL]", "").replace("[SAT]", "")
                    
                    hisse_data = yf.Ticker(f"{hisse_adi}.IS").history(period="1d")
                    if not hisse_data.empty:
                        canli_fiyat = hisse_data['Close'].iloc[-1]
                        yuzde_fark = ((canli_fiyat - yuklenen_fiy) / yuklenen_fiy) * 100 if yuklenen_fiy > 0 else 0.0
                        durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yuklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                        tablo_verisi.append({"Hisse Kodu": hisse_adi, "Sinyal Metni": u_val, "Yüklenen Fiyat": f"{yuklenen_fiy:.2f} TL", "Canlı Fiyat": f"{canli_fiyat:.2f} TL", "Durum Oranı": durum_str})
                except:
                    pass
        if tablo_verisi:
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
        else:
            st.warning("Excel şablonunda aktif AL SAT sinyali bulunamadı.")

    # 🟢 2. ADIM: YEŞİL BUTON (DOĞRUDAN W SÜTUNUNA BAKAR)
    if al_butonu and df_kaynak is not None:
        tablo_verisi_al = []
        sutun_sayisi = len(df_kaynak.columns)
        for i in range(len(df_kaynak)):
            if sutun_sayisi > 22:
                w_val = str(df_kaynak.iloc[i, 22]).strip() # W Sütunu (AL)
                
                if not w_val or w_val.upper() in ["NAN", "AL", ""]:
                    continue
                    
                try:
                    # Hücrenin içindeki ilk kelimeyi alıyoruz (Örn: ALKLC [AL] -> ALKLC)
                    hisse_adi = w_val.split()[0].upper().replace("[AL]", "").replace("[SAT]", "")
                    
                    hisse_data = yf.Ticker(f"{hisse_adi}.IS").history(period="1d")
                    if not hisse_data.empty:
                        canli_fiyat = hisse_data['Close'].iloc[-1]
                        yuklenen_fiy = canli_fiyat 
                        yuzde_fark = 0.0  
                        durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı"
                        
                        st.session_state["ozel_takip_kutusu"][hisse_adi] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                        tablo_verisi_al.append({"Hisse Kodu": hisse_adi, "Sinyal": w_val, "Yüklenen Fiyat": f"{yuklenen_fiy:.2f} TL", "Canlı Fiyat": f"{canli_fiyat:.2f} TL", "Durum Oranı": durum_str})
                except:
                    pass
        if tablo_verisi_al:
            st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
        else:
            st.warning("Excel şablonunda aktif [AL] sinyali bulunamadı.")

    # Takip Kutusu Gösterimi
    if st.session_state["ozel_takip_kutusu"]:
        st.markdown("---")
        st.subheader("📥 Kaydedilen AL Sinyali Takip Kutusu")
        kutu_tablo = []
        for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
            try:
                hisse_data = yf.Ticker(f"{hisse}.IS").history(period="1d")
                if not hisse_data.empty:
                    guncel_canli = hisse_data['Close'].iloc[-1]
                    eski_fiyat = bilge["kayit_fiyati"]
                    yuzde_fark = ((guncel_canli - eski_fiyat) / eski_fiyat) * 100 if eski_fiyat > 0 else 0.0
                    durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if guncel_canli >= eski_fiyat else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                    kutu_tablo.append({"Hisse Kodu": hisse, "Kayıt Fiyatı": f"{eski_fiyat:.2f} TL", "Güncel Fiyat": f"{guncel_canli:.2f} TL", "Kar/Zarar": durum_str, "Zaman": bilge["kayit_zamani"]})
            except:
                pass
        if kutu_tablo:
            st.dataframe(pd.DataFrame(kutu_tablo), use_container_width=True, hide_index=True)
            if st.button("🗑️ Kutuyu Sıfırla"):
                st.session_state["ozel_takip_kutusu"] = {}
                st.rerun()

with sag_taraf:
    st.subheader("💬 BTA Sohbet Odası")
    isat = st.text_input("Sohbet Takma Adınız:", value="BTA Sohbet")
    
    if isat.strip().lower() == "nurican":
        st.markdown(f"### 🚪 Oda Sayısı: {st.session_state['oda_sayisi']} | 👑 Yetkili Girişi")
        st.markdown(f"📊 **Ziyaret Sayısı:** `{st.session_state['ziyaret_sayaci']}`")
        if st.button("🗑️ Tüm Mesajları Temizle"):
            st.session_state["chat_history"] = []
            st.rerun()
            
    mesaj = st.text_input("Mesajınızı yazın:")
    if st.button("Mesajı Gönder 🚀") and mesaj.strip():
        mesaj_kucuk = mesaj.strip().lower()
        if not any(yasakli in mesaj_kucuk for yasakli in st.session_state["engellenen_kelimeler"]):
            st.session_state["chat_history"].append(f"<b>{isat}</b>: {mesaj}")
            st.rerun()

    st.markdown("<div style='background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;'>", unsafe_allow_html=True)
    for ch in reversed(st.session_state["chat_history"]):
        st.markdown(ch, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ⭐ Yıldız Değerlendirme
st.markdown("---")
yildiz_skor = st.feedback("stars")
