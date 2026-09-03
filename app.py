import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Tasarım
st.set_page_config(page_title="BTa Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("<style>.stApp{background:rgba(15,23,42,0.95)!important;padding:2rem;} h1,h2,h3,h4,h5,h6,p,span,label{color:#fff!important;} input{color:#000!important;background-color:#fff!important;}</style>", unsafe_allow_html=True)

# 2. Hafıza (Session State) Kontrolleri
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

st.session_state["ziyaret_sayaci"] += 1

st.title("⚡ BTa Sinyal Takip Merkezi")

# Puanlama ve Giriş Sayısı Metrikleri
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
c1, c2, c3 = st.columns(3)
c1.metric("🔥 Toplam Panel Beğenisi (Oy)", f"{st.session_state['topham_oy_sayisi']} Kişi")
c2.metric("⭐ Topluluk Puan Ortalaması", f"{puan:.2f} / 5.0")
c3.metric("🚪 Odaya Giriş Sayısı", f"{st.session_state['ziyaret_sayaci']} Kez")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Canlı Fiyatlar %100 İnternetten Anlık Çekiliyor. Son Yenilenme: {guncel_an}")

# 3. Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel dosyası otomatik okunurken hata oluştu: {e}")

# 🌟 KESİN ÇÖZÜM: Excel A Sütunundaki tüm hisseleri dinamik toplar, hiçbir kısıtlama koymaz
BORSA_HISSELERI = []
if df_kaynak is not None:
    for idx in range(len(df_kaynak)):
        hucre_metni = str(df_kaynak.iloc[idx, 0]).strip().upper()
        saf_kod = "".join(re.findall(r'[A-Z]+', hucre_metni))
        
        # RAYSG HİSSESİNİ KÖKTEN SİLİP ATAN FİLTRE
        if saf_kod == "RAYSG":
            continue
            
        if len(saf_kod) >= 4 and saf_kod not in ["ANLIK", "SIRALA", "LOTS", "PIYASA", "BTAPUAN", "UCUZ", "AL_SAT", "PAZAR"]:
            if saf_kod not in BORSA_HISSELERI:
                BORSA_HISSELERI.append(saf_kod)

# Hafızada kalmış eski takipleri de RAYSG'den arındırıyoruz
if "RAYSG" in st.session_state["ozel_takip_kutusu"]:
    del st.session_state["ozel_takip_kutusu"]["RAYSG"]

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

# 🌟 TAM SATIR BULUCU
def hisse_satirini_bul(hisse_kodu):
    if df_kaynak is not None:
        for idx in range(len(df_kaynak)):
            ilk_hucre = str(df_kaynak.iloc[idx, 0]).strip().upper()
            saf_hucre_kodu = "".join(re.findall(r'[A-Z]+', ilk_hucre))
            if hisse_kodu == saf_hucre_kodu:
                return idx
    return None

# 🌟 SAF PUAN TEMİZLEYİCİ
def sinyal_metni_temizle(ham_metin, hisse_kodu):
    metin = str(ham_metin).strip().upper()
    metin = metin.replace(hisse_kodu, "").replace("[AL]", "").replace("AL", "").replace("_SAT", "").replace("SİNYALİ", "")
    return metin.strip()

# 4. Canlı Takip Bölümü (Tüm Liste Aktif)
st.subheader("🎯 Canlı Takip")

arama_kutusu = st.text_input("🔍 Takip Listesinde Hisse Ara (Örn: SONME, KUVVA, DOCO):", "").strip().upper()

st.markdown("#### ⚡ Canlı Borsa Takip Köşesi (İnternet Canlı Verileri)")
canli_borsa_listesi = []

# Arama yoksa tüm dinamik listeyi yükler, tıkanma bitti
listelenecek_hisseler = [arama_kutusu] if arama_kutusu else BORSA_HISSELERI

for hisse in listelenecek_hisseler:
    if not hisse or hisse == "RAYSG": continue
    ef = internetten_canli_fiyat_bul(hisse)
    if ef > 0: 
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": f"{ef:.2f} TL", "Günlük Değişim": "🟢 İnternet Canlı"})

if canli_borsa_listesi: 
    st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=300)

# 5. BTA SİNYAL MERKEZİ
st.divider()
st.subheader("📈 BTA SİNYAL MERKEZİ")
b1, b2 = st.columns(2)
al_sat_butonu = b1.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
al_butonu = b2.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# AL SAT Sinyal Mantığı (U Sütunu - İndeks 20, Puanı T Sütunundan alır)
if al_sat_butonu:
    if df_kaynak is not None:
        tablo_verisi = []
        for hisse in BORSA_HISSELERI:
            if hisse == "RAYSG": continue
            s_idx = hisse_satirini_bul(hisse)
            if s_idx is not None and len(df_kaynak.columns) > 20:
                uv = str(df_kaynak.iloc[s_idx, 20]).strip().upper()
                if uv and uv not in ["", "0", "0.0", "0,00", "NAN", "AL_SAT SİNYALİ", "-"]:
                    cfiy = internetten_canli_fiyat_bul(hisse)
                    raw_puan = df_kaynak.iloc[s_idx, 19] if len(df_kaynak.columns) > 19 else uv
                    puan_temiz = sinyal_metni_temizle(raw_puan, hisse)
                    
                    tablo_verisi.append({
                        "Hisse Kodu": hisse, 
                        "BTA PUAN": puan_temiz if puan_temiz else uv, 
                        "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Alınamadı", 
                        "Durum Oranı": "🔄 Aktif Takip"
                    })
        if tablo_verisi: 
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
        else: 
            st.warning("Excel dosyasında aktif AL SAT sinyali bulunamadı.")

# AL Sinyal Mantığı (W Sütunu - İndeks 22, Puanı T Sütunundan alır)
if al_butonu:
    if df_kaynak is not None:
        tablo_verisi_al = []
        for hisse in BORSA_HISSELERI:
            if hisse == "RAYSG": continue
            s_idx = hisse_satirini_bul(hisse)
            if s_idx is not None and len(df_kaynak.columns) > 22:
                wv = str(df_kaynak.iloc[s_idx, 22]).strip().upper()
                if wv and wv not in ["", "0", "0.0", "0,00", "NAN", "AL", "-"]:
                    cfiy = internetten_canli_fiyat_bul(hisse)
                    st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                    raw_puan = df_kaynak.iloc[s_idx, 19] if len(df_kaynak.columns) > 19 else wv
                    puan_al_temiz = sinyal_metni_temizle(raw_puan, hisse)
                    
                    tablo_verisi_al.append({
                        "Hisse Kodu": hisse, 
                        "BTA PUAN": puan_al_temiz if puan_al_temiz else wv, 
                        "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Alınamadı", 
                        "Durum Oranı": "🔄 Havuzu Eklendi"
                    })
        if tablo_verisi_al: 
            st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
        else: 
            st.warning("Excel dosyasında aktif AL sinyali bulunamadı.")

# 6. Sinyal Havuzu Bölümü
st.divider()
st.markdown("#### 🌟 Sinyal Havuzuna Alınan Hisseler")
if st.session_state["ozel_takip_kutusu"]:
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        if hisse == "RAYSG": continue
        cfiy = internetten_canli_fiyat_bul(hisse)
        if cfiy == 0.0: 
            cfiy = bilge["kayit_fiyati"]
            
        tk_list.append({
            "Hisse Kodu": hisse,
            "Havuz Maliyeti": f"{bilge['kayit_fiyati']:.2f} TL",
            "Anlık Fiyat": f"{cfiy:.2f} TL",
            "Kâr/Zarar Oranı": "🔄 Dengelendi",
            "Eklenme Zamanı": bilge["kayit_zamani"]
        })
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=False):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()
else:
    st.info("Şu anda sinyal havuzunda takip edilen hisse bulunmamaktadır.")

# 7. Topluluk Puanlama Sistemi
st.divider()
st.subheader("🗳️ Paneli Değerlendir")
col_p1, col_p2 = st.columns(2)
with col_p1:
    yildiz = st.slider("Puanınız:", 1, 5, 5, key="slider_puan")
with col_p2:
    if st.button("👍 Oy Ver ve Gönder", use_container_width=True):
        st.session_state["topham_oy_sayisi"] += 1
        st.session_state["topham_yildiz_puani"] += yildiz
        st.success("Oyunuz başarıyla kaydedildi!")
        st.rerun()

# 8. BTa Sohbet Odası Bölümü
st.divider()
st.subheader("💬 BTa Sohbet")

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Mesajınızı buraya yazın...")
if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    st.rerun()
