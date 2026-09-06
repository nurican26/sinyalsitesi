import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time
import streamlit.components.v1 as components

# 1. Sayfa Yapılandırması ve Modern Koyu Matris Tasarım
st.set_page_config(page_title="BTA Sinyal", page_icon="📈", layout="wide")

st.markdown('''
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 100%)!important; 
        padding: 0.5rem;
    }
    h1,h2,h3,h4,h5,h6,p,span,label {
        color: #fff!important; 
        font-family: "Segoe UI", sans-serif;
    }
    input {
        color: #000!important; 
        background-color: #fff!important;
        border-radius: 6px !important;
    }
    /* Cam Efekti Verilen Giriş Paneli Kutusu */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .stDataFrame {
        width: 100% !important; 
        border: 1px solid #10b981 !important; 
        border-radius: 8px;
    }
    div.block-container {
        padding-top: 1rem; 
        padding-bottom: 0.5rem;
    }
    /* Başlık Grupları */
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #111827 100%); 
        padding: 10px; 
        border-radius: 6px; 
        font-weight: bold; 
        margin-top: 15px;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #111827 100%); 
        padding: 10px; 
        border-radius: 6px; 
        font-weight: bold; 
        margin-top: 25px;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        font-size: 1.25rem !important; 
        font-weight: bold !important; 
        color: #ffffff !important;
    }
    /* Canlı Parlayan Buton Tasarımları */
    div[data-testid="stButton"] button {
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        transition: all 0.3s ease-in-out;
        font-weight: bold !important;
    }
    div[data-testid="stButton"] button:hover {
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.6) !important;
        border-color: #10b981 !important;
        transform: scale(1.02);
    }
</style>
''', unsafe_allow_html=True)

# 🔑 PARAMETRELER VE DOSYA KONTROLLERİ
ZIYARETCI_SIFRESI = "bta3015"
YONETICI_SIFRESI = "3015"
DURUM_DOSYASI = "site_durumu.txt"

if not os.path.exists(DURUM_DOSYASI):
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: 
        f.write("Açık")

with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
    mevcut_kilit = f.read().strip()

# Hafıza Yönetimi
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "ziyaret_sayaci" not in st.session_state: st.session_state["ziyaret_sayaci"] = 0

st.session_state["ziyaret_sayaci"] += 1

# 🟢 ZİKZAKLI DOLANAN NEON YEŞİL BTA LOGO ALANI
bta_zikzak_efekti = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 160px; background: transparent; overflow: hidden; margin-top: 15px; margin-bottom: 15px;">
    <canvas id="btaCanvas" width="800" height="150" style="background: transparent;"></canvas>
</div>

<script>
const canvas = document.getElementById('btaCanvas');
const ctx = canvas.getContext('2d');

let textObj = {
    x: canvas.width / 2,
    y: -30,
    targetY: canvas.height / 2 + 10,
    speedY: 2.2, 
    angle: 0,
    amp: 55, 
    text: "BTA",
    fadedOut: false
};

let particles = [];
const letters = ["B", "T", "A"];

function createParticles(x, y) {
    for (let i = 0; i < 60; i++) {
        let angle = Math.random() * Math.PI * 2;
        let speed = Math.random() * 2 + 0.5; 
        particles.push({
            x: x,
            y: y,
            char: letters[Math.floor(Math.random() * letters.length)],
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            alpha: 1,
            fade: Math.random() * 0.015 + 0.01,
            size: Math.random() * 8 + 18,
            angle: Math.random() * 360,
            rotSpeed: Math.random() * 0.05 - 0.025
        });
    }
}

function drawLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!textObj.fadedOut) {
        textObj.y += textObj.speedY;
        textObj.angle += 0.06; 
        let currentX = (canvas.width / 2) + Math.sin(textObj.angle) * textObj.amp;

        for(let i = 0; i < 5; i++) {
            let trailAlpha = 0.9 - (i * 0.18);
            ctx.fillStyle = `rgba(0, 255, 127, ${trailAlpha})`; 
            ctx.font = "bold 65px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            
            let trailX = (canvas.width / 2) + Math.sin(textObj.angle - (i * 0.25)) * textObj.amp;
            ctx.fillText(textObj.text, trailX, textObj.y - (i * 5));
        }

        if (textObj.y >= textObj.targetY) {
            textObj.fadedOut = true;
            createParticles(currentX, textObj.y);
        }
    } else {
        let activeParticles = 0;
        
        particles.forEach((p) => {
            if (p.alpha > 0) {
                activeParticles++;
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.02; 
                p.alpha -= p.fade;
                p.angle += p.rotSpeed;

                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.angle);
                ctx.fillStyle = `rgba(50, 255, ${Math.floor(Math.random() * 100 + 150)}, ${p.alpha})`;
                ctx.font = `bold ${p.size}px Arial`;
                ctx.textAlign = "center";
                ctx.fillText(p.char, 0, 0);
                ctx.restore();
            }
        });

        if (activeParticles === 0) {
            textObj.y = -30;
            textObj.angle = 0;
            textObj.fadedOut = false;
            particles = [];
        }
    }
    requestAnimationFrame(drawLoop);
}
drawLoop();
</script>
"""
components.html(bta_zikzak_efekti, height=160)

# 🔐 ERİŞİM KONTROLÜ (Görsel Cam Panel İçinde)
st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
st.markdown("### 🔐 Erişim Paneli")
girilen_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")

is_admin = (girilen_sifre == YONETICI_SIFRESI)
if is_admin:
    st.info(f"👑 **Yönetici Girişi Başarılı.** Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

erisim_izni = (mevcut_kilit == "Açık" or girilen_sifre == ZIYARETCI_SIFRESI or girilen_sifre == YONETICI_SIFRESI)

if not erisim_izni:
    st.warning("⚠️ Bu içeriği görebilmek için geçerli bir erişim şifresi girmeniz gerekmektedir.")
st.markdown('</div>', unsafe_allow_html=True)

# 💥 YENİ ENTEGRASYONLU CANLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price, trend = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300: 
            return saved_price, trend
            
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="2d") # Trend tespiti için 2 günlük veri çekiyoruz
        if len(data) >= 2:
            bugun_fiyat = float(data['Close'].iloc[-1])
            dun_fiyat = float(data['Close'].iloc[-2])
            
            # Trend Belirleme Mekanizması
            if bugun_fiyat > dun_fiyat:
                trend = " ▲"  # Yeşil neon yükseliş oku
            elif bugun_fiyat < dun_fiyat:
                trend = " ▼"  # Kırmızı neon düşüş oku
            else:
                trend = " ▬"
                
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), bugun_fiyat, trend)
            return bugun_fiyat, trend
    except:
        pass
    return 0.0, ""

# 🟢 VERİ İŞLEME VE TABLOLAR
if erisim_izni:
    st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; margin-bottom: 20px; font-weight: bold;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)

    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: 
            pass

    tablo_alsat, tablo_al = [], []
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                    wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                    t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                    
                    if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', uv)
                        if h_ara:
                            hisse = str(h_ara[0]) # Kodu bozan liste hatası düzeltildi
                            cfiy, trend_oku = hızlı_canli_fiyat_bul(hisse)
