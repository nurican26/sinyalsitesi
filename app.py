import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTa Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: 'Segoe UI', sans-serif;} 
    input {color: #000!important; background-color: #fff!important;}
    
    /* Mobil ve Masaüstü için tabloları rahatlatan ayar */
    .stDataFrame {width: 100% !important; border: 1px solid #4338ca !important; border-radius: 8px;}
    div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;}
    
    /* Canlı sinyal başlıkları için özel neon kutular */
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    .spk-kutusu {
        background-color: rgba(220, 38, 38, 0.1);
        border: 1px solid #dc2626; padding: 8px;
        border-radius: 6px; margin-top: 15px; margin-bottom: 10px;
        color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;
    }
    .bta-ana-baslik {
        font-size: 2rem !important; 
        font-weight: bold !important; 
        margin-top: 20px !important; 
        margin-bottom: 5px !important;
        text-align: left;
    }
    .bta-alt-metrik {
        font-size: 0.95rem !important; 
        color: #cbd5e1 !important;
        margin-bottom: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Hafıza Kontrolleri
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

st.session_state["ziyaret_sayaci"] += 1

# BAŞLIK VE METRİK ALANI
st.markdown('<div class="bta-ana-baslik">⚡ BTa Sinyal Takip Paneli 🚀</div>', unsafe_allow_html=True)

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
st.markdown(f'<div class="bta-alt-metrik">⭐ <b>Puan:</b> {puan:.2f} | 🔥 <b>Oy:</b> {st.session_state["topham_oy_sayisi"]} | 🚪 <b>Giriş:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel okuma hatası: {e}")

# 📌 OPTİMİZE EDİLMİŞ HIZLI FİYAT MOTORU (Sonsuz yükleme döngüsünü bitirir)
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300: # 5 dakika hafızada tutar
            return saved_price
            
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except:
        pass
    return 0.0

def temiz_metin_al(val):
    if pd.isna(val): return ""
    return str(val).strip().upper()

# 🌟 EXCEL VERİ AYIKLAMA VE TABLOLAMA MOTORU
tablo_alsat = []
tablo_al = []

if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            if len(df_kaynak.columns) > 22:
                uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20]) # U Sütunu
                wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22]) # W Sütunu
                t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])  # T Sütunu
                
                # 🟡 1. ADIM: AL SAT Sinyal Taraması
                if uv_degeri and uv_degeri not in ["NAN", "NONE", "0", "0.0", "-", "AL_SAT SİNYALİ"]:
                    hisse_ara = re.findall(r'[A-Z]+', uv_degeri)
                    if hisse_ara:
                        hisse = hisse_ara[0]
                        canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                        puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                        bta_puan = puan_bul[0] if puan_bul else (t_degeri if t_degeri else uv_degeri)
                        
                        tablo_alsat.append({
                            "Hisse Kodu 📈": hisse, 
                            "BTA PUAN (T)": bta_puan,
                            "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."
                        })
                
                # 🟢 2. ADIM: AL Sinyal Taraması
                if wv_degeri and wv_degeri not in ["NAN", "NONE", "0", "0.0", "-", "AL", "AL SİNYALİ"]:
                    hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                    if hisse_ara:
                        hisse = hisse_ara[0]
                        canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                        puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv_degeri)
                        bta_puan = puan_bul[0] if puan_bul else (t_degeri if t_degeri else wv_degeri)
                        
                        if hisse not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                        
                        tablo_al.append({
                            "Hisse Kodu 🚀": hisse, 
                            "BTA PUAN (T)": bta_puan,
                            "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."
                        })
        except:
            pass

# 🟡 AL SAT SİNYAL ALANI
st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
if tablo_alsat:
    st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else:
    st.write("🔒 Aktif AL SAT sinyali taranıyor...")

# 🟢 BTA SİNYAL MERKEZİ
st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
if tablo_al:
    st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else:
    st.write("🔒 Aktif BTA sinyali taranıyor...")

# 6. Sinyal Havuzu Bölümü
st.markdown("#### 🌟 Özel Takip Havuzu 💰")
if st.session_state["ozel_takip_kutusu"]:
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        cfiy = hızlı_canli_fiyat_bul(hisse)
        if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
            
        tk_list.append({
            "Hisse Kodu 🗝️": hisse,
            "Havuz Maliyeti": f"{bilge['kayit_fiyati']:.2f} TL",
            "Anlık Güncel": f"{cfiy:.2f} TL"
        })
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=True):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()

# 7. ⭐ TOPLULUK PUANLAMA SİSTEMİ
st.write("---")
st.subheader("⭐ Paneli Değerlendir")
yildiz_secimi = st.feedback("stars") 
if yildiz_secimi is not None:
    verilen_puan = yildiz_secimi + 1
    st.session_state["topham_oy_sayisi"] += 1
    st.session_state["topham_yildiz_puani"] += verilen_puan
    st.success(f"Teşekkürler! {verilen_puan} yıldız verdiniz. 🎉")
    st.rerun()

# 8. BTa Sohbet Odası Bölümü
st.write("---")
st.subheader("💬 BTa Canlı Sohbet")
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Mesajınızı buraya yazın...")
if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    st.rerun()

# 🚨 SPK YASAL UYARI KUTUSU EN ALTA SABİT
st.markdown("""
<div class="spk-kutusu">
    <strong>⚖️ SPK YASAL UYARI:</strong> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
    Veriler matematiksel olarak listelenmektedir.
</div>
""", unsafe_allow_html=True)
