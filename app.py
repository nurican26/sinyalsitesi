import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# Sayfa Yapılandırması (Ultra Hafif)
st.set_page_config(page_title="BTA", layout="wide")

# Tepede sadece el yazısı stilinde temiz BTA başlığı
st.markdown('<h1 style="font-family: \'Brush Script MT\', cursive, sans-serif; font-size: 50px; color: #00ffcc; text-align: center; margin-bottom: 5px;">BTA</h1>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

# --- KASMAYAN VE KİLİTLENMEYEN SOHBET BELLEĞİ ---
if "bta_sohbet_hafiza_sistemi" not in st.session_state:
    st.session_state["bta_sohbet_hafiza_sistemi"] = [
        {"isim": "Ahmet Y.", "saat": "12:15", "yorum": "Sistem donma zırhı sayesinde artık roket gibi hızlandı, elinize sağlık."},
        {"isim": "BTA Sistem", "saat": "10:00", "yorum": "BTA Canlı Sohbet Alanına Hoş Geldiniz!"}
    ]

# Giriş sayaçları bellek ayarı
if "toplam_sayac" not in st.session_state: st.session_state["toplam_sayac"] = 1450
if "gunluk_sayac" not in st.session_state: st.session_state["gunluk_sayac"] = 120
st.session_state["toplam_sayac"] += 1
st.session_state["gunluk_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# DONMAYI ENGELLEYEN AKILLI FİNANSAL VERİ ÖNBELLEĞİ (15 Dk Gecikmeli)
# ===================================================================== #
@st.cache_data(ttl=900) # Verileri 15 dakika hafızada tutar, sitenin donmasını KESİN önler!
def finansal_verileri_getir(hisse_listesi_input):
    veriler = {}
    try:
        bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=1.5)['Close'].iloc[-1])
        ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=1.5)['Close'].iloc[-1])
        usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=1.5)['Close'].iloc[-1])
        veriler["bist"] = bist_f
        veriler["gram"] = (ons_f / 31.1034768) * usd_f
    except:
        veriler["bist"] = 0.0
        veriler["gram"] = 0.0
        
    # Tablodaki hisselerin fiyatlarını toplu çeker
    for h in hisse_listesi_input:
        try:
            h_veri = yf.Ticker(f"{h}.IS").history(period="1d", timeout=1.5)
            veriler[h] = float(h_veri['Close'].iloc[-1]) if not h_veri.empty else 0.0
        except:
            veriler[h] = 0.0
    return veriler

# ===================================================================== #
# Excel Dosyası Kontrolü ve Hisse Listesi Çıkarma
# ===================================================================== #
hisse_kodlari = []
if os.path.exists(excel_yolu):
    try:
        df_excel = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        for idx in range(min(10, len(df_excel))):
            ha = str(df_excel.iloc[idx, 0]).strip().upper() if pd.notna(df_excel.iloc[idx, 0]) else ""
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                hisse_kodlari.append(ha)
    except:
        pass

# Önbellekten zırhlı veri çekimi tetikleniyor
canli_piyasa = finansal_verileri_getir(hisse_kodlari)

# ===================================================================== #
# PİYASA METRİK KARTLARI GÖSTERİMİ
# ===================================================================== #
if canli_piyasa.get("gram", 0.0) > 0:
    pk1, pk2, pk3, pk4 = st.columns(4)
    pk1.metric("GRAM ALTIN", f"{canli_piyasa['gram']:,.1f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{canli_piyasa['gram'] * 1.63:,.1f} TL")
    pk3.metric("TAM ALTIN", f"{canli_piyasa['gram'] * 6.52:,.1f} TL")
    pk4.metric("BIST 100", f"{canli_piyasa['bist']:,.1f}")
else:
    st.info("⏳ Finansal Veri Bandı Yenileniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE ALGORİTMİK TABLO
# ===================================================================== #
st.write("")
if os.path.exists(excel_yolu):
    try:
        tablo_html = '<table style="width:100%; border-collapse:collapse; margin:10px 0;"><tr><th style="text-align:left; padding:8px;">PUAN</th><th style="text-align:left; padding:8px;">HİSSE 🔗</th><th style="text-align:left; padding:8px;">ALIM</th><th style="text-align:left; padding:8px;">FİYAT</th><th style="text-align:left; padding:8px;">K/Z</th></tr>'
        veri_var_mi = False
        
        for idx in range(min(10, len(df_excel))):
            try:
                ha = str(df_excel.iloc[idx, 0]).strip().upper() if pd.notna(df_excel.iloc[idx, 0]) else ""
                alim_c = str(df_excel.iloc[idx, 2]).strip() if pd.notna(df_excel.iloc[idx, 2]) else ""
                puan_d = df_excel.iloc[idx, 3]
                
                if ha in hisse_kodlari:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    c_fiyat = canli_piyasa.get(ha, 0.0)
                    try: maliyet = float(alim_c.replace(",", "."))
                    except: maliyet = 0.0
                    
                    if maliyet > 0 and c_fiyat > 0:
                        or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                        kz_str = f'▲ %{or_dg:.1f}' if or_dg >= 0 else f'▼ %{or_dg:.1f}'
                    else: kz_str = "-"
                    
                    link_url = f"https://doviz.com{ha.lower()}"
                    hisse_kopru = f'<a href="{link_url}" target="_blank" style="color:#1e90ff; font-weight:bold;">🔍 {ha}</a>'
                    
                    tablo_html += f'<tr style="border-bottom:1px solid #444;"><td style="padding:8px;">{p_temiz}</td><td style="padding:8px;">{hisse_kopru}</td><td style="padding:8px;">{maliyet:,.1f} TL</td><td style="padding:8px;">{c_fiyat:,.1f} TL</td><td style="padding:8px;">{kz_str}</td></tr>'
            except: continue
            
        tablo_html += '</table>'
        st.subheader("📈 BTA ALGORİTMİK HİSSE")
        if veri_var_mi: st.markdown(tablo_html, unsafe_allow_html=True)
    except: st.error("Veri yüklenemedi.")
else: st.error("Excel bulunamadı.")

# ===================================================================== #
# 4. GÜNCEL GELİŞMELER & SÜPER PANEL
# ===================================================================== #
st.write("---")
st.subheader("🔔 GÜNCEL GELİŞMELER & SÜPER PANEL")

col_sol, col_sag = st.columns(2)
with col_sol:
    st.write("**🚀 Yeni Halka Arz Listesi**")
    st.dataframe(pd.DataFrame({"Hisse Kodu": ["XYZEN", "ABCDE"], "Şirket": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum": ["Talep Başladı", "SPK Bekliyor"]}), use_container_width=True, hide_index=True)

with col_sag:
    st.write("**📺 TV GÜNDEM & DÜNYA HABERLERİ**")
    st.write("[SON DAKİKA] Küresel piyasalarda altın ve döviz hareketliliği yakından takip ediliyor.")
    st.write("[Gündem] İç piyasada borsa endeksleri haftaya dengeli bir seyirle başladı.")
    st.write("[Dünya] Ekonomi yönetiminden makro ekonomik verilere dair yeni açıklamalar geldi.")

# ===================================================================== #
# 5. ASLA DONMAYAN VE ANINDA GÜNCELLEŞEN CANLI SOHBET SİSTEMİ
# ===================================================================== #
st.write("---")
st.subheader("💬 KULLANICI YORUMLARI VE CANLI SOHBET")

# Kilitlenmeleri bitiren form yapısı
with st.form(key="bta_donmaz_sohbet_formu", clear_on_submit=True):
    y_is = st.text_input("Adınız / Rumuzunuz:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=80)
    bta_yayinla = st.form_submit_button("Mesajı Yayınla 📨", use_container_width=True)
    
    if bta_yayinla:
        if y_is.strip() and y_me.strip():
            m_kucuk = y_me.lower().replace(" ", "")
            if not any(z in m_kucuk for z in ["orospu", "amk", "oç", "oc", "siktir", "piç", "salak"]):
                y_satir = {"isim": y_is.strip(), "saat": datetime.datetime.now().strftime("%H:%M"), "yorum": y_me.strip()}
                st.session_state["bta_sohbet_hafiza_sistemi"].insert(0, y_satir)
                st.rerun()
            else:
                st.error("⚠ Argo/Küfür içerikli kelimeler engellendi!")
        else:
            st.error("❌ Lütfen adınızı ve mesajınızı doldurun.")

# YÖNETİCİ MODERASYON PANELİ (BTA123 AKTİF)
with st.expander("🛠 Yönetici Girişi"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"
    if adm_mod: st.success("🔓 Silme yetkisi aktif!")

# SOHBET AKIŞINI GÖRÜNTÜLEME
for s, sh in enumerate(st.session_state["bta_sohbet_hafiza_sistemi"]):
    st.write(f"👤 **{sh['isim']}** ({sh['saat']}): {sh['yorum']}")
    if adm_mod:
        if st.button(f"Sil ❌ (Sıra: {s+1})", key=f"sl_{s}"):
            st.session_state["bta_sohbet_hafiza_sistemi"].pop(s)
            st.rerun()

# ===================================================================== #
# YASAL UYARI VE EN ALTA SABİTLENEN SAYAÇLAR
# ===================================================================== #
st.write("---")
st.caption("⚠ SPK YASAL UYARI: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz. Panel üzerindeki borsa verileri kurallar gereği en az 15 dakika gecikmelidir.")
st.caption(f"📊 Bugün Giriş: {st.session_state['gunluk_sayac']} | 💎 Genel Toplam Giriş: {st.session_state['toplam_sayac']}")
