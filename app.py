import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="BTA Merkez", layout="wide")

# Başlık
st.title("✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨")

excel_yolu = "nurican.xls.xlsm"
db_sohbet = "bta_sohbet_kalici.csv"

# KALICI SOHBET VERİTABANI BAŞLATMA (KASMA YAPMAZ HAFİF SÜRÜM)
if not os.path.exists(db_sohbet):
    pd.DataFrame(columns=["isim", "saat", "yorum"]).to_csv(db_sohbet, index=False)

# --- HAFİF SAYAÇ MİMARİSİ ---
if "toplam_sayac" not in st.session_state: st.session_state["toplam_sayac"] = 1450
if "gunluk_sayac" not in st.session_state: st.session_state["gunluk_sayac"] = 120
st.session_state["toplam_sayac"] += 1
st.session_state["gunluk_sayac"] += 1

def formatla_tl(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except: return str(deger)

# ===================================================================== #
# 2. CANLI ALTIN VE BIST 100 PİYASA ALANI
# ===================================================================== #
try:
    bist_f = float(yf.Ticker("XU100.IS").history(period="1d", timeout=2)['Close'].iloc[-1])
    ons_f = float(yf.Ticker("GC=F").history(period="1d", timeout=2)['Close'].iloc[-1])
    usd_f = float(yf.Ticker("TRY=X").history(period="1d", timeout=2)['Close'].iloc[-1])
    gram_f = (ons_f / 31.1034768) * usd_f
    
    pk1, pk2, pk3, pk4 = st.columns(4)
    pk1.metric("GRAM ALTIN", f"{gram_f:,.1f} TL")
    pk2.metric("ÇEYREK ALTIN", f"{gram_f * 1.63:,.1f} TL")
    pk3.metric("TAM ALTIN", f"{gram_f * 6.52:,.1f} TL")
    pk4.metric("BIST 100", f"{bist_f:,.1f}")
except:
    st.info("⏳ Finansal Veriler Güncelleniyor...")

# ===================================================================== #
# 3. VERİ MOTORU VE TABLOLAR
# ===================================================================== #
st.write("")
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table style="width:100%; border-collapse:collapse; margin:10px 0;"><tr><th style="text-align:left; padding:8px;">PUAN</th><th style="text-align:left; padding:8px;">HİSSE 🔗</th><th style="text-align:left; padding:8px;">ALIM</th><th style="text-align:left; padding:8px;">FİYAT</th><th style="text-align:left; padding:8px;">K/Z</th></tr>'
        veri_var_mi = False
        
        for idx in range(min(10, len(df))):
            try:
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
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
# 4. GÜNCEL GELİŞMELER
# ===================================================================== #
st.write("---")
st.subheader("🔔 GÜNCEL GELİŞMELER & SÜPER PANEL")

col_sol, col_sag = st.columns(2)

with col_sol:
    st.write("**🚀 Yeni Halka Arz Listesi**")
    st.dataframe(pd.DataFrame({"Hisse Kodu": ["XYZEN", "ABCDE"], "Şirket": ["XYZ Enerji A.Ş.", "ABC Gıda Sanayi"], "Durum": ["Talep Başladı", "SPK Bekliyor"]}), use_container_width=True, hide_index=True)

with col_sag:
    st.write("**📺 TV GÜNDEM & DÜNYA HABERLERİ**")
    st.write("🔴 [SON DAKİKA] Küresel piyasalarda altın ve döviz hareketliliği yakından takip ediliyor.")
    st.write("🔴 [Gündem] İç piyasada borsa endeksleri haftaya dengeli bir seyirle başladı.")
    st.write("🔴 [Dünya] Ekonomi yönetiminden makro ekonomik verilere dair yeni açıklamalar geldi.")

# ===================================================================== #
# 5. KALICI CANLI SOHBET KUTUSU VE YÖNETİCİ GİRİŞİ (GERİ GELDİ)
# ===================================================================== #
st.write("---")
st.subheader("💬 KULLANICI YORUMLARI VE CANLI SOHBET")

with st.form(key="s_frm", clear_on_submit=True):
    y_is = st.text_input("Adınız:", max_chars=25)
    y_me = st.text_area("Mesajınız:", max_chars=300, height=80)
    if st.form_submit_button("Mesajı Yayınla 📨", use_container_width=True) and y_is.strip() and y_me.strip():
        m_kucuk = y_me.lower().replace(" ", "")
        if not any(z in m_kucuk for z in ["orospu", "amk", "oç", "oc", "siktir", "piç", "salak"]):
            # Kalıcı CSV Veritabanına Yazma
            df_s = pd.read_csv(db_sohbet)
            y_satir = pd.DataFrame([{"isim": y_is.strip(), "saat": datetime.datetime.now().strftime("%H:%M"), "yorum": y_me.strip()}])
            pd.concat([y_satir, df_s], ignore_index=True).to_csv(db_sohbet, index=False)
            st.rerun()
        else:
            st.error("⚠ Argo/Küfür içerikli kelimeler engellendi!")

# YÖNETİCİ KONTROL ALANI (GERİ GELDİ)
with st.expander("🛠 Yönetici Girişi"):
    adm_mod = st.text_input("Şifre:", type="password", key="adm") == "bta123"
    if adm_mod:
        st.success("🔓 Silme yetkisi aktif!")

# MESAJLARI KALICI METİNDEN OKUYUP BASMA
df_sohbet_oku = pd.read_csv(db_sohbet)
for s in range(len(df_sohbet_oku)):
    sh = df_sohbet_oku.iloc[s]
    st.write(f"👤 **{sh['isim']}** ({sh['saat']}): {sh['yorum']}")
    if adm_mod:
        if st.button(f"Sil ❌ (Sıra: {s+1})", key=f"sl_{s}"):
            df_sl = pd.read_csv(db_sohbet)
            df_sl.drop(s).reset_index(drop=True).to_csv(db_sohbet, index=False)
            st.rerun()

# ===================================================================== #
# YASAL UYARI VE EN ALTA YERLEŞEN GİRİŞ SAYAÇLARI
# ===================================================================== #
st.write("---")
st.caption("⚠ SPK YASAL UYARI: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz. Panel üzerindeki borsa verileri kurallar gereği en az 15 dakika gecikmelidir.")
st.caption(f"📊 Bugün Giriş: {st.session_state['gunluk_sayac']} | 💎 Genel Toplam Giriş: {st.session_state['toplam_sayac']}")
