import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# =====================================================================
# 1. SAYFA YAPILANDIRMASI VE OTOMATİK YENİLEYİCİ (MUTLAKA İLK SIRADA OLMALI)
# =====================================================================
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 10 saniyede bir veya ihtiyacınıza göre yenilenen ana tetikleyici
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")

# =====================================================================
# 2. KUSURSUZ MERKEZLENMİŞ BTA PANELİ (HATA DÜZELTME)
# =====================================================================
st.markdown('''
<style>
/* Streamlit genel arka planı */
.stApp {
    background-color: #0f1115 !important;
}

/* Tüm elemanları kapsayan ve ortalayan ana panel */
.bta-main-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 30px 0;
}

/* Şeffaf, cam efektli merkezi panel */
.bta-container {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 35px;
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 20px !important;
    padding: 25px 45px !important;
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5),
                inset 0 0 20px rgba(255, 255, 255, 0.02) !important;
}

/* Renkli, El Yazısı ve Hafif Gölgeli BTA Logosu */
.bta-logo {
    font-family: 'Brush Script MT', 'Dancing Script', 'Segoe Script', cursive !important;
    font-size: 64px !important;
    font-weight: bold !important;
    background: linear-gradient(45deg, #00d2ff, #3a7bd5) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    filter: drop-shadow(2px 4px 8px rgba(0, 0, 0, 0.7))
            drop-shadow(0 0 15px rgba(0, 210, 255, 0.3)) !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Sağ taraftaki borsa alanı */
.bta-borsa-box {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    border-left: 2px solid rgba(255, 255, 255, 0.1) !important;
    padding-left: 25px !important;
}

.bta-ticker {
    font-family: 'Courier New', monospace !important;
    font-size: 18px !important;
    color: #00e676 !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-weight: bold !important;
    margin: 0 0 5px 0 !important;
}

/* Nabız gibi hafifçe atan borsa oku */
.bta-arrow {
    display: inline-block !important;
    animation: pulseArrow 2s infinite ease-in-out !important;
}

/* Canlı akan grafik çizgisi */
.bta-chart-line {
    width: 100px !important;
    height: 30px !important;
}

.bta-chart-path {
    stroke-dasharray: 100;
    stroke-dashoffset: 100;
    animation: drawLine 3s infinite linear !important;
}

@keyframes pulseArrow {
    0%, 100% { transform: translateY(0); opacity: 0.8; }
    50% { transform: translateY(-3px); opacity: 1; filter: drop-shadow(0 0 4px #00e676); }
}

@keyframes drawLine {
    to { stroke-dashoffset: 0; }
}
</style>

<div class="bta-main-wrapper">
    <div class="bta-container">
        <!-- Sol Taraf: BTA Logosu -->
        <h1 class="bta-logo">BTA</h1>
        
        <!-- Sağ Taraf: Borsa Kutusu -->
        <div class="bta-borsa-box">
            <div class="bta-ticker">
                BIST100 <span class="bta-arrow">▲</span> <span style="font-size:14px; font-weight:normal; color:#aaa;">%1.45</span>
            </div>
            <svg class="bta-chart-line" viewBox="0 0 100 30" fill="none" xmlns="http://w3.org">
                <path class="bta-chart-path" d="M0,25 Q15,5 30,20 T60,10 T90,5 L100,8" stroke="#00e676" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# =====================================================================
# 3. YASAL UYARILAR VE MOTOR ALANI (Kodunuz buradan aşağıya aynen devam ediyor)
# =====================================================================
st.markdown('<p style="color:#ffaa00; font-weight:bold;">⚠ Dikkat: Panel üzerindeki borsa verileri borsa kuralları gereği en az 15 dakika gecikmeli olarak yansıtılmaktadır.</p>', unsafe_allow_html=True)
