 import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# =====================================================================
# 1. SAYFA YAPILANDIRMASI VE OTOMATİK YENİLEYİCİ
# =====================================================================
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 10 saniyede bir veya ihtiyacınıza göre yenilenen ana tetikleyici
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")

# Arka plan rengini sabitlemek için en güvenli arka plan CSS'i
st.markdown('<style>.stApp { background-color: #0f1115 !important; }</style>', unsafe_allow_html=True)

# =====================================================================
# 2. İZOLE EDİLMİŞ ŞEFFAF BTA LOGO VE ANIMASYON PANELİ (GÜVENLİ MİMARİ)
# =====================================================================
logo_html = """
<div style="
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
">
    <!-- Merkezi Şeffaf Cam Panel -->
    <div style="
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 20px 40px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.01);
    ">
        <!-- Sol Taraf: El Yazısı, Gölgeli BTA Logosu -->
        <h1 style="
            font-family: 'Brush Script MT', 'Dancing Script', 'Segoe Script', cursive;
            font-size: 56px;
            font-weight: bold;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(2px 4px 6px rgba(0, 0, 0, 0.7)) drop-shadow(0 0 12px rgba(0, 210, 255, 0.25));
            margin: 0;
            padding: 0;
            line-height: 1;
        ">BTA</h1>
        
        <!-- Sağ Taraf: Animasyonlu Borsa Kutusu -->
        <div style="
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 2px solid rgba(255, 255, 255, 0.1);
            padding-left: 25px;
        ">
            <div style="
                font-family: 'Courier New', monospace;
                font-size: 17px;
                color: #00e676;
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: bold;
                margin: 0 0 5px 0;
            ">
                BIST100 
                <span style="
                    display: inline-block;
                    animation: pulseArrow 2s infinite ease-in-out;
                ">▲</span> 
                <span style="font-size: 13px; font-weight: normal; color: #aaa;">%1.45</span>
            </div>
            
            <!-- Canlı Akan Grafik Çizgisi -->
            <svg style="width: 100px; height: 25px;" viewBox="0 0 100 30" fill="none" xmlns="http://w3.org">
                <path d="M0,25 Q15,5 30,20 T60,10 T90,5 L100,8" stroke="#00e676" stroke-width="2.5" stroke-linecap="round" 
                      style="stroke-dasharray: 100; stroke-dashoffset: 100; animation: drawLine 3s infinite linear;"/>
            </svg>
        </div>
    </div>
</div>

<style>
@keyframes pulseArrow {
    0%, 100% { transform: translateY(0); opacity: 0.8; }
    50% { transform: translateY(-3px); opacity: 1; filter: drop-shadow(0 0 3px #00e676); }
}
@keyframes drawLine {
    to { stroke-dashoffset: 0; }
}
</style>
"""

# HTML bileşenini güvenli bir şekilde ekrana basıyoruz (Yüksekliği panel kadar ayarlandı)
components.html(logo_html, height=140)

# --- 15 DAKİKA GECİKMELİ VERİ UYARISI VE YASAL UYARI ---
st.markdown('<p style="color:#ffaa00; font-weight:bold; margin-top:20px;">⚠ Dikkat: Panel üzerindeki borsa verileri borsa kuralları gereği en az 15 dakika gecikmeli olarak yansıtılmaktadır.</p>', unsafe_allow_html=True)
