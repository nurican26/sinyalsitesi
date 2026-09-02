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
        background: rgba(15, 23, 42, 0.90);
        backdrop-filter: blur(10px);
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

EXCEL_FILE_PATH = "nurican.xls.xlsm"

# ==========================================
# 💾 HAFIZA BAŞLATMALARI (SESSION STATE)
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "ozel_takip_kutusu" not in st.session_state:
    st.session_state["ozel_takip_kutusu"] = {}

if "kisitli_kullanicilar" not in st.session_state:
    st.session_state["kisitli_kullanicilar"] = set()

if "oda_sayisi" not in st.session_state:
    st.session_state["oda_sayisi"] = 1

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

# 🟡 1. ADIM: AL SAT SİNYAL GÖSTERİMİ
if al_sat_butonu:
    with st.spinner("Excel verileri okunuyor..."):
        if os.path.exists(EXCEL_FILE_PATH):
            try:
                excel_obj = pd.ExcelFile(EXCEL_FILE_PATH)
                sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet)
                
                tablo_verisi = []
                for i in range(len(df)):
                    hisse_kodu_ham = str(df.iloc[i, 0]).strip().upper()
                    excel_anlik_verisi = str(df.iloc[i, 7]).replace(",", ".").strip()
                    bta_sinyal_al_sat = str(df.iloc[i, 20]).strip().upper() if df.shape > 20 else ""
                    
                    if not hisse_kodu_ham or hisse_kodu_ham in ["NAN", ""]:
                        continue
                        
                    hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                    
                    if "+" in bta_sinyal_al_sat or "AL" in bta_sinyal_al_sat:
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                        yüklenen_fiy = float(sayilar) if sayilar else 0.0
                        
                        ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                        
                        if not hisse_data.empty:
                            canli_fiyat = hisse_data['Close'].iloc[-1]
                            yuzde_fark = ((canli_fiyat - yüklenen_fiy) / yüklenen_fiy) * 100 if yüklenen_fiy > 0 else 0.0
                            durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yüklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                            
                            tablo_verisi.append({
                                "Hisse Kodu": hisse_temiz,
                                "Yüklediğiniz Fiyat": f"{yüklenen_fiy:.2f} TL",
                                "Anlık Canlı Fiyat": f"{canli_fiyat:.2f} TL",
                                "Canlı Kar/Zarar Oranı": durum_str
                            })
                
                if tablo_verisi:
                    st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
                else:
                    st.warning("U sütununda aktif Al-Sat sinyali bulunamadı.")
            except Exception as e:
                st.error(f"Veri işleme hatası: {e}")
        else:
            st.error("Excel dosyası bulunamadı!")

# 🟢 2. ADIM: AL SİNYALİNİ FARKLI KUTUYA ANLIK FİYATIYLA KAYDETME
if al_butonu:
    with st.spinner("AL sinyali veren hisseler kutuya kaydediliyor..."):
        if os.path.exists(EXCEL_FILE_PATH):
            try:
                excel_obj = pd.ExcelFile(EXCEL_FILE_PATH)
                sheet = "BTA" if "BTA" in excel_obj.sheet_names else excel_obj.sheet_names
                df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet)
                
                for i in range(len(df)):
                    hisse_kodu_ham = str(df.iloc[i, 0]).strip().upper()
                    excel_anlik_verisi = str(df.iloc[i, 7]).replace(",", ".").strip()
                    w_sutun_verisi = str(df.iloc[i, 22]).strip().upper() if df.shape > 22 else ""
                    
                    if not hisse_kodu_ham or hisse_kodu_ham in ["NAN", ""]:
                        continue
                        
                    hisse_temiz = hisse_kodu_ham.replace("[AL]", "").replace("[SAT]", "").replace(" ", "")
                    
                    if "[AL]" in w_sutun_verisi or "AL" in w_sutun_verisi:
                        sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", excel_anlik_verisi)
                        yüklenen_fiy = float(sayilar) if sayilar else 0.0
                        
                        ticker_kod = f"{hisse_temiz}.IS" if not hisse_temiz.endswith(".IS") else hisse_temiz
                        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
                        
                        if not hisse_data.empty:
                            canli_fiyat = hisse_data['Close'].iloc[-1]
                            
                            st.session_state["ozel_takip_kutusu"][hisse_temiz] = {
                                "kayit_fiyati": canli_fiyat,
                                "yuklenen_fiyat": yüklenen_fiy,
                                "kayit_zamani": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
                            }
                st.toast("🟢 [AL] Sinyalli hisseler aşağıdaki özel kutuya başarıyla kaydedildi!")
            except Exception as e:
                st.error(f"Sinyal hesaplama hatası: {e}")
        else:
            st.error("Excel dosyası bulunamadı!")

# 📦 SADECE AL SİNYALİ GELEN HİSSELERİN KAYDEDİLDİĞİ FARKLI KUTU
if st.session_state["ozel_takip_kutusu"]:
    st.markdown("---")
    st.subheader("📥 Kaydedilen AL Sinyali Takip Kutusu")
    
    kutu_tablo_verisi = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        ticker_kod = f"{hisse}.IS" if not hisse.endswith(".IS") else hisse
        hisse_data = yf.Ticker(ticker_kod).history(period="1d")
        
        if not hisse_data.empty:
            guncel_canli = hisse_data['Close'].iloc[-1]
            eski_fiyat = bilge["kayit_fiyati"]
            yuzde_fark = ((guncel_canli - eski_fiyat) / eski_fiyat) * 100 if eski_fiyat > 0 else 0.0
            durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if guncel_canli >= eski_fiyat else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
            
            kutu_tablo_verisi.append({
                "Hisse Kodu": hisse,
                "Kayıt Anındaki Canlı Fiyat": f"{eski_fiyat:.2f} TL",
                "Güncel Canlı Fiyat": f"{guncel_canli:.2f} TL",
                "Anlık Kar/Zarar Oranı": durum_str,
                "Kayıt Tarihi": bilge["kayit_zamani"]
            })
            
    if kutu_tablo_verisi:
        st.dataframe(pd.DataFrame(kutu_tablo_verisi), use_container_width=True, hide_index=True)
        if st.button("🗑️ Kutuyu Sıfırla"):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()

# ==========================================
# ⚠️ SPK YASAL UYARI METNİ
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style="background-color: rgba(220, 38, 38, 0.15); border-left: 5px solid #dc2626; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
        <p style="margin: 0; font-weight: bold; color: #f87171 !important;">⚠️ SPK YASAL UYARI (YATIRIM TAVSİYESİ KESİNLİKLE DEĞİLDİR):</p>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: #cbd5e1 !important; line-height: 1.5;">
            Burada yer alan yatırım bilgi, yorum ve tavsiyeleri <b>yatırım danışmanlığı kapsamında değildir.</b> 
            Yatırım danışmanlığı hizmeti, yetkili kuruluşlar tarafından kişilerin risk ve getiri tercihleri dikkate alınarak kişiye özel sunulmaktadır. 
            Burada yer alan yorum ve tahminler ise genel niteliktedir ve mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. 
            Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 💬 3. BÖLÜM: BTA SOHBET ODASI & YÖNETİM
# ==========================================
st.markdown("---")

# Kullanıcı "Nurican" yazdığında başlığın yanına gizli oda ikonu ve sayısı gelecek
