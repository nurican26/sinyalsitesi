import os
from datetime import datetime

import pandas as pd
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh


# ==========================================
# SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem Portalı",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# TASARIM VE MOBİL UYUMLULUK
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07131f !important;
        background-image:
            linear-gradient(
                rgba(7, 19, 31, 0.88),
                rgba(7, 19, 31, 0.96)
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
        background: rgba(5, 15, 26, 0.97) !important;
    }

    .main .block-container {
        max-width: 1400px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    h1, h2, h3, h4, p, label, span, div {
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.55);
    }

    [data-testid="stMetric"],
    [data-testid="stExpander"],
    [data-testid="stForm"] {
        background: rgba(10, 28, 45, 0.90) !important;
        border: 1px solid rgba(0, 230, 190, 0.35) !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }

    .spk-uyari {
        background: rgba(52, 18, 24, 0.95);
        border: 1px solid #ff5264;
        border-radius: 8px;
        padding: 14px;
        margin-top: 30px;
        color: #ffffff;
        font-size: 13px;
        line-height: 1.65;
        text-align: justify;
    }

    .kayit-baslik {
        color: #00e6be;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.7rem 1.5rem 0.7rem !important;
        }

        h1 {
            font-size: 1.65rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
        }

        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.4rem !important;
        }

        [data-testid="stMetric"] {
            width: 100% !important;
        }

        [data-testid="stTabs"] button {
            font-size: 11px !important;
            padding: 8px 5px !important;
        }

        .spk-uyari {
            font-size: 11px;
            padding: 10px;
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


# ==========================================
# DOSYA VE KAYIT AYARLARI
# ==========================================
KAYIT_DOSYASI = "bta_tarihli_kayit_defteri.csv"

KAYIT_SUTUNLARI = [
    "id",
    "tarih",
    "hissedar",
    "hisse_kodu",
    "bta_puani",
    "bta_alim_fiyati",
    "adet"
]

if not os.path.exists(KAYIT_DOSYASI):
    pd.DataFrame(
        columns=KAYIT_SUTUNLARI
    ).to_csv(
        KAYIT_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )


def kayitlari_oku():
    try:
        return pd.read_csv(
            KAYIT_DOSYASI,
            encoding="utf-8-sig"
        )
    except Exception:
        return pd.DataFrame(columns=KAYIT_SUTUNLARI)


def kayit_ekle(
    hissedar,
    hisse_kodu,
    bta_puani,
    bta_alim_fiyati,
    adet
):
    if bta_alim_fiyati <= 0:
        return False

    df_kayitlar = kayitlari_oku()

    yeni_kayit = pd.DataFrame(
        [{
            "id": int(datetime.now().timestamp() * 1000),
            "tarih": datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S"
            ),
            "hissedar": hissedar,
            "hisse_kodu": hisse_kodu.upper(),
            "bta_puani": bta_puani,
            "bta_alim_fiyati": bta_alim_fiyati,
            "adet": adet
        }]
    )

    df_kayitlar = pd.concat(
        [df_kayitlar, yeni_kayit],
        ignore_index=True
    )

    df_kayitlar.to_csv(
        KAYIT_DOSYASI,
        index=False,
        encoding="utf-8-sig"
    )

    return True


# ==========================================
# SPK METNİ
# ==========================================
spk_metni = (
    "SPK YASAL UYARI: Bu platformda yer alan bilgiler yalnızca genel "
    "bilgilendirme amacıyla sunulmaktadır. Buradaki hiçbir veri, yorum, "
    "puan veya fiyat yatırım danışmanlığı, hedef fiyat ya da AL, SAT, "
    "TUT tavsiyesi değildir. Yatırım kararlarınızı kendi araştırmanız "
    "ve yetkili yatırım kuruluşlarıyla görüşerek vermeniz gerekir."
)


# ==========================================
# OTURUM VERİLERİ
# ==========================================
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "id": 1,
            "user": "Sistem",
            "time": datetime.now().strftime("%H:%M:%S"),
            "text": "BTA canlı sohbet odasına hoş geldiniz."
        }
    ]


# ==========================================
# SOL MENÜ
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

admin_pass = st.sidebar.text_input(
    "Yönetici Şifresi",
    type="password"
)

is_admin = admin_pass == "BTA2026"

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
        key="bta_otomatik_yenileme"
    )


# ==========================================
# ANA BAŞLIK
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")

st.markdown(
    "BTA puanı ve BTA alım fiyatı bulunan hisseler takip edilmektedir."
)


# ==========================================
# SEKME MENÜSÜ
# ==========================================
tab_excel, tab_live, tab_register, tab_chat = st.tabs(
    [
        "📂 Excel Analizi",
        "📈 KONYA Canlı Takip",
        "📒 BTA Kayıt Defteri",
        "💬 Canlı Sohbet"
    ]
)


# ==========================================
# EXCEL ANALİZİ
# ==========================================
with tab_excel:
    st.header("📂 BTA Excel Veri Analizi")

    excel_dosyalari = [
        dosya
        for dosya in os.listdir(".")
        if dosya.endswith((".xlsx", ".xlsm"))
    ]

    if not excel_dosyalari:
        st.info("Klasörde Excel dosyası bulunamadı.")
    else:
        secilen_dosya = st.selectbox(
            "Excel dosyası seçin:",
            excel_dosyalari
        )

        try:
            excel_objesi = pd.ExcelFile(
                secilen_dosya,
                engine="openpyxl"
            )

            sayfa = st.selectbox(
                "Çalışma sayfası seçin:",
                excel_objesi.sheet_names
            )

            df_excel = pd.read_excel(
                secilen_dosya,
                sheet_name=sayfa,
                engine="openpyxl"
            )

            if df_excel.empty:
                st.info("Excel sayfası boş.")
            else:
                # None, NONE, NaN ve boş hisse kodlarını temizle
                df_excel = df_excel.dropna(how="all").copy()

                df_excel = df_excel[
                    ~df_excel.astype(str)
                    .apply(
                        lambda satir: satir.str.strip().str.upper().isin(
                            ["NONE", "NAN", "NULL", ""]
                        ).all(),
                        axis=1
                    )
                ]

                arama = st.text_input(
                    "Excel içinde hisse veya isim arayın:"
                )

                if arama:
                    filtre = (
                        df_excel.astype(str)
                        .apply(
                            lambda sutun: sutun.str.contains(
                                arama,
                                case=False,
                                na=False
                            )
                        )
                        .any(axis=1)
                    )

                    df_excel = df_excel[filtre]

                st.dataframe(
                    df_excel,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as hata:
            st.error(f"Excel okunamadı: {hata}")


# ==========================================
# KONYA CANLI TAKİP
# ==========================================
with tab_live:
    st.header("📈 KONYA Canlı Kar/Zarar Takip Paneli")

    sembol = "KONYA.IS"
    bta_alim_fiyati = 4100.00

    try:
        hisse = yf.Ticker(sembol)

        veri = hisse.history(
            period="5d",
            interval="1d"
        )

        if veri.empty:
            st.warning("KONYA için canlı veri bulunamadı.")
        else:
            son_fiyat = float(veri["Close"].iloc[-1])
            kar_zarar = son_fiyat - bta_alim_fiyati
            kar_zarar_yuzde = (
                kar_zarar / bta_alim_fiyati
            ) * 100

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Anlık Fiyat",
                f"{son_fiyat:.2f} TL"
            )

            col2.metric(
                "BTA Alım Fiyatı",
                f"{bta_alim_fiyati:.2f} TL"
            )

            col3.metric(
                "Kar/Zarar",
                f"{kar_zarar_yuzde:.2f}%"
            )

            st.line_chart(
                veri[["Close"]].rename(
                    columns={"Close": "KONYA Fiyatı"}
                )
            )

    except Exception as hata:
        st.error(f"Canlı veri alınamadı: {hata}")


# ==========================================
# BTA TARİHLİ KAYIT DEFTERİ
# ==========================================
with tab_register:
    st.header("📒 BTA Tarihli Kayıt Defteri")

    st.info(
        "Yalnızca BTA alım fiyatı bulunan hisseler kaydedilir. "
        "Kayıtlar tarih ve saat bilgisiyle geçmişte saklanır."
    )

    with st.form(
        "bta_kayit_formu",
        clear_on_submit=True
    ):
        col1, col2 = st.columns(2)

        with col1:
            hissedar = st.text_input(
                "Hissedar Adı",
                placeholder="Örnek: Nurican Bey"
            )

            hisse_kodu = st.text_input(
                "Hisse Kodu",
                placeholder="Örnek: KONYA"
            )

            bta_puani = st.number_input(
                "BTA Puanı",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )

        with col2:
            alim_fiyati = st.number_input(
                "BTA Alım Fiyatı TL",
                min_value=0.0,
                value=0.0,
                step=0.01
            )

            adet = st.number_input(
                "Hisse Adedi",
                min_value=1,
                value=1,
                step=1
            )

        kaydet = st.form_submit_button(
            "Tarihli Kaydı Ekle ✅",
            use_container_width=True
        )

        if kaydet:
            temiz_hisse = hisse_kodu.strip().upper()

            if not hissedar.strip():
                st.error("Hissedar adı boş bırakılamaz.")
            elif not temiz_hisse:
                st.error("Hisse kodu boş bırakılamaz.")
            elif temiz_hisse in ["NONE", "NAN", "NULL"]:
                st.error("Geçersiz hisse kodu.")
            elif alim_fiyati <= 0:
                st.error(
                    "BTA alım fiyatı olmayan hisseler kaydedilemez."
                )
            else:
                kayit_ekle(
                    hissedar=hissedar.strip(),
                    hisse_kodu=temiz_hisse,
                    bta_puani=bta_puani,
                    bta_alim_fiyati=alim_fiyati,
                    adet=adet
                )

                st.success(
                    "✅ Hisse, BTA fiyatı ve puanı ile tarihli "
                    "kayıt defterine eklendi."
                )

                st.rerun()

    st.markdown("---")
    st.subheader("📚 Geçmiş Kayıtlar")

    df_kayitlar = kayitlari_oku()

    if df_kayitlar.empty:
        st.info("Henüz kayıtlı hisse geçmişi bulunmuyor.")
    else:
        # Eski veya hatalı kayıtları gösterme
        df_kayitlar = df_kayitlar[
            df_kayitlar["hisse_kodu"]
            .astype(str)
            .str.strip()
            .str.upper()
            .isin(["NONE", "NAN", "NULL", ""]) == False
        ]

        df_kayitlar = df_kayitlar[
            pd.to_numeric(
                df_kayitlar["bta_alim_fiyati"],
                errors="coerce"
            ).fillna(0) > 0
        ]

        gorunum = df_kayitlar.rename(
            columns={
                "tarih": "Kayıt Tarihi",
                "hissedar": "Hissedar",
                "hisse_kodu": "Hisse Kodu",
                "bta_puani": "BTA Puanı",
                "bta_alim_fiyati": "BTA Alım Fiyatı",
                "adet": "Adet"
            }
        )

        st.dataframe(
            gorunum[
                [
                    "Kayıt Tarihi",
                    "Hissedar",
                    "Hisse Kodu",
                    "BTA Puanı",
                    "BTA Alım Fiyatı",
                    "Adet"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Kayıt Defterini İndir 📥",
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
                "Tüm Kayıtları Sil 🗑️",
                use_container_width=True
            ):
                pd.DataFrame(
                    columns=KAYIT_SUTUNLARI
                ).to_csv(
                    KAYIT_DOSYASI,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success("Tüm kayıtlar silindi.")
                st.rerun()


# ==========================================
# CANLI SOHBET
# ==========================================
with tab_chat:
    st.header("💬 BTA Canlı Sohbet Odası")

    kullanici_adi = st.text_input(
        "Kullanıcı adınız:",
        value="Hissedar"
    )

    with st.form(
        "sohbet_formu",
        clear_on_submit=True
    ):
        mesaj = st.text_input("Mesajınız:")
        gonder = st.form_submit_button("Gönder 🚀")

        if gonder and mesaj.strip():
            st.session_state["chat_messages"].append(
                {
                    "id": int(datetime.now().timestamp() * 1000),
                    "user": kullanici_adi,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": mesaj.strip()
                }
            )

            st.rerun()

    st.subheader("📝 Sohbet Akışı")

    for index, mesaj_data in enumerate(
        reversed(st.session_state["chat_messages"])
    ):
        col1, col2 = st.columns([0.85, 0.15])

        with col1:
            st.markdown(
                f"**[{mesaj_data['time']}] "
                f"{mesaj_data['user']}:** "
                f"{mesaj_data['text']}"
            )

        with col2:
            if is_admin:
                if st.button(
                    "Sil",
                    key=f"mesaj_sil_{mesaj_data['id']}_{index}"
                ):
                    st.session_state["chat_messages"] = [
                        mesaj
                        for mesaj in st.session_state["chat_messages"]
                        if mesaj["id"] != mesaj_data["id"]
                    ]

                    st.rerun()

        st.divider()


# ==========================================
# ALT SPK UYARISI
# ==========================================
st.markdown(
    f"""
    <div class="spk-uyari">
        <strong>⚠️ {spk_metni}</strong>
    </div>
    """,
    unsafe_allow_html=True
)
