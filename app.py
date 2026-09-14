import os
import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st
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
# PARA FORMATLAMA
# 4100 -> 4.100,00 TL
# ==================================================
def tl_format(deger):
    try:
        sayi = float(deger)

        return (
            f"{sayi:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            + " TL"
        )
    except Exception:
        return "-"


def sayi_format(deger):
    try:
        sayi = float(deger)

        return (
            f"{sayi:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
    except Exception:
        return "-"


# ==================================================
# ARKA PLAN VE TASARIM
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07131f !important;
        background-image:
            linear-gradient(
                rgba(5, 14, 25, 0.88),
                rgba(5, 14, 25, 0.96)
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
        background: rgba(4, 13, 24, 0.97) !important;
    }

    .main .block-container {
        max-width: 1450px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    h1, h2, h3, h4, p, label, span, div {
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.65);
    }

    .bta-logo-alani {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        margin: 0 0 12px 0;
        padding: 0;
    }

    .bta-kayan-logo {
        display: inline-block;
        color: #00f5c8;
        font-family: "Brush Script MT", "Segoe Script", cursive;
        font-size: 58px;
        font-weight: bold;
        text-shadow:
            0 0 8px #00f5c8,
            0 0 16px #00f5c8,
            0 0 26px #168cff;
        animation: bta-kayma 14s linear infinite;
    }

    @keyframes bta-kayma {
        0% {
            transform: translateX(-100%);
        }

        100% {
            transform: translateX(100vw);
        }
    }

    .bilgi-kutusu {
        background: rgba(9, 31, 48, 0.93);
        border: 1px solid rgba(0, 245, 200, 0.4);
        border-radius: 9px;
        padding: 13px;
        color: #ffffff;
        margin: 10px 0;
    }

    .spk-uyari {
        background: rgba(70, 18, 27, 0.96);
        border: 1px solid #ff5264;
        border-radius: 8px;
        padding: 13px;
        color: white;
        font-size: 12px;
        line-height: 1.6;
        text-align: justify;
        margin-top: 30px;
    }

    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 0.8rem 0.6rem 1.5rem 0.6rem !important;
        }

        h1 {
            font-size: 1.6rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        .bta-kayan-logo {
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

        [data-testid="stDataFrame"] {
            font-size: 11px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# DOSYA AYARLARI
# ==================================================
KAYIT_DOSYASI = "bta_tarihli_kayit_defteri.csv"

KAYIT_SUTUNLARI = [
    "kayit_id",
    "kayit_tarihi",
    "excel_yukleme_tarihi",
    "hisse_kodu",
    "bta_alim_fiyati",
    "bta_puani",
    "kaynak_dosyasi"
]

if not os.path.exists(KAYIT_DOSYASI):
    pd.DataFrame(
        columns=KAYIT_SUTUNLARI
    ).to_csv(
        KAYIT_DOSYASI,
        index=False,
        encoding="utf-8-sig"
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


def kayit_anahtari_olustur(
    hisse_kodu,
    alim_fiyati,
    bta_puani
):
    metin = (
        f"{hisse_kodu}|"
        f"{float(alim_fiyati):.4f}|"
        f"{float(bta_puani):.4f}"
    )

    return hashlib.sha256(
        metin.encode("utf-8")
    ).hexdigest()[:20]


def excel_kayitlarini_ekle(
    df_excel,
    dosya_adi,
    yukleme_tarihi
):
    mevcut_kayitlar = kayitlari_oku()
    yeni_kayitlar = []

    for _, satir in df_excel.iterrows():
        hisse_kodu = str(
            satir["Hisse Kodu"]
        ).strip().upper()

        if (
            not hisse_kodu
            or hisse_kodu in ["NONE", "NAN", "NULL", "NA"]
        ):
            continue

        try:
            alim_fiyati = float(
                satir["BTA Alım Fiyatı"]
            )
        except Exception:
            continue

        if alim_fiyati <= 0:
            continue

        try:
            bta_puani = float(
                satir["BTA Puanı"]
            )
        except Exception:
            bta_puani = 0.0

        kayit_id = kayit_anahtari_olustur(
            hisse_kodu,
            alim_fiyati,
            bta_puani
        )

        daha_once_kayitli = (
            mevcut_kayitlar["kayit_id"]
            .astype(str)
            .eq(kayit_id)
            .any()
        )

        if daha_once_kayitli:
            continue

        yeni_kayitlar.append(
            {
                "kayit_id": kayit_id,
                "kayit_tarihi": datetime.now().strftime(
                    "%d.%m.%Y %H:%M:%S"
                ),
                "excel_yukleme_tarihi": yukleme_tarihi,
                "hisse_kodu": hisse_kodu,
                "bta_alim_fiyati": alim_fiyati,
                "bta_puani": bta_puani,
                "kaynak_dosyasi": dosya_adi
            }
        )

    if not yeni_kayitlar:
        return 0

    yeni_df = pd.DataFrame(yeni_kayitlar)

    sonuc_df = pd.concat(
        [mevcut_kayitlar, yeni_df],
        ignore_index=True
    )

    sonuc_df.to_csv(
        KAYIT_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )

    return len(yeni_kayitlar)


# ==================================================
# LOGO
# ==================================================
st.markdown(
    """
    <div class="bta-logo-alani">
        <div class="bta-kayan-logo">
            BTA ALGORİTMİK İŞLEM
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SPK METNİ
# ==================================================
SPK_METNI = (
    "SPK YASAL UYARI: Bu platformda yer alan bilgiler yalnızca genel "
    "bilgilendirme amacıyla sunulmaktadır. Buradaki hiçbir veri, puan "
    "veya fiyat yatırım danışmanlığı, hedef fiyat ya da AL, SAT, TUT "
    "tavsiyesi değildir. Yatırım kararlarınızı kendi araştırmanız ve "
    "yetkili yatırım kuruluşlarıyla görüşerek vermeniz gerekir."
)


# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

admin_sifre = st.sidebar.text_input(
    "Yönetici Şifresi",
    type="password"
)

is_admin = admin_sifre == "BTA2026"

if is_admin:
    st.sidebar.success("Yönetici yetkileri aktif.")

otomatik_yenileme = st.sidebar.checkbox(
    "Otomatik yenilemeyi aktif et",
    value=True
)

if otomatik_yenileme:
    yenileme_suresi = st.sidebar.slider(
        "Yenileme süresi",
        min_value=5,
        max_value=60,
        value=15
    )

    st_autorefresh(
        interval=yenileme_suresi * 1000,
        key="bta_yenileme"
    )


# ==================================================
# ANA BAŞLIK
# ==================================================
st.title("BTA Algoritmik İşlem ve Analiz Portalı")

st.markdown(
    """
    <div class="bilgi-kutusu">
        Excel dosyanızdaki A, C ve D sütunları analiz edilir.
        BTA alım fiyatı bulunan hisseler otomatik olarak tarihli kayıt
        defterine eklenir.
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SEKME MENÜSÜ
# ==================================================
tab_excel, tab_live, tab_records = st.tabs(
    [
        "📂 Excel Analizi",
        "📈 KONYA Canlı Takip",
        "📒 Tarihli Kayıt Defteri"
    ]
)


# ==================================================
# EXCEL ANALİZİ
# A = Hisse Kodu
# C = BTA Alım Fiyatı
# D = BTA Puanı
# ==================================================
with tab_excel:
    st.header("📂 Excel Veri Analizi")

    st.info(
        "Excel'in A, C ve D sütunları kullanılır. "
        "BTA alım fiyatı bulunmayan hisseler gösterilmez."
    )

    excel_dosyalari = [
        dosya
        for dosya in os.listdir(".")
        if dosya.lower().endswith((".xlsx", ".xlsm"))
    ]

    yuklenen_dosya = st.file_uploader(
        "Excel dosyanızı yükleyin",
        type=["xlsx", "xlsm"]
    )

    if yuklenen_dosya is not None:
        kaynak = yuklenen_dosya
        dosya_adi = yuklenen_dosya.name
    elif excel_dosyalari:
        dosya_adi = st.selectbox(
            "Klasördeki Excel dosyası",
            excel_dosyalari
        )
        kaynak = dosya_adi
    else:
        kaynak = None
        dosya_adi = ""

    if kaynak is None:
        st.warning("Henüz Excel dosyası seçilmedi.")
    else:
        try:
            excel_objesi = pd.ExcelFile(
                kaynak,
                engine="openpyxl"
            )

            sayfa_adi = st.selectbox(
                "Excel sayfası",
                excel_objesi.sheet_names
            )

            ham_df = pd.read_excel(
                kaynak,
                sheet_name=sayfa_adi,
                engine="openpyxl",
                header=None
            )

            if ham_df.shape[1] < 4:
                st.error(
                    "Excel dosyasında A, C ve D sütunları bulunmalıdır."
                )
            else:
                # A, C ve D sütunlarını al
                analiz_df = ham_df.iloc[:, [0, 2, 3]].copy()

                analiz_df.columns = [
                    "Hisse Kodu",
                    "BTA Alım Fiyatı",
                    "BTA Puanı"
                ]

                # Başlık satırı varsa kaldır
                analiz_df = analiz_df[
                    ~analiz_df["Hisse Kodu"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .isin(
                        [
                            "NONE",
                            "NAN",
                            "NULL",
                            "HİSSE",
                            "HISSE",
                            "HİSSE KODU",
                            "HISSE KODU"
                        ]
                    )
                ]

                # Hisse kodunu temizle
                analiz_df["Hisse Kodu"] = (
                    analiz_df["Hisse Kodu"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

                # Fiyat ve puanı sayıya çevir
                analiz_df["BTA Alım Fiyatı"] = pd.to_numeric(
                    analiz_df["BTA Alım Fiyatı"]
                    .astype(str)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False),
                    errors="coerce"
                )

                analiz_df["BTA Puanı"] = pd.to_numeric(
                    analiz_df["BTA Puanı"]
                    .astype(str)
                    .str.replace(",", ".", regex=False),
                    errors="coerce"
                )

                # Geçersiz ve alım fiyatı olmayan hisseleri gizle
                analiz_df = analiz_df[
                    analiz_df["Hisse Kodu"].notna()
                ]

                analiz_df = analiz_df[
                    ~analiz_df["Hisse Kodu"].isin(
                        ["", "NONE", "NAN", "NULL", "NA"]
                    )
                ]

                analiz_df = analiz_df[
                    analiz_df["BTA Alım Fiyatı"].notna()
                ]

                analiz_df = analiz_df[
                    analiz_df["BTA Alım Fiyatı"] > 0
                ]

                analiz_df = analiz_df.drop_duplicates(
                    subset=["Hisse Kodu"],
                    keep="last"
                )

                if analiz_df.empty:
                    st.warning(
                        "BTA alım fiyatı bulunan geçerli hisse yok."
                    )
                else:
                    yukleme_tarihi = datetime.now().strftime(
                        "%d.%m.%Y %H:%M:%S"
                    )

                    eklenen_sayi = excel_kayitlarini_ekle(
                        analiz_df,
                        dosya_adi,
                        yukleme_tarihi
                    )

                    if eklenen_sayi > 0:
                        st.success(
                            f"{eklenen_sayi} yeni hisse tarihli "
                            "kayıt defterine otomatik eklendi."
                        )

                    st.subheader(
                        "📊 Web Sayfasında Gösterilen Excel Verileri"
                    )

                    web_df = analiz_df.copy()

                    web_df["BTA Alım Fiyatı"] = (
                        web_df["BTA Alım Fiyatı"]
                        .apply(tl_format)
                    )

                    web_df["BTA Puanı"] = (
                        web_df["BTA Puanı"]
                        .apply(sayi_format)
                    )

                    st.dataframe(
                        web_df[
                            [
                                "Hisse Kodu",
                                "BTA Alım Fiyatı",
                                "BTA Puanı"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        f"Excel yükleme tarihi: {yukleme_tarihi}"
                    )

        except Exception as hata:
            st.error(
                f"Excel işlenirken hata oluştu: {hata}"
            )


# ==================================================
# KONYA CANLI TAKİP
# ==================================================
with tab_live:
    st.header("📈 KONYA Canlı Takip")

    sembol = "KONYA.IS"
    konya_bta_alim_fiyati = 4100.00

    try:
        hisse = yf.Ticker(sembol)

        veri = hisse.history(
            period="5d",
            interval="1d"
        )

        if veri.empty:
            st.warning(
                "KONYA için canlı veri alınamadı."
            )
        else:
            son_fiyat = float(
                veri["Close"].iloc[-1]
            )

            kar_zarar_yuzde = (
                (son_fiyat - konya_bta_alim_fiyati)
                / konya_bta_alim_fiyati
            ) * 100

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Anlık Fiyat",
                tl_format(son_fiyat)
            )

            col2.metric(
                "BTA Alım Fiyatı",
                tl_format(konya_bta_alim_fiyati)
            )

            col3.metric(
                "Kar/Zarar",
                f"%{sayi_format(kar_zarar_yuzde)}"
            )

            st.line_chart(
                veri[["Close"]].rename(
                    columns={"Close": "KONYA Fiyatı"}
                )
            )

    except Exception as hata:
        st.error(
            f"Canlı veri alınamadı: {hata}"
        )


# ==================================================
# TARİHLİ KAYIT DEFTERİ
# ==================================================
with tab_records:
    st.header("📒 BTA Tarihli Kayıt Defteri")

    st.info(
        "Kayıtlar Excel yüklendiğinde otomatik oluşturulur. "
        "Elle hisse ekleme kapalıdır."
    )

    df_kayitlar = kayitlari_oku()

    if df_kayitlar.empty:
        st.info(
            "Henüz kayıt bulunmuyor. "
            "BTA alım fiyatı bulunan bir Excel yükleyin."
        )
    else:
        df_kayitlar = df_kayitlar[
            pd.to_numeric(
                df_kayitlar["bta_alim_fiyati"],
                errors="coerce"
            ).fillna(0) > 0
        ]

        gorunum_df = df_kayitlar.rename(
            columns={
                "kayit_tarihi": "Kayıt Tarihi",
                "excel_yukleme_tarihi": "Excel Yükleme Tarihi",
                "hisse_kodu": "Hisse Kodu",
                "bta_alim_fiyati": "BTA Alım Fiyatı",
                "bta_puani": "BTA Puanı",
                "kaynak_dosyasi": "Excel Dosyası"
            }
        )

        gorunum_df["BTA Alım Fiyatı"] = (
            gorunum_df["BTA Alım Fiyatı"]
            .apply(tl_format)
        )

        gorunum_df["BTA Puanı"] = (
            gorunum_df["BTA Puanı"]
            .apply(sayi_format)
        )

        st.dataframe(
            gorunum_df[
                [
                    "Kayıt Tarihi",
                    "Excel Yükleme Tarihi",
                    "Hisse Kodu",
                    "BTA Alım Fiyatı",
                    "BTA Puanı",
                    "Excel Dosyası"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Tarihli Kayıt Defterini İndir 📥",
            data=df_kayitlar.to_csv(
                index=False,
                encoding="utf-8-sig"
            ),
            file_name="bta_tarihli_kayit_defteri.csv",
            mime="text/csv",
            use_container_width=True
        )

        if is_admin:
            if st.button(
                "Tüm Geçmiş Kayıtları Sil 🗑️",
                use_container_width=True
            ):
                pd.DataFrame(
                    columns=KAYIT_SUTUNLARI
                ).to_csv(
                    KAYIT_DOSYASI,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success(
                    "Tüm kayıt geçmişi silindi."
                )

                st.rerun()


# ==================================================
# ALT SPK UYARISI
# ==================================================
st.markdown(
    f"""
    <div class="spk-uyari">
        <strong>⚠️ {SPK_METNI}</strong>
    </div>
    """,
    unsafe_allow_html=True
)
