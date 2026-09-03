import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

# 1. Sayfa Yapılandırması ve Tasarım
st.set_page_config(page_title="BTa Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("""
<style>
    .stApp {background: rgba(15,23,42,0.95)!important; padding: 0.5rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important;} 
    input {color: #000!important; background-color: #fff!important;}
    .stDataFrame {width: 100% !important;}
    div.block-container {padding-top: 1rem; padding-bottom: 1rem;}
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

st.title("⚡ BTa Sinyal Takip")

# Üst Bilgiler
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
st.write(f"⭐ **Puan:** {puan:.2f} | 🚪 **Giriş:** {st.session_state['ziyaret_sayaci']}")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        # Excel'i tamamen ham haliyle, hiçbir başlığı atlamadan okuyoruz
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

# 🌟 METNİN İÇİNDEN HİSSE KODUNU AYIKLAYAN SİHRİBAZ (Örn: "KUVVA +2,80" -> "KUVVA")
def metinden_hisse_kodu_bul(metin):
    parcalar = str(metin).strip().upper().split()
    if parcalar:
        temiz_kod = "".join(re.findall(r'[A-Z]+', parcalar[0]))
        if len(temiz_kod) >= 4 and temiz_kod not in ["ANLIK", "SIRALA", "LOTS", "PIYASA", "BTAPUAN", "UCUZ", "AL_SAT", "PAZAR", "HISSE", "NONE", "NAN"]:
            return temiz_kod
    return None

# 5. BTA SİNYAL MERKEZİ
st.subheader("📈 BTA SİNYAL MERKEZİ")

b1 = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
b2 = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

if b1: st.session_state["al_sat_goster"] = not st.session_state["al_sat_goster"]
if b2: st.session_state["al_goster"] = not st.session_state["al_goster"]

# 🟡 AL SAT Sinyal Mantığı
if st.session_state["al_sat_goster"]:
    if df_kaynak is not None:
        tablo_verisi = []
        # Excel'deki tüm sütunları tarayarak dinamik AL_SAT başlığını buluyoruz
        col_idx = None
        for c in df_kaynak.columns:
            column_str = str(df_kaynak[c].iloc[:5]).upper()
            if "AL_SAT" in column_str or "AL SAT" in column_str:
                col_idx = c
                break
        if col_idx is None: col_idx = 20 # Bulamazsa varsayılan U sütunu

        for idx in range(len(df_kaynak)):
            uv = str(df_kaynak.iloc[idx, col_idx]).strip().upper()
            
            # Sütunda 0,00 veya boşluk harici gerçek bir yazı/sinyal var mı?
            if uv and uv not in ["", "0", "0.0", "0,00", "0.00", "NAN", "-", "NONE"]:
                hisse = metinden_hisse_kodu_bul(uv)
                if hisse and hisse != "RAYSG":
                    excel_anlik = str(df_kaynak.iloc[idx, col_idx - 2]).strip() if col_idx >= 2 else "-" # S Sütunu
                    bta_puan = str(df_kaynak.iloc[idx, col_idx - 1]).strip() if col_idx >= 1 else "-" # T Sütunu
                    canli_fiyat = internetten_canli_fiyat_bul(hisse)
                    
                    tablo_verisi.append({
                        "Hisse Kodu": hisse, 
                        "BTA PUAN (T)": bta_puan,
                        "Excel Anlık (S)": excel_anlik,
                        "İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Veri Alınamadı",
                        "Sinyal İçeriği (U)": uv
                    })
        if tablo_verisi: 
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)


# 🟢 AL Sinyal Mantığı
if st.session_state["al_goster"]:
    if df_kaynak is not None:
        tablo_verisi_al = []
        # Excel'deki tüm sütunları tarayarak dinamik AL başlığını buluyoruz
        col_idx_w = None
        for c in df_kaynak.columns:
            column_str = str(df_kaynak[c].iloc[:5]).upper()
            if "AL" in column_str and "AL_SAT" not in column_str and "AL SAT" not in column_str:
                col_idx_w = c
                break
        if col_idx_w is None: col_idx_w = 22 # Bulamazsa varsayılan W sütunu

        for idx in range(len(df_kaynak)):
            wv = str(df_kaynak.iloc[idx, col_idx_w]).strip().upper()
            
            # Sütunda 0,00 veya boşluk harici gerçek bir yazı/sinyal var mı?
            if wv and wv not in ["", "0", "0.0", "0,00", "0.00", "NAN", "-", "NONE"]:
                hisse = metinden_hisse_kodu_bul(wv)
                if hisse and hisse != "RAYSG":
                    excel_anlik = str(df_kaynak.iloc[idx, col_idx_w - 4]).strip() if col_idx_w >= 4 else "-" # S Sütunu
                    bta_puan = str(df_kaynak.iloc[idx, col_idx_w - 3]).strip() if col_idx_w >= 3 else "-" # T Sütunu
                    canli_fiyat = internetten_canli_fiyat_bul(hisse)
                    
                    if hisse not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                        st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                    
                    tablo_verisi_al.append({
                        "Hisse Kodu": hisse, 
                        "BTA PUAN (T)": bta_puan,
                        "Excel Anlık (S)": excel_anlik,
                        "İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Veri Alınamadı",
                        "Sinyal İçeriği (W)": wv
                    })
        if tablo_verisi_al: 
            st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)


# 6. Sinyal Havuzu Bölümü
st.markdown("#### 🌟 Sinyal Havuzu")
if st.session_state["ozel_takip_kutusu"]:
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        if hisse == "RAYSG": continue
        cfiy = internetten_canli_fiyat_bul(hisse)
        if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
            
        tk_list.append({
            "Hisse Kodu": hisse,
            "Havuz Giriş Fiyatı": f"{bilge['kayit_fiyati']:.2f} TL",
            "Anlık Fiyat": f"{cfiy:.2f} TL"
        })
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=True):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()

# 7. BTa Sohbet Odası Bölümü
st.divider()
st.subheader("💬 BTa Sohbet")
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Mesajınızı yazın...")
if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    st.rerun()
