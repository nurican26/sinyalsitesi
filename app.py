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
    layout="wide"
)


# ==========================================
# ARKA PLAN TASARIMI
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07131f !important;
        background-image:
            linear-gradient(
                rgba(7, 19, 31, 0.86),
                rgba(7, 19, 31, 0.94)
            ),
            url("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=2400&q=85") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: rgba(7, 19, 31, 0.95) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# DOSYA AYARLARI
# ==========================================
KAYIT_DOSYASI = "bta_kayit_defteri.csv"

KAYIT_SUTUNLARI = [
    "id",
    "tarih",
    "hissedar",
    "hisse_kodu",
    "bta_puani",
    "alim_fiyati",
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


# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
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
    alim_fiyati,
    adet
):
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
            "alim_fiyati": alim_fiyati,
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
# YASAL UYARI
# ==========================================
spk_metni = (
    "⚠️ Bu platform yatırım danışmanlığı kapsamında değildir. "
    "Buradaki veriler yalnızca genel bilgilendirme amacıyla sunulmaktadır. "
    "Hiçbir bilgi AL, SAT veya TUT tavsiyesi değildir."
)


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

st.sidebar.markdown("---")
st.sidebar.warning(spk_metni)


# ==========================================
# ANA BAŞLIK
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")
st.warning(spk_metni)


# ==========================================
# SEKME MENÜSÜ
# ==========================================
tab_excel, tab_live, tab_search, tab_register, tab_chat = st.tabs(
    [
        "📂 Excel Analizi",
        "📈 KONYA Canlı Takip",
        "🔎 Borsa Arama Motoru",
        "📒 BTA Kayıt Defteri",
        "💬 Canlı Sohbet"
    ]
)


# ==========================================
# EXCEL ANALİZİ
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri Analizi")

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

            arama = st.text_input(
                "Excel içinde arama yapın:"
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
    alim_fiyati = 4100.00

    try:
        hisse = yf.Ticker(sembol)

        veri = hisse.history(
            period="5d",
            interval="1d"
        )

        if veri.empty:
            st.warning("KONYA için veri bulunamadı.")
        else:
            son_fiyat = float(veri["Close"].iloc[-1])
            kar_zarar = son_fiyat - alim_fiyati
            kar_zarar_yuzde = (
                kar_zarar / alim_fiyati
            ) * 100

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Anlık Fiyat",
                f"{son_fiyat:.2f} TL"
            )

            col2.metric(
                "BTA Alım Fiyatı",
                f"{alim_fiyati:.2f} TL"
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
# BORSA ARAMA MOTORU
# ==========================================
with tab_search:
    st.header("🔎 Canlı Borsa Arama Motoru")

    arama_kodu = st.text_input(
        "Hisse kodunu yazın:",
        placeholder="Örnek: KONYA, THYAO, ASELS"
    )

    ara = st.button(
        "Canlı Veriyi Getir 🔍",
        use_container_width=True
    )

    if ara:
        if not arama_kodu.strip():
            st.warning("Lütfen hisse kodu girin.")
        else:
            aranan_sembol = arama_kodu.strip().upper()

            if not aranan_sembol.endswith(".IS"):
                aranan_sembol += ".IS"

            try:
                hisse = yf.Ticker(aranan_sembol)

                veri = hisse.history(
                    period="1d",
                    interval="1m"
                )

                if veri.empty:
                    veri = hisse.history(
                        period="5d",
                        interval="1d"
                    )

                if veri.empty:
                    st.warning(
                        "Bu hisse için veri bulunamadı."
                    )
                else:
                    son_fiyat = float(
                        veri["Close"].iloc[-1]
                    )

                    if len(veri) > 1:
                        onceki_fiyat = float(
                            veri["Close"].iloc[-2]
                        )

                        fark = son_fiyat - onceki_fiyat
                        fark_yuzde = (
                            fark / onceki_fiyat
                        ) * 100
                    else:
                        fark = 0
                        fark_yuzde = 0

                    st.subheader(
                        f"📊 {aranan_sembol.replace('.IS', '')}"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Anlık Fiyat",
                        f"{son_fiyat:.2f} TL"
                    )

                    col2.metric(
                        "Değişim",
                        f"{fark:.2f} TL",
                        f"{fark_yuzde:.2f}%"
                    )

                    col3.metric(
                        "Güncelleme",
                        datetime.now().strftime(
                            "%H:%M:%S"
                        )
                    )

                    st.subheader("📈 Fiyat Grafiği")

                    grafik = veri[["Close"]].rename(
                        columns={"Close": "Fiyat"}
                    )

                    st.line_chart(grafik)

                    st.subheader("Son Veriler")

                    st.dataframe(
                        veri.tail(20),
                        use_container_width=True
                    )

            except Exception as hata:
                st.error(
                    f"Borsa verisi alınırken hata oluştu: {hata}"
                )


# ==========================================
# BTA KAYIT DEFTERİ
# ==========================================
with tab_register:
    st.header("📒 BTA Hisse Kayıt Defteri")

    st.info(
        "Hisse kodu, BTA puanı, alım fiyatı ve adet "
        "bilgilerini geçmişe dönük kaydedebilirsiniz."
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
            kayit_alim_fiyati = st.number_input(
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
            "KAYDI DEFTERE EKLE ✅",
            use_container_width=True
        )

        if kaydet:
            if not hissedar.strip():
                st.error("Hissedar adı boş bırakılamaz.")
            elif not hisse_kodu.strip():
                st.error("Hisse kodu boş bırakılamaz.")
            elif kayit_alim_fiyati <= 0:
                st.error("Alım fiyatı sıfırdan büyük olmalıdır.")
            else:
                kayit_ekle(
                    hissedar=hissedar.strip(),
                    hisse_kodu=hisse_kodu.strip(),
                    bta_puani=bta_puani,
                    alim_fiyati=kayit_alim_fiyati,
                    adet=adet
                )

                st.success(
                    "✅ BTA kaydı başarıyla oluşturuldu."
                )

                st.rerun()

    st.markdown("---")
    st.subheader("📚 Geçmiş BTA Kayıtları")

    df_kayitlar = kayitlari_oku()

    if df_kayitlar.empty:
        st.info("Henüz kayıtlı geçmiş bulunmuyor.")
    else:
        gorunum = df_kayitlar.rename(
            columns={
                "tarih": "Kayıt Tarihi",
                "hissedar": "Hissedar",
                "hisse_kodu": "Hisse Kodu",
                "bta_puani": "BTA Puanı",
                "alim_fiyati": "BTA Alım Fiyatı",
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

        csv_verisi = df_kayitlar.to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            "Kayıt Defterini İndir 📥",
            data=csv_verisi,
            file_name="bta_kayit_defteri.csv",
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
        mesaj = st.text_input(
            "Mesajınız:"
        )

        gonder = st.form_submit_button(
            "Gönder 🚀"
        )

        if gonder and mesaj.strip():
            st.session_state["chat_messages"].append(
                {
                    "id": int(datetime.now().timestamp() * 1000),
                    "user": kullanici_adi,
                    "time": datetime.now().strftime(
                        "%H:%M:%S"
                    ),
                    "text": mesaj
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
