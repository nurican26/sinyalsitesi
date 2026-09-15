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
    "bta_alim_fiyati",
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

    .paylas-paneli {
        background: rgba(9, 31, 48, 0.95);
        border: 2px solid #00f5c8;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }

    .paylas-buton {
        display: inline-block;
        margin: 8px 4px;
        padding: 12px 16px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        text-align: center;
        min-width: 120px;
    }

    .paylas-twitter {
        background-color: #1DA1F2;
        color: white;
    }

    .paylas-twitter:hover {
        background-color: #1a8cd8;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(29, 161, 242, 0.5);
    }

    .paylas-facebook {
        background-color: #1877F2;
        color: white;
    }

    .paylas-facebook:hover {
        background-color: #0a66c2;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(24, 119, 242, 0.5);
    }

    .paylas-linkedin {
        background-color: #0A66C2;
        color: white;
    }

    .paylas-linkedin:hover {
        background-color: #084998;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(10, 102, 194, 0.5);
    }

    .paylas-whatsapp {
        background-color: #25D366;
        color: white;
    }

    .paylas-whatsapp:hover {
        background-color: #1eaa54;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(37, 211, 102, 0.5);
    }

    .paylas-telegram {
        background-color: #0088cc;
        color: white;
    }

    .paylas-telegram:hover {
        background-color: #006ba3;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 136, 204, 0.5);
    }

    .paylas-email {
        background-color: #EA4335;
        color: white;
    }

    .paylas-email:hover {
        background-color: #c5221f;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(234, 67, 53, 0.5);
    }

    .paylas-kopya {
        background-color: #00f5c8;
        color: #07131f;
        font-weight: bold;
    }

    .paylas-kopya:hover {
        background-color: #00d4a8;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 245, 200, 0.5);
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
            display: block;
            width: 100%;
            margin: 5px 0;
            padding: 12px;
            min-width: unset;
        }

        .paylas-paneli {
            padding: 15px;
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
def paylas_linki_olustur(platform, url, baslik, aciklama):
    """
    Farklı platformlar için paylaşım linki oluşturur
    """
    encoded_url = urllib.parse.quote(url)
    encoded_baslik = urllib.parse.quote(baslik)
    encoded_aciklama = urllib.parse.quote(aciklama)
    
    linkler = {
        "twitter": f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_baslik}%0A{encoded_aciklama}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        "whatsapp": f"https://wa.me/?text={encoded_baslik}%0A{encoded_aciklama}%0A{encoded_url}",
        "telegram": f"https://t.me/share/url?url={encoded_url}&text={encoded_baslik}%0A{encoded_aciklama}",
        "email": f"mailto:?subject={encoded_baslik}&body={encoded_aciklama}%0A{encoded_url}"
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
# YÖNETİCİ
# ==================================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

admin_sifre = st.sidebar.text_input(
    "Yönetici Şifresi",
    type="password"
)

is_admin = admin_sifre == "BTA2026"

if is_admin:
    st.sidebar.success(
        "Yönetici yetkileri aktif."
    )


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
        "💬 Canlı Sohbet",
        "📒 Tarihli Kayıtlar",
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
    # TAKİP VE BEĞENİ PANELİ (Sohbet İçinde)
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

                istatistik_kaydet(
                    takip,
                    begeni
                )

                st.session_state["takip_edildi"] = True
                st.rerun()
        else:
            st.info(
                "⭐ Odayı takip ediyorsunuz."
            )

    with col2:
        if "begeni_verildi" not in st.session_state:
            st.session_state["begeni_verildi"] = False

        if not st.session_state["begeni_verildi"]:
            if st.button(
                "👍 Beğen",
                use_container_width=True
            ):
                begeni += 1

                istatistik_kaydet(
                    takip,
                    begeni
                )

                st.session_state["begeni_verildi"] = True
                st.rerun()
        else:
            st.info(
                "👍 Beğeniniz kaydedildi."
            )

    with col3:
        st.metric(
            "👥 Takipçi",
            f"{takip} kişi"
        )

    with col4:
        st.metric(
            "👍 Beğeni",
            f"{begeni}"
        )

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

            if is_admin:
                if st.button(
                    "Mesajı Sil",
                    key=f"mesaj_sil_{mesaj_id}_{index}"
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

        gorunum = df_kayitlar.rename(
            columns={
                "kayit_tarihi": "Kayıt Tarihi",
                "hisse_kodu": "Hisse Kodu",
                "bta_alim_fiyati": "BTA Alım Fiyatı",
                "bta_puani": "BTA Puanı"
            }
        )

        gorunum["BTA Alım Fiyatı"] = (
            gorunum["BTA Alım Fiyatı"]
            .apply(tl_format)
        )

        gorunum["BTA Puanı"] = (
            gorunum["BTA Puanı"]
            .apply(sayi_format)
        )

        st.dataframe(
            gorunum[
                [
                    "Kayıt Tarihi",
                    "Hisse Kodu",
                    "BTA Alım Fiyatı",
                    "BTA Puanı"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Kayıtları İndir",
            data=df_kayitlar.to_csv(
                index=False,
                encoding="utf-8-sig"
            ),
            file_name="bta_tarihli_kayitlar.csv",
            mime="text/csv",
            use_container_width=True
        )


# ==================================================
# PAYLAŞ TAB'I
# ==================================================
with tab_paylas:
    st.header("🔗 Sayfayı Paylaş")

    st.markdown(
        """
        BTA Algoritmik İşlem platformunu sosyal medya ve 
        diğer kanallar aracılığıyla arkadaşlarınızla paylaşın.
        """
    )

    st.divider()

    # ==================================================
    # PAYLAŞ AYARLARI
    # ==================================================
    st.subheader("📝 Paylaşım Ayarları")

    sayfa_url = st.text_input(
        "🌐 Platform URL'sini girin:",
        value="https://bta-algoritmi.streamlit.app",
        help="Lütfen paylaşmak istediğiniz sayfanın tam URL'sini girin"
    )

    baslik = st.text_input(
        "📌 Paylaşım Başlığı:",
        value="BTA Algoritmik İşlem Platformu"
    )

    st.divider()

    # ==================================================
    # PAYLAŞ BUTONLARI
    # ==================================================
    st.subheader("🚀 Sosyal Medyada Paylaş")

    # Twitter
    twitter_link = paylas_linki_olustur(
        "twitter",
        sayfa_url,
        baslik,
        "Borsa verilerini takip et, canlı sohbete katıl ve algoritmik işlem sinyallerini al!"
    )

    # Facebook
    facebook_link = paylas_linki_olustur(
        "facebook",
        sayfa_url,
        baslik,
        "Borsa verilerini takip et, canlı sohbete katıl ve algoritmik işlem sinyallerini al!"
    )

    # LinkedIn
    linkedin_link = paylas_linki_olustur(
        "linkedin",
        sayfa_url,
        baslik,
        "Profesyonel yatırım analizi ve algoritmik işlem sinyalleri"
    )

    # WhatsApp
    whatsapp_link = paylas_linki_olustur(
        "whatsapp",
        sayfa_url,
        baslik,
        "Borsa verilerini takip et, canlı sohbete katıl ve algoritmik işlem sinyallerini al!"
    )

    # Telegram
    telegram_link = paylas_linki_olustur(
        "telegram",
        sayfa_url,
        baslik,
        "Borsa verilerini takip et, canlı sohbete katıl ve algoritmik işlem sinyallerini al!"
    )

    # Email
    email_link = paylas_linki_olustur(
        "email",
        sayfa_url,
        baslik,
        "Borsa verilerini takip et, canlı sohbete katıl ve algoritmik işlem sinyallerini al!"
    )

    # Butonları göster
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <a href="{twitter_link}" target="_blank" class="paylas-buton paylas-twitter">
                🐦 Twitter
            </a>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <a href="{facebook_link}" target="_blank" class="paylas-buton paylas-facebook">
                👍 Facebook
            </a>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <a href="{linkedin_link}" target="_blank" class="paylas-buton paylas-linkedin">
                in LinkedIn
            </a>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <a href="{whatsapp_link}" target="_blank" class="paylas-buton paylas-whatsapp">
                💬 WhatsApp
            </a>
            """,
            unsafe_allow_html=True
        )

    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown(
            f"""
            <a href="{telegram_link}" target="_blank" class="paylas-buton paylas-telegram">
                ✈️ Telegram
            </a>
            """,
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            f"""
            <a href="{email_link}" class="paylas-buton paylas-email">
                ✉️ E-Posta
            </a>
            """,
            unsafe_allow_html=True
        )

    with col7:
        st.markdown(
            f"""
            <button class="paylas-buton paylas-kopya" onclick="
                navigator.clipboard.writeText('{sayfa_url}');
                alert('Link kopyalandı! 📋');
            ">
                📋 Linki Kopyala
            </button>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ==================================================
    # QR KOD
    # ==================================================
    st.subheader("📱 QR Kod")

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
                caption="Platformu taramak için QR Kodu kullanın",
                use_column_width=True
            )

    except ImportError:
        st.info("QR kod göstermek için 'qrcode' kütüphanesini yükleyin: pip install qrcode[pil]")

    st.divider()

    # ==================================================
    # İSTATİSTİKLER
    # ==================================================
    st.subheader("📊 Paylaşım İstatistikleri")

    col1, col2, col3 = st.columns(3)

    takip, begeni = istatistik_oku()

    with col1:
        st.metric(
            "👥 Platform Takipçileri",
            takip
        )

    with col2:
        st.metric(
            "👍 Toplam Beğeni",
            begeni
        )

    with col3:
        st.metric(
            "💬 Mesaj Sayısı",
            len(mesajlari_oku())
        )

    st.divider()

    # ==================================================
    # PAYLAŞ İPUÇLARI
    # ==================================================
    st.subheader("💡 Paylaşım İpuçları")

    st.markdown(
        """
        - **Basit ve Kısa:** Paylaşım metninizi basit ve kısa tutun
        - **Çekici Başlık:** Dikkat çeken başlıklar daha fazla tıklama alır
        - **Emoji Kullanın:** Emojiler gönderileri daha göze çarpkılır hale getirir
        - **Zamanlamayı Önemseyin:** En aktif saatlerde paylaşım yapın
        - **Hashtag Ekleyin:** İlgili hashtag'ler paylaşımınızın ulaşımını artırır
        - **Arkadaş Davet Edin:** Arkadaşlarınızı doğrudan davet etmek katılımı artırır
        - **Profesyonel Ton:** Finans platformunda resmi ve profesyonel kalın
        """
    )


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
