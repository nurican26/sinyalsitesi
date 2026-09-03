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
    input, textarea {color: #000!important; background-color: #fff!important;}
    
    .stDataFrame {width: 100% !important; border: 1px solid #4338ca !important; border-radius: 8px;}
    div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;}
    
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
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
    .mesaj-kutusu {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #6366f1;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 💾 ORTAK VERİ TABANI AYARLARI (Dosya Tabanlı Mesajlaşma)
MESAJ_DOSYASI = "ortak_mesajlar.csv"

def mesajlari_yukle():
    if os.path.exists(MESAJ_DOSYASI):
        try:
            return pd.read_csv(MESAJ_DOSYASI).to_dict(orient="records")
        except:
            return []
    return []

def mesaj_kaydet(isim, mesaj, saat):
    yeni_data = pd.DataFrame([{"isim": isim, "mesaj": mesaj, "saat": saat}])
    if os.path.exists(MESAJ_DOSYASI):
        yeni_data.to_csv(MESAJ_DOSYASI, mode='a', header=False, index=False)
    else:
        yeni_data.to_csv(MESAJ_DOSYASI, mode='w', header=True, index=False)

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "ziyaret_sayaci" not in st.session_state: st.session_state["ziyaret_sayaci"] = 1
else:
    if "sayac_arttirildi" not in st.session_state:
        st.session_state["ziyaret_sayaci"] += 1
        st.session_state["sayac_arttirildi"] = True

for k in ["kisitli_liste", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0

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

# 📌 OPTİMİZE EDİLMİŞ HIZLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300:
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
                uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
                t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])
                
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

# 💬 GERÇEK ZAMANLI VE ORTAK MESAJ KUTUSU
st.write("---")
st.subheader("💬 Topluluk Mesaj Panosu (Ortak Havuzlu)")

with st.form(key="mesaj_formu", clear_on_submit=True):
    kullanici_adi = st.text_input("İsminiz / Rumuzunuz", value="Anonim")
    yeni_mesaj = st.text_area("Mesajınız veya Analiz Notunuz", placeholder="Buraya yazabilirsiniz...")
    gonder_butonu = st.form_submit_button("Mesajı Yayınla 🚀")
    
    if gonder_butonu and yeni_mesaj.strip():
        zaman_damgasi = datetime.datetime.now().strftime("%d.%m %H:%M")
        # Mesajı kalıcı olarak yerel dosyaya kaydet
        mesaj_kaydet(kullanici_adi, yeni_mesaj.strip(), zaman_damgasi)
        st.toast("Mesajınız ortak panoya kaydedildi! Görmek için sayfayı yenileyin.")
        time.sleep(0.5)
        st.rerun()

# Mesajları yerel dosyadan çekerek listele (Her cihazda görünür olur)
tum_mesajlar = mesajlari_yukle()
if tum_mesajlar:
    # Son atılan mesaj en üstte görünecek şekilde ters çeviriyoruz
    for m in reversed(tum_mesajlar[-15:]): 
        st.markdown(f"""
        <div class="mesaj-kutusu">
            <b>👤 {m['isim']}</b> <span style='color:#818cf8; font-size:0.8rem;'>({m['saat']})</span><br>
            <p style='margin-top:5px; color:#e2e8f0!important;'>{m['mesaj']}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Henüz mesaj yazılmamış. İlk ortak notu siz bırakın!")

# 7. ⭐ PANELİ DEĞERLENDİR
st.write("---")
st.subheader("⭐ Paneli Değerlendir")
yildiz_secimi = st.feedback("stars", key="panel_puanlama") 
if yildiz_secimi is not None:
    puan_anahtari = f"puanlandi_{yildiz_secimi}"
    if puan_anahtari not in st.session_state:
        verilen_puan = yildiz_secimi + 1
        st.session_state["topham_oy_sayisi"] += 1
        st.session_state["topham_yildiz_puani"] += verilen_puan
        st.session_state[puan_anahtari] = True
