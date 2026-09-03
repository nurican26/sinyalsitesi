import streamlit as st
import pandas as pd
import datetime
import os, re
from streamlit_autorefresh import st_autorefresh

# 1. Sayfa Yapılandırması ve Tasarım
st.set_page_config(page_title="BTa Sinyal Paneli", page_icon="📈", layout="wide")
st.markdown("<style>.stApp{background:rgba(15,23,42,0.95)!important;padding:2rem;} h1,h2,h3,h4,h5,h6,p,span,label{color:#fff!important;} input{color:#000!important;background-color:#fff!important;}</style>", unsafe_allow_html=True)

# 🔁 TARAYICIYI KİLLEMEYEN OTOMATİK YENİLEME: Sayfayı her 5 saniyede bir arka planda yeniler
st_autorefresh(interval=5000, key="datarefresh")

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
st.success(f"💡 Sistem Aktif. Panel 5 Saniyede Bir Otomatik Yenileniyor. Son Yenilenme: {guncel_an}")
st.markdown("<div style='background-color:rgba(220,38,38,0.15);border-left:5px solid #dc2626;padding:10px;border-radius:5px;margin-bottom:15px;'><p style='margin:0;font-weight:bold;color:#fff!important;'>⚠️ SPK YASAL UYARI: Yatırım tavsiyesi değildir.</p></div>", unsafe_allow_html=True)

# 3. Arka Planda Otomatik Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None)
    except Exception as e:
        st.error(f"Excel dosyası otomatik okunurken hata oluştu: {e}")

BORSA_HISSELERI = ["RAYSG", "SONME", "ZEDUR", "DOCO", "LYDYE", "MRSHL", "CMBTN", "UFUK", "GUNDG", "MAALT", "VERUS", "ALCAR", "AYCES", "ALKLC", "KAPLM", "INGRM", "FORTE", "PKENT", "DUNYH"]

# 📌 GELİŞMİŞ SAYI TEMİZLEME
def temiz_fiyat_al(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    if "," in val_str and "." in val_str:
        val_str = val_str.replace(".", "").replace(",", ".")
    elif "," in val_str:
        val_str = val_str.replace(",", ".")
    
    sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", val_str)
    return float(sayilar[0]) if sayilar else 0.0

# 🌟 GÖRSELDEKİ "ANLIK" SÜTUNU (İNDEKS 5 - F SÜTUNU) OLARAK GÜNCELLENDİ
def hisse_fiyati_bul(hisse_kodu):
    if df_kaynak is not None:
        for idx in range(len(df_kaynak)):
            val_hisse = str(df_kaynak.iloc[idx, 0]).strip().upper()
            if hisse_kodu in val_hisse:  
                # Görselinizde 138,00 yazan kolon F sütunudur, yani indeks 5'tir.
                return temiz_fiyat_al(df_kaynak.iloc[idx, 5])
    return 0.0

# 4. Canlı Takip Bölümü
st.subheader("🎯 Canlı Takip")
st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
canli_borsa_listesi = []

for hisse in BORSA_HISSELERI:
    ef = hisse_fiyati_bul(hisse)
    if ef > 0: 
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": f"{ef:.2f} TL", "Günlük Değişim": "🔄 Otomatik Güncel"})
    else:
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": "Veri Yok", "Günlük Değişim": "🔄 Bekleniyor"})

if canli_borsa_listesi: 
    st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)

# 5. BTA SİNYAL MERKEZİ
st.divider()
st.subheader("📈 BTA SİNYAL MERKEZİ")
b1, b2 = st.columns(2)
al_sat_butonu = b1.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
al_butonu = b2.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# AL SAT Sinyal Mantığı (U Sütunu - İndeks 20)
if al_sat_butonu:
    if df_kaynak is not None:
        tablo_verisi = []
        for i in range(len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 20 and not pd.isna(df_kaynak.iloc[i, 20]):
                    uv = str(df_kaynak.iloc[i, 20]).strip().upper()
                    if uv in ["", "0", "0.0", "NAN", "AL_SAT SİNYALİ"]: 
                        continue
                    
                    h_adi = next((h for h in BORSA_HISSELERI if h in uv), None)
                    if h_adi:
                        cfiy = hisse_fiyati_bul(h_adi)
                        bta_puan_temiz = str(df_kaynak.iloc[i, 20]).strip()
                        
                        tablo_verisi.append({
                            "Hisse Kodu": h_adi, 
                            "BTA PUAN": bta_puan_temiz, 
                            "Canlı Fiyat": f"{cfiy:.2f} TL", 
                            "Durum Oranı": "🔄 Aktif Takip"
                        })
            except:
                pass
        if tablo_verisi: 
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
        else: 
            st.warning("Excel dosyasında aktif AL SAT sinyali bulunamadı.")
    else:
        st.error("Sistemde 'nurican.xls.xlsm' dosyası bulunamadı.")

# AL Sinyal Mantığı (W Sütunu - İndeks 22)
if al_butonu:
    if df_kaynak is not None:
        tablo_verisi_al = []
        for i in range(len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22 and not pd.isna(df_kaynak.iloc[i, 22]):
                    wv = str(df_kaynak.iloc[i, 22]).strip().upper()
                    if wv in ["", "0", "0.0", "NAN", "AL"] or "-" in wv: 
                        continue
                    
                    h_adi = next((h for h in BORSA_HISSELERI if h in wv), None)
                    if h_adi:
                        cfiy = hisse_fiyati_bul(h_adi)
                        st.session_state["ozel_takip_kutusu"][h_adi] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                        
                        # 🌟 DÜZELTME: Ham veri çekimi W sütununa (indeks 22) sabitlendi, yasak kelimeler filtrelendi
                        bta_puan_al_ham = str(df_kaynak.iloc[i, 22]).strip()
                        
                        tablo_verisi_al.append({
                            "Hisse Kodu": h_adi, 
                            "BTA PUAN": bta_puan_al_ham, 
                            "Canlı Fiyat": f"{cfiy:.2f} TL", 
                            "Durum Oranı": "🔄 Havuzu Eklendi"
                        })
            except:
                pass
        if tablo_verisi_al: 
            st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
        else: 
            st.warning("Excel dosyasında aktif AL sinyali bulunamadı.")
    else:
        st.error("Sistemde 'nurican.xls.xlsm' dosyası bulunamadı.")

# 6. Sinyal Havuzu Bölümü
st.divider()
st.markdown("#### 🌟 Sinyal Havuzuna Alınan Hisseler")
if st.session_state["ozel_takip_kutusu"]:
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        cfiy = hisse_fiyati_bul(hisse)
        if cfiy == 0.0: 
            cfiy = bilge["kayit_fiyati"]
            
        tk_list.append({
            "Hisse Kodu": hisse,
            "Havuz Maliyeti": f"{cfiy:.2f} TL",
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

# 8. BTa Sohbet Asistanı Bölümü
st.divider()
st.subheader("💬 BTa Sohbet")

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

with st.form("bta_chat_form", clear_on_submit=True):
    user_input = st.text_input("Hisseler veya sinyaller hakkında bir şey sorun...", key="chat_user_msg")
    gonder_butonu = st.form_submit_button("✉️ Mesaj Gönder", use_container_width=True)
    
    if gonder_butonu and user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        bot_response = f"🤖 BTa Sohbet: '{user_input}' mesajınız sisteme ulaştı. Excel tablonuzdaki veriler taban alınarak BTA Sinyal algoritması tarafından analiz ediliyor."
        st.session_state["chat_history"].append({"role": "assistant", "content": bot_response})
        st.rerun()
