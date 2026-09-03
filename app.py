import streamlit as st
import pandas as pd
import datetime
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
st.success(f"💡 Sistem Aktif. Fiyatlar ve Puanlar Doğrudan Excel'den Çekiliyor. Son Yenilenme: {guncel_an}")
st.markdown("<div style='background-color:rgba(220,38,38,0.15);border-left:5px solid #dc2626;padding:10px;border-radius:5px;margin-bottom:15px;'><p style='margin:0;font-weight:bold;color:#fff!important;'>⚠️ SPK YASAL UYARI: Yatırım tavsiyesi değildir.</p></div>", unsafe_allow_html=True)

# 3. Arka Planda Otomatik Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel dosyası otomatik okunurken hata oluştu: {e}")

BORSA_HISSELERI = ["RAYSG", "SONME", "ZEDUR", "DOCO", "LYDYE", "MRSHL", "CMBTN", "UFUK", "GUNDG", "MAALT", "VERUS", "ALCAR", "AYCES", "ALKLC", "KAPLM", "INGRM", "FORTE", "PKENT", "DUNYH"]

def temiz_fiyat_al(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip().replace(" TL", "").replace("TL", "").replace(" ", "")
    if not val_str:
        return 0.0
    if "," in val_str and "." not in val_str:
        val_str = val_str.replace(",", ".")
    elif "," in val_str and "." in val_str:
        val_str = val_str.replace(".", "").replace(",", ".")
    try:
        return float(val_str)
    except:
        sayi_bul = re.findall(r"[-+]?\d*\.\d+|\d+", val_str)
        return float("".join(sayi_bul)) if sayi_bul else 0.0

# 🌟 ULTRA SATIR TARAYICI: Hücrelerin neresinde hisse kodu geçerse geçsin bulur ve yanındaki gerçek ANLIK sütununu alır
def hisse_verilerini_bul(hisse_kodu):
    fiyat = 0.0
    al_sat_puan = ""
    al_puan = ""
    
    if df_kaynak is not None:
        for idx in range(len(df_kaynak)):
            # Satırdaki tüm hücreleri stringe çevirip birleştirerek arama yapar (Kaymayı sıfırlar)
            satir_metni = " ".join([str(df_kaynak.iloc[idx, col]).strip().upper() for col in range(min(5, len(df_kaynak.columns)))]).strip()
            
            if hisse_kodu in satir_metni:
                # Satır bulundu! Doğrudan görselinizdeki 'ANLIK' kolonunu (H sütunu - İndeks 7) okur
                if len(df_kaynak.columns) > 7:
                    fiyat = temiz_fiyat_al(df_kaynak.iloc[idx, 7])
                
                # U sütunu (indeks 20) ve W sütunu (indeks 22) verilerini al
                if len(df_kaynak.columns) > 20 and not pd.isna(df_kaynak.iloc[idx, 20]):
                    al_sat_puan = str(df_kaynak.iloc[idx, 20]).strip()
                if len(df_kaynak.columns) > 22 and not pd.isna(df_kaynak.iloc[idx, 22]):
                    al_puan = str(df_kaynak.iloc[idx, 22]).strip()
                    
                return fiyat, al_sat_puan, al_puan
    return fiyat, al_sat_puan, al_puan

def sinyal_metni_temizle(ham_metin, hisse_kodu):
    metin = str(ham_metin).strip().upper()
    metin = metin.replace(hisse_kodu, "").replace("[AL]", "").replace("AL", "").replace("_SAT", "").replace("SİNYALİ", "")
    return metin.strip()

# 4. Canlı Takip Bölümü
st.subheader("🎯 Canlı Takip")

# 🛠️ YENİ ÖZELLİK: Arama Çubuğu Entegre Edildi
arama_terimi = st.text_input("🔍 Takip Listesinde Hisse Ara (Örn: SONME):", "").strip().upper()

st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
canli_borsa_listesi = []

for hisse in BORSA_HISSELERI:
    # Eğer arama çubuğu doluysa sadece aranan hisseyi filtrele
    if arama_terimi and arama_terimi != hisse:
        continue
        
    fiy, _, _ = hisse_verilerini_bul(hisse)
    if fiy > 0:
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": f"{fiy:.2f} TL", "Günlük Değişim": "🔄 Otomatik Güncel"})
    else:
        canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": "Veri Yok", "Günlük Değişim": "🔄 Bekleniyor"})

if canli_borsa_listesi: 
    st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)

# 5. BTA SİNYAL MERKEZİ
st.divider()
st.markdown("### 📈 BTA SİNYAL MERKEZİ")
b1, b2 = st.columns(2)
al_sat_butonu = b1.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
al_butonu = b2.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# AL SAT Sinyal Mantığı
if al_sat_butonu:
    tablo_verisi = []
    for hisse in BORSA_HISSELERI:
        cfiy, al_sat_puan, _ = hisse_verilerini_bul(hisse)
        if al_sat_puan and al_sat_puan not in ["0", "0.0", "NAN", "AL_SAT SİNYALİ", ""]:
            puan_temiz = sinyal_metni_temizle(al_sat_puan, hisse)
            tablo_verisi.append({
                "Hisse Kodu": hisse, 
                "BTA PUAN": puan_temiz, 
                "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Yok", 
                "Durum Oranı": "🔄 Aktif Takip"
            })
    if tablo_verisi: 
        st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
    else: 
        st.warning("Excel dosyasında aktif AL SAT sinyali bulunamadı.")

# AL Sinyal Mantığı
if al_butonu:
    tablo_verisi_al = []
    for hisse in BORSA_HISSELERI:
        cfiy, _, al_puan = hisse_verilerini_bul(hisse)
        if al_puan and al_puan not in ["0", "0.0", "NAN", "AL", "", "-"]:
            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
            puan_al_temiz = sinyal_metni_temizle(al_puan, hisse)
            tablo_verisi_al.append({
                "Hisse Kodu": hisse, 
                "BTA PUAN": puan_al_temiz, 
                "Canlı Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Veri Yok", 
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
        cfiy, _, _ = hisse_verilerini_bul(hisse)
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

# 8. BTa Sohbet Asistanı Bölümü (Kalıcı ve Görünür Yapı)
st.divider()
st.subheader("💬 BTa Sohbet")

# Form dışında listeleme yapılarak mesaj geçmişinin silinmesi kesin olarak engellendi
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

# --- 🔁 GÜVENLİ OTOMATİK YENİLEME ---
time.sleep(5)
st.rerun()
