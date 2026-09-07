# --- HAREKETLİ BTA LOGOSU VE STYLES (GÖZ YORMAYAN ŞEFFAF PANEL VE BORSA ANİMASYONU) ---
st.markdown('''
<style>
/* Streamlit genel arka planını göz almayan koyu antrasit tonuna çekiyoruz */
.stApp {
    background-color: #0f1115 !important;
}

/* Şeffaf ve hafif ışıklı merkezi logo paneli */
.bta-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 30px;
    background: rgba(255, 255, 255, 0.03); /* Çok hafif şeffaf beyaz */
    backdrop-filter: blur(12px); /* Cam efekti */
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.06); /* Çok ince panel sınırı */
    border-radius: 16px;
    padding: 20px 40px;
    margin: 20px auto;
    max-width: 600px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37),
                inset 0 0 15px rgba(255, 255, 255, 0.02); /* İç derinlik */
}

/* Renkli, El Yazısı ve Gölgeli BTA Logosu */
.bta-logo {
    font-family: 'Brush Script MT', 'Comic Sans MS', 'Dancing Script', cursive;
    font-size: 58px;
    font-weight: bold;
    /* Göz almayan ama renkli geçiş (Yumuşak Turkuaz -> Soft Mavi) */
    background: linear-gradient(45deg, #4facfe, #00f2fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    /* Loş ve göz almayan arka plan ışığı ve gölgesi */
    filter: drop-shadow(2px 4px 6px rgba(0, 0, 0, 0.6))
            drop-shadow(0 0 12px rgba(79, 172, 254, 0.25));
}

/* Logosunun yanındaki hareketli/animasyonlu borsa alanı */
.bta-borsa-box {
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-left: 2px solid rgba(255, 255, 255, 0.1);
    padding-left: 20px;
}

.bta-ticker {
    font-family: monospace;
    font-size: 16px;
    color: #00e676; /* Soft yeşil borsa rengi */
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: bold;
}

/* Nabız gibi hafifçe atan (Göz almayan) yukarı borsa oku animasyonu */
.bta-arrow {
    display: inline-block;
    animation: pulseArrow 2s infinite ease-in-out;
}

/* Canlı akan grafik çizgisi simülasyonu */
.bta-chart-line {
    width: 90px;
    height: 25px;
    margin-top: 5px;
    stroke-dasharray: 100;
    stroke-dashoffset: 100;
    animation: drawLine 4s infinite linear;
}

@keyframes pulseArrow {
    0%, 100% { transform: translateY(0) scale(1); opacity: 0.8; }
    50% { transform: translateY(-3px) scale(1.1); opacity: 1; filter: drop-shadow(0 0 4px #00e676); }
}

@keyframes drawLine {
    to { stroke-dashoffset: 0; }
}
</style>

<div class="bta-container">
    <!-- El Yazısı, Renkli ve Gölgeli Şeffaf BTA Logosu -->
    <div class="bta-logo">BTA</div>
    
    <!-- Yanındaki Animasyonlu Borsa Sayfası Alanı -->
    <div class="bta-borsa-box">
        <div class="bta-ticker">
            BIST100 <span class="bta-arrow">▲</span> <span style="font-size:13px; font-weight:normal; color:#aaa;">%1.45</span>
        </div>
        <!-- Yumuşak hareket eden borsa mini grafik çizgisi -->
        <svg class="bta-chart-line" viewBox="0 0 100 30" fill="none" xmlns="http://w3.org">
            <path d="M0,25 Q15,5 30,20 T60,10 T90,5 L100,8" stroke="#00e676" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
    </div>
</div>
''', unsafe_allow_html=True)

# --- 15 DAKİKA GECİKMELİ VERİ UYARISI VE YASAL UYARI ---
