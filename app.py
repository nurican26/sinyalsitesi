import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

# 1. Sayfa Yapılandırması ve Tasarım (Mobil Uyumlu)
st.set_page_config(page_title="BTa Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("""
<style>
    .stApp {background: rgba(15,23,42,0.95)!important; padding: 1rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important;} 
    input {color: #000!important; background-color: #fff!important;}
    /* Mobil cihazlarda tabloların taşmasını önleyen ve rahat kaydırılan ayar */
    .stDataFrame {width: 100% !important;}
</style>
""", unsafe_allow_html=True)

# 2. Hafıza (Session State) Kontrolleri
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

st.session_state["ziyaret_sayaci"] += 1

st.title("⚡ BTa Sinyal Takip Merkezi")

# Metrikleri telefonda düzgün görünmesi için dikey/esnek formatta sunuyoruz
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
st.write(f"🔥 **Toplam Panel Beğenisi:** {st.session_state['topham_oy_sayisi']} Kişi | ⭐ **Topluluk Puanı:** {puan:.2f} / 5.0 | 🚪 **Oda Girişi:** {st.session_state['ziyaret_sayaci']}")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Sadece sinyalli hisselerin canlı fiyatları anlık çekiliyor. Son Yenilenme: {guncel_an}")

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel dosyası otomatik okunurken hata oluştu: {e}")

# 📌 İNTERNETTEN CANLI FİYAT ÇEKİCİ (Sadece sinyalliler için çağrılacak)
def internetten_canli_fiyat_bul(hisse_kodu):
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            return float(data['Close'].iloc[-1])
    except:
        pass
    return 0.0

# 🌟 AKTİF SİNYALLİ HİSSELİRİ TARAMA (Tıkanmayı önleyen ana motor)
aktif_sinyal_listesi = []

if df_kaynak is not None:
    for idx in range(len(df_kaynak)):
        ilk_hucre = str(df_kaynak.iloc[idx, 0]).strip().upper()
        hisse = "".join(re.findall(r'[A-Z]+', ilk_hucre))
        
        # Geçersiz satırları ve RAYSG'yi atla
        if not hisse or hisse == "RAYSG" or len(hisse) < 4 or hisse in ["ANLIK", "SIRALA", "LOTS", "PIYASA", "BTAPUAN", "UCUZ", "AL_SAT", "PAZAR"]:
            continue
            
        # Sütun kontrolleri (U:20, W:22, T:19)
        uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if len(df_kaynak.columns) > 20 else ""
        wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if len(df_kaynak.columns) > 22 else ""
        raw_puan = str(df_kaynak.iloc[idx, 19]).strip() if len(df_kaynak.columns) > 19 else "-"
        
        is_al_sat = uv and uv not in ["", "0", "0.0", "0,00", "NAN", "AL_SAT SİNYALİ", "-", "NONE"]
        is_al = (wv and wv not in ["", "0", "0.0", "0,00", "NAN", "AL", "-", "NONE"]) or "AL" in wv
        
        # Eğer hissede AL veya AL SAT sinyallerinden biri varsa listeye ekle
        if is_al_sat or is_al:
            sinyal_tipi = "🟡 AL SAT" if is_al_sat else "🟢 AL"
            cfiy = internetten_canli_fiyat_bul(hisse) # Sadece bu hisse için internete gidiyor!
            
            # Eğer AL sinyalindeyse otomatik havuz hafızasına ekle
            if is_al and cfiy > 0:
                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                
            aktif_sinyal_listesi.append({
                "Hisse Kodu": hisse,
                "Sinyal Tipi": sinyal_tipi,
                "BTA PUAN (T)": raw_puan,
                "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Alınamadı"
            })

# 4. AKTİF SİNYAL MERKEZİ TABLOSU (Açılışta direkt gösterilir, buton aramaya gerek kalmaz)
st.subheader("📈 Aktif BTa Sinyal Listesi")
if aktif_sinyal_listesi:
    df_sinyal = pd.DataFrame(aktif_sinyal_listesi)
    st.dataframe(df_sinyal, use_container_width=True, hide_index=True)
else:
    st.info("Excel dosyasında şu an aktif AL veya AL SAT sinyali veren hisse bulunamadı.")

# 5. Sinyal Havuzu Bölümü
st.divider()
st.markdown("#### 🌟 Sinyal Havuzuna Alınan Hisseler")
if st.session_state["ozel_takip_kutusu"]:
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        if hisse == "RAYSG": continue
        # Havuzdaki az sayıda hisse için hızlı fiyat kontrolü
        cfiy = internetten_canli_fiyat_bul(hisse)
        if cfiy == 0.0: 
            cfiy = bilge["kayit_fiyati"]
            
        tk_list.append({
            "Hisse Kodu": hisse,
            "Havuz Maliyeti": f"{bilge['kayit_fiyati']:.2f} TL",
            "Anlık Fiyat": f"{cfiy:.2f} TL",
            "Eklenme Zamanı": bilge["kayit_zamani"]
        })
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=True):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()
else:
    st.info("Şu anda sinyal havuzunda takip edilen hisse bulunmamaktadır.")

# 6. Topluluk Puanlama Sistemi (Telefona uygun alt alta tasarım)
st.divider()
st.subheader("🗳️ Paneli Değerlendir")
yildiz = st.slider("Puanınız:", 1, 5, 5, key="slider_puan")
if st.button("👍 Oy Ver ve Gönder", use_container_width=True):
    st.session_state["topham_oy_sayisi"] += 1
    st.session_state["topham_yildiz_puani"] += yildiz
    st.success("Oyunuz başarıyla kaydedildi!")
    st.rerun()

# 7. BTa Sohbet Odası Bölümü
st.divider()
st.subheader("💬 BTa Sohbet")

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Mesajınızı buraya yazın...")
if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    st.rerun()
