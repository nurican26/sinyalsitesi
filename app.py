import os
import hashlib
from datetime import datetime
import urllib.parse

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
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
# DOSYA AYARLARI
# ==================================================
KAYIT_DOSYASI = "bta_tarihli_kayit_defteri.csv"
ISTATISTIK_DOSYASI = "bta_oda_istatistik.csv"
MESAJ_DOSYASI = "bta_canli_mesajlar.csv"

KAYIT_SUTUNLARI = [
    "kayit_id",
    "kayit_tarihi",
    "hisse_kodu",
    "bta_Algoritmik_fiyati",
    "bta_puani"
]

ISTATISTIK_SUTUNLARI = [
    "takip_sayisi",
    "begeni_sayisi"
]

MESAJ_SUTUNLARI = [
    "mesaj_id",
    "tarih",
    "kullanici",
    "mesaj"
]


def dosya_olustur(dosya, sutunlar):
    if not os.path.exists(dosya):
        pd.DataFrame(
            columns=sutunlar
        ).to_csv(
            dosya,
            index=False,
            encoding="utf-8-sig"
        )


dosya_olustur(KAYIT_DOSYASI, KAYIT_SUTUNLARI)
dosya_olustur(ISTATISTIK_DOSYASI, ISTATISTIK_SUTUNLARI)
dosya_olustur(MESAJ_DOSYASI, MESAJ_SUTUNLARI)


# ==================================================
# FORMATLAMA
# ==================================================
def tl_format(deger):
    try:
        return (
            f"{float(deger):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            + " TL"
        )
    except Exception:
        return "-"


def sayi_format(deger):
    try:
        return (
            f"{float(deger):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
    except Exception:
        return "-"


def turkce_sayi_cevir(deger):
    if pd.isna(deger):
        return None

    if isinstance(deger, (int, float)):
        return float(deger)

    metin = str(deger).strip()
    metin = metin.replace("TL", "")
    metin = metin.replace("tl", "")
    metin = metin.replace(" ", "")

    if not metin:
        return None

    try:
        if "." in metin and "," in metin:
            metin = metin.replace(".", "")
            metin = metin.replace(",", ".")

        elif "," in metin:
            son_parca = metin.split(",")[-1]

            if len(son_parca) == 3:
                metin = metin.replace(",", "")
            else:
                metin = metin.replace(",", ".")

        elif "." in metin:
            son_parca = metin.split(".")[-1]

            if len(son_parca) == 3:
                metin = metin.replace(".", "")

        return float(metin)

    except Exception:
        return None


# ==================================================
# KAR/ZARAR FONKSİYONLARI
# ==================================================
def kar_zarar_hesapla(alim_fiyati, cari_fiyat):
    """Kar/Zarar miktarını hesaplar"""
    if pd.isna(alim_fiyati) or pd.isna(cari_fiyat):
        return None
    try:
        return float(cari_fiyat) - float(alim_fiyati)
    except Exception:
        return None


def kar_zarar_yuzde_hesapla(alim_fiyati, cari_fiyat):
    """Kar/Zarar yüzdesini hesaplar"""
    if pd.isna(alim_fiyati) or pd.isna(cari_fiyat) or float(alim_fiyati) == 0:
        return None
    try:
        return ((float(cari_fiyat) - float(alim_fiyati)) / float(alim_fiyati)) * 100
    except Exception:
        return None


def kar_zarar_rengi(deger):
    """Kar/Zarar değerine göre renk döndürür"""
    if deger is None:
        return "#ffffff"
    if deger > 0:
        return "#00ff00"  # Yeşil (Kar)
    elif deger < 0:
        return "#ff0000"  # Kırmızı (Zarar)
    else:
        return "#ffffff"  # Beyaz (Eşit)


# ==================================================
# TASARIM
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07131f !important;
        background-image:
            linear-gradient(
                rgba(5, 14, 25, 0.89),
                rgba(5, 14, 25, 0.97)
            ),
            url("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=2400&q=85") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: rgba(4, 13, 24, 0.98) !important;
    }

    .main .block-container {
        max-width: 1450px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    h1, h2, h3, h4, p, label, span, div {
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.7);
    }

    .bta-logo-alani {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        margin-bottom: 12px;
    }

    .bta-logo {
        display: inline-block;
        color: #00f5c8;
        font-family: "Brush Script MT", "Segoe Script", cursive;
        font-size: 58px;
        font-weight: bold;
        text-shadow:
            0 0 8px #00f5c8,
            0 0 18px #00f5c8,
            0 0 28px #168cff;
        animation: kayan_logo 14s linear infinite;
    }

    @keyframes kayan_logo {
        0% {
            transform: translateX(100vw);
        }

        100% {
            transform: translateX(-100%);
        }
    }

    .mesaj-karti {
        background: rgba(8, 29, 45, 0.95);
        border-left: 3px solid #00f5c8;
        border-radius: 7px;
        padding: 10px;
        margin: 7px 0;
    }

    .bilgi-karti {
        background: rgba(9, 31, 48, 0.95);
        border: 1px solid rgba(0, 245, 200, 0.35);
        border-radius: 9px;
        padding: 14px;
        margin: 10px 0;
        line-height: 1.8;
    }

    .kar-zarar-karti {
        background: rgba(9, 31, 48, 0.95);
        border: 2px solid;
        border-radius: 9px;
        padding: 16px;
        margin: 15px 0;
        line-height: 2;
    }

    .kar-zarar-karti-positive {
        border-color: #00ff00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }

    .kar-zarar-karti-negative {
        border-color: #ff0000;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
    }

    .kar-zarar-karti-neutral {
        border-color: #00f5c8;
        box-shadow: 0 0 10px rgba(0, 245, 200, 0.3);
    }

    .paylas-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: center;
        margin: 20px 0;
    }

    .paylas-buton {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 14px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        text-align: center;
        min-width: 140px;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .paylas-twitter {
        background-color: #1DA1F2;
        color: white;
    }

    .paylas-twitter:hover {
        background-color: #1a8cd8;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(29, 161, 242, 0.6);
    }

    .paylas-facebook {
        background-color: #1877F2;
        color: white;
    }

    .paylas-facebook:hover {
        background-color: #0a66c2;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(24, 119, 242, 0.6);
    }

    .paylas-linkedin {
        background-color: #0A66C2;
        color: white;
    }

    .paylas-linkedin:hover {
        background-color: #084998;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(10, 102, 194, 0.6);
    }

    .paylas-whatsapp {
        background-color: #25D366;
        color: white;
    }

    .paylas-whatsapp:hover {
        background-color: #1eaa54;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.6);
    }

    .paylas-telegram {
        background-color: #0088cc;
        color: white;
    }

    .paylas-telegram:hover {
        background-color: #006ba3;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 136, 204, 0.6);
    }

    .paylas-email {
        background-color: #EA4335;
        color: white;
    }

    .paylas-email:hover {
        background-color: #c5221f;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(234, 67, 53, 0.6);
    }

    .paylas-kopya {
        background-color: #00f5c8;
        color: #07131f;
        font-weight: bold;
    }

    .paylas-kopya:hover {
        background-color: #00d4a8;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 245, 200, 0.6);
    }

    .spk-uyari {
        background: rgba(70, 18, 27, 0.96);
        border: 1px solid #ff5264;
        border-radius: 8px;
        padding: 13px;
        margin-top: 30px;
        color: white;
        font-size: 12px;
        line-height: 1.6;
        text-align: justify;
    }

    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 0.8rem 0.6rem 1.5rem 0.6rem !important;
        }

        .bta-logo {
            font-size: 38px;
        }

        [data-testid="stTabs"] button {
            font-size: 10px !important;
            padding: 7px 4px !important;
        }

        .spk-uyari {
            font-size: 11px;
            text-align: left;
        }

        .paylas-buton {
            min-width: 120px;
            padding: 12px 16px;
            font-size: 12px;
        }

        .paylas-container {
            gap: 8px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# KAYIT FONKSİYONLARI
# ==================================================
def kayitlari_oku():
    try:
        df = pd.read_csv(
            KAYIT_DOSYASI,
            encoding="utf-8-sig"
        )

        for sutun in KAYIT_SUTUNLARI:
            if sutun not in df.columns:
                df[sutun] = ""

        return df[KAYIT_SUTUNLARI]

    except Exception:
        return pd.DataFrame(columns=KAYIT_SUTUNLARI)


def kayit_id_olustur(hisse, fiyat, puan):
    metin = (
        f"{hisse}|"
        f"{float(fiyat):.4f}|"
        f"{float(puan):.4f}"
    )

    return hashlib.sha256(
        metin.encode("utf-8")
    ).hexdigest()[:20]


def excel_kayitlarini_ekle(df):
    mevcut = kayitlari_oku()
    yeni_kayitlar = []

    for _, satir in df.iterrows():
        hisse = str(
            satir["Hisse Kodu"]
        ).strip().upper()

        fiyat = satir["BTA Alım Fiyatı"]
        puan = satir["BTA Puanı"]

        if hisse in [
            "",
            "NONE",
            "NAN",
            "NULL",
            "NA",
            "HİSSE",
            "HISSE",
            "HİSSE KODU",
            "HISSE KODU"
        ]:
            continue

        if pd.isna(fiyat) or float(fiyat) <= 0:
            continue

        if pd.isna(puan):
            puan = 0.0

        kayit_id = kayit_id_olustur(
            hisse,
            fiyat,
            puan
        )

        if mevcut["kayit_id"].astype(str).eq(kayit_id).any():
            continue

        yeni_kayitlar.append(
            {
                "kayit_id": kayit_id,
                "kayit_tarihi": datetime.now().strftime(
                    "%d.%m.%Y %H:%M:%S"
                ),
                "hisse_kodu": hisse,
                "bta_alim_fiyati": float(fiyat),
                "bta_puani": float(puan)
            }
        )

    if yeni_kayitlar:
        sonuc = pd.concat(
            [
                mevcut,
                pd.DataFrame(yeni_kayitlar)
            ],
            ignore_index=True
        )

        sonuc.to_csv(
            KAYIT_DOSYASI,
            index=False,
            encoding="utf-8-sig"
        )


# ==================================================
# TAKİP VE BEĞENİ FONKSİYONLARI
# ==================================================
def istatistik_oku():
    try:
        df = pd.read_csv(
            ISTATISTIK_DOSYASI,
            encoding="utf-8-sig"
        )

        if df.empty:
            return 0, 0

        satir = df.iloc[0]

        takip = pd.to_numeric(
            satir.get("takip_sayisi", 0),
            errors="coerce"
        )

        begeni = pd.to_numeric(
            satir.get("begeni_sayisi", 0),
            errors="coerce"
        )

        return (
            int(takip) if pd.notna(takip) else 0,
            int(begeni) if pd.notna(begeni) else 0
        )

    except Exception:
        return 0, 0


def istatistik_kaydet(takip, begeni):
    pd.DataFrame(
        [{
            "takip_sayisi": takip,
            "begeni_sayisi": begeni
        }]
    ).to_csv(
        ISTATISTIK_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )


# ==================================================
# MESAJ FONKSİYONLARI
# ==================================================
def mesajlari_oku():
    try:
        df = pd.read_csv(
            MESAJ_DOSYASI,
            encoding="utf-8-sig"
        )

        for sutun in MESAJ_SUTUNLARI:
            if sutun not in df.columns:
                df[sutun] = ""

        return df[MESAJ_SUTUNLARI]

    except Exception:
        return pd.DataFrame(columns=MESAJ_SUTUNLARI)


def mesaj_ekle(kullanici, metin):
    mesajlar = mesajlari_oku()

    yeni_mesaj = pd.DataFrame(
        [{
            "mesaj_id": int(
                datetime.now().timestamp() * 1000
            ),
            "tarih": datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S"
            ),
            "kullanici": kullanici,
            "mesaj": metin
        }]
    )

    mesajlar = pd.concat(
        [
            mesajlar,
            yeni_mesaj
        ],
        ignore_index=True
    )

    mesajlar.to_csv(
        MESAJ_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )


# ==================================================
# PAYLAŞIM FONKSİYONLARI
# ==================================================
def paylas_linki_olustur(platform, url, baslik):
    """
    Farklı platformlar için paylaşım linki oluşturur
    """
    encoded_url = urllib.parse.quote(url)
    encoded_baslik = urllib.parse.quote(baslik)
    
    linkler = {
        "twitter": f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_baslik}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        "whatsapp": f"https://wa.me/?text={encoded_baslik}%0A{encoded_url}",
        "telegram": f"https://t.me/share/url?url={encoded_url}&text={encoded_baslik}",
        "email": f"mailto:?subject={encoded_baslik}&body={encoded_url}"
    }
    
    return linkler.get(platform, "#")


# ==================================================
# MESAJ SESİ
# ==================================================
def mesaj_sesi_cal():
    components.html(
        """
        <script>
        try {
            const audioContext = new (
                window.AudioContext ||
                window.webkitAudioContext
            )();

            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.type = "sine";
            oscillator.frequency.setValueAtTime(
                880,
                audioContext.currentTime
            );

            gainNode.gain.setValueAtTime(
                0.0001,
                audioContext.currentTime
            );

            gainNode.gain.exponentialRampToValueAtTime(
                0.18,
                audioContext.currentTime + 0.02
            );

            gainNode.gain.exponentialRampToValueAtTime(
                0.0001,
                audioContext.currentTime + 0.35
            );

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.35);
        } catch (error) {
            console.log("Bildirim sesi oynatılamadı:", error);
        }
        </script>
        """,
        height=0,
        width=0
    )


# ==================================================
# CANLI YENİLEME
# ==================================================
st_autorefresh(
    interval=5000,
    key="bta_canli_yenileme"
)


# ==================================================
# LOGO
# ==================================================
st.markdown(
    """
    <div class="bta-logo-alani">
        <div class="bta-logo">
            BTA ALGORİTMİK İŞLEM
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# YÖNETİCİ SİSTEMİ
# ==================================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

admin_sifre = st.sidebar.text_input(
    "Yönetici Şifresi",
    type="password",
    help="Yönetici paneline erişmek için şifre girin"
)

is_admin = admin_sifre == "3015"

if is_admin:
    st.sidebar.success("✅ Yönetici yetkileri aktif")
    
    with st.sidebar.expander("🔧 Yönetici Paneli"):
        st.subheader("İstatistikleri Yönet")
        
        takip, begeni = istatistik_oku()
        
        col1, col2 = st.columns(2)
        
        with col1:
            yeni_takip = st.number_input(
                "Takipçi Sayısı",
                value=takip,
                min_value=0
            )
        
        with col2:
            yeni_begeni = st.number_input(
                "Beğeni Sayısı",
                value=begeni,
                min_value=0
            )
        
        if st.button("İstatistikleri Kaydet", use_container_width=True):
            istatistik_kaydet(yeni_takip, yeni_begeni)
            st.success("✅ İstatistikler güncellendi")


# ==================================================
# EXCEL'İ OTOMATİK OKU
# A = Hisse Kodu
# C = BTA Alım Fiyatı
# D = BTA Puanı
# ==================================================
excel_dosyalari = [
    dosya
    for dosya in os.listdir(".")
    if dosya.lower().endswith(
        (".xlsx", ".xlsm")
    )
]

excel_df = pd.DataFrame(
    columns=[
        "Hisse Kodu",
        "BTA Alım Fiyatı",
        "BTA Puanı"
    ]
)

if excel_dosyalari:
    secilen_excel = excel_dosyalari[0]

    try:
        ham_df = pd.read_excel(
            secilen_excel,
            sheet_name=0,
            engine="openpyxl",
            header=None
        )

        if ham_df.shape[1] >= 4:
            excel_df = ham_df.iloc[:, [0, 2, 3]].copy()

            excel_df.columns = [
                "Hisse Kodu",
                "BTA Alım Fiyatı",
                "BTA Puanı"
            ]

            excel_df["Hisse Kodu"] = (
                excel_df["Hisse Kodu"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            excel_df["BTA Alım Fiyatı"] = (
                excel_df["BTA Alım Fiyatı"]
                .apply(turkce_sayi_cevir)
            )

            excel_df["BTA Puanı"] = (
                excel_df["BTA Puanı"]
                .apply(turkce_sayi_cevir)
            )

            excel_df = excel_df[
                ~excel_df["Hisse Kodu"].isin(
                    [
                        "",
                        "NONE",
                        "NAN",
                        "NULL",
                        "NA",
                        "HİSSE",
                        "HISSE",
                        "HİSSE KODU",
                        "HISSE KODU"
                    ]
                )
            ]

            excel_df = excel_df[
                excel_df["BTA Alım Fiyatı"].notna()
            ]

            excel_df = excel_df[
                excel_df["BTA Alım Fiyatı"] > 0
            ]

            excel_df["BTA Puanı"] = (
                excel_df["BTA Puanı"].fillna(0)
            )

            excel_df = excel_df.drop_duplicates(
                subset=["Hisse Kodu"],
                keep="last"
            )

            excel_kayitlarini_ekle(excel_df)

    except Exception as hata:
        st.error(
            f"Excel okunamadı: {hata}"
        )


# ==================================================
# PANELLER
# ==================================================
tab_algoritmik, tab_sohbet, tab_kayit, tab_paylas = st.tabs(
    [
        "🤖 Algoritmik Bilgiler",
        "💬 Sohbet",
        "📒 Kayıtlar",
        "🔗 Paylaş"
    ]
)


# ==================================================
# ALGORİTMİK BİLGİLER
# ==================================================
with tab_algoritmik:
    st.header("🤖 Algoritmik İşlem Bilgileri")

    if excel_df.empty:
        st.warning(
            "BTA alım fiyatı bulunan hisse bulunamadı."
        )
    else:
        secilen_hisse = st.selectbox(
            "🔍 BTA Algoritma Hissesi Seç:",
            excel_df["Hisse Kodu"].tolist()
        )

        sembol = secilen_hisse

        if not sembol.endswith(".IS"):
            sembol += ".IS"

        try:
            hisse = yf.Ticker(sembol)
            bilgi = hisse.info

            fiyat = bilgi.get(
                "regularMarketPrice"
            )

            onceki_kapanis = bilgi.get(
                "regularMarketPreviousClose"
            )

            en_yuksek = bilgi.get(
                "dayHigh"
            )

            en_dusuk = bilgi.get(
                "dayLow"
            )

            hacim = bilgi.get(
                "volume"
            )

            piyasa_degeri = bilgi.get(
                "marketCap"
            )

            kayit = excel_df[
                excel_df["Hisse Kodu"] == secilen_hisse
            ].iloc[0]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "BTA Alım Fiyatı",
                tl_format(
                    kayit["BTA Alım Fiyatı"]
                )
            )

            col2.metric(
                "BTA Puanı",
                sayi_format(
                    kayit["BTA Puanı"]
                )
            )

            col3.metric(
                "Anlık Fiyat",
                tl_format(fiyat)
            )

            st.markdown(
                f"""
                <div class="bilgi-karti">
                    <strong>Hisse Kodu:</strong> {secilen_hisse}<br>
                    <strong>Önceki Kapanış:</strong>
                    {tl_format(onceki_kapanis)}<br>
                    <strong>Günlük En Yüksek:</strong>
                    {tl_format(en_yuksek)}<br>
                    <strong>Günlük En Düşük:</strong>
                    {tl_format(en_dusuk)}<br>
                    <strong>İşlem Hacmi:</strong>
                    {sayi_format(hacim)}<br>
                    <strong>Piyasa Değeri:</strong>
                    {sayi_format(piyasa_degeri)}<br>
                    <strong>Veri Durumu:</strong>
                    En az 15 dakika gecikmeli olabilir.
                </div>
                """,
                unsafe_allow_html=True
            )

            # ==================================================
            # KAR/ZARAR HESAPLAMASI
            # ==================================================
            st.divider()
            st.subheader("📊 Kar/Zarar Analizi")

            alim_fiyati = kayit["BTA Alım Fiyatı"]
            kar_zarar = kar_zarar_hesapla(alim_fiyati, fiyat)
            kar_zarar_yuzde = kar_zarar_yuzde_hesapla(alim_fiyati, fiyat)
            renk = kar_zarar_rengi(kar_zarar)

            if kar_zarar is not None and kar_zarar_yuzde is not None:
                if kar_zarar > 0:
                    durum = "✅ KAR"
                    sınıf = "kar-zarar-karti-positive"
                elif kar_zarar < 0:
                    durum = "❌ ZARAR"
                    sınıf = "kar-zarar-karti-negative"
                else:
                    durum = "➖ EŞIT"
                    sınıf = "kar-zarar-karti-neutral"

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "💰 Kar/Zarar",
                        tl_format(kar_zarar),
                        delta=f"{kar_zarar_yuzde:+.2f}%"
                    )

                with col2:
                    st.metric(
                        "📈 Yüzde (%)",
                        f"{kar_zarar_yuzde:+.2f}%"
                    )

                with col3:
                    st.metric(
                        "🎯 Durum",
                        durum
                    )

                st.markdown(
                    f"""
                    <div class="kar-zarar-karti {sınıf}">
                        <strong>📌 Kar/Zarar Özeti</strong><br>
                        <strong>Alım Fiyatı:</strong> {tl_format(alim_fiyati)}<br>
                        <strong>Cari Fiyat:</strong> {tl_format(fiyat)}<br>
                        <strong>Kar/Zarar Miktarı:</strong> 
                        <span style="color: {renk};">
                            {tl_format(kar_zarar)}
                        </span><br>
                        <strong>Kar/Zarar Oranı:</strong> 
                        <span style="color: {renk};">
                            {kar_zarar_yuzde:+.2f}%
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        except Exception as hata:
            st.warning(
                f"Algoritmik bilgiler alınamadı: {hata}"
            )


# ==================================================
# CANLI SOHBET
# ==================================================
with tab_sohbet:
    st.header("💬 Canlı Sohbet Odası")

    # ==================================================
    # TAKİP VE BEĞENİ PANELİ
    # ==================================================
    st.subheader("⭐ BTA Oda Takip Paneli")

    takip, begeni = istatistik_oku()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if "takip_edildi" not in st.session_state:
            st.session_state["takip_edildi"] = False

        if not st.session_state["takip_edildi"]:
            if st.button(
                "⭐ Odayı Takip Et",
                use_container_width=True
            ):
                takip += 1
                istatistik_kaydet(takip, begeni)
                st.session_state["takip_edildi"] = True
                st.rerun()
        else:
            st.info("⭐ Odayı takip ediyorsunuz.")

    with col2:
        if "begeni_verildi" not in st.session_state:
            st.session_state["begeni_verildi"] = False

        if not st.session_state["begeni_verildi"]:
            if st.button(
                "👍 Beğen",
                use_container_width=True
            ):
                begeni += 1
                istatistik_kaydet(takip, begeni)
                st.session_state["begeni_verildi"] = True
                st.rerun()
        else:
            st.info("👍 Beğeniniz kaydedildi.")

    with col3:
        st.metric("👥 Takipçi", f"{takip} kişi")

    with col4:
        st.metric("👍 Beğeni", f"{begeni}")

    st.divider()

    # ==================================================
    # MESAJ FORMU
    # ==================================================
    st.subheader("💬 Mesaj Gönder")

    kullanici = st.text_input(
        "Kullanıcı adı",
        value="Hissedar"
    )

    with st.form(
        "mesaj_formu",
        clear_on_submit=True
    ):
        mesaj = st.text_area(
            "Mesajınız",
            height=90,
            placeholder="Mesajınızı yazın..."
        )

        gonder = st.form_submit_button(
            "Mesaj Gönder 🚀",
            use_container_width=True
        )

        if gonder:
            if not kullanici.strip():
                st.error(
                    "Kullanıcı adı boş bırakılamaz."
                )
            elif not mesaj.strip():
                st.error(
                    "Mesaj boş bırakılamaz."
                )
            else:
                mesaj_ekle(
                    kullanici.strip(),
                    mesaj.strip()
                )

                st.success(
                    "Mesajınız gönderildi."
                )

                st.rerun()

    st.divider()

    # ==================================================
    # MESAJ LİSTESİ
    # ==================================================
    st.subheader("📨 Mesajlar")

    mesajlar = mesajlari_oku()

    if not mesajlar.empty:
        son_mesaj_id = str(
            mesajlar.iloc[-1]["mesaj_id"]
        )

        if "son_ses_mesaj_id" not in st.session_state:
            st.session_state["son_ses_mesaj_id"] = (
                son_mesaj_id
            )
        elif (
            st.session_state["son_ses_mesaj_id"]
            != son_mesaj_id
        ):
            mesaj_sesi_cal()

            st.session_state["son_ses_mesaj_id"] = (
                son_mesaj_id
            )

    if mesajlar.empty:
        st.info(
            "Henüz mesaj bulunmuyor."
        )
    else:
        for index, satir in mesajlar.iloc[::-1].iterrows():
            mesaj_id = str(satir["mesaj_id"])

            col1, col2 = st.columns([10, 1])
            
            with col1:
                st.markdown(
                    f"""
                    <div class="mesaj-karti">
                        <strong>👤 {satir["kullanici"]}</strong>
                        <small> · {satir["tarih"]}</small>
                        <br>
                        {satir["mesaj"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if is_admin:
                    if st.button(
                        "🗑️",
                        key=f"mesaj_sil_{mesaj_id}_{index}",
                        help="Mesajı sil"
                    ):
                        mesajlar = mesajlar[
                            mesajlar["mesaj_id"].astype(str)
                            != mesaj_id
                        ]

                        mesajlar.to_csv(
                            MESAJ_DOSYASI,
                            index=False,
                            encoding="utf-8-sig"
                        )

                        st.rerun()


# ==================================================
# TARİHLİ KAYITLAR
# ==================================================
with tab_kayit:
    st.header("📒 Tarihli Kayıt Defteri")

    df_kayitlar = kayitlari_oku()

    if df_kayitlar.empty:
        st.info(
            "Henüz kayıt bulunmuyor."
        )
    else:
        df_kayitlar["bta_alim_fiyati"] = pd.to_numeric(
            df_kayitlar["bta_alim_fiyati"],
            errors="coerce"
        )

        df_kayitlar = df_kayitlar[
            df_kayitlar["bta_alim_fiyati"] > 0
        ]

        # ==================================================
        # KAYITLARA KAR/ZARAR EKLE
        # ==================================================
        kayitlar_kar_zarar = []

        for _, satir in df_kayitlar.iterrows():
            hisse_kodu = satir["hisse_kodu"]
            alim_fiyati = satir["bta_alim_fiyati"]
            
            sembol = hisse_kodu
            if not sembol.endswith(".IS"):
                sembol += ".IS"
            
            try:
                hisse = yf.Ticker(sembol)
                cari_fiyat = hisse.info.get("regularMarketPrice")
                
                kar_zarar = kar_zarar_hesapla(alim_fiyati, cari_fiyat)
                kar_zarar_yuzde = kar_zarar_yuzde_hesapla(alim_fiyati, cari_fiyat)
                
                kayitlar_kar_zarar.append({
                    "Kayıt Tarihi": satir["kayit_tarihi"],
                    "Hisse Kodu": hisse_kodu,
                    "BTA Alım Fiyatı": tl_format(alim_fiyati),
                    "Cari Fiyat": tl_format(cari_fiyat) if cari_fiyat else "-",
                    "Kar/Zarar": tl_format(kar_zarar) if kar_zarar is not None else "-",
                    "Yüzde": f"{kar_zarar_yuzde:+.2f}%" if kar_zarar_yuzde is not None else "-",
                    "BTA Puanı": sayi_format(satir["bta_puani"])
                })
            except Exception:
                kayitlar_kar_zarar.append({
                    "Kayıt Tarihi": satir["kayit_tarihi"],
                    "Hisse Kodu": hisse_kodu,
                    "BTA Alım Fiyatı": tl_format(alim_fiyati),
                    "Cari Fiyat": "-",
                    "Kar/Zarar": "-",
                    "Yüzde": "-",
                    "BTA Puanı": sayi_format(satir["bta_puani"])
                })

        gorunum_df = pd.DataFrame(kayitlar_kar_zarar)

        st.dataframe(
            gorunum_df,
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "📥 Kayıtları İndir",
                data=df_kayitlar.to_csv(
                    index=False,
                    encoding="utf-8-sig"
                ),
                file_name="bta_tarihli_kayitlar.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            if is_admin:
                if st.button(
                    "🗑️ Tüm Kayıtları Sil",
                    use_container_width=True
                ):
                    pd.DataFrame(
                        columns=KAYIT_SUTUNLARI
                    ).to_csv(
                        KAYIT_DOSYASI,
                        index=False,
                        encoding="utf-8-sig"
                    )
                    st.success("✅ Tüm kayıtlar silindi")
                    st.rerun()


# ==================================================
# PAYLAŞ TAB'I
# ==================================================
with tab_paylas:
    st.header("🔗 Sayfayı Sosyal Medyada Paylaş")

    st.divider()

    # ==================================================
    # PAYLAŞ URL'Sİ
    # ==================================================
    st.subheader("📍 Paylaş Linki")

    sayfa_url = st.text_input(
        "Platform URL:",
        value="https://btasinyal.streamlit.app",
        help="Paylaşmak istediğiniz sayfanın tam URL'sini girin"
    )

    baslik = st.text_input(
        "Paylaşım Başlığı:",
        value="BTA Algoritmik İşlem Platformu - Borsa Sinyalleri"
    )

    st.divider()

    # ==================================================
    # PAYLAŞ BUTONLARI
    # ==================================================
    st.subheader("📱 Sosyal Medya Kanalları")

    # Paylaşım linklerini oluştur
    twitter_link = paylas_linki_olustur("twitter", sayfa_url, baslik)
    facebook_link = paylas_linki_olustur("facebook", sayfa_url, baslik)
    linkedin_link = paylas_linki_olustur("linkedin", sayfa_url, baslik)
    whatsapp_link = paylas_linki_olustur("whatsapp", sayfa_url, baslik)
    telegram_link = paylas_linki_olustur("telegram", sayfa_url, baslik)
    email_link = paylas_linki_olustur("email", sayfa_url, baslik)

    # Butonları göster
    st.markdown(
        f"""
        <div class="paylas-container">
            <a href="{twitter_link}" target="_blank" class="paylas-buton paylas-twitter">🐦 Twitter</a>
            <a href="{facebook_link}" target="_blank" class="paylas-buton paylas-facebook">👍 Facebook</a>
            <a href="{linkedin_link}" target="_blank" class="paylas-buton paylas-linkedin">💼 LinkedIn</a>
            <a href="{whatsapp_link}" target="_blank" class="paylas-buton paylas-whatsapp">💬 WhatsApp</a>
            <a href="{telegram_link}" target="_blank" class="paylas-buton paylas-telegram">✈️ Telegram</a>
            <a href="{email_link}" class="paylas-buton paylas-email">✉️ E-Posta</a>
            <button class="paylas-buton paylas-kopya" onclick="
                navigator.clipboard.writeText('{sayfa_url}');
                alert('Link kopyalandı! 📋');
            ">📋 Linki Kopyala</button>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ==================================================
    # QR KOD
    # ==================================================
    st.subheader("📱 QR Kod ile Hızlı Erişim")

    try:
        import qrcode
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(sayfa_url)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="00f5c8", back_color="07131f")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.image(
                qr_img,
                caption="QR Kodu tarayarak platforma erişin",
                use_column_width=True
            )

    except ImportError:
        st.info("QR kod göstermek için: pip install qrcode[pil]")

    st.divider()

    # ==================================================
    # İSTATİSTİKLER
    # ==================================================
    st.subheader("📊 Platform İstatistikleri")

    takip, begeni = istatistik_oku()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("👥 Takipçiler", takip)

    with col2:
        st.metric("👍 Beğeniler", begeni)

    with col3:
        st.metric("💬 Mesajlar", len(mesajlari_oku()))


# ==================================================
# SPK UYARISI
# ==================================================
st.markdown(
    """
    <div class="spk-uyari">
        <strong>⚠️ SPK YASAL UYARI:</strong>
        Bu platformda yer alan veriler yalnızca genel bilgilendirme
        amacıyla sunulmaktadır. Borsa verileri en az 15 dakika gecikmeli
        olabilir ve anlık işlem verisi olarak kabul edilmemelidir.
        Buradaki hiçbir veri, puan veya fiyat yatırım danışmanlığı,
        hedef fiyat ya da AL, SAT, TUT tavsiyesi değildir.
    </div>
    """,
    unsafe_allow_html=True
)
