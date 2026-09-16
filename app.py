import os
import hashlib
import html
import xml.etree.ElementTree as ET
import concurrent.futures
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import urllib.parse

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

try:
    from zoneinfo import ZoneInfo
    TURKIYE_TZ = ZoneInfo("Europe/Istanbul")
except Exception:
    # Sunucuda tzdata veritabanı yoksa (bazı minimal Linux
    # kurulumlarında olabilir), sabit UTC+3 ofsetine düşülür.
    # Türkiye 2016'dan beri yaz saati uygulamadığı için bu
    # sabit ofset her zaman doğrudur.
    TURKIYE_TZ = timezone(timedelta(hours=3))


def turkiye_saati():
    """
    Sunucunun çalıştığı saat dilimi ne olursa olsun
    (çoğu bulut sunucusu UTC kullanır), her zaman doğru
    Türkiye saatini (UTC+3) döndürür.
    """
    return datetime.now(TURKIYE_TZ)


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
# KAR YÜZDESI HESAPLA
# ==================================================
def kar_yuzdesi_hesapla(bta_fiyat, anlık_fiyat):
    if bta_fiyat <= 0 or pd.isna(bta_fiyat) or pd.isna(anlık_fiyat):
        return None
    
    kar = ((anlık_fiyat - bta_fiyat) / bta_fiyat) * 100
    return kar


# ==================================================
# KAR YÜZDESI FORMATLAMA
# ==================================================
def kar_yuzdesi_format(kar_yuzde):
    if kar_yuzde is None:
        return "-"
    
    durum = "📈" if kar_yuzde >= 0 else "📉"
    renk = "#00f5c8" if kar_yuzde >= 0 else "#ff5264"
    
    return f"""
    <div style="
        background: rgba(0, 0, 0, 0.3);
        border-left: 4px solid {renk};
        border-radius: 5px;
        padding: 12px;
        margin: 10px 0;
        text-align: center;
    ">
        <div style="font-size: 24px; font-weight: bold; color: {renk};">
            {durum} {kar_yuzde:+.2f}%
        </div>
        <div style="font-size: 12px; color: #999;">
            {'💰 Kar' if kar_yuzde >= 0 else '📊 Zarar'}
        </div>
    </div>
    """


# ==================================================
# BEDELLİ / BEDELSİZ HESAPLAMA
# ==================================================
def bedelli_bedelsiz_hesapla(
    eski_fiyat,
    sahip_lot,
    bedelli_orani,
    bedelli_fiyat,
    bedelsiz_orani
):
    """
    BIST sermaye artırımı (bedelli/bedelsiz) hesaplama makinesi.
    Oranlar yüzde (%) cinsinden girilir (örn. %50 bedelsiz için 50).
    Teorik (düzeltilmiş) fiyat, BIST'in resmi sermaye artırımı
    fiyat düzeltme formülüne göre hesaplanır:

        Teorik Fiyat =
            (Eski Fiyat + (Bedelli Oranı x Bedelli Fiyatı))
            / (1 + Bedelli Oranı + Bedelsiz Oranı)
    """
    try:
        eski_fiyat = float(eski_fiyat)
        sahip_lot = float(sahip_lot)
        bedelli_orani_yuzde = float(bedelli_orani)
        bedelli_fiyat = float(bedelli_fiyat)
        bedelsiz_orani_yuzde = float(bedelsiz_orani)
    except Exception:
        return None

    if eski_fiyat <= 0 or sahip_lot < 0:
        return None

    if bedelli_orani_yuzde < 0 or bedelsiz_orani_yuzde < 0:
        return None

    bedelli_orani = bedelli_orani_yuzde / 100
    bedelsiz_orani = bedelsiz_orani_yuzde / 100

    payda = 1 + bedelli_orani + bedelsiz_orani

    if payda <= 0:
        return None

    # Yeni pay (lot) sayıları - mevcut sahiplik üzerinden
    bedelli_yeni_lot = sahip_lot * bedelli_orani
    bedelsiz_yeni_lot = sahip_lot * bedelsiz_orani
    toplam_yeni_lot = bedelli_yeni_lot + bedelsiz_yeni_lot
    toplam_lot_sonrasi = sahip_lot + toplam_yeni_lot

    # Bedelli hakkının kullanılması için ödenecek tutar
    odenecek_tutar = bedelli_yeni_lot * bedelli_fiyat

    # Teorik (düzeltilmiş) fiyat
    teorik_fiyat = (
        eski_fiyat + (bedelli_orani * bedelli_fiyat)
    ) / payda

    # Portföy değerleri (bedelli tutarı yatırılmış varsayımıyla)
    eski_portfoy_degeri = sahip_lot * eski_fiyat
    yeni_portfoy_degeri = toplam_lot_sonrasi * teorik_fiyat

    fiyat_degisim_yuzde = (
        ((teorik_fiyat - eski_fiyat) / eski_fiyat) * 100
    )

    return {
        "eski_fiyat": eski_fiyat,
        "sahip_lot": sahip_lot,
        "bedelli_yeni_lot": bedelli_yeni_lot,
        "bedelsiz_yeni_lot": bedelsiz_yeni_lot,
        "toplam_yeni_lot": toplam_yeni_lot,
        "toplam_lot_sonrasi": toplam_lot_sonrasi,
        "odenecek_tutar": odenecek_tutar,
        "teorik_fiyat": teorik_fiyat,
        "eski_portfoy_degeri": eski_portfoy_degeri,
        "yeni_portfoy_degeri": yeni_portfoy_degeri,
        "fiyat_degisim_yuzde": fiyat_degisim_yuzde
    }


def bedelli_bedelsiz_kart_format(sonuc):
    if sonuc is None:
        return "-"

    durum = "📉" if sonuc["fiyat_degisim_yuzde"] < 0 else "📈"
    renk = (
        "#ff5264"
        if sonuc["fiyat_degisim_yuzde"] < 0
        else "#00f5c8"
    )

    return f"""
    <div style="
        background: rgba(0, 0, 0, 0.3);
        border-left: 4px solid {renk};
        border-radius: 5px;
        padding: 12px;
        margin: 10px 0;
        text-align: center;
    ">
        <div style="font-size: 13px; color: #999;">
            Teorik (Düzeltilmiş) Fiyat
        </div>
        <div style="font-size: 26px; font-weight: bold; color: {renk};">
            {tl_format(sonuc["teorik_fiyat"])}
        </div>
        <div style="font-size: 13px; color: {renk};">
            {durum} {sonuc["fiyat_degisim_yuzde"]:+.2f}%
        </div>
    </div>
    """


# ==================================================
# TEK SEMBOL İÇİN FİYAT + DEĞİŞİM
# ==================================================
@st.cache_data(ttl=30, show_spinner=False)
def fiyat_degisim_getir(sembol, marj_kontrolu=True):
    """
    Tek bir sembol için son fiyatı ve önceki kapanışa göre değişim
    yüzdesini döndürür.

    Öncelik sırası:
      1) fast_info -> last_price / previous_close
         (borsanın resmi "önceki kapanış" değeri; sermaye artırımı ve
          temettü düzeltmelerini doğru yansıtır)
      2) history() -> son iki kapanış (yedek yöntem)

    marj_kontrolu=True iken BIST'in günlük ±%10 fiyat marjı gözetilir;
    bunun dışında kalan değerler (ör. bedelsiz/temettü kaynaklı veri
    kopukluğu) hatalı kabul edilip elenir. Endeks, döviz ve emtia için
    bu kontrol kapatılmalıdır.

    Hata durumunda (None, None, hata_metni) döner.
    """
    # BIST günlük fiyat marjı %10'dur; veri gürültüsüne
    # küçük bir tolerans bırakılır.
    MARJ_SINIRI = 11.0

    son = None
    onceki = None

    try:
        hisse = yf.Ticker(sembol)

        # ----- 1. YÖNTEM: fast_info -----
        try:
            hizli = hisse.fast_info

            aday_son = getattr(hizli, "last_price", None)
            aday_onceki = getattr(hizli, "previous_close", None)

            if aday_son is None and hasattr(hizli, "get"):
                aday_son = hizli.get("last_price")
            if aday_onceki is None and hasattr(hizli, "get"):
                aday_onceki = hizli.get("previous_close")

            if aday_son and aday_onceki:
                son = float(aday_son)
                onceki = float(aday_onceki)

        except Exception:
            son = None
            onceki = None

        # ----- 2. YÖNTEM (YEDEK): history -----
        if son is None or onceki is None or onceki <= 0:
            gecmis = hisse.history(
                period="5d",
                interval="1d",
                auto_adjust=False
            )

            if (
                gecmis is None
                or gecmis.empty
                or "Close" not in gecmis.columns
            ):
                return None, None, "veri boş döndü"

            kapanislar = gecmis["Close"]

            if pd.isna(kapanislar.iloc[-1]):
                return (
                    None,
                    None,
                    "bugünkü kapanış kaydı henüz yok (anlık veri için fast_info gerekli)"
                )

            kapanislar = kapanislar.dropna()

            if len(kapanislar) < 2:
                return None, None, "yetersiz geçmiş veri"

            onceki = float(kapanislar.iloc[-2])
            son = float(kapanislar.iloc[-1])

        if (
            onceki is None
            or son is None
            or onceki <= 0
            or pd.isna(onceki)
            or pd.isna(son)
        ):
            return None, None, "geçersiz fiyat"

        degisim = ((son - onceki) / onceki) * 100

        if marj_kontrolu and abs(degisim) > MARJ_SINIRI:
            return (
                None,
                None,
                f"marj dışı değişim (%{degisim:.2f}) - "
                "muhtemelen bedelsiz/temettü kaynaklı veri kopukluğu"
            )

        return son, degisim, None

    except Exception as hata:
        return None, None, str(hata)


# ==================================================
# TAVAN KUTLAMA KARTI
# ==================================================
# ==================================================
# HİSSE FİYAT KARTI (GENEL AMAÇLI)
# ==================================================
def hisse_karti_format(hisse_kodu, fiyat, degisim, renk, sira=0):
    durum = "▲" if degisim >= 0 else "▼"

    # Her satırın altına belirgin çizgi (çizgili defter görünümü)
    # ve gözü yormaması için hafif zebra (alternatif) zemin.
    _zemin = (
        "rgba(0, 0, 0, 0.38)"
        if sira % 2 == 0
        else "rgba(255, 255, 255, 0.05)"
    )

    return f"""
    <div style="
        background: {_zemin};
        border-left: 5px solid {renk};
        border-bottom: 1px solid rgba(255, 255, 255, 0.32);
        padding: 11px 16px;
        margin: 0;
        display: grid;
        grid-template-columns: 1fr auto auto;
        align-items: center;
        column-gap: 18px;
    ">
        <span style="
            font-size: 19px;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: {renk};
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.15);
        ">{hisse_kodu}</span>
        <span style="
            font-size: 18px;
            color: #e6e6e6;
            text-align: right;
            min-width: 105px;
        ">{tl_format(fiyat)}</span>
        <span style="
            font-size: 19px;
            font-weight: 700;
            color: {renk};
            text-align: right;
            min-width: 95px;
        ">{durum} {degisim:+.2f}%</span>
    </div>
    """


def sekme_baslik_format(logo, baslik, renk):
    return f"""
    <div class="sekme-baslik" style="border-left-color: {renk};">
        <span class="sb-logo">{logo}</span>
        <span style="color: {renk};">{baslik}</span>
    </div>
    """


def tavan_kutlama_format(hisse_kodu, fiyat, degisim):
    return f"""
    <div style="
        background: linear-gradient(
            120deg,
            rgba(0, 245, 200, 0.22),
            rgba(22, 140, 255, 0.22)
        );
        border: 2px solid #00f5c8;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 0 22px rgba(0, 245, 200, 0.45);
        animation: tavan_parlama 1.6s ease-in-out infinite alternate;
    ">
        <div style="font-size: 26px;">
            🎉 🚀 🥳
        </div>
        <div style="
            font-size: 21px;
            font-weight: 800;
            color: #00f5c8;
            margin-top: 4px;
        ">
            Tebrikler! {hisse_kodu} bugün TAVAN yaptı!
        </div>
        <div style="font-size: 15px; color: #d8fff5; margin-top: 4px;">
            {tl_format(fiyat)} &nbsp;•&nbsp; {degisim:+.2f}%
        </div>
    </div>
    <style>
        @keyframes tavan_parlama {{
            from {{
                box-shadow: 0 0 14px rgba(0, 245, 200, 0.35);
            }}
            to {{
                box-shadow: 0 0 30px rgba(0, 245, 200, 0.75);
            }}
        }}
    </style>
    """


# ==================================================
# PİYASA ÖZETİ (BIST100 / USDTRY / EURTRY / GRAM ALTIN)
# ==================================================
@st.cache_data(ttl=30, show_spinner=False)
def piyasa_ozeti_getir():
    """
    Ana endeks, döviz ve altın kartları için veri toplar.
    Gram Altın (TL), ons altın (USD) fiyatının USDTRY ile çarpılıp
    31.1035 gramlık ons ağırlığına bölünmesiyle yaklaşık hesaplanır.
    """
    sonuclar = []

    bist_son, bist_degisim, bist_hata = fiyat_degisim_getir(
        "XU100.IS",
        marj_kontrolu=False
    )
    sonuclar.append(
        {
            "isim": "BIST100",
            "fiyat": bist_son,
            "degisim": bist_degisim,
            "tur": "sayi",
            "hata": bist_hata
        }
    )

    usd_son, usd_degisim, usd_hata = fiyat_degisim_getir(
        "USDTRY=X",
        marj_kontrolu=False
    )
    sonuclar.append(
        {
            "isim": "USDTRY",
            "fiyat": usd_son,
            "degisim": usd_degisim,
            "tur": "sayi",
            "hata": usd_hata
        }
    )

    eur_son, eur_degisim, eur_hata = fiyat_degisim_getir(
        "EURTRY=X",
        marj_kontrolu=False
    )
    sonuclar.append(
        {
            "isim": "EURTRY",
            "fiyat": eur_son,
            "degisim": eur_degisim,
            "tur": "sayi",
            "hata": eur_hata
        }
    )

    ons_son, ons_degisim, ons_hata = fiyat_degisim_getir(
        "GC=F",
        marj_kontrolu=False
    )

    if ons_son is not None and usd_son is not None:
        gram_fiyat = (ons_son / 31.1035) * usd_son
        gram_degisim = ons_degisim
        gram_hata = None
    else:
        gram_fiyat = None
        gram_degisim = None
        gram_hata = ons_hata or usd_hata or "veri alınamadı"

    sonuclar.append(
        {
            "isim": "GRAM ALTIN (yakl.)",
            "fiyat": gram_fiyat,
            "degisim": gram_degisim,
            "tur": "tl",
            "hata": gram_hata
        }
    )

    # Veri gerçekten bu an çekildiği için zaman damgası da
    # burada, önbelleklenen sonucun içinde üretilir. Böylece
    # ekranda gösterilen saat, sayfanın yenilenme anını değil,
    # verinin GERÇEKTEN çekildiği anı yansıtır.
    cekim_zamani = turkiye_saati().strftime("%d.%m.%Y %H:%M:%S")

    return sonuclar, cekim_zamani


# ==================================================
# SON DAKİKA HABERLERİ (GOOGLE NEWS RSS)
# ==================================================
@st.cache_data(ttl=600, show_spinner=False)
def son_dakika_haberleri_getir():
    """
    Google News ana (gündem) akışından son haberleri getirir.
    SADECE ekonomi değil: TV haberleri ve gündem başlıkları da gelir.
    Yalnızca son 48 saatte yayınlananlar listelenir; eski haberler atlanır.
    """
    try:
        # Google News Türkiye ana gündem akışı (ekonomi + TV + genel)
        url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"

        yanit = requests.get(
            url,
            timeout=12,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            }
        )

        kok = ET.fromstring(yanit.content)
        ogeler = kok.findall(".//item")

        simdi = turkiye_saati()
        sinir_zaman = simdi - timedelta(hours=48)

        haberler = []

        for oge in ogeler:
            baslik = (oge.findtext("title") or "").strip()
            link = (oge.findtext("link") or "").strip()
            yayin = (oge.findtext("pubDate") or "").strip()

            if not baslik:
                continue

            try:
                yayin_zamani = parsedate_to_datetime(
                    yayin
                ).astimezone(TURKIYE_TZ)
            except Exception:
                continue

            # Sadece son 48 saatte yayınlanan haberler
            if yayin_zamani < sinir_zaman:
                continue

            zaman = yayin_zamani.strftime("%H:%M")

            haberler.append(
                (
                    html.escape(baslik),
                    html.escape(link),
                    html.escape(zaman)
                )
            )

            if len(haberler) >= 20:
                break

        return haberler

    except Exception:
        return []


# ==================================================
# GÜNCEL ARZ (HALKA ARZ) HABERLERİ - GOOGLE NEWS ARAMA
# ==================================================
@st.cache_data(ttl=600, show_spinner=False)
def arz_haberleri_getir():
    """
    Google News'te 'halka arz' konulu son haberleri getirir.
    Yalnızca son 48 saatte yayınlananlar listelenir; eski haberler atlanır.
    """
    try:
        # Google News Türkiye "halka arz" arama akışı
        sorgu = urllib.parse.quote_plus(
            '"halka arz" OR "halka arzda" OR "halka arza"'
        )

        url = (
            "https://news.google.com/rss/search?q="
            f"{sorgu}&hl=tr&gl=TR&ceid=TR:tr"
        )

        yanit = requests.get(
            url,
            timeout=12,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            }
        )

        kok = ET.fromstring(yanit.content)
        ogeler = kok.findall(".//item")

        simdi = turkiye_saati()
        sinir_zaman = simdi - timedelta(hours=48)

        haberler = []

        for oge in ogeler:
            baslik = (oge.findtext("title") or "").strip()
            link = (oge.findtext("link") or "").strip()
            yayin = (oge.findtext("pubDate") or "").strip()
            kaynak = (oge.findtext("source") or "").strip()

            if not baslik:
                continue

            try:
                yayin_zamani = parsedate_to_datetime(
                    yayin
                ).astimezone(TURKIYE_TZ)
            except Exception:
                continue

            # Sadece son 48 saatte yayınlanan haberler
            if yayin_zamani < sinir_zaman:
                continue

            zaman = yayin_zamani.strftime("%H:%M")

            haberler.append(
                (
                    html.escape(baslik),
                    html.escape(link),
                    html.escape(zaman),
                    html.escape(kaynak)
                )
            )

            if len(haberler) >= 20:
                break

        return haberler

    except Exception:
        return []
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
        text-align: center;
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
    }

    /* ============================================
       PİYASA ÖZETİ - EKRAN KÖŞESİNDE KOMPAKT KART
       ============================================ */
    .piyasa-ozet-badge {
        background: rgba(5, 18, 32, 0.94);
        border: 1px solid rgba(0, 245, 200, 0.45);
        border-left: 4px solid #00f5c8;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 0 0 14px auto;
        max-width: 460px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.55);
    }

    .piyasa-ozet-badge-header {
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #00f5c8;
        margin-bottom: 6px;
        text-align: right;
    }

    .piyasa-ozet-satir {
        display: grid;
        grid-template-columns: 1fr 105px 72px;
        align-items: center;
        column-gap: 8px;
        padding: 7px 2px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.14);
        font-size: 15px;
        font-weight: 600;
        white-space: nowrap;
    }

    .piyasa-ozet-satir:last-child {
        border-bottom: none;
    }

    .piyasa-ozet-isim {
        color: #eaf4fa;
        font-weight: 700;
        text-align: left;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .piyasa-ozet-fiyat {
        color: #ffffff;
        font-weight: 800;
        font-size: 16px;
        font-variant-numeric: tabular-nums;
        text-align: right;
        letter-spacing: 0.3px;
    }

    .piyasa-ozet-degisim {
        font-weight: 800;
        font-size: 15px;
        font-variant-numeric: tabular-nums;
        text-align: right;
    }

    @media screen and (max-width: 768px) {
        .piyasa-ozet-badge {
            max-width: 100%;
            padding: 6px 10px;
        }

        .piyasa-ozet-satir {
            grid-template-columns: 1fr 92px 66px;
            font-size: 13px;
            padding: 6px 2px;
        }

        .piyasa-ozet-fiyat {
            font-size: 14px;
        }
    }

    /* ============================================
       SON DAKİKA HABERLERİ PANELİ
       ============================================ */
    .son-dakika-baslik {
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(
            90deg,
            rgba(255, 82, 100, 0.18),
            rgba(255, 82, 100, 0.04)
        );
        border: 1px solid rgba(255, 82, 100, 0.55);
        border-radius: 8px;
        padding: 8px 14px;
        margin: 6px 0 0 0;
        font-size: 17px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(255, 82, 100, 0.8);
    }

    .son-dakika-nokta {
        width: 11px;
        height: 11px;
        border-radius: 50%;
        background: #ff3b4e;
        box-shadow: 0 0 12px #ff3b4e;
        animation: son_dakika_yanip_son 1s ease-in-out infinite;
        flex-shrink: 0;
    }

    @keyframes son_dakika_yanip_son {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.25;
        }
    }

    .son-dakika-tarih {
        margin-left: auto;
        font-size: 12px;
        font-weight: 600;
        color: #ff9da8;
    }

    .son-dakika-cerceve {
        background: rgba(6, 20, 33, 0.6);
        border: 1px solid rgba(255, 82, 100, 0.35);
        border-radius: 10px;
        padding: 10px 12px;
        max-height: 380px;
        overflow-y: auto;
        scroll-behavior: smooth;
        margin: 0 0 6px 0;
    }

    .son-dakika-cerceve::-webkit-scrollbar {
        width: 6px;
    }

    .son-dakika-cerceve::-webkit-scrollbar-thumb {
        background: rgba(255, 82, 100, 0.4);
        border-radius: 4px;
    }

    .son-dakika-cerceve::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    .son-dakika-haber-kart {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: #000000;
        border-left: 3px solid #3a3a3a;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 6px 0;
        font-size: 13.5px;
        line-height: 1.45;
        word-break: break-word;
    }

    .son-dakika-haber-saat {
        flex-shrink: 0;
        color: #b0b0b0;
        font-size: 11.5px;
        font-weight: 600;
        padding-top: 2px;
        min-width: 46px;
    }

    .son-dakika-haber-link {
        color: #f2f2f2 !important;
        text-decoration: none;
        font-weight: 600;
        text-shadow: none !important;
    }

    .son-dakika-haber-link:hover {
        color: #ffffff !important;
        text-decoration: underline;
    }

    @media screen and (max-width: 768px) {
        .son-dakika-baslik {
            font-size: 14px;
            padding: 7px 10px;
            gap: 8px;
        }

        .son-dakika-cerceve {
            max-height: 320px;
            padding: 8px 8px;
        }

        .son-dakika-haber-kart {
            font-size: 12.5px;
            padding: 7px 9px;
            gap: 8px;
        }

        .son-dakika-haber-saat {
            font-size: 11px;
            min-width: 42px;
        }
    }

    .mesaj-karti {
        background: rgba(8, 29, 45, 0.95);
        border-left: 3px solid #00f5c8;
        border-radius: 7px;
        padding: 10px;
        margin: 7px 0;
    }

    /* ============================================
       SOHBET - ÇERÇEVE İÇİNDE KAYAN MESAJLAR
       ============================================ */
    .sohbet-cerceve {
        background: rgba(6, 20, 33, 0.6);
        border: 1px solid rgba(0, 245, 200, 0.35);
        border-radius: 10px;
        padding: 10px 12px;
        max-height: 460px;
        overflow-y: auto;
        scroll-behavior: smooth;
        margin-bottom: 10px;
    }

    .sohbet-cerceve::-webkit-scrollbar {
        width: 6px;
    }

    .sohbet-cerceve::-webkit-scrollbar-thumb {
        background: rgba(0, 245, 200, 0.35);
        border-radius: 4px;
    }

    .sohbet-cerceve::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    .sohbet-kart {
        background: rgba(8, 29, 45, 0.97);
        border-left: 3px solid #00f5c8;
        border-radius: 7px;
        padding: 8px 12px;
        margin: 6px 0;
        font-size: 14px;
        word-break: break-word;
    }

    .sohbet-kart-baslik {
        font-size: 13px;
        font-weight: 700;
        color: #ffd166;
        margin-bottom: 2px;
    }

    .sohbet-kart-saat {
        font-size: 11px;
        color: #8aa7bb;
    }

    .sohbet-mesaj-metni {
        color: #f0f0f0;
        line-height: 1.5;
    }

    .sohbet-silme {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 4px;
    }

    .sohbet-sil-buton {
        background: rgba(255, 82, 100, 0.18);
        border: 1px solid rgba(255, 82, 100, 0.5);
        color: #ff8d99;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 11px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }

    .sohbet-sil-buton:hover {
        background: rgba(255, 82, 100, 0.35);
        color: white;
    }

    /* ============================================
       BEĞENİ - ŞEFFAF PARMAK İŞARETİ + (SAYI)
       ============================================ */
    .st-key-bta_begeni_buton {
        background: transparent !important;
        border: 1px solid transparent !important;
        box-shadow: none !important;
        font-size: 26px !important;
        padding: 4px 10px !important;
        color: #00f5c8 !important;
    }

    .st-key-bta_begeni_buton:hover {
        background: rgba(0, 245, 200, 0.12) !important;
        border: 1px solid rgba(0, 245, 200, 0.4) !important;
    }

    .sohbet-begeni-sayi {
        display: flex;
        align-items: center;
        height: 100%;
        font-size: 20px;
        font-weight: 800;
        color: #00f5c8;
        text-shadow: 0 0 8px rgba(0, 245, 200, 0.6);
        padding: 0 4px;
    }

    .sohbet-haber-cerceve .sohbet-kart {
        border-left-color: #ff9f43;
    }

    /* ============================================
       SON HABER BÜLTENİ (büyük ve okunaklı)
       ============================================ */
    .haber-bulteni-baslik {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
        background: linear-gradient(
            90deg,
            rgba(255, 82, 100, 0.22),
            rgba(255, 82, 100, 0.06)
        );
        border: 1px solid rgba(255, 82, 100, 0.6);
        border-radius: 9px;
        padding: 12px 18px;
        margin: 4px 0 12px 0;
        font-size: 17px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 1px;
        text-shadow: 0 0 12px rgba(255, 82, 100, 0.8);
    }

    .haber-bulteni-baslik span {
        font-size: 13px;
        font-weight: 600;
        color: #ff9da8;
    }

    .haber-bulteni-kart {
        background: #000000;
        border-left: 4px solid #3a3a3a;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        padding: 16px 18px;
        margin: 8px 0;
        transition: background 0.3s ease;
    }

    .haber-bulteni-kart:hover {
        background: #141414;
    }

    .haber-bulteni-saat {
        font-size: 14px;
        font-weight: 600;
        color: #b0b0b0;
        margin-bottom: 6px;
    }

    /* GÜNCEL ARZ HABERLERİ - sade */
    .arz-kart {
        border-left-color: #3a3a3a;
    }

    .arz-kaynak {
        color: #b0b0b0;
        font-weight: 600;
    }

    .haber-bulteni-link,
    .haber-bulteni-cerceve .haber-bulteni-link {
        display: block;
        color: #f2f2f2 !important;
        text-decoration: none;
        font-size: 18px;
        font-weight: 600;
        line-height: 1.45;
        word-break: break-word;
        text-shadow: none !important;
    }

    .haber-bulteni-link:hover {
        color: #ffffff !important;
        text-decoration: underline;
    }

    @media screen and (max-width: 768px) {
        .haber-bulteni-baslik {
            font-size: 15px;
            padding: 10px 14px;
        }

        .haber-bulteni-link {
            font-size: 16px;
        }

        .haber-bulteni-kart {
            padding: 13px 14px;
        }
    }

    @media screen and (max-width: 768px) {
        .sohbet-cerceve {
            max-height: 420px;
            padding: 8px 8px;
        }

        .sohbet-kart {
            padding: 7px 10px;
            font-size: 13px;
        }

        .st-key-bta_begeni_buton {
            font-size: 22px !important;
            padding: 4px 8px !important;
        }

        .sohbet-begeni-sayi {
            font-size: 17px;
        }
    }

    .bilgi-karti {
        background: rgba(9, 31, 48, 0.95);
        border: 1px solid rgba(0, 245, 200, 0.35);
        border-radius: 9px;
        padding: 14px;
        margin: 10px 0;
        line-height: 1.8;
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
            font-size: clamp(15px, 6.2vw, 33px);
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

    /* ================================================
       SEKME (TAB) ÇUBUĞU - DAHA BELİRGİN
       ================================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 245, 200, 0.07);
        border: 1px solid rgba(0, 245, 200, 0.35);
        border-radius: 10px;
        padding: 6px 6px 0 6px;
        gap: 4px;
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 800 !important;
        letter-spacing: 0.3px;
        padding: 10px 14px !important;
        white-space: nowrap;
        border-radius: 8px !important;
        margin: 2px 1px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(1),
    .stTabs [data-baseweb="tab"]:first-of-type {
        color: #00f5c8 !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(0, 245, 200, 0.22),
            rgba(0, 245, 200, 0.07)
        ) !important;
        border-color: rgba(0, 245, 200, 0.55) !important;
        text-shadow: 0 0 10px rgba(0, 245, 200, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(2),
    .stTabs [data-baseweb="tab"]:nth-of-type(2) {
        color: #4da6ff !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(77, 166, 255, 0.22),
            rgba(77, 166, 255, 0.07)
        ) !important;
        border-color: rgba(77, 166, 255, 0.55) !important;
        text-shadow: 0 0 10px rgba(77, 166, 255, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(3),
    .stTabs [data-baseweb="tab"]:nth-of-type(3) {
        color: #b48bff !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(180, 139, 255, 0.22),
            rgba(180, 139, 255, 0.07)
        ) !important;
        border-color: rgba(180, 139, 255, 0.55) !important;
        text-shadow: 0 0 10px rgba(180, 139, 255, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(4),
    .stTabs [data-baseweb="tab"]:nth-of-type(4) {
        color: #ff6ec7 !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(255, 110, 199, 0.22),
            rgba(255, 110, 199, 0.07)
        ) !important;
        border-color: rgba(255, 110, 199, 0.55) !important;
        text-shadow: 0 0 10px rgba(255, 110, 199, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(5),
    .stTabs [data-baseweb="tab"]:nth-of-type(5) {
        color: #ff5264 !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(255, 82, 100, 0.22),
            rgba(255, 82, 100, 0.07)
        ) !important;
        border-color: rgba(255, 82, 100, 0.55) !important;
        text-shadow: 0 0 10px rgba(255, 82, 100, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(6),
    .stTabs [data-baseweb="tab"]:nth-of-type(6) {
        color: #ffd166 !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(255, 209, 102, 0.22),
            rgba(255, 209, 102, 0.07)
        ) !important;
        border-color: rgba(255, 209, 102, 0.55) !important;
        text-shadow: 0 0 10px rgba(255, 209, 102, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(7),
    .stTabs [data-baseweb="tab"]:nth-of-type(7) {
        color: #7ddb6e !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(125, 219, 110, 0.22),
            rgba(125, 219, 110, 0.07)
        ) !important;
        border-color: rgba(125, 219, 110, 0.55) !important;
        text-shadow: 0 0 10px rgba(125, 219, 110, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(8),
    .stTabs [data-baseweb="tab"]:nth-of-type(8) {
        color: #ff9f43 !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(255, 159, 67, 0.22),
            rgba(255, 159, 67, 0.07)
        ) !important;
        border-color: rgba(255, 159, 67, 0.55) !important;
        text-shadow: 0 0 10px rgba(255, 159, 67, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] button:nth-of-type(9),
    .stTabs [data-baseweb="tab"]:nth-of-type(9) {
        color: #66d9ff !important;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(102, 217, 255, 0.22),
            rgba(102, 217, 255, 0.07)
        ) !important;
        border-color: rgba(102, 217, 255, 0.55) !important;
        text-shadow: 0 0 10px rgba(102, 217, 255, 0.7);
    }

    .stTabs button[role="tab"][aria-selected="true"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 18px rgba(0, 245, 200, 0.35);
        transform: scale(1.03);
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(1) {
        background: rgba(0, 245, 200, 0.45) !important;
        border-color: #00f5c8 !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(2) {
        background: rgba(77, 166, 255, 0.45) !important;
        border-color: #4da6ff !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(3) {
        background: rgba(180, 139, 255, 0.45) !important;
        border-color: #b48bff !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(4) {
        background: rgba(255, 110, 199, 0.45) !important;
        border-color: #ff6ec7 !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(5) {
        background: rgba(255, 82, 100, 0.45) !important;
        border-color: #ff5264 !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(6) {
        background: rgba(255, 209, 102, 0.45) !important;
        border-color: #ffd166 !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(7) {
        background: rgba(125, 219, 110, 0.45) !important;
        border-color: #7ddb6e !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(8) {
        background: rgba(255, 159, 67, 0.45) !important;
        border-color: #ff9f43 !important;
    }

    .stTabs button[role="tab"][aria-selected="true"]:nth-of-type(9) {
        background: rgba(102, 217, 255, 0.45) !important;
        border-color: #66d9ff !important;
    }

    .stTabs [role="tablist"] [aria-selected="true"] + *::before,
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* SEKMELERİN İÇİNDEKİ BAŞLIK PANKARTLARI - her biri
       kendi logosu ve rengiyle ayırt edilir */
    .sekme-baslik {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 21px;
        font-weight: 800;
        letter-spacing: 0.5px;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 6px 0 14px 0;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-left-width: 6px;
        background: rgba(0, 0, 0, 0.35);
    }

.sekme-baslik .sb-logo {
        font-size: 30px;
    }

    .sekme-baslik .sekme-baslik-tarih {
        font-size: 12px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.75);
        background: rgba(0, 0, 0, 0.35);
        border-radius: 12px;
        padding: 3px 10px;
    }

    /* QR paylaşım kartı - beyaz QR'ın çevresine platform
       kimliği eklenir; telefonla okunabilir durumda kalır */
    .qr-kart {
        background: rgba(5, 18, 32, 0.96);
        border: 1px solid rgba(0, 245, 200, 0.45);
        border-top: 4px solid #00f5c8;
        border-radius: 14px;
        padding: 16px;
        max-width: 360px;
        margin: 0 auto;
        text-align: center;
        box-shadow: 0 6px 22px rgba(0, 0, 0, 0.55);
    }

    .qr-kart-ust {
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #00f5c8;
        margin-bottom: 12px;
    }

    .qr-kart-gorsel {
        background: #ffffff;
        border-radius: 10px;
        padding: 10px;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
        max-width: 100%;
    }

    .qr-kart-gorsel img {
        display: block;
        width: 100%;
        max-width: 240px;
        height: auto;
        border-radius: 4px;
    }

    .qr-kart-link {
        font-size: 13px;
        color: #9bd6ff;
        word-break: break-all;
        margin-top: 12px;
        font-weight: 600;
    }

    .qr-kart-alt {
        font-size: 12px;
        color: #c8d6e2;
        margin-top: 8px;
        line-height: 1.5;
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
                "kayit_tarihi": turkiye_saati().strftime(
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
                turkiye_saati().timestamp() * 1000
            ),
            "tarih": turkiye_saati().strftime(
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
# Not: Sayfa geneli otomatik yenileme (eski st_autorefresh) KALDIRILDI.
# Artık yalnızca canlı bölümler (piyasa kartı, günlük liste, sohbet)
# st.fragment(run_every=...) ile ARKA PLANDA tazelenir; böylece
# sayfanın baştan çizilmesinden (ekranın sönüp yenilenmesinden)
# kaçınılır. Statik içerik (logo, sekmeler, formlar) yerinde kalır.


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
# BTA GÜNLÜK ALGORİTMA - SABİT GÜNCELLEME SAATİ
# ==================================================
BTA_DURUM_DOSYASI = "bta_gunluk_durum.csv"


def bta_gunluk_zaman_yukle():
    """
    "BTA Günlük Algoritma" bölümünün güncelleme saati ve tarihi,
    Excel dosyasının yüklendiği İLK anda bir kez üretilir ve
    'bta_gunluk_durum.csv' dosyasına yazılır. Sayfa her yenilenmede
    bu kaydedilmiş saat yeniden okunur, yani saat/tarih ekranda
    hiçbir yenilemede DEĞİŞMEZ (sabit kalır).
    """
    try:
        if os.path.exists(BTA_DURUM_DOSYASI):
            durum = pd.read_csv(
                BTA_DURUM_DOSYASI,
                encoding="utf-8-sig"
            )

            if not durum.empty and "guncel_zaman" in durum.columns:
                deger = str(durum.iloc[0]["guncel_zaman"]).strip()
                if deger:
                    return deger
    except Exception:
        pass

    zaman = turkiye_saati().strftime("%d.%m.%Y %H:%M:%S")

    try:
        pd.DataFrame(
            [{"guncel_zaman": zaman}]
        ).to_csv(
            BTA_DURUM_DOSYASI,
            index=False,
            encoding="utf-8-sig"
        )
    except Exception:
        pass

    return zaman


# Güncelleme saati sayfanın ilk açılışında oluşturulup sabitlenir.
_bta_gunluk_sabit_zaman = bta_gunluk_zaman_yukle()


# ==================================================
# PİYASA ÖZETİ KARTLARI (BIST100 / USDTRY / EURTRY / GRAM ALTIN)
# EKRANIN SAĞ KÖŞESİNDE KOMPAKT KART
# ==================================================

@st.fragment(run_every=5)
def piyasa_ozeti_fragment():
    """
    Canlı piyasa kartı. Sayfa baştan çizilmeden yalnızca bu kart
    arka planda 5 saniyede bir yenilenir (st.fragment).
    """
    _ozet_veriler, _ozet_zamani = piyasa_ozeti_getir()

    _ozet_satirlar = ""

    for _i, _veri in enumerate(_ozet_veriler):
        _fiyat_metni, _degisim_metni, _renk = _piyasa_ozet_hazirla(_veri)

        _ozet_satirlar += f"""
        <div class="piyasa-ozet-satir">
            <span class="piyasa-ozet-isim">
                {_veri["isim"]}
            </span>
            <span class="piyasa-ozet-fiyat">{_fiyat_metni}</span>
            <span class="piyasa-ozet-degisim" style="color:{_renk};">
                {_degisim_metni}
            </span>
        </div>
        """

    st.markdown(
        f"""
        <div class="piyasa-ozet-badge">
            <div class="piyasa-ozet-badge-header">
                📈 CANLI PİYASA · {_ozet_zamani}
            </div>
            {_ozet_satirlar}
        </div>
        """,
        unsafe_allow_html=True
    )


def _piyasa_ozet_hazirla(_veri):
    if _veri["fiyat"] is None:
        return "-", "--%", "#8aa7bb"

    if _veri["tur"] == "tl":
        _deger = tl_format(_veri["fiyat"])
    else:
        _deger = sayi_format(_veri["fiyat"])

    if _veri["degisim"] is None:
        return _deger, "--%", "#f2f2f2"

    _degisim = f"{_veri['degisim']:+.2f}%"
    _renk = "#00f5c8" if _veri["degisim"] >= 0 else "#ff5264"

    return _deger, _degisim, _renk


piyasa_ozeti_fragment()


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
# B = BTA Günlük Algoritma Hisseleri
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

# BTA klasöründe bazen ESKİ yedek dosyalar da durabilir
# (ör. nurican.xls.xlsm). os.listdir sırası garanti olmadığından
# "bta" ile başlayan dosya ÖNCELİKLİ seçilir; yoksa ilk bulunan alınır.
excel_dosyalari.sort(
    key=lambda _ad: (
        not _ad.lower().startswith("bta"),
        _ad.lower()
    )
)

excel_df = pd.DataFrame(
    columns=[
        "Hisse Kodu",
        "BTA Alım Fiyatı",
        "BTA Puanı"
    ]
)

gunluk_algoritma_df = pd.DataFrame(columns=["Hisse Kodu"])

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

            # ----- B SÜTUNU: BTA Günlük Algoritma hisseleri -----
            if ham_df.shape[1] >= 2:
                gunluk_algoritma_df = ham_df.iloc[:, [1]].copy()

                gunluk_algoritma_df.columns = ["Hisse Kodu"]

                gunluk_algoritma_df["Hisse Kodu"] = (
                    gunluk_algoritma_df["Hisse Kodu"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

                gunluk_algoritma_df = gunluk_algoritma_df[
                    ~gunluk_algoritma_df["Hisse Kodu"].isin(
                        [
                            "", "NONE", "NAN", "NULL", "NA",
                            "BTA AL SAT", "AL SAT",
                            "HİSSE", "HISSE"
                        ]
                    )
                ]

                gunluk_algoritma_df = (
                    gunluk_algoritma_df.drop_duplicates(
                        subset=["Hisse Kodu"],
                        keep="last"
                    )
                )

    except Exception as hata:
        st.error(
            f"Excel okunamadı: {hata}"
        )


# ==================================================
# TAVAN KUTLAMA (BTA TAKİP LİSTESİ)
# ==================================================
if not excel_df.empty:
    _tavan_listesi = []

    def _tek_hisse_tavan_kontrol(_hisse_kodu):
        try:
            _kod = str(_hisse_kodu).strip().upper()

            if not _kod:
                return _hisse_kodu, None, None, "boş hisse kodu"

            _sembol = _kod

            if not _sembol.endswith(".IS"):
                _sembol += ".IS"

            _son, _degisim, _hata = fiyat_degisim_getir(_sembol)
            return _kod, _son, _degisim, _hata

        except Exception as _ic_hata:
            return _hisse_kodu, None, None, str(_ic_hata)

    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=10
        ) as _havuz:
            for _hisse_kodu, _son, _degisim, _hata in _havuz.map(
                _tek_hisse_tavan_kontrol,
                excel_df["Hisse Kodu"].tolist()
            ):
                if (
                    _hata is None
                    and _son is not None
                    and _degisim is not None
                    and _degisim >= 9.0
                ):
                    _tavan_listesi.append(
                        (_hisse_kodu, _son, _degisim)
                    )
    except Exception:
        _tavan_listesi = []

    for _hisse_kodu, _son, _degisim in _tavan_listesi:
        st.markdown(
            tavan_kutlama_format(_hisse_kodu, _son, _degisim),
            unsafe_allow_html=True
        )

    if _tavan_listesi:
        st.divider()


# ==================================================
# PANELLER
# ==================================================
st.markdown(
    """
    <div style="
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        color: #00f5c8;
        margin-bottom: 6px;
    ">
        👇 👉
    </div>
    """,
    unsafe_allow_html=True
)

tab_algoritmik, tab_gunluk, tab_bedelli, tab_sohbet, tab_haber, \
    tab_teknik, tab_arz, tab_kayit, tab_paylas = st.tabs(
        [
            "🤖 Algoritmik Bilgiler",
            "📅 BTA Günlük Algoritma",
            "🧮 Bedelli/Bedelsiz- HESAPLAMA",
            "💬 Sohbet",
            "📰 Haber Bülteni",
            "📊 Teknik Analiz",
            "🚀 Güncel Arz Haberleri",
            "📒 Kayıtlar",
            "🔗 Paylaş"
        ]
    )


# ==================================================
# ALGORİTMİK BİLGİLER
# ==================================================
with tab_algoritmik:
    st.markdown(
        sekme_baslik_format(
            "🤖", "Algoritmik Bilgiler", "#00f5c8"
        ),
        unsafe_allow_html=True
    )

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

            fiyat, degisim_yuzde, hata = fiyat_degisim_getir(
                sembol, marj_kontrolu=False
            )

            onceki_kapanis = bilgi.get(
                "regularMarketPreviousClose"
            )
            if onceki_kapanis is None:
                onceki_kapanis = getattr(
                    hisse.fast_info, "previous_close", None
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

            bta_alim_fiyati = kayit["BTA Alım Fiyatı"]
            kar_yuzde = kar_yuzdesi_hesapla(bta_alim_fiyati, fiyat)

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "BTA Algoritma Fiyatı",
                tl_format(bta_alim_fiyati)
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

            # Kar Yüzdesi Göster
            st.markdown(
                kar_yuzdesi_format(kar_yuzde),
                unsafe_allow_html=True
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
# BTA GÜNLÜK ALGORİTMA (CANLI FİYATLAR)
# ==================================================
with tab_gunluk:
    st.markdown(
        sekme_baslik_format(
            "📅", "BTA Günlük Algoritma", "#4da6ff"
        ),
        unsafe_allow_html=True
    )

    @st.fragment(run_every=5)
    def _gunluk_liste_fragment():
        """Günlük hisse listesi; sayfa titretilmeden 5 sn'de bir
        arka planda güncellenir (st.fragment)."""
        if gunluk_algoritma_df.empty:
            st.info(
                "BTA Günlük Algoritma listesi bulunamadı. "
                "Excel dosyasının B sütununa hisse kodlarını girin."
            )
        else:
            _gunluk_hisseler = [
                str(_h).strip().upper()
                for _h in gunluk_algoritma_df["Hisse Kodu"].tolist()
                if str(_h).strip()
            ]

            def _gunluk_tek_hisse(_hisse_kodu):
                # Ne gelirse gelsin (float, None, NaN vb.) önce
                # güvenli biçimde metne çevrilir; tek bir bozuk
                # satır yüzünden tüm tarama durmasın diye fonksiyon
                # hiçbir zaman hata fırlatmaz, hatayı veri olarak
                # döndürür.
                try:
                    _kod = str(_hisse_kodu).strip().upper()

                    if not _kod:
                        return _hisse_kodu, None, None, "boş hisse kodu"

                    _sembol = _kod

                    if not _sembol.endswith(".IS"):
                        _sembol += ".IS"

                    _son, _degisim, _hata = fiyat_degisim_getir(_sembol)
                    return _kod, _son, _degisim, _hata

                except Exception as _ic_hata:
                    return _hisse_kodu, None, None, str(_ic_hata)

            _gunluk_sonuclar = []
            _gunluk_hatalar = []

            try:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=15
                ) as _gunluk_havuz:
                    for _h, _s, _d, _e in _gunluk_havuz.map(
                        _gunluk_tek_hisse,
                        _gunluk_hisseler
                    ):
                        if _e is not None or _s is None:
                            _gunluk_hatalar.append(f"{_h}: {_e}")
                            continue

                        _gunluk_sonuclar.append((_h, _s, _d))
            except Exception as _hata:
                st.error(f"Veri çekilirken hata oluştu: {_hata}")

            # Güncelleme saati, Excel dosyasının yüklendiği anda bir kez
            # oluşturulur ve bta_gunluk_durum.csv içinde SAKLANIR. Sayfa
            # her yenilenmede ekrandaki saat ve tarih AYNI KALIR.
            _gunluk_zamani = _bta_gunluk_sabit_zaman

            st.markdown(
                f"""
                <div style="
                    display: inline-block;
                    background: rgba(0, 245, 200, 0.12);
                    border: 1px solid rgba(0, 245, 200, 0.4);
                    border-radius: 20px;
                    padding: 5px 14px;
                    margin-bottom: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #00f5c8;
                ">
                    🕒 Algoritmik İşlem  saati: {_gunluk_zamani}
                </div>
                """,
                unsafe_allow_html=True
            )

            if not _gunluk_sonuclar:
                st.info(
                    "Şu anda canlı fiyat alınamadı, birazdan "
                    "tekrar denenecek."
                )
            else:
                # Değişim yüzdesine göre büyükten küçüğe sıralanır
                # (her yenilemede tutarlı şekilde aynı sıralama).
                _gunluk_sonuclar = sorted(
                    _gunluk_sonuclar,
                    key=lambda _oge: _oge[2],
                    reverse=True
                )

                # Ekranda sınırlı genişlikte, ortalanmış tek kolon
                # olarak gösterilir (telefon ekranına da sığar).
                _, _gunluk_orta, _ = st.columns([1, 3, 1])

                with _gunluk_orta:
                    for _sira, (_h, _s, _d) in enumerate(
                        _gunluk_sonuclar
                    ):
                        _renk = "#00f5c8" if _d >= 0 else "#ff5264"

                        st.markdown(
                            hisse_karti_format(
                                _h, _s, _d, _renk, sira=_sira
                            ),
                            unsafe_allow_html=True
                        )

            if _gunluk_hatalar:
                with st.expander(
                    f"⚠️ {len(_gunluk_hatalar)} hisse için "
                    "veri alınamadı"
                ):
                    for _satir in _gunluk_hatalar[:20]:
                        st.code(_satir, language=None)

            st.caption(
                f"Toplam {len(gunluk_algoritma_df)} hisse "
                "izleniyor. Veriler en az 15 dakika gecikmeli "
                "olabilir ve yaklaşık 30 saniyede bir yenilenir."
            )

    _gunluk_liste_fragment()


# ==================================================
# BEDELLİ / BEDELSİZ HESAPLAMA MAKİNESİ
# ==================================================
with tab_bedelli:
    st.markdown(
        sekme_baslik_format(
            "🧮",
            "Bedelli / Bedelsiz Hesaplama Makinesi",
            "#b48bff"
        ),
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="bilgi-karti">
            Sermaye artırımı (bedelli/bedelsiz) sonrası portföyünüzde
            oluşacak <strong>yeni pay sayısını</strong> ve
            <strong>teorik (düzeltilmiş) fiyatı</strong> hesaplayın.
            Oranları hisse için açıklanan sermaye artırımı
            duyurusundaki yüzdelerle girin.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # FİYAT KAYNAĞI SEÇİMİ
    # ==================================================
    hisse_listesi = (
        excel_df["Hisse Kodu"].tolist()
        if not excel_df.empty
        else []
    )

    kaynak_secenekleri = ["✍️ Manuel Fiyat Gir"]

    if hisse_listesi:
        kaynak_secenekleri = [
            "📈 Listeden Hisse Seç (Anlık Fiyat)"
        ] + kaynak_secenekleri

    kaynak = st.radio(
        "Fiyat Kaynağı",
        kaynak_secenekleri,
        horizontal=True
    )

    varsayilan_fiyat = 0.0
    secilen_hisse_bedelli = None

    if kaynak == "📈 Listeden Hisse Seç (Anlık Fiyat)":
        secilen_hisse_bedelli = st.selectbox(
            "🔍 Hisse Seç:",
            hisse_listesi,
            key="bedelli_hisse_secim"
        )

        sembol_bedelli = secilen_hisse_bedelli

        if not sembol_bedelli.endswith(".IS"):
            sembol_bedelli += ".IS"

        try:
            hisse_bedelli = yf.Ticker(sembol_bedelli)
            bilgi_bedelli = hisse_bedelli.info

            varsayilan_fiyat = bilgi_bedelli.get(
                "regularMarketPrice"
            ) or 0.0

            st.caption(
                f"Anlık fiyat otomatik dolduruldu: "
                f"{tl_format(varsayilan_fiyat)} "
                f"(en az 15 dakika gecikmeli olabilir)"
            )

        except Exception as hata:
            st.warning(
                f"Anlık fiyat alınamadı, manuel girebilirsiniz: {hata}"
            )

    st.divider()

    # ==================================================
    # GİRDİ FORMU
    # ==================================================
    col1, col2 = st.columns(2)

    with col1:
        eski_fiyat_girdi = st.number_input(
            "Mevcut / Önceki Kapanış Fiyatı (TL)",
            min_value=0.0,
            value=float(varsayilan_fiyat or 0.0),
            step=0.01,
            format="%.4f"
        )

        sahip_lot_girdi = st.number_input(
            "Sahip Olduğunuz Pay (Lot) Adedi",
            min_value=0.0,
            value=100.0,
            step=1.0
        )

    with col2:
        bedelli_orani_girdi = st.number_input(
            "Bedelli Sermaye Artırım Oranı (%)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            help="Örn. %50 bedelli için 50 girin. Bedelli yoksa 0 bırakın."
        )

        bedelli_fiyat_girdi = st.number_input(
            "Bedelli Pay Alım Fiyatı (TL)",
            min_value=0.0,
            value=1.00,
            step=0.01,
            format="%.4f",
            help="Genellikle nominal değer (1 TL) üzerinden yapılır."
        )

        bedelsiz_orani_girdi = st.number_input(
            "Bedelsiz Sermaye Artırım Oranı (%)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            help="Örn. %20 bedelsiz için 20 girin. Bedelsiz yoksa 0 bırakın."
        )

    st.divider()

    hesapla_buton = st.button(
        "🧮 Hesapla",
        use_container_width=True,
        type="primary"
    )

    # ==================================================
    # NOT: Sayfa 5 saniyede bir otomatik yenilendiği için
    # (st_autorefresh) sonuç "if hesapla_buton:" içinde
    # tutulursa bir sonraki otomatik yenilemede kaybolur.
    # Bu yüzden sonuç, session_state'e yazılıp aşağıda
    # butondan bağımsız olarak her zaman gösterilir.
    # ==================================================
    if hesapla_buton:
        if eski_fiyat_girdi <= 0:
            st.session_state["bedelli_sonuc"] = None
            st.session_state["bedelli_hata"] = (
                "Lütfen geçerli bir mevcut fiyat girin."
            )
        elif bedelli_orani_girdi == 0 and bedelsiz_orani_girdi == 0:
            st.session_state["bedelli_sonuc"] = None
            st.session_state["bedelli_hata"] = (
                "Lütfen bedelli veya bedelsiz oranından "
                "en az birini girin."
            )
        else:
            sonuc = bedelli_bedelsiz_hesapla(
                eski_fiyat_girdi,
                sahip_lot_girdi,
                bedelli_orani_girdi,
                bedelli_fiyat_girdi,
                bedelsiz_orani_girdi
            )

            if sonuc is None:
                st.session_state["bedelli_sonuc"] = None
                st.session_state["bedelli_hata"] = (
                    "Hesaplama yapılamadı, "
                    "girdiğiniz değerleri kontrol edin."
                )
            else:
                st.session_state["bedelli_sonuc"] = sonuc
                st.session_state["bedelli_hata"] = None

    if st.session_state.get("bedelli_hata"):
        st.error(st.session_state["bedelli_hata"])

    sonuc_kalici = st.session_state.get("bedelli_sonuc")

    if sonuc_kalici:
        st.markdown(
            bedelli_bedelsiz_kart_format(sonuc_kalici),
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Bedelli Yeni Pay",
            sayi_format(sonuc_kalici["bedelli_yeni_lot"])
        )

        col2.metric(
            "Bedelsiz Yeni Pay",
            sayi_format(sonuc_kalici["bedelsiz_yeni_lot"])
        )

        col3.metric(
            "Toplam Yeni Pay",
            sayi_format(sonuc_kalici["toplam_yeni_lot"])
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Artırım Sonrası Toplam Pay",
            sayi_format(sonuc_kalici["toplam_lot_sonrasi"])
        )

        col2.metric(
            "Bedelli İçin Ödenecek Tutar",
            tl_format(sonuc_kalici["odenecek_tutar"])
        )

        col3.metric(
            "Fiyat Değişimi",
            f"{sonuc_kalici['fiyat_degisim_yuzde']:+.2f}%"
        )

        st.markdown(
            f"""
            <div class="bilgi-karti">
                <strong>Sermaye Artırımı Öncesi Portföy Değeri:</strong>
                {tl_format(sonuc_kalici["eski_portfoy_degeri"])}<br>
                <strong>Sermaye Artırımı Sonrası Portföy Değeri:</strong>
                {tl_format(sonuc_kalici["yeni_portfoy_degeri"])}<br>
                <strong>Not:</strong> Sonrası değer, bedelli tutarının
                nakit olarak yatırıldığı varsayımıyla hesaplanmıştır.
                Teorik fiyat, borsanın ilan ettiği kesin referans
                fiyattan farklılık gösterebilir.
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "✖️ Sonucu Temizle",
            use_container_width=True,
            key="bedelli_sonuc_temizle"
        ):
            st.session_state["bedelli_sonuc"] = None
            st.session_state["bedelli_hata"] = None
            st.rerun()


# ==================================================
# CANLI SOHBET
# ==================================================
with tab_sohbet:
    st.markdown(
        sekme_baslik_format(
            "💬", "Sohbet", "#ff6ec7"
        ),
        unsafe_allow_html=True
    )

    @st.fragment(run_every=5)
    def _sohbet_fragment():
        """Beğeni butonu, mesaj formu ve mesaj listesi. Tıklama veya
        yeni mesaj geldiğinde yalnızca bu bölüm arka planda yenilenir;
        sayfa baştan çizilip ekran sönmez."""
        takip, begeni = istatistik_oku()

        # ============================================
        # BEĞENİ BUTONU (şeffaf 👍 + sayı)
        # ============================================
        kol_begeni, kol_sayi = st.columns([1, 6])

        with kol_begeni:
            if st.button(
                "👍",
                key="bta_begeni_buton",
                help="Beğen",
                use_container_width=False
            ):
                begeni += 1
                istatistik_kaydet(takip, begeni)
                st.rerun(scope="fragment")

        with kol_sayi:
            st.markdown(
                f"""
                <div class="sohbet-begeni-sayi">
                    ({begeni})
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # ============================================
        # MESAJ FORMU (MESAJ GÖNDERME ALANI ÜSTTE DURUR)
        # ============================================
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

                    st.rerun(scope="fragment")

        st.divider()

        # ============================================
        # MESAJ LİSTESİ
        # ============================================
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
            # Aynı kullanıcı hep aynı rengi alır; farklı
            # kullanıcılar birbirinden ayrılır. (Sonlu ve sabit
            # karma için std hash değil, karakter toplamı kullanılır.)
            _kullanici_palet = [
                "#00f5c8", "#4da6ff", "#b48bff",
                "#ff6ec7", "#ffd166", "#ff9f43", "#7ddb6e"
            ]

            # En yeni mesaj en üstte olacak şekilde sıralanır.
            # Silme, tarayıcı "kopyala" menüsü açan ?bta_sil linki
            # yerine gerçek bir Streamlit butonu ile yapılır; böylece
            # mobilde dokununca sayfa kaybolmaz, mesaj doğrudan silinir.
            for index, satir in mesajlar.iloc[::-1].iterrows():
                _mesaj_id = str(satir["mesaj_id"])
                _kullanici = html.escape(str(satir["kullanici"]))
                _mesaj_metni = html.escape(
                    str(satir["mesaj"])
                ).replace("\n", "<br>")

                _kc = (
                    sum(_kullanici.encode("utf-8"))
                    % len(_kullanici_palet)
                )
                _kenar_renk = _kullanici_palet[_kc]

                _kart_html = f"""
                <div class="sohbet-kart"
                     style="border-left-color: {_kenar_renk};">
                    <div class="sohbet-kart-baslik"
                         style="color: {_kenar_renk};">
                        👤 {_kullanici}
                        <span class="sohbet-kart-saat">
                            · {html.escape(str(satir["tarih"]))}
                        </span>
                    </div>
                    <div class="sohbet-mesaj-metni">
                        {_mesaj_metni}
                    </div>
                </div>
                """

                if is_admin:
                    _kart_kol, _sil_kol = st.columns([5, 1])

                    with _kart_kol:
                        st.markdown(
                            _kart_html,
                            unsafe_allow_html=True
                        )

                    with _sil_kol:
                        st.write("")
                        if st.button(
                            "🗑️",
                            key=f"bta_mesaj_sil_{_mesaj_id}",
                            help="Bu mesajı sil",
                            use_container_width=True
                        ):
                            _kalan = mesajlari_oku()
                            _kalan = _kalan[
                                _kalan["mesaj_id"].astype(str)
                                != _mesaj_id
                            ]
                            _kalan.to_csv(
                                MESAJ_DOSYASI,
                                index=False,
                                encoding="utf-8-sig"
                            )
                            st.rerun(scope="fragment")
                else:
                    st.markdown(
                        _kart_html,
                        unsafe_allow_html=True
                    )

    _sohbet_fragment()


# ==================================================
# SON HABER BÜLTENİ (bugünün gündemi, büyük ve okunaklı)
# ==================================================
with tab_haber:
    _haberler = son_dakika_haberleri_getir()

    st.markdown(
        f"""
        <div class="sekme-baslik" style="
            border-left-color: #ff5264;
            border-color: #ff5264;
            background: linear-gradient(
                90deg,
                rgba(255, 82, 100, 0.22),
                rgba(255, 82, 100, 0.06)
            );
            box-shadow: 0 0 18px rgba(255, 82, 100, 0.3);
        ">
            <span class="sb-logo">🔴</span>
            <span style="color: #ff5264;
                         text-shadow: 0 0 14px rgba(255, 82, 100, 0.8);">
                SON HABER BÜLTENİ
            </span>
            <span class="sekme-baslik-tarih">Son 48 Saat</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not _haberler:
        st.info(
            "Şu anda habere ulaşılamadı, birazdan "
            "tekrar deneniyor."
        )
    else:
        _haber_renkleri = [
            "#00f5c8", "#4da6ff", "#b48bff",
            "#ff6ec7", "#ffd166", "#ff9f43", "#7ddb6e"
        ]

        for _baslik, _link, _zaman in _haberler:
            st.markdown(
                f"""
                <div class="haber-bulteni-kart">
                    <div class="haber-bulteni-saat">
                        🕒 {_zaman}
                    </div>
                    <a href="{_link}" target="_blank"
                       class="haber-bulteni-link">
                        {_baslik}
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "Haberler Google News gündem akışından alınır; "
        "yalnızca bugün yayınlananlar listelenir. "
        "Başlığa dokunarak haber kaynağına gidebilirsiniz."
    )


# ==================================================
# TEKNİK ANALİZ - GRAFİK VE İNDİKATÖRLER
# ==================================================
with tab_teknik:
    st.markdown(
        sekme_baslik_format(
            "📊", "Teknik Analiz Grafikleri", "#ffd166"
        ),
        unsafe_allow_html=True
    )

    st.caption(
        "BIST hisseleri için sembolün sonuna .IS ekleyin "
        "(ör. THYAO.IS). Yabancı borsalar için ör. AAPL, "
        "EURUSD=X, BTC-USD kullanabilirsiniz."
    )

    col_sembol, col_periyot = st.columns([3, 1])

    with col_sembol:
        sembol = st.text_input(
            "Sembol",
            value="THYAO.IS",
            key="teknik_sembol"
        ).strip().upper()

    with col_periyot:
        periyot = st.selectbox(
            "Periyot",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            key="teknik_periyot"
        )

    analiz_buton = st.button(
        "📈 Grafiği Çiz",
        use_container_width=True,
        key="teknik_analiz_buton"
    )

    if analiz_buton and not sembol:
        st.error("Lütfen bir sembol girin.")

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np

    def teknik_veri_cek(sembol, periyot):
        """yfinance ile OHLCV verisini çeker."""
        import yfinance as yf

        veri = yf.Ticker(sembol).history(
            period=periyot,
            interval="1d",
            auto_adjust=True
        )

        if veri.empty:
            raise ValueError("Veri bulunamadı.")

        return veri

    def teknik_indikatorler(veri):
        """SMA/EMA/RSI/MACD indikatörlerini hesaplar."""
        if "Close" not in veri:
            return veri

        kapanis = veri["Close"]

        # Basit ve üstel hareketli ortalamalar
        veri["SMA20"] = kapanis.rolling(20).mean()
        veri["SMA50"] = kapanis.rolling(50).mean()
        veri["EMA12"] = kapanis.ewm(span=12).mean()
        veri["EMA26"] = kapanis.ewm(span=26).mean()

        # MACD ve sinyal çizgisi
        veri["MACD"] = veri["EMA12"] - veri["EMA26"]
        veri["MACD_SINYAL"] = veri["MACD"].ewm(span=9).mean()

        # RSI (14)
        delta = kapanis.diff()
        kazanc = delta.clip(lower=0)
        kayip = -delta.clip(upper=0)
        ort_kazanc = kazanc.ewm(alpha=1 / 14).mean()
        ort_kayip = kayip.ewm(alpha=1 / 14).mean()
        rs = ort_kazanc / ort_kayip.replace(0, np.nan)
        veri["RSI"] = 100 - (100 / (1 + rs))

        return veri

    if analiz_buton and sembol:
        try:
            with st.spinner("Veri çekiliyor, grafik hazırlanıyor..."):
                ham_veri = teknik_veri_cek(sembol, periyot)
                grafik_veri = teknik_indikatorler(ham_veri)

            # Alt grafikler: fiyat + MACD + RSI
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.06,
                row_heights=[0.55, 0.2, 0.25],
                subplot_titles=(
                    f"{sembol} · {periyot}",
                    "MACD (12,26,9)",
                    "RSI (14)"
                )
            )

            fig.add_trace(
                go.Candlestick(
                    x=grafik_veri.index,
                    open=grafik_veri["Open"],
                    high=grafik_veri["High"],
                    low=grafik_veri["Low"],
                    close=grafik_veri["Close"],
                    name="Fiyat",
                    increasing_line_color="#00f5c8",
                    decreasing_line_color="#ff5264"
                ),
                row=1, col=1
            )

            for _cizgi, _renk, _ad in [
                ("SMA20", "#4da6ff", "SMA20"),
                ("SMA50", "#b48bff", "SMA50")
            ]:
                fig.add_trace(
                    go.Scatter(
                        x=grafik_veri.index,
                        y=grafik_veri[_cizgi],
                        mode="lines",
                        line=dict(width=1.2, color=_renk),
                        name=_ad
                    ),
                    row=1, col=1
                )

            fig.add_trace(
                go.Bar(
                    x=grafik_veri.index,
                    y=grafik_veri["Volume"],
                    name="Hacim",
                    marker_color="rgba(0,245,200,0.35)"
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=grafik_veri.index,
                    y=grafik_veri["MACD"],
                    mode="lines",
                    line=dict(width=1.4, color="#00f5c8"),
                    name="MACD"
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=grafik_veri.index,
                    y=grafik_veri["MACD_SINYAL"],
                    mode="lines",
                    line=dict(width=1.2, color="#ff9f43"),
                    name="Sinyal"
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=grafik_veri.index,
                    y=grafik_veri["RSI"],
                    mode="lines",
                    line=dict(width=1.4, color="#b48bff"),
                    name="RSI"
                ),
                row=3, col=1
            )

            fig.add_hline(y=70, line_dash="dash",
                          line_color="#ff5264", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash",
                          line_color="#00f5c8", row=3, col=1)

            fig.update_layout(
                height=780,
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#eaf4fa"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=10, r=10, t=45, b=10)
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

            # Son değer özeti
            son = grafik_veri.dropna().iloc[-1]

            _son_fiyat = f"{son['Close']:.2f}"

            _degisim = (
                (son["Close"] / grafik_veri["Close"].iloc[-2] - 1)
                * 100
            )

            _ok = "🟢" if _degisim >= 0 else "🔴"

            col_o1, col_o2, col_o3 = st.columns(3)

            col_o1.metric("Son Fiyat", _son_fiyat,
                          f"{_ok} {_degisim:+.2f}%")

            _rsi_deger = (
                f"{son['RSI']:.1f}"
                if pd.notna(son.get("RSI"))
                else "-"
            )
            col_o2.metric("RSI (14)", _rsi_deger)

            _macd_deger = (
                f"{son['MACD']:.3f}"
                if pd.notna(son.get("MACD"))
                else "-"
            )
            col_o3.metric("MACD", _macd_deger)

        except Exception as _hata:
            st.error(
                f"Veri alınamadı: {_hata}. Sembolü kontrol edin "
                "(ör. THYAO.IS, GARAN.IS, AAPL)."
            )

    st.caption(
        "Veriler yFinance'ten alınır; yatırım tavsiyesi değildir. "
        "SMA20/SMA50, MACD ve RSI göstergeleri bilgilendirme amaçlıdır."
    )


# ==================================================
# GÜNCEL ARZ (HALKA ARZ) HABERLERİ
# ==================================================
with tab_arz:
    _arz_haberler = arz_haberleri_getir()

    st.markdown(
        f"""
        <div class="sekme-baslik" style="
            border-left-color: #7ddb6e;
            border-color: #7ddb6e;
            background: linear-gradient(
                90deg,
                rgba(125, 219, 110, 0.22),
                rgba(125, 219, 110, 0.06)
            );
            box-shadow: 0 0 18px rgba(125, 219, 110, 0.3);
        ">
            <span class="sb-logo">🚀</span>
            <span style="color: #7ddb6e;
                         text-shadow: 0 0 14px rgba(125, 219, 110, 0.8);">
                GÜNCEL ARZ HABERLERİ
            </span>
            <span class="sekme-baslik-tarih">Son 48 Saat</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not _arz_haberler:
        st.info(
            "Şu anda halka arz haberi bulunamadı, birazdan "
            "tekrar deneniyor."
        )
    else:
        for (
            _baslik, _link, _zaman, _kaynak
        ) in _arz_haberler:
            st.markdown(
                f"""
                <div class="haber-bulteni-kart arz-kart">
                    <div class="haber-bulteni-saat">
                        🕒 {_zaman}
                        <span class="arz-kaynak">
                            · {_kaynak or "Haber"}
                        </span>
                    </div>
                    <a href="{_link}" target="_blank"
                       class="haber-bulteni-link">
                        {_baslik}
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "Halka arz haberleri Google News arama akışından alınır; "
        "yatırım tavsiyesi değildir. Başlığa dokunarak kaynağa gidebilirsiniz."
    )


# ==================================================
# TARİHLİ KAYITLAR
# ==================================================
with tab_kayit:
    st.markdown(
        sekme_baslik_format(
            "📒", "Tarihli Kayıt Defteri", "#ffd166"
        ),
        unsafe_allow_html=True
    )

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
                    if st.confirm("Emin misiniz?"):
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
    st.markdown(
        sekme_baslik_format(
            "🔗", "Sayfayı Sosyal Medyada Paylaş", "#ff9f43"
        ),
        unsafe_allow_html=True
    )

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
    # QR KOD - NORMAL (SİYAH-BEYAZ), KART GÖRÜNÜMLÜ
    # ==================================================
    st.subheader("📱 QR Kod ile Hızlı Erişim")

    try:
        import io
        import base64
        import qrcode

        # Telefon kamerasının okuyabilmesi için QR her zaman
        # SİYAH kareler + BEYAZ zemin olmalıdır. Önceki renkli
        # (turkuaz/koyu lacivert) sürüm telefonlarda okunmuyordu.
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(sayfa_url)
        qr.make(fit=True)

        qr_img = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        _qr_buf = io.BytesIO()
        qr_img.save(_qr_buf, format="PNG")
        _qr_b64 = (
            base64.b64encode(
                _qr_buf.getvalue()
            ).decode("utf-8")
        )

        st.markdown(
            f"""
            <div class="qr-kart">
                <div class="qr-kart-ust">
                    📱 BTA Platform · Hızlı Erişim
                </div>
                <div class="qr-kart-gorsel">
                    <img src="data:image/png;base64,{_qr_b64}"
                         alt="BTA QR kodu" />
                </div>
                <div class="qr-kart-link">
                    🔗 {sayfa_url}
                </div>
                <div class="qr-kart-alt">
                    Kameranızla okutup paylaşın · Basıp
                    arkadaşınıza gösterebilirsiniz
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    except ImportError:
        st.info("QR kod göstermek için: pip install qrcode[pil]")

    st.divider()

    # ==================================================
    # İSTATİSTİKLER
    # ==================================================
    st.subheader("📊 Platform İstatistikleri")

    begeni = istatistik_oku()[1]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("👍 Beğeniler", begeni)

    with col2:
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
