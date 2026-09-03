import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

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

# Puanlama Metrikleri
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
c1, c2 = st.columns(2)
c1.metric("🔥 Toplam Panel Beğenisi (Oy)", f"{st.session_state['topham_oy_sayisi']} Kişi")
c2.metric("⭐ Topluluk Puan Ortalaması", f"{puan:.2f} / 5.0")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Son Panel Yenilenme Zamanı: {guncel_an}")
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

# 4. Canlı Takip Bölümü
st.subheader("🎯 Canlı Takip")

# 🔄 Özel Fiyat Güncelleme Butonu
if st.button("🔄 ANLIK FİYATLARI GÜNCELLE", use_container_width=True):
    st.rerun()

st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
canli_borsa_listesi = []

for hisse in BORSA_HISSELERI:
    try:
        h_data = yf.Ticker(f"{hisse}.IS").history(period="2d")
        if len(h_data) >= 2 and not pd.isna(h_data['Close'].iloc[-1]):
            gf = h_data['Close'].iloc[-1]
            ok = h_data['Close'].iloc[-2]
            fark = ((gf - ok) / ok) * 100
            canli_borsa_listesi.append({
                "Hisse Kodu": hisse, 
                "Anlık Fiyat": f"{gf:.2f} TL", 
                "Günlük Değişim": f"🟢 %+{fark:.2f}" if fark >= 0 else f"🔴 %{fark:.2f}"
            })
        else:
            ef = 0.0
            if df_kaynak is not None:
                for idx in range(len(df_kaynak)):
                    val_hisse = str(df_kaynak.iloc[idx, 0]).replace(" ", "").strip().upper()
                    if hisse in val_hisse:
                        raw_fiyat = str(df_kaynak.iloc[idx, 7]).replace(",", ".").strip()
                        sayi = re.findall(r"[-+]?\d*\.\d+|\d+", raw_fiyat)
                        ef = float(sayi[0]) if sayi else 0.0
                        break
            if ef > 0: 
                canli_borsa_listesi.append({"Hisse Kodu": hisse, "Anlık Fiyat": f"{ef:.2f} TL", "Günlük Değişim": "🔄 Sabit"})
    except: 
        pass

if canli_borsa_listesi: 
    st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)

# 5. Sinyal Üretim Merkezi
st.divider()
st.subheader("📈 BTa Sinyal Üretim Merkezi")
b1, b2 = st.columns(2)
al_sat_butonu = b1.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
al_butonu = b2.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)

# Geliştirilmiş AL SAT Sinyal Mantığı (Sarı Sütun - U Sütunu - İndeks 20)
if al_sat_butonu:
    if df_kaynak is not None:
        tablo_verisi = []
        for i in range(len(df_kaynak)):
            try:
                # Satırdaki hisse kodunu temizle
                satir_hisse = str(df_kaynak.iloc[i, 0]).replace(" ", "").strip().upper()
                if satir_hisse in BORSA_HISSELERI:
                    if len(df_kaynak.columns) > 20 and not pd.isna(df_kaynak.iloc[i, 20]):
                        uv = str(df_kaynak.iloc[i, 20]).replace(" ", "").strip().upper()
                        
                        # Hücre geçersiz metinler veya formül hataları içeriyorsa atla
                        if uv in ["", "0", "0.0", "NAN", "AL_SATSİNYALİ"] or "#" in uv: 
                            continue
                        
                        raw_fiyat = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip()
                        sayi = re.findall(r"[-+]?\d*\.\d+|\d+", raw_fiyat)
                        yfiy = float(sayi[0]) if sayi else 0.0
                        
                        h_obj = yf.Ticker(f"{satir_hisse}.IS").history(period="1d")
                        cfiy = h_obj['Close'].iloc[-1] if not h_obj.empty else yfiy
                        if pd.isna(cfiy) or cfiy == 0.0: cfiy = yfiy
                        
                        zfark = ((cfiy - yfiy) / yfiy) * 100 if yfiy > 0 else 0.0
                        tablo_verisi.append({
                            "Hisse Kodu": satir_hisse, 
                            "Sinyal Metni": str(df_kaynak.iloc[i, 20]).strip(), 
                            "Maliyet Fiyatı": f"{yfiy:.2f} TL", 
                            "Canlı Fiyat": f"{cfiy:.2f} TL", 
                            "Durum Oranı": f"🟢 %{zfark:.2f} Kazandı" if cfiy >= yfiy else f"🔴 %{abs(zfark):.2f} İçeride"
                        })
            except:
                pass
        if tablo_verisi: 
            st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
        else: 
            st.warning("Excel dosyasında aktif AL SAT sinyali bulunamadı.")
    else:
        st.error("Sistemde 'nurican.xls.xlsm' dosyası bulunamadı.")

# Geliştirilmiş AL Sinyal Mantığı (Yeşil Sütun - W Sütunu - İndeks 22)
if al_butonu:
    if df_kaynak is not None:
        tablo_verisi_al = []
        for i in range(len(df_kaynak)):
            try:
                satir_hisse = str(df_kaynak.iloc[i, 0]).replace(" ", "").strip().upper()
                if satir_hisse in BORSA_HISSELERI:
                    if len(df_kaynak.columns) > 22 and not pd.isna(df_kaynak.iloc[i, 22]):
                        wv = str(df_kaynak.iloc[i, 22]).replace(" ", "").strip().upper()
                        
                        # Geçersiz verileri ve formül hatalarını süz
                        if wv in ["", "0", "0.0", "NAN", "AL"] or "-" in wv or "#" in wv: 
                            continue
                        
                        raw_fiyat = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip()
                        sayi = re.findall(r"[-+]?\d*\.\d+|\d+", raw_fiyat)
                        efiy = float(sayi[0]) if sayi else 0.0
                        
                        h_obj = yf.Ticker(f"{satir_hisse}.IS").history(period="1d")
                        cfiy = h_obj['Close'].iloc[-1] if not h_obj.empty else efiy
                        if pd.isna(cfiy) or cfiy == 0.0: cfiy = efiy
                        
                        st.session_state["ozel_takip_kutusu"][satir_hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                        tablo_verisi_al.append({
                            "Hisse Kodu": satir_hisse, 
                            "Sinyal": str(df_kaynak.iloc[i, 22]).strip(), 
                            "Maliyet Fiyatı": f"{efiy:.2f} TL", 
                            "Canlı Fiyat": f"{cfiy:.2f} TL", 
                            "Durum Oranı": "🔄 Havuza Eklendi"
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
        try:
            h_obj = yf.Ticker(f"{hisse}.IS").history(period="1d")
            cf = h_obj['Close'].iloc[-1] if not h_obj.empty else bilge["kayit_fiyati"]
            if pd.isna(cf) or cf == 0.0: cf = bilge["kayit_fiyati"]
            deg = ((cf - bilge["kayit_fiyati"]) / bilge["kayit_fiyati"]) * 100 if bilge["kayit_fiyati"] > 0 else 0.0
            tk_list.append({
                "Hisse Kodu": hisse, 
                "Giriş Fiyatı": f"{bilge['kayit_fiyati']:.2f} TL", 
                "Anlık Fiyat": f"{cf:.2f} TL", 
                "Performans": f"🟢 %{deg:.2f}" if deg >= 0 else f"🔴 %{deg:.2f}", 
                "Kayıt Zamanı": bilge["kayit_zamani"]
            })
        except: 
            pass
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Takip Listesini Temizle", use_container_width=True): 
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()
else: 
    st.info("Henüz takibe alınan dinamik bir hisse bulunmuyor.")

# 7. Topluluk Sohbet Odası
st.divider()
st.subheader("💬 Topluluk Sohbet Odası")
with st.form("mesaj_formu", clear_on_submit=True):
    mesaj = st.text_input("Mesajınızı yazın:", placeholder="Buraya yazın...")
