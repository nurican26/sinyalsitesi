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
    page_title="BTA Algoritmik İşlem Analiz Portalı",
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
    "oy_sayisi",
    "puan_toplami"
]

MESAJ_SUTUNLARI = [
    "mesaj_id",
    "tarih",
    "kullanici",
    "mesaj"
]


def dosya_olustur(dosya_adi, sutunlar):
    if not os.path.exists(dosya_adi):
        pd.DataFrame(
            columns=sutunlar
        ).to_csv(
            dosya_adi,
            index=False,
            encoding="utf-8-sig"
        )


dosya_olustur(KAYIT_DOSYASI, KAYIT_SUTUNLARI)
dosya_olustur(ISTATISTIK_DOSYASI, ISTATISTIK_SUTUNLARI)
dosya_olustur(MESAJ_DOSYASI, MESAJ_SUTUNLARI)


# ==================================================
# FORMAT FONKSİYONLARI
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
            parcalar = metin.split(",")

            if len(parcalar[-1]) == 3:
                metin = metin.replace(",", "")
            else:
                metin = metin.replace(",", ".")
        elif "." in metin:
            parcalar = metin.split(".")

            if len(parcalar[-1]) == 3:
                metin = metin.replace(".", "")

        return float(metin)

    except Exception:
        return None


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
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.7);
    }

    .bta-logo-alani {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        margin-bottom: 12px;
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

    .oda-karti {
        background: rgba(9, 31, 48, 0.94);
        border: 1px solid rgba(0, 245, 200, 0.4);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }

    .mesaj-karti {
        background: rgba(8, 29, 45, 0.94);
        border-left: 3px solid #00f5c8;
        border-radius: 7px;
        padding: 10px;
        margin: 7px 0;
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
            font-size: 1.5rem !important;
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
        return pd.DataFrame(
            columns=KAYIT_SUTUNLARI
        )


def kayit_id_olustur(
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


def excel_kayitlarini_ekle(df_excel):
    mevcut_kayitlar = kayitlari_oku()
    yeni_kayitlar = []

    for _, satir in df_excel.iterrows():
        hisse_kodu = str(
            satir["Hisse Kodu"]
        ).strip().upper()

        alim_fiyati = satir["BTA Alım Fiyatı"]
        bta_puani = satir["BTA Puanı"]

        if not hisse_kodu:
            continue

        if hisse_kodu in [
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

        if pd.isna(alim_fiyati):
            continue

        if float(alim_fiyati) <= 0:
            continue

        if pd.isna(bta_puani):
            bta_puani = 0.0

        kayit_id = kayit_id_olustur(
            hisse_kodu,
            alim_fiyati,
            bta_puani
        )

        if (
            mevcut_kayitlar["kayit_id"]
            .astype(str)
            .eq(kayit_id)
            .any()
        ):
            continue

        yeni_kayitlar.append(
            {
                "kayit_id": kayit_id,
                "kayit_tarihi": datetime.now().strftime(
                    "%d.%m.%Y %H:%M:%S"
                ),
                "hisse_kodu": hisse_kodu,
                "bta_alim_fiyati": float(alim_fiyati),
                "bta_puani": float(bta_puani)
            }
        )

    if not yeni_kayitlar:
        return

    sonuc_df = pd.concat(
        [
            mevcut_kayitlar,
            pd.DataFrame(yeni_kayitlar)
        ],
        ignore_index=True
    )

    sonuc_df.to_csv(
        KAYIT_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )


# ==================================================
# İSTATİSTİK FONKSİYONLARI
# ==================================================
def istatistik_oku():
    try:
        df = pd.read_csv(
            ISTATISTIK_DOSYASI,
            encoding="utf-8-sig"
        )

        if df.empty:
            return {
                "takip_sayisi": 0,
                "oy_sayisi": 0,
                "puan_toplami": 0.0
            }

        return {
            "takip_sayisi": int(
                pd.to_numeric(
                    df.iloc[0]["takip_sayisi"],
                    errors="coerce"
                ) or 0
            ),
            "oy_sayisi": int(
                pd.to_numeric(
                    df.iloc[0]["oy_sayisi"],
                    errors="coerce"
                ) or 0
            ),
            "puan_toplami": float(
                pd.to_numeric(
                    df.iloc[0]["puan_toplami"],
                    errors="coerce"
                ) or 0
            )
        }

    except Exception:
        return {
            "takip_sayisi": 0,
            "oy_sayisi": 0,
            "puan_toplami": 0.0
        }


def istatistik_kaydet(
    takip_sayisi,
    oy_sayisi,
    puan_toplami
):
    pd.DataFrame(
        [{
            "takip_sayisi": takip_sayisi,
            "oy_sayisi": oy_sayisi,
            "puan_toplami": puan_toplami
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
        return pd.DataFrame(
            columns=MESAJ_SUTUNLARI
        )


def mesaj_kaydet(kullanici, mesaj):
    df_mesajlar = mesajlari_oku()

    yeni_mesaj = pd.DataFrame(
        [{
            "mesaj_id": int(
                datetime.now().timestamp() * 1000
            ),
            "tarih": datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S"
            ),
            "kullanici": kullanici,
            "mesaj": mesaj
        }]
    )

    df_mesajlar = pd.concat(
        [df_mesajlar, yeni_mesaj],
        ignore_index=True
    )

    df_mesajlar.to_csv(
        MESAJ_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )


# ==================================================
# OTOMATİK YENİLEME
# ==================================================
st_autorefresh(
    interval=5000,
    key="bta_canli_yenileme"
)


# ==================================================
# LOGO VE BAŞLIK
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

st.title("BTA Algoritmik İşlem Analiz Portalı")


# ==================================================
# YÖNETİCİ GİRİŞİ
# ==================================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

admin_sifre = st.sidebar.text_input(
    "Yönetici Şifresi",
    type="password"
)

is_admin = admin_sifre == "BTA2026"

if is_admin:
    st.sidebar.success("Yönetici yetkileri aktif.")


# ==================================================
# EXCEL'İ OTOMATİK OKU
# ==================================================
excel_dosyalari = [
    dosya
    for dosya in os.listdir(".")
    if dosya.lower().endswith(
        (".xlsx", ".xlsm")
    )
]

secilen_excel = None

if excel_dosyalari:
    bta_dosyalari = [
        dosya
        for dosya in excel_dosyalari
        if "bta" in dosya.lower()
    ]

    secilen_excel = (
        bta_dosyalari[0]
        if bta_dosyalari
        else excel_dosyalari[0]
    )

if secilen_excel:
    try:
        ham_df = pd.read_excel(
            secilen_excel,
            sheet_name=0,
            engine="openpyxl",
            header=None
        )

        if ham_df.shape[1] >= 4:
            analiz_df = ham_df.iloc[:, [0, 2, 3]].copy()

            analiz_df.columns = [
                "Hisse Kodu",
                "BTA Alım Fiyatı",
                "BTA Puanı"
            ]

            analiz_df["Hisse Kodu"] = (
                analiz_df["Hisse Kodu"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            analiz_df["BTA Alım Fiyatı"] = (
                analiz_df["BTA Alım Fiyatı"]
                .apply(turkce_sayi_cevir)
            )

            analiz_df["BTA Puanı"] = (
                analiz_df["BTA Puanı"]
                .apply(turkce_sayi_cevir)
            )

            analiz_df = analiz_df[
                ~analiz_df["Hisse Kodu"].isin(
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

            analiz_df = analiz_df[
                analiz_df["BTA Alım Fiyatı"].notna()
            ]

            analiz_df = analiz_df[
                analiz_df["BTA Alım Fiyatı"] > 0
            ]

            analiz_df["BTA Puanı"] = (
                analiz_df["BTA Puanı"].fillna(0)
            )

            analiz_df = analiz_df.drop_duplicates(
                subset=["Hisse Kodu"],
                keep="last"
            )

            excel_kayitlarini_ekle(analiz_df)

            gosterim_df = analiz_df.copy()

            gosterim_df["BTA Alım Fiyatı"] = (
                gosterim_df["BTA Alım Fiyatı"]
                .apply(tl_format)
            )

            gosterim_df["BTA Puanı"] = (
                gosterim_df["BTA Puanı"]
                .apply(sayi_format)
            )

            st.subheader("📊 BTA Hisse Analizi")

            st.dataframe(
                gosterim_df[
                    [
                        "Hisse Kodu",
                        "BTA Alım Fiyatı",
                        "BTA Puanı"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    except Exception as hata:
        st.error(f"Excel okunamadı: {hata}")
else:
    st.warning("Excel dosyası bulunamadı.")


# ==================================================
# ODA TAKİP VE YILDIZ PUANI
# ==================================================
st.markdown("---")
st.header("💬 BTA Canlı Takip ve Mesajlaşma Odası")

istatistik = istatistik_oku()

takip_sayisi = istatistik["takip_sayisi"]
oy_sayisi = istatistik["oy_sayisi"]
puan_toplami = istatistik["puan_toplami"]

col1, col2, col3 = st.columns(3)

with col1:
    if "oda_takip_edildi" not in st.session_state:
        st.session_state["oda_takip_edildi"] = False

    if not st.session_state["oda_takip_edildi"]:
        if st.button(
            "⭐ Odayı Takip Et",
            use_container_width=True
        ):
            takip_sayisi += 1
            istatistik_kaydet(
                takip_sayisi,
                oy_sayisi,
                puan_toplami
            )

            st.session_state["oda_takip_edildi"] = True
            st.rerun()
    else:
        st.success("✅ Odayı takip ediyorsunuz.")

with col2:
    st.metric(
        "👥 Odayı Takip Eden",
        f"{takip_sayisi} kişi"
    )

with col3:
    ortalama_puan = (
        puan_toplami / oy_sayisi
        if oy_sayisi > 0
        else 0
    )

    st.metric(
        "⭐ Ortalama Puan",
        f"{ortalama_puan:.1f} / 5"
    )


# ==================================================
# YILDIZLAMA
# ==================================================
st.subheader("⭐ BTA Odasını Puanla")

if "puan_verildi" not in st.session_state:
    st.session_state["puan_verildi"] = False

if not st.session_state["puan_verildi"]:
    secilen_puan = st.radio(
        "Puanınız:",
        [1, 2, 3, 4, 5],
        format_func=lambda puan: "⭐" * puan,
        horizontal=True
    )

    if st.button(
        "Puanı Gönder",
        use_container_width=True
    ):
        puan_toplami += secilen_puan
        oy_sayisi += 1

        istatistik_kaydet(
            takip_sayisi,
            oy_sayisi,
            puan_toplami
        )

        st.session_state["puan_verildi"] = True
        st.success("Puanınız kaydedildi.")
        st.rerun()
else:
    st.info("Bu oturumda daha önce puan verdiniz.")


# ==================================================
# CANLI MESAJLAŞMA
# ==================================================
st.subheader("🟢 Canlı Mesajlaşma")

kullanici_adi = st.text_input(
    "Kullanıcı adınız",
    value="Hissedar"
)

with st.form(
    "canli_mesaj_formu",
    clear_on_submit=True
):
    mesaj = st.text_area(
        "Mesajınızı yazın",
        height=90,
        placeholder="Odaya mesajınızı yazın..."
    )

    gonder = st.form_submit_button(
        "Mesajı Gönder 🚀",
        use_container_width=True
    )

    if gonder:
        if not kullanici_adi.strip():
            st.error("Kullanıcı adı boş bırakılamaz.")
        elif not mesaj.strip():
            st.error("Mesaj boş bırakılamaz.")
        else:
            mesaj_kaydet(
                kullanici_adi.strip(),
                mesaj.strip()
            )

            st.success("Mesajınız gönderildi.")
            st.rerun()


df_mesajlar = mesajlari_oku()

if df_mesajlar.empty:
    st.info("Henüz mesaj bulunmuyor.")
else:
    for index, satir in df_mesajlar.iloc[::-1].iterrows():
        tarih = str(satir["tarih"])
        kullanici = str(satir["kullanici"])
        mesaj_metni = str(satir["mesaj"])
        mesaj_id = str(satir["mesaj_id"])

        st.markdown(
            f"""
            <div class="mesaj-karti">
                <strong>👤 {kullanici}</strong>
                <small> · {tarih}</small>
                <br>
                {mesaj_metni}
            </div>
            """,
            unsafe_allow_html=True
        )

        if is_admin:
            if st.button(
                "Mesajı Sil",
                key=f"mesaj_sil_{mesaj_id}_{index}"
            ):
                df_mesajlar = df_mesajlar[
                    df_mesajlar["mesaj_id"].astype(str)
                    != mesaj_id
                ]

                df_mesajlar.to_csv(
                    MESAJ_DOSYASI,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.rerun()


# ==================================================
# KONYA CANLI TAKİP
# ==================================================
st.markdown("---")
st.header("📈 KONYA Canlı Takip")

try:
    konya = yf.Ticker("KONYA.IS")

    konya_veri = konya.history(
        period="5d",
        interval="1d"
    )

    if not konya_veri.empty:
        son_fiyat = float(
            konya_veri["Close"].iloc[-1]
        )

        konya_alim_fiyati = 4100.00

        kar_zarar_yuzde = (
            (son_fiyat - konya_alim_fiyati)
            / konya_alim_fiyati
        ) * 100

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Anlık Fiyat",
            tl_format(son_fiyat)
        )

        col2.metric(
            "BTA Alım Fiyatı",
            tl_format(konya_alim_fiyati)
        )

        col3.metric(
            "Kar/Zarar",
            f"%{sayi_format(kar_zarar_yuzde)}"
        )

        st.line_chart(
            konya_veri[["Close"]].rename(
                columns={
                    "Close": "KONYA Fiyatı"
                }
            )
        )
    else:
        st.warning("KONYA canlı verisi alınamadı.")

except Exception as hata:
    st.error(f"KONYA verisi alınamadı: {hata}")


# ==================================================
# TARİHLİ KAYIT DEFTERİ
# ==================================================
st.markdown("---")
st.header("📒 Tarihli Kayıt Defteri")

df_kayitlar = kayitlari_oku()

if df_kayitlar.empty:
    st.info("Henüz kayıt bulunmuyor.")
else:
    df_kayitlar["bta_alim_fiyati"] = pd.to_numeric(
        df_kayitlar["bta_alim_fiyati"],
        errors="coerce"
    )

    df_kayitlar = df_kayitlar[
        df_kayitlar["bta_alim_fiyati"] > 0
    ]

    gorunum_df = df_kayitlar.rename(
        columns={
            "kayit_tarihi": "Kayıt Tarihi",
            "hisse_kodu": "Hisse Kodu",
            "bta_alim_fiyati": "BTA Alım Fiyatı",
            "bta_puani": "BTA Puanı"
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
                "Hisse Kodu",
                "BTA Alım Fiyatı",
                "BTA Puanı"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Kayıt Defterini İndir",
        data=df_kayitlar.to_csv(
            index=False,
            encoding="utf-8-sig"
        ),
        file_name="bta_tarihli_kayit_defteri.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==================================================
# ALT SPK UYARISI
# ==================================================
st.markdown(
    """
    <div class="spk-uyari">
        <strong>⚠️ SPK YASAL UYARI:</strong>
        Bu platformda yer alan bilgiler yalnızca genel bilgilendirme
        amacıyla sunulmaktadır. Buradaki hiçbir veri, puan veya fiyat
        yatırım danışmanlığı, hedef fiyat ya da AL, SAT, TUT tavsiyesi
        değildir. Yatırım kararlarınızı kendi araştırmanız ve yetkili
        yatırım kuruluşlarıyla görüşerek vermeniz gerekir.
    </div>
    """,
    unsafe_allow_html=True
)
