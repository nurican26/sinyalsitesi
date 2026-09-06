import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time
import streamlit.components.v1 as components  # Efekt için gerekli kütüphane

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 5px; margin-bottom: 5px; width: 100%; height: 180px; position: relative;} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta3015"         # Sadece hisseleri görme yetkisi
YONETICI_SIFRESI = "3015"     # Kilitleyip açma (Yönetici) yetkisi

MESAJ_DOSYASI = "gelen_mesajlar.txt"
DURUM_DOSYASI = "site_durumu.txt"

# 💾 Kalıcı Kilit Durumunu Dosyadan Okuma
if not os.path.exists(DURUM_DOSYASI):
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
        f.write("Açık")

with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
    mevcut_kilit = f.read().strip()

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

# Giriş sayısı her etkileşimde hızlıca yükselmesi için kısıtlama kaldırıldı
st.session_state["ziyaret_sayaci"] += 1


# 🔥 BTA BOMBA DÜŞME VE DAĞILMA ANİMASYONU MOTORU (HTML5 CANVAS)
bta_bomba_efekti = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; background: transparent; overflow: hidden;">
    <canvas id="btaCanvas" width="900" height="180" style="background: transparent;"></canvas>
</div>

<script>
const canvas = document.getElementById('btaCanvas');
const ctx = canvas.getContext('2d');

let bomb = {
    x: canvas.width / 2,
    y: -50,
    targetY: canvas.height / 2 + 20,
    speed: 6,
    text: "BTA",
    exploded: false
};

let particles = [];
const letters = ["B", "T", "A"];

function createParticles(x, y) {
    for (let i = 0; i < 90; i++) {
        let angle = Math.random() * Math.PI * 2;
        let speed = Math.random() * 6 + 2;
        particles.push({
            x: x,
            y: y,
            char: letters[Math.floor(Math.random() * letters.length)],
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed - Math.random() * 2,
            alpha: 1,
            fade: Math.random() * 0.02 + 0.015,
            size: Math.random() * 12 + 16,
            angle: 0,
            rotSpeed: Math.random() * 0.2 - 0.1
        });
    }
}

function drawLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!bomb.exploded) {
        // Bomba Aşağı Düşüyor
        bomb.y += bomb.speed;
        
        // Düşerken arkada bıraktığı kuyruk izi efekti
        for(let i = 0; i < 4; i++) {
            ctx.fillStyle = `rgba(255, 0, 255, ${0.8 - (i * 0.2)})`;
            ctx.font = "bold 65px 'Brush Script MT', 'Comic Sans MS', cursive, sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(bomb.text, bomb.x, bomb.y - (i * 10));
        }

        // Çarpma/Patlama Kontrolü
        if (bomb.y >= bomb.targetY) {
            bomb.exploded = true;
            createParticles(bomb.x, bomb.y);
        }
    } else {
        // Harflerin Dağılma ve Yerçekimi Mekaniği
        let activeParticles = 0;
        
        particles.forEach((p) => {
            if (p.alpha > 0) {
                activeParticles++;
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.12; // Yerçekimi ivmesi
                p.alpha -= p.fade;
                p.angle += p.rotSpeed;

                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.angle);
                // Matris yeşili ile neon pembe/turuncu arası geçişli renk yapısı
                ctx.fillStyle = `rgba(${Math.floor(p.alpha * 255)}, ${Math.floor(Math.random() * 200 + 55)}, 255, ${p.alpha})`;
                ctx.font = `bold ${p.size}px Arial`;
                ctx.textAlign = "center";
                ctx.fillText(p.char, 0, 0);
                ctx.restore();
            }
        });

        // Tüm harfler dağılıp bittiğinde döngüyü yeniden başlat (RESET)
        if (activeParticles === 0) {
            bomb.y = -50;
            bomb.exploded = false;
            particles = [];
        }
    }
    requestAnimationFrame(drawLoop);
}
drawLoop();
</script>
"""

# Eski statik logonun yerine dinamik bomba animasyonunu çağırıyoruz
components.html(bta_bomba_efekti, height=180)


# 🔐 GİRİŞ KUTUSU
st.markdown("### 🔐 Erişim Paneli")
girilen_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")

# 🎛️ BAĞIMSIZ YÖNETİCİ ODASI
is_admin = False
if girilen_sifre == YONETICI_SIFRESI:
    is_admin = True

if is_admin:
    st.info(f"👑 **Yönetici Girişi Başarılı.** Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE (Herkes Şifre Girsin)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

# 🛠️ ERİŞİM KONTROL MANTIĞI
erisim_izni = False
if mevcut_kilit == "Açık" or girilen_sifre == ZIYARETCI_SIFRESI or girilen_sifre == YONETICI_SIFRESI:
    erisim_izni = True
else:
    st.warning("⚠️ Bu içeriği görebilmek için geçerli bir erişim şifresi girmeniz gerekmektedir.")

# 💥 CANLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300: return saved_price
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except: pass
    return 0.0

# 🟢 1. BLOK: ERİŞİM İZNİ VARSA SİTE DETAYLARI VE HİSSELER SORUNSUZ YÜKLENİR
if erisim_izni:
    st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; margin-bottom: 20px; font-weight: bold;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)

    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: pass

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
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                            
                    if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', wv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
