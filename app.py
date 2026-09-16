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

            aday_son = (
                hizli.get("last_price")
                if hasattr(hizli, "get")
                else getattr(hizli, "last_price", None)
            )
            aday_onceki = (
                hizli.get("previous_close")
                if hasattr(hizli, "get")
                else getattr(hizli, "previous_close", None)
            )

            if aday_son and aday_onceki:
                son = float(aday_son)
                onceki = float(aday_onceki)

        except Exception:
            son = None
            onceki = None

