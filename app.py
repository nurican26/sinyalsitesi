# ==================================================
# BORSA YÜKSELEN / DÜŞEN HİSSELER
# ==================================================

HAREKET_SUTUNLARI = [
    "Hisse Kodu",
    "Son Fiyat",
    "Önceki Kapanış",
    "Değişim %",
    "Yön"
]


@st.cache_data(ttl=60, show_spinner=False)
def borsa_hareketlerini_getir(hisse_listesi):
    """
    Excel dosyasındaki hisselerin son iki günlük fiyat değişimini hesaplar.
    Veriler en fazla 60 saniyede bir güncellenir.
    """

    if not hisse_listesi:
        return pd.DataFrame(columns=HAREKET_SUTUNLARI)

    sembol_haritasi = {}

    for hisse in hisse_listesi:
        kod = str(hisse).strip().upper()

        if kod in [
            "",
            "NAN",
            "NONE",
            "NULL",
            "NA"
        ]:
            continue

        sembol = kod if kod.endswith(".IS") else f"{kod}.IS"

        gorunum_kodu = kod

        if gorunum_kodu.endswith(".IS"):
            gorunum_kodu = gorunum_kodu[:-3]

        sembol_haritasi[sembol] = gorunum_kodu

    semboller = tuple(sembol_haritasi.keys())

    if not semboller:
        return pd.DataFrame(columns=HAREKET_SUTUNLARI)

    try:
        veri = yf.download(
            tickers=list(semboller),
            period="5d",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
            group_by="column"
        )

        if veri is None or veri.empty:
            return pd.DataFrame(columns=HAREKET_SUTUNLARI)

        # yfinance bazen MultiIndex, bazen normal kolon döndürür
        if isinstance(veri.columns, pd.MultiIndex):
            seviye_0 = list(veri.columns.get_level_values(0))
            seviye_1 = list(veri.columns.get_level_values(1))

            if "Close" in seviye_0:
                kapanislar = veri.xs(
                    "Close",
                    axis=1,
                    level=0
                )
            elif "Close" in seviye_1:
                kapanislar = veri.xs(
                    "Close",
                    axis=1,
                    level=1
                )
            else:
                return pd.DataFrame(columns=HAREKET_SUTUNLARI)

        else:
            if "Close" not in veri.columns:
                return pd.DataFrame(columns=HAREKET_SUTUNLARI)

            kapanislar = veri["Close"]

            if isinstance(kapanislar, pd.Series):
                kapanislar = kapanislar.to_frame(
                    name=semboller[0]
                )

        kapanislar.columns = [
            str(kolon)
            for kolon in kapanislar.columns
        ]

        sonuc_listesi = []

        for sembol in semboller:
            if sembol not in kapanislar.columns:
                continue

            seri = pd.to_numeric(
                kapanislar[sembol],
                errors="coerce"
            ).dropna()

            if len(seri) < 2:
                continue

            onceki_kapanis = float(seri.iloc[-2])
            son_fiyat = float(seri.iloc[-1])

            if onceki_kapanis <= 0:
                continue

            degisim_yuzde = (
                (son_fiyat - onceki_kapanis)
                / onceki_kapanis
            ) * 100

            sonuc_listesi.append(
                {
                    "Hisse Kodu": sembol_haritasi[sembol],
                    "Son Fiyat": son_fiyat,
                    "Önceki Kapanış": onceki_kapanis,
                    "Değişim %": degisim_yuzde,
                    "Yön": (
                        "📈 Yükselen"
                        if degisim_yuzde > 0
                        else "📉 Düşen"
                        if degisim_yuzde < 0
                        else "⏸️ Sabit"
                    )
                }
            )

        if not sonuc_listesi:
            return pd.DataFrame(columns=HAREKET_SUTUNLARI)

        sonuc_df = pd.DataFrame(sonuc_listesi)

        return sonuc_df.sort_values(
            by="Değişim %",
            ascending=False
        ).reset_index(drop=True)

    except Exception:
        return pd.DataFrame(columns=HAREKET_SUTUNLARI)
