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
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
st.write(f"⭐ **Puan:** {puan:.2f} | 🚪 **Giriş:** {st.session_state['ziyaret_sayaci']}")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        # Excel'i formülleri atlayarak, sadece ham metin olarak okuyoruz
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

# Metinden sadece ilk kelimeyi alan temizleyici (Örn: "KUVVA +2,80" -> "KUVVA")
def ilk_kelimeyi_ayikla(metin):
    ham_metin = str(metin).strip().upper()
    parcalar = ham_metin.split()
    if parcalar:
        saf_kelime = "".join(re.findall(r'[A-Z]+', parcalar[0]))
        if len(saf_kelime) >= 4 and saf_kelime not in ["NONE", "NAN", "AL_SAT", "PUAN", "BTA", "UCUZ"]:
            return saf_kelime
    return None

# 5. BTA SİNYAL MERKEZİ
st.subheader("📈 BTA SİNYAL MERKEZİ")

b1 = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
b2 = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

if b1: st.session_state["al_sat_goster"] = not st.session_state["al_sat_goster"]
if b2: st.session_state["al_goster"] = not st.session_state["al_goster"]

# 🟡 AL SAT Sinyal Mantığı (Sabit Sütunlar: U=20, T=19, S=18)
if st.session_state["al_sat_goster"]:
    if df_kaynak is not None:
        tablo_verisi = []
        for idx in range(len(df_kaynak)):
            # İlk 4 satır başlık veya çöp veridir, taramayı es geç
            if idx < 4: continue
            
            if len(df_kaynak.columns) > 20:
                uv = str(df_kaynak.iloc[idx, 20]).strip().upper()
                
                # Hücre boş değilse, 0 veya 0,00 değilse aktif sinyaldir
                if uv and uv not in ["", "0", "0.0", "0,00", "0.00", "NAN", "-", "NONE", "AL_SAT SİNYALİ"]:
                    hisse = ilk_kelimeyi_ayikla(uv)
                    if not hisse: # Eğer U sütunundan çıkaramazsa A sütunundaki koda bak
                        hisse = "".join(re.findall(r'[A-Z]+', str(df_kaynak.iloc[idx, 0]).strip().upper()))
                    
                    if hisse and hisse != "RAYSG" and len(hisse) >= 4:
                        excel_anlik = str(df_kaynak.iloc[idx, 18]).strip() # S Sütunu
                        bta_puan = str(df_kaynak.iloc[idx, 19]).strip() # T Sütunu
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


# 🟢 AL Sinyal Mantığı (Sabit Sütunlar: W=22, T=19, S=18)
if st.session_state["al_goster"]:
    if df_kaynak is not None:
        tablo_verisi_al = []
        for idx in range(len(df_kaynak)):
            # İlk 4 satır başlık veya çöp veridir, taramayı es geç
            if idx < 4: continue
            
            if len(df_kaynak.columns) > 22:
                wv = str(df_kaynak.iloc[idx, 22]).strip().upper()
                
                # Hücre boş değilse, 0 veya 0,00 değilse aktif sinyaldir
                if wv and wv not in ["", "0", "0.0", "0,00", "0.00", "NAN", "-", "NONE", "AL"]:
                    hisse = ilk_kelimeyi_ayikla(wv)
                    if not hisse: # Eğer W sütunundan çıkaramazsa A sütunundaki koda bak
                        hisse = "".join(re.findall(r'[A-Z]+', str(df_kaynak.iloc[idx, 0]).strip().upper()))
                    
                    if hisse and hisse != "RAYSG" and len(hisse) >= 4:
                        excel_anlik = str(df_kaynak.iloc[idx, 18]).strip() # S Sütunu
                        bta_puan = str(df_kaynak.iloc[idx, 19]).strip() # T Sütunu
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
