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
st.success(f"💡 Sistem Aktif. Canlı Fiyatlar İnternet Üzerinden (Yahoo Finance) Anlık Çekiliyor. Son Yenilenme: {guncel_an}")
st.markdown("<div style='background-color:rgba(220,38,38,0.15);border-left:5px solid #dc2626;padding:10px;border-radius:5px;margin-bottom:15px;'><p style='margin:0;font-weight:bold;color:#fff!important;'>⚠️ SPK YASAL UYARI: Yatırım tavsiyesi değildir.</p></div>", unsafe_allow_html=True)

# 3. Sinyal Puanları İçin Arka Planda Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel dosyası sinyal puanları için okunurken hata oluştu: {e}")

BORSA_HISSELERI = ["RAYSG", "SONME", "ZEDUR", "DOCO", "LYDYE", "MRSHL", "CMBTN", "UFUK", "GUNDG", "MAALT", "VERUS", "ALCAR", "AYCES", "ALKLC", "KAPLM", "INGRM", "FORTE", "PKENT", "DUNYH"]

# 🌟 KESİN İNTERNET ÇÖZÜMÜ: Fiyatı Excel'den değil, internet üzerinden (Borsa İstanbul canlı verisinden) çeker
def internetten_canli_fiyat_bul(hisse_kodu):
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        # En güncel günlük kapanış veya anlık fiyat verisini indirir
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            return float(data['Close'].iloc[-1])
    except:
        pass
    return 0.0

# 🌟 SİNYAL METNİ TEMİZLEME: "SONME [AL]" gibi metinlerden yasaklı kelimeleri silip saf puanı (+0,08 vb.) bırakır
def sinyal_metni_temizle(ham_metin, hisse_kodu):
    metin = str(ham_metin).strip().upper()
    metin = metin.replace(hisse_kodu, "").replace("[AL]", "").replace("AL", "").replace("_SAT", "").replace("SİNYALİ", "")
    return metin.strip()

# 4. Canlı Takip Bölümü (TAMAMEN İNTERNET TABANLI YAPILDI)
st.subheader("🎯 Canlı Takip")
st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi (İnternet Verisi)")
canli_borsa_listesi = []

for hisse in BORSA_HISSELERI:
    ef = internetten_canli_fiyat_bul(hisse)
    if ef > 0: 
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": f"{ef:.2f} TL", "Günlük Değişim": "🟢 Canlı İnternet Verisi"})
    else:
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": "Yükleniyor...", "Günlük Değişim": "🔄 Bekleniyor"})

if canli_borsa_listesi: 
    st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)

# 5. BTA SİNYAL MERKEZİ
st.divider()
st.subheader("📈 BTA SİNYAL MERKEZİ")
b1, b2 = st.columns(2)
al_sat_butonu = b1.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
al_butonu = b2.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# AL SAT Sinyal Mantığı
if al_sat_butonu:
    if df_kaynak is not None:
        tablo_verisi = []
        for i in range(len(df_kaynak)):
            try:
                # Excel'in ilgili sütunlarında sinyal arar
                for col_check in:
                    if len(df_kaynak.columns) > col_check and not pd.isna(df_kaynak.iloc[i, col_check]):
                        uv = str(df_kaynak.iloc[i, col_check]).strip().upper()
                        if "AL_SAT" in uv or "+" in uv:
                            h_adi = next((h for h in BORSA_HISSELERI if h in uv), None)
                            if not h_adi:
                                h_adi = next((h for h in BORSA_HISSELERI if h in str(df_kaynak.iloc[i, 0]).strip().upper()), None)
                            
                            if h_adi:
                                # Fiyat kaymasını önlemek için canlı fiyatı internetten çeker
                                cfiy = internetten_canli_fiyat_bul(h_adi)
                                puan_temiz = sinyal_metni_temizle(df_kaynak.iloc[i, col_check], h_adi)
                                tablo_verisi.append({
                                    "Hisse Kodu": h_adi, 
                                    "BTA PUAN": puan_temiz, 
                                    "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Alınamadı", 
                                    "Durum Oranı": "🔄 Aktif Takip"
                                })
                                break
            except:
                pass
        if tablo_verisi: 
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
        else: 
            st.warning("Excel dosyasında aktif AL SAT sinyali bulunamadı.")
    else:
        st.error("Sistemde 'nurican.xls.xlsm' dosyası bulunamadı.")

# AL Sinyal Mantığı
if al_butonu:
    if df_kaynak is not None:
        tablo_verisi_al = []
        for i in range(len(df_kaynak)):
            try:
                for col_check in:
                    if len(df_kaynak.columns) > col_check and not pd.isna(df_kaynak.iloc[i, col_check]):
                        wv = str(df_kaynak.iloc[i, col_check]).strip().upper()
                        if "AL" in wv or "+" in wv:
                            h_adi = next((h for h in BORSA_HISSELERI if h in wv), None)
                            if not h_adi:
                                h_adi = next((h for h in BORSA_HISSELERI if h in str(df_kaynak.iloc[i, 0]).strip().upper()), None)
                            
                            if h_adi:
                                cfiy = internetten_canli_fiyat_bul(h_adi)
                                st.session_state["ozel_takip_kutusu"][h_adi] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                                puan_al_temiz = sinyal_metni_temizle(df_kaynak.iloc[i, col_check], h_adi)
                                
                                tablo_verisi_al.append({
                                    "Hisse Kodu": h_adi, 
                                    "BTA PUAN": puan_al_temiz, 
                                    "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Alınamadı", 
                                    "Durum Oranı": "🔄 Havuzu Eklendi"
                                })
                                break
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
        cfiy = internetten_canli_fiyat_bul(hisse)
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
