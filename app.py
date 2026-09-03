import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

# 1. Sayfa Yapılandırması ve Canlı Neon Tasarım (Siteyi Şenlendirdik)
st.set_page_config(page_title="BTa Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: 'Segoe UI', sans-serif;} 
    input {color: #000!important; background-color: #fff!important;}
    .stDataFrame {border: 1px solid #6366f1 !important; border-radius: 8px;}
    div.block-container {padding-top: 1rem; padding-bottom: 1rem;}
    
    /* Butonları Şenlendiren Neon Işıklar */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #eab308 0%, #ca8a04 100%) !important;
        color: white !important; font-weight: bold !important;
        border: none !important; box-shadow: 0 4px 15px rgba(234, 179, 8, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:nth-child(2) {
        background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important; font-weight: bold !important;
        border: none !important; box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
        transition: all 0.3s ease;
    }
    /* SPK Uyarısı Özel Kutusu */
    .spk-kutusu {
        background-color: rgba(220, 38, 38, 0.1);
        border: 2px solid #dc2626; padding: 10px;
        border-radius: 8px; margin-bottom: 15px;
        color: #fca5a5 !important; font-size: 0.85rem; text-align: justify;
    }
</style>
""", unsafe_allow_html=True)

# 2. Hafıza Kontrolleri
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "al_sat_goster" not in st.session_state: st.session_state["al_sat_goster"] = False
if "al_goster" not in st.session_state: st.session_state["al_goster"] = False

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

st.session_state["ziyaret_sayaci"] += 1

# 🚨 ZORUNLU SPK YASAL UYARISI (En Üstte)
st.markdown("""
<div class="spk-kutusu">
    <strong>⚖️ SPK YASAL UYARI:</strong> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
    Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında 
    imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan sinyaller ve puanlar tamamen matematiksel 
    verilere dayalı olup, mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir.
</div>
""", unsafe_allow_html=True)

st.title("⚡ BTa Sinyal Takip Merkezi 🚀")

# Üst Canlı Metrik Alanı
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
st.write(f"⭐ **Topluluk Puanı:** {puan:.2f} / 5.0 | 🔥 **Oy Veren:** {st.session_state['topham_oy_sayisi']} Kişi | 🚪 **Giriş Sayısı:** {st.session_state['ziyaret_sayaci']}")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"🟢 Canlı Bağlantı Aktif. Veriler Işık Hızında Çekiliyor. {guncel_an}")

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel dosyası okuma hatası: {e}")

# 📌 İNTERNETTEN CANLI FİYAT ÇEKİCİ
def internetten_canli_fiyat_bul(hisse_kodu):
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            return float(data['Close'].iloc[-1])
    except:
        pass
    return 0.0

def sayisal_mi(deger):
    try:
        float(str(deger).strip().replace(",", "."))
        return True
    except:
        return False

def sayiya_cevir(deger):
    try:
        return float(str(deger).strip().replace(",", "."))
    except:
        return 0.0

# 5. BTA SİNYAL MERKEZİ
st.subheader("📈 BTA SİNYAL MERKEZİ")

b1 = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
b2 = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

if b1: st.session_state["al_sat_goster"] = not st.session_state["al_sat_goster"]
if b2: st.session_state["al_goster"] = not st.session_state["al_goster"]

# 🟡 AL SAT Sinyal Mantığı (KUVVA)
if st.session_state["al_sat_goster"]:
    if df_kaynak is not None:
        tablo_verisi = []
        son_gecerli_hisse = "-"
        
        for idx in range(2, len(df_kaynak)):
            ilk_hucre = str(df_kaynak.iloc[idx, 0]).strip().upper()
            saf_kod = "".join(re.findall(r'[A-Z]+', ilk_hucre))
            if saf_kod and len(saf_kod) >= 4 and saf_kod not in ["NONE", "NAN", "AL_SAT", "PUAN", "BTA", "UCUZ", "ANAPAZAR", "YILDIZ"]:
                son_gecerli_hisse = saf_kod
            
            if len(df_kaynak.columns) > 19:
                t_degeri = df_kaynak.iloc[idx, 19]
                
                if sayisal_mi(t_degeri) and sayiya_cevir(t_degeri) >= 0.01:
                    hisse = son_gecerli_hisse
                    if hisse == "KUVVA":
                        canli_fiyat = internetten_canli_fiyat_bul(hisse)
                        puan_float = sayiya_cevir(t_degeri)
                        
                        tablo_verisi.append({
                            "Hisse Kodu 📈": hisse, 
                            "BTA PUAN (T) 📊": f"{puan_float:.2f}",
                            "💥 Canlı Fiyat": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Veri Alınamadı"
                        })
        if tablo_verisi: 
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)

# 🟢 AL Sinyal Mantığı (SONME)
if st.session_state["al_goster"]:
    if df_kaynak is not None:
        tablo_verisi_al = []
        son_gecerli_hisse_al = "-"
        
        for idx in range(2, len(df_kaynak)):
            ilk_hucre = str(df_kaynak.iloc[idx, 0]).strip().upper()
            saf_kod = "".join(re.findall(r'[A-Z]+', ilk_hucre))
            if saf_kod and len(saf_kod) >= 4 and saf_kod not in ["NONE", "NAN", "AL_SAT", "PUAN", "BTA", "UCUZ", "ANAPAZAR", "YILDIZ"]:
                son_gecerli_hisse_al = saf_kod
                
            if len(df_kaynak.columns) > 19:
                r_degeri = df_kaynak.iloc[idx, 17]
                t_degeri = df_kaynak.iloc[idx, 19]
                
                if sayisal_mi(r_degeri) and sayisal_mi(t_degeri) and sayiya_cevir(t_degeri) >= 0.01:
                    hisse = son_gecerli_hisse_al
                    if hisse == "SONME":
                        canli_fiyat = internetten_canli_fiyat_bul(hisse)
                        puan_float = sayiya_cevir(t_degeri)
                        
                        if hisse not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                        
                        tablo_verisi_al.append({
                            "Hisse Kodu 🚀": hisse, 
                            "BTA PUAN (T) 📊": f"{puan_float:.2f}",
                            "💥 Canlı Fiyat": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Veri Alınamadı"
                        })
        if tablo_verisi_al: 
            st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)

# 6. Sinyal Havuzu Bölümü
st.markdown("#### 🌟 Sinyal Havuzu 💰")
if st.session_state["ozel_takip_kutusu"]:
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        if hisse == "RAYSG": continue
        cfiy = internetten_canli_fiyat_bul(hisse)
        if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
            
        tk_list.append({
            "Hisse Kodu 🗝️": hisse,
            "Havuz Giriş Maliyeti": f"{bilge['kayit_fiyati']:.2f} TL",
            "Anlık Güncel Fiyat": f"{cfiy:.2f} TL"
        })
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=True):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()

# 7. ⭐ TOPLULUK PUANLAMA SİSTEMİ (GERİ GETİRİLDİ & ŞENLENDİRİLDİ)
st.divider()
st.subheader("🗳️ Paneli Değerlendir & Yıldız Ver")
yildiz = st.slider("Hizmet Kalitesi Puanınız (1-5 Yıldız):", 1, 5, 5, key="slider_puan")
if st.button("👍 Oy Ver ve Gönder", use_container_width=True):
    st.session_state["topham_oy_sayisi"] += 1
    st.session_state["topham_yildiz_puani"] += yildiz
    st.success("Oyunuz sisteme kaydedildi, teşekkür ederiz! 🎉")
    st.rerun()

# 8. BTa Sohbet Odası Bölümü
st.divider()
st.subheader("💬 BTa Canlı Sohbet Odası")
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Mesajınızı buraya yazın...")
if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    st.rerun()
