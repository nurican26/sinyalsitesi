import os
import hashlib
from datetime import datetime
import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# ==================================================
# SAYFA AYARLARI
# ==================================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# DOSYA VE VERİTABANI AYARLARI
# ==================================================
KAYIT_DOSYASI = "bta_tarihli_kayit_defteri.csv"
ISTATISTIK_DOSYASI = "bta_oda_istatistik.csv"
MESAJ_DOSYASI = "bta_canli_mesajlar.csv"

KAYIT_SUTUNLARI = ["kayit_id", "kayit_tarihi", "hisse_kodu", "bta_alim_fiyati", "bta_puani"]
ISTATISTIK_SUTUNLARI = ["takip_sayisi", "begeni_sayisi"]
MESAJ_SUTUNLARI = ["mesaj_id", "tarih", "kullanici", "mesaj"]

def dosya_olustur(dosya, sutunlar):
    if not os.path.exists(dosya):
        pd.DataFrame(columns=sutunlar).to_csv(dosya, index=False, encoding="utf-8-sig")

dosya_olustur(KAYIT_DOSYASI, KAYIT_SUTUNLARI)
dosya_olustur(ISTATISTIK_DOSYASI, ISTATISTIK_SUTUNLARI)
dosya_olustur(MESAJ_DOSYASI, MESAJ_SUTUNLARI)

# ==================================================
# İNTERNETTEN CANLI BİST TAVAN / YÜKSELEN VERİSİ ÇEKME
# ==================================================
@st.cache_data(ttl=10)
def canli_bist_verisi_internet_cek():
    """Bigpara canlı borsa servisinden TÜM hisseleri internetten anlık çeker."""
    url = "https://bigpara.hurriyet.com.tr/borsa/canli-borsa/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            rows = soup.find_all("tr")
            veriler = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    hisse_raw = cols[0].text.strip()
                    fiyat_raw = cols[1].text.strip()
                    degisim_raw = cols[2].text.strip()

                    # Temizlik işlemi
                    if hisse_raw and "%" in degisim_raw:
                        hisse = hisse_raw.split()[0].upper()
                        fiyat_str = fiyat_raw.replace(".", "").replace(",", ".")
                        degisim_str = degisim_raw.replace("%", "").replace(".", "").replace(",", ".")
                        
                        try:
                            fiyat = float(fiyat_str)
                            degisim = float(degisim_str)
                            veriler.append({
                                "Hisse": hisse,
                                "Son Fiyat (TL)": fiyat,
                                "Değişim (%)": degisim
                            })
                        except ValueError:
                            continue

            if veriler:
                df = pd.DataFrame(veriler)
                return df.drop_duplicates(subset=["Hisse"])
    except Exception:
        pass

    # YEDEK İNTERNET KAYNAĞI (Mynet Finans)
    try:
        url_backup = "https://finans.mynet.com/borsa/hisseler/"
        response_b = requests.get(url_backup, headers=headers, timeout=6)
        if response_b.status_code == 200:
            tables = pd.read_html(response_b.text)
            if tables:
                df_b = tables[0].iloc[:, [0, 2, 3]]
                df_b.columns = ["Hisse", "Son Fiyat (TL)", "Değişim (%)"]
                df_b["Son Fiyat (TL)"] = df_b["Son Fiyat (TL)"].astype(str).str.replace(".", "").str.replace(",", ".").str.extract(r'([\d.]+)').astype(float)
                df_b["Değişim (%)"] = df_b["Değişim (%)"].astype(str).str.replace("%", "").str.replace(",", ".").str.extract(r'([-\d.]+)').astype(float)
                return df_b.dropna().drop_duplicates(subset=["Hisse"])
    except Exception:
        pass

    return pd.DataFrame()

# ==================================================
# FORMATLAMA BİLEŞENLERİ
# ==================================================
def tl_format(deger):
    try:
        return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except Exception:
        return "-"

def sayi_format(deger):
    try:
        return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"

def turkce_sayi_cevir(deger):
    if pd.isna(deger): return None
    if isinstance(deger, (int, float)): return float(deger)
    metin = str(deger).strip().lower().replace("tl", "").replace(" ", "")
    if not metin: return None
    try:
        if "." in metin and "," in metin: metin = metin.replace(".", "").replace(",", ".")
        elif "," in metin:
            son_parca = metin.split(",")[-1]
            metin = metin.replace(",", "") if len(son_parca) == 3 else metin.replace(",", ".")
        elif "." in metin:
            son_parca = metin.split(".")[-1]
            if len(son_parca) == 3: metin = metin.replace(".", "")
        return float(metin)
    except Exception: return None

def kar_yuzdesi_hesapla(bta_fiyat, anlik_fiyat):
    if not bta_fiyat or not anlik_fiyat or bta_fiyat <= 0: return None
    return ((anlik_fiyat - bta_fiyat) / bta_fiyat) * 100

def kar_yuzdesi_format(kar_yuzde):
    if kar_yuzde is None: return "-"
    durum = "📈" if kar_yuzde >= 0 else "📉"
    renk = "#00f5c8" if kar_yuzde >= 0 else "#ff5264"
    return f"""
    <div style="background: rgba(0, 0, 0, 0.3); border-left: 4px solid {renk}; border-radius: 5px; padding: 12px; margin: 10px 0; text-align: center;">
        <div style="font-size: 24px; font-weight: bold; color: {renk};">{durum} {kar_yuzde:+.2f}%</div>
        <div style="font-size: 12px; color: #999;">{'💰 Kar' if kar_yuzde >= 0 else '📊 Zarar'}</div>
    </div>
    """

def bedelli_bedelsiz_hesapla(eski_fiyat, sahip_lot, bedelli_orani, bedelli_fiyat, bedelsiz_orani):
    try:
        eski_fiyat, sahip_lot = float(eski_fiyat), float(sahip_lot)
        bedelli_orani_yuzde, bedelli_fiyat = float(bedelli_orani), float(bedelli_fiyat)
        bedelsiz_orani_yuzde = float(bedelsiz_orani)
    except Exception: return None

    if eski_fiyat <= 0 or sahip_lot < 0 or bedelli_orani_yuzde < 0 or bedelsiz_orani_yuzde < 0: return None
    bedelli_orani, bedelsiz_orani = bedelli_orani_yuzde / 100, bedelsiz_orani_yuzde / 100
    payda = 1 + bedelli_orani + bedelsiz_orani
    if payda <= 0: return None

    bedelli_yeni_lot = sahip_lot * bedelli_orani
    bedelsiz_yeni_lot = sahip_lot * bedelsiz_orani
    toplam_lot_sonrasi = sahip_lot + bedelli_yeni_lot + bedelsiz_yeni_lot
    teorik_fiyat = (eski_fiyat + (bedelli_orani * bedelli_fiyat)) / payda

    return {
        "teorik_fiyat": teorik_fiyat,
        "toplam_lot_sonrasi": toplam_lot_sonrasi
    }

# ==================================================
# CSS VE ARAYÜZ TASARIMI
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07131f !important;
        background-image: linear-gradient(rgba(5, 14, 25, 0.89), rgba(5, 14, 25, 0.97)),
            url("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=2400&q=85") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] > div:first-child { background: rgba(4, 13, 24, 0.98) !important; }
    .main .block-container { max-width: 950px !important; padding-top: 1rem !important; }
    .bta-logo-alani { width: 100%; overflow: hidden; white-space: nowrap; margin-bottom: 12px; }
    .bta-logo {
        display: inline-block; color: #00f5c8; font-family: "Brush Script MT", cursive; font-size: 58px; font-weight: bold;
        text-shadow: 0 0 8px #00f5c8, 0 0 18px #00f5c8, 0 0 28px #168cff; animation: kayan_logo 14s linear infinite;
    }
    @keyframes kayan_logo { 0% { transform: translateX(100vw); } 100% { transform: translateX(-100%); } }
    .mesaj-karti { background: rgba(8, 29, 45, 0.95); border-left: 3px solid #00f5c8; border-radius: 7px; padding: 10px; margin: 7px 0; }
    .spk-uyari { background: rgba(70, 18, 27, 0.96); border: 1px solid #ff5264; border-radius: 8px; padding: 13px; margin-top: 30px; color: white; font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# VERİ OKUMA / YAZMA FONKSİYONLARI
# ==================================================
def kayitlari_oku():
    try:
        df = pd.read_csv(KAYIT_DOSYASI, encoding="utf-8-sig")
        for s in KAYIT_SUTUNLARI:
            if s not in df.columns: df[s] = ""
        return df[KAYIT_SUTUNLARI]
    except Exception: return pd.DataFrame(columns=KAYIT_SUTUNLARI)

def kayit_id_olustur(hisse, fiyat, puan):
    return hashlib.sha256(f"{hisse}|{float(fiyat):.4f}|{float(puan):.4f}".encode("utf-8")).hexdigest()[:20]

def excel_kayitlarini_ekle(df):
    mevcut = kayitlari_oku()
    yeni_kayitlar = []
    for _, satir in df.iterrows():
        hisse = str(satir["Hisse Kodu"]).strip().upper()
        fiyat, puan = satir["BTA Alım Fiyatı"], satir["BTA Puanı"]
        if not hisse or pd.isna(fiyat) or float(fiyat) <= 0: continue
        puan = 0.0 if pd.isna(puan) else puan
        kayit_id = kayit_id_olustur(hisse, fiyat, puan)
        if mevcut["kayit_id"].astype(str).eq(kayit_id).any(): continue
        yeni_kayitlar.append({
            "kayit_id": kayit_id, "kayit_tarihi": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "hisse_kodu": hisse, "bta_alim_fiyati": float(fiyat), "bta_puani": float(puan)
        })
    if yeni_kayitlar:
        pd.concat([mevcut, pd.DataFrame(yeni_kayitlar)], ignore_index=True).to_csv(KAYIT_DOSYASI, index=False, encoding="utf-8-sig")

def istatistik_oku():
    try:
        df = pd.read_csv(ISTATISTIK_DOSYASI, encoding="utf-8-sig")
        if df.empty: return 0, 0
        return int(df.iloc[0].get("takip_sayisi", 0)), int(df.iloc[0].get("begeni_sayisi", 0))
    except Exception: return 0, 0

def istatistik_kaydet(takip, begeni):
    pd.DataFrame([{"takip_sayisi": takip, "begeni_sayisi": begeni}]).to_csv(ISTATISTIK_DOSYASI, index=False, encoding="utf-8-sig")

def mesajlari_oku():
    try:
        df = pd.read_csv(MESAJ_DOSYASI, encoding="utf-8-sig")
        for s in MESAJ_SUTUNLARI:
            if s not in df.columns: df[s] = ""
        return df[MESAJ_SUTUNLARI]
    except Exception: return pd.DataFrame(columns=MESAJ_SUTUNLARI)

def mesaj_ekle(kullanici, metin):
    mesajlar = mesajlari_oku()
    yeni = pd.DataFrame([{
        "mesaj_id": int(datetime.now().timestamp() * 1000),
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "kullanici": kullanici, "mesaj": metin
    }])
    pd.concat([mesajlar, yeni], ignore_index=True).to_csv(MESAJ_DOSYASI, index=False, encoding="utf-8-sig")

# CANLI OTOMATİK YENİLEME (10 SANİYE)
st_autorefresh(interval=10000, key="bta_canli_yenileme")
st.markdown('<div class="bta-logo-alani"><div class="bta-logo">BTA ALGORİTMİK İŞLEM</div></div>', unsafe_allow_html=True)

# YÖNETİCİ PANELİ
st.sidebar.header("⚙️ Sistem Kontrolleri")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi", type="password")
is_admin = admin_sifre == "3015"

if is_admin:
    st.sidebar.success("✅ Yönetici yetkileri aktif")
    with st.sidebar.expander("🔧 Yönetici Paneli"):
        takip, begeni = istatistik_oku()
        yt = st.number_input("Takipçi", value=takip, min_value=0)
        yb = st.number_input("Beğeni", value=begeni, min_value=0)
        if st.button("Kaydet", use_container_width=True):
            istatistik_kaydet(yt, yb)
            st.success("Güncellendi")

# EXCEL OKUMA
excel_dosyalari = [d for d in os.listdir(".") if d.lower().endswith((".xlsx", ".xlsm"))]
excel_df = pd.DataFrame(columns=["Hisse Kodu", "BTA Alım Fiyatı", "BTA Puanı"])

if excel_dosyalari:
    try:
        ham_df = pd.read_excel(excel_dosyalari[0], sheet_name=0, engine="openpyxl", header=None)
        if ham_df.shape[1] >= 4:
            excel_df = ham_df.iloc[:, [0, 2, 3]].copy()
            excel_df.columns = ["Hisse Kodu", "BTA Alım Fiyatı", "BTA Puanı"]
            excel_df["Hisse Kodu"] = excel_df["Hisse Kodu"].astype(str).str.strip().str.upper()
            excel_df["BTA Alım Fiyatı"] = excel_df["BTA Alım Fiyatı"].apply(turkce_sayi_cevir)
            excel_df["BTA Puanı"] = excel_df["BTA Puanı"].apply(turkce_sayi_cevir)
            excel_df = excel_df[excel_df["BTA Alım Fiyatı"] > 0].drop_duplicates(subset=["Hisse Kodu"], keep="last")
            excel_kayitlarini_ekle(excel_df)
    except Exception as e:
        st.error(f"Excel Okuma Hatalı: {e}")

# ==================================================
# PANELLER (TABS)
# ==================================================
tab_algoritmik, tab_yukselenler, tab_dusenler, tab_bedelli, tab_sohbet, tab_kayit, tab_paylas = st.tabs([
    "🤖 Algoritmik Bilgiler", "🚀 En Çok Yükselenler", "📉 En Çok Düşenler", "🧮 Bedelli/Bedelsiz", "💬 Sohbet", "📒 Kayıtlar", "🔗 Paylaş"
])

# İNTERNETTEN CANLI BİST VERİSİ
df_piyasa = canli_bist_verisi_internet_cek()

# --------------------------------------------------
# TAB 1: ALGORİTMİK BİLGİLER
# --------------------------------------------------
with tab_algoritmik:
    st.header("🤖 Algoritmik İşlem Bilgileri")
    if excel_df.empty:
        st.warning("Excel dosyasından yüklenmiş geçerli hisse bulunamadı.")
    else:
        secilen_hisse = st.selectbox("🔍 BTA Algoritma Hissesi Seç:", excel_df["Hisse Kodu"].tolist())
        
        fiyat = 0.0
        if not df_piyasa.empty:
            match = df_piyasa[df_piyasa["Hisse"] == secilen_hisse]
            if not match.empty:
                fiyat = match.iloc[0]["Son Fiyat (TL)"]

        kayit = excel_df[excel_df["Hisse Kodu"] == secilen_hisse].iloc[0]
        bta_alim_fiyati = kayit["BTA Alım Fiyatı"]
        kar_yuzde = kar_yuzdesi_hesapla(bta_alim_fiyati, fiyat)

        col1, col2, col3 = st.columns(3)
        col1.metric("BTA Alım Fiyatı", tl_format(bta_alim_fiyati))
        col2.metric("BTA Puanı", sayi_format(kayit["BTA Puanı"]))
        col3.metric("Anlık Fiyat", tl_format(fiyat) if fiyat > 0 else "Veri bağlanıyor...")

        st.markdown(kar_yuzdesi_format(kar_yuzde), unsafe_allow_html=True)

# --------------------------------------------------
# TAB 2: EN ÇOK YÜKSELENLER VE TAVANLAR
# --------------------------------------------------
with tab_yukselenler:
    st.header("🚀 BİST En Çok Yükselen Hisseler (İnternet Canlı)")
    if not df_piyasa.empty:
        df_yukselen = df_piyasa.sort_values(by="Değişim (%)", ascending=False).head(15).reset_index(drop=True)
        
        st.dataframe(
            df_yukselen,
            column_config={
                "Hisse": st.column_config.TextColumn("Hisse Kodu", width="small"),
                "Son Fiyat (TL)": st.column_config.NumberColumn("Son Fiyat (TL)", format="%.2f TL", width="medium"),
                "Değişim (%)": st.column_config.NumberColumn("Değişim (%)", format="%+.2f%%", width="medium")
            },
            hide_index=True,
            height=420,
            use_container_width=True
        )
    else:
        st.info("🌐 İnternet canlı BİST verisi çekiliyor, lütfen bekleyin...")

# --------------------------------------------------
# TAB 3: EN ÇOK DÜŞEN HİSSELER
# --------------------------------------------------
with tab_dusenler:
    st.header("📉 BİST En Çok Düşen Hisseler (İnternet Canlı)")
    if not df_piyasa.empty:
        df_dusen = df_piyasa.sort_values(by="Değişim (%)", ascending=True).head(15).reset_index(drop=True)
        
        st.dataframe(
            df_dusen,
            column_config={
                "Hisse": st.column_config.TextColumn("Hisse Kodu", width="small"),
                "Son Fiyat (TL)": st.column_config.NumberColumn("Son Fiyat (TL)", format="%.2f TL", width="medium"),
                "Değişim (%)": st.column_config.NumberColumn("Değişim (%)", format="%+.2f%%", width="medium")
            },
            hide_index=True,
            height=420,
            use_container_width=True
        )
    else:
        st.info("🌐 İnternet canlı BİST verisi çekiliyor, lütfen bekleyin...")

# --------------------------------------------------
# TAB 4: BEDELLİ / BEDELSİZ HESAPLAMA
# --------------------------------------------------
with tab_bedelli:
    st.header("🧮 Bedelli/Bedelsiz Hesaplama Makinesi")
    hisse_listesi = excel_df["Hisse Kodu"].tolist() if not excel_df.empty else []
    kaynak_secenekleri = ["📈 Listeden Hisse Seç"] if hisse_listesi else ["✍️ Manuel Fiyat Gir"]
    kaynak = st.radio("Fiyat Kaynağı", kaynak_secenekleri + ["✍️ Manuel Fiyat Gir"], horizontal=True)

    varsayilan_fiyat = 0.0
    if kaynak == "📈 Listeden Hisse Seç":
        sh = st.selectbox("🔍 Hisse Seç:", hisse_listesi)
        if not df_piyasa.empty:
            match = df_piyasa[df_piyasa["Hisse"] == sh]
            if not match.empty:
                varsayilan_fiyat = match.iloc[0]["Son Fiyat (TL)"]

    c1, c2 = st.columns(2)
    with c1:
        eski_fiyat = st.number_input("Önceki Kapanış Fiyatı (TL)", min_value=0.0, value=float(varsayilan_fiyat), format="%.4f")
        sahip_lot = st.number_input("Pay Adedi (Lot)", min_value=0.0, value=100.0)
    with c2:
        bedelli_orani = st.number_input("Bedelli Oranı (%)", min_value=0.0, value=0.0)
        bedelli_fiyat = st.number_input("Bedelli Pay Fiyatı (TL)", min_value=0.0, value=1.00, format="%.4f")
        bedelsiz_orani = st.number_input("Bedelsiz Oranı (%)", min_value=0.0, value=0.0)

    if st.button("🧮 Hesapla", use_container_width=True, type="primary"):
        res = bedelli_bedelsiz_hesapla(eski_fiyat, sahip_lot, bedelli_orani, bedelli_fiyat, bedelsiz_orani)
        if res: st.session_state["bedelli_sonuc"] = res
        else: st.error("Girdileri kontrol ediniz.")

    if st.session_state.get("bedelli_sonuc"):
        r = st.session_state["bedelli_sonuc"]
        st.success(f"Teorik Fiyat: {tl_format(r['teorik_fiyat'])} | Toplam Lot: {sayi_format(r['toplam_lot_sonrasi'])}")

# --------------------------------------------------
# TAB 5: CANLI SOHBET
# --------------------------------------------------
with tab_sohbet:
    st.header("💬 Canlı Sohbet Odası")
    takip, begeni = istatistik_oku()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⭐ Takip Et", use_container_width=True): istatistik_kaydet(takip+1, begeni); st.rerun()
    with c2:
        if st.button("👍 Beğen", use_container_width=True): istatistik_kaydet(takip, begeni+1); st.rerun()
    c3.metric("👥 Takipçi", takip)
    c4.metric("👍 Beğeni", begeni)

    st.divider()
    kullanici = st.text_input("Kullanıcı Adı", value="Hissedar")
    with st.form("mesaj_form", clear_on_submit=True):
        mesaj = st.text_area("Mesajınız")
        if st.form_submit_button("Gönder 🚀") and mesaj.strip():
            mesaj_ekle(kullanici, mesaj.strip())
            st.rerun()

    mesajlar = mesajlari_oku()
    for idx, row in mesajlar.iloc[::-1].iterrows():
        st.markdown(f'<div class="mesaj-karti"><strong>👤 {row["kullanici"]}</strong> <small>({row["tarih"]})</small><br>{row["mesaj"]}</div>', unsafe_allow_html=True)

# --------------------------------------------------
# TAB 6: TARİHLİ KAYITLAR
# --------------------------------------------------
with tab_kayit:
    st.header("📒 Tarihli Kayıt Defteri")
    df_kayitlar = kayitlari_oku()
    if not df_kayitlar.empty:
        st.dataframe(df_kayitlar, use_container_width=True)
    else:
        st.info("Kayıt bulunamadı.")

# --------------------------------------------------
# TAB 7: PAYLAŞ
# --------------------------------------------------
with tab_paylas:
    st.header("🔗 Platformu Paylaş")
    st.info("https://btasinyal.streamlit.app bağlantısını kopyalayarak arkadaşlarınızla paylaşabilirsiniz.")

# YASAL UYARI
st.markdown('<div class="spk-uyari"><strong>⚠️ SPK YASAL UYARI:</strong> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Veriler gecikmeli veya farklı kaynaklardan sağlanıyor olabilir.</div>', unsafe_allow_html=True)
