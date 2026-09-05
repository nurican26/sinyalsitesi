import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# 1. SAYFA YAPILANDIRMASI VE TELEFON UYUMLU SÜPER NEON TASARIM
st.set_page_config(page_title="BTA Canlı Piyasalar", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    @keyframes rainbowNeon {
        0% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f; }
        50% { color: #00f2fe !important; text-shadow: 0 0 15px #00f2fe; }
        100% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f; }
    }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
    } 
    h1, h2, h3, p, span, label {
        color: #fff !important; 
        font-family: "Segoe UI", sans-serif;
    } 
    input {
        color: #000 !important; 
        background-color: #fff !important;
    }
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
        padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 10px;
    } 
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
        padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 10px;
    } 
    .bta-logo-konteyner {
        width: 100%; overflow: hidden; white-space: nowrap;
        margin: 15px 0; padding: 10px 0; background: rgba(255, 255, 255, 0.02); border-radius: 8px;
    } 
    .bta-logo {
        display: inline-block; font-family: 'Segoe UI', sans-serif; font-style: italic;
        font-weight: bold; font-size: 4rem; padding-left: 100%; 
        animation: marquee 20s infinite linear, rainbowNeon 6s infinite linear; 
    } 
    .spk-kutusu {
        background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444;
        padding: 15px; border-radius: 8px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

if "oda_kilitli_mi" not in st.session_state:
    st.session_state["oda_kilitli_mi"] = False
if "sohbet_gecmisi" not in st.session_state:
    st.session_state["sohbet_gecmisi"] = []

# LOGO VE SPK UYARISI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA TRADING</div></div>', unsafe_allow_html=True)
st.markdown("""
<div class="spk-kutusu">
    <h4 style="color:#ef4444 !important; margin-top:0;">⚠️ SPK YASAL UYARI</h4>
    <p style="font-size:0.9rem; color:#cbd5e1 !important; margin-bottom:0;">
        Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
        Burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir.
    </p>
</div>
""", unsafe_allow_html=True)

# YÖNETİCİ PANELİ (SOL YAN MENÜ)
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    if st.sidebar.button("🔓 Odadaki Kilidi Kaldır / Kilitle", use_container_width=True):
        st.session_state["oda_kilitli_mi"] = not st.session_state["oda_kilitli_mi"]
        st.rerun()

# KİLİT KONTROLÜ
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div style="background:rgba(255,255,255,0.05); border-left:4px solid #ca8a04; padding:15px; border-radius:6px;">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Sistem verileri güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
    st.stop()

# ÜST PANEL SEKMELERİ
sekme_arama, sekme_altin, sekme_sohbet = st.tabs(["🔎 TÜM BIST ARAMA MOTORU", "🪙 Canlı Altın Takibi", "💬 Sohbet & Not Alanı"])

with sekme_arama:
    st.markdown("### 🔎 Canlı BIST Tüm Hisse Arama Motoru")
    arama_girdisi = st.text_input("Bulmak istediğiniz hisse kodunu yazın (Örn: THYAO, ASELS, EREGL):", "").strip().upper()
    
    # 🎯 TÜM AKTİF BIST HİSSE LİSTESİ HAFIZASI
    bist_all = [
        "A1CAP", "ACSEL", "ADEL", "ADESE", "AGHOL", "AGROT", "AHGAZ", "AKBNK", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY", "ALARK", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALGGY", "ALKA", "ALKIM", "ALTNY", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ARTMS", "ASCEG", "ASELS", "ASGYO", "ASTOR", "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVTUR", "AYCES", "AYDEM", "AYEN", "AYGAZ", "AZTEK", "BAGFS", "BAKAB", "BALAT", "BANVT", "BARMA", "BASCM", "BASGZ", "BATIS", "BAYRK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENY", "BIGCH", "BIMAS", "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTR", "BOBET", "BORLE", "BORSK", "BOSSA", "BRISA", "BRKVY", "BRMEN", "BRSAN", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "BYDNR", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CEOEM", "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO", "CRDFA", "CUSAN", "CVKMD", "CWENE", "DAGHL", "DAGI", "DAPGM", "DARDL", "DGATE", "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMSAS", "DNISI", "DOAS", "DOCO", "DOGUB", "DOHOL", "DOKTA", "DURDO", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKGYO", "EKIZ", "EKLOS", "EKOS", "ELITE", "EMKEL", "ENERY", "ENJSA", "ENKAI", "EPLAS", "ERBOS", "EREGL", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR", "EUPWR", "EUREK", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FRIGO", "FROTO", "FZLGY", "GARAN", "GENTS", "GEREL", "GESAN", "GIPTA", "GLBMD", "GLCVY", "GLRYH", "GLYHO", "GMTTR", "GNEV", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GSDHO", "GSDDE", "GSRAY", "GUBRF", "GWIND", "GZNMI", "HATEK", "HEDEF", "HEKTS", "HKTM", "HLGYO", "HTTBT", "HUBVC", "HUNER", "HURGZ", "ICBCT", "ICKU", "IDGYO", "IEYHO", "IHAAS", "IHEVA", "IHGZT", "IHLAL", "IHLAS", "IHMAD", "IKND", "IMAGE", "INGRM", "INTEM", "INVEST", "ISATR", "ISBTR", "ISCTR", "ISDMR", "ISFIN", "ISGSY", "ISGYO", "ISKPL", "ISMEN", "ISYAT", "ITTFH", "IZENR", "IZFAS", "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KBTX", "KBUTY", "KCAER", "KCHOL", "KENT", "KERVN", "KERVT", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLMSN", "KLNMA", "KLRGY", "KLSYN", "KLYS", "KMELE", "KMPUR", "KNFRT", "KOBIL", "KONFG", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KPLN", "KPTL", "KRALS", "KRTEK", "KRVGD", "KSTUR", "KTLEV", "KTSKR", "KUTPO", "KUVVA", "KVAZ", "LIDER", "LIDFA", "LINK", "LMKDC", "LOGO", "LRSHO", "LUKSK", "MAALT", "MACKO", "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEPET", "MERCN", "MERIT", "MERKO", "METUR", "METRO", "MGROS", "MIPAZ", "MIATK", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MOGAN", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS", "NIBAS", "NTGAZ", "NUGYO", "NUHCM", "OBAMS", "ODAS", "ODINE", "ONCSM", "ORCA", "ORGE", "ORMA", "OSMEN", "OSTIM", "OTKAR", "OYAKC", "OYAYO", "OYLUM", "OYYAT", "OZATD", "OZGYO", "OZKGY", "OZSUB", "OZUCP", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATRK", "PCILT", "PEGYO", "PEKGY", "PENGD", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKENT", "PKART", "PLTUR", "PNLSN", "PNSUT", "POLHO", "POLTK", "PRKAB", "PRKME", "PRMA", "PRZMA", "PSDTC", "PSGYO", "QNBFB", "QNBFL", "QUAGR", "RALYH", "RAYSG", "REEDR", "RNPOL", "RODRG", "ROYAL", "RYSAS", "RYGYO", "SAFKR", "SAHOL", "SAMAT", "SANEL", "SANFM", "SANKO", "SARKY", "SASA", "SAYAS", "SDTTR", "SEKFA", "SEKO", "SELEC", "SELVA", "SEYKM", "SILVR", "SIMART", "SINKO", "SNGYO", "SNTRA", "SOKMD", "SONME", "SRVGY", "SUWEN", "TABGD", "TAFEX", "TARKM", "TATEN", "TATGD", "TAVHL", "TBORG", "TCELL", "TDGYO", "TEKTU", "TEZOL", "TGSAS", "THYAO", "TLMAN", "TMPOL", "TMSN", "TNZTP", "TOASO", "TORUN", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURGG", "TURSG", "UFUK", "ULAS", "ULFA", "ULKER", "ULUSE", "UNLU", "USAK", "VAKFN", "VAKKO", "VAKMY", "VALF", "VANET", "VBTYZ", "VERTU", "VESTL", "VKFYO", "VKGYO", "VKING", "YAPRK", "YATAS", "YAYLA", "YBCLK", "YEOTK", "YGGYO", "YGYO", "YKBNK", "YLTEK", "YONGA", "YOTK", "YUNSA", "YYLGD", "ZEDUR", "ZRGYO"
    ]
    
    if arama_girdisi:
        if arama_girdisi in bist_all:
            # Tekil hisse sorgusunu en kararlı şekilde yfinance ile indir
            h_data = yf.download(f"{arama_girdisi}.IS", period="1d", progress=False)
            if not h_data.empty:
                c_price = float(h_data['Close'].dropna().iloc[-1])
                st.success(f"📈 **{arama_girdisi}** Hissesi Başarıyla Bulundu!")
                st.metric(label="Anlık Canlı Fiyat (TL)", value=f"{c_price:,.2f} TL")
            else:
                st.error("Fiyat bilgisi şu an Yahoo sunucularından çekilemedi.")
        else:
            # Benzer kodları süzüp göster
            benzerler = [h for h in bist_all if arama_girdisi in h]
            if benzerler:
                st.info(f"Aradığınız koda benzer {len(benzerler)} hisse bulundu: " + ", ".join(benzerler))
            else:
                st.error("Borsa İstanbul listesinde böyle bir hisse kodu bulunamadı!")

with sekme_altin:
    st.markdown("### 🪙 Canlı Altın Piyasası Takibi")
    altin_df_data = pd.DataFrame({"Altın Türü": ["Veri Alınamadı"], "Fiyat (TL)": ["0.00"]})
    try:
        altin_download = yf.download(["GC=F", "TRY=X"], period="1d", progress=False)
        ons_v = float(altin_download['Close']['GC=F'].dropna().iloc[-1])
        usd_v = float(altin_download['Close']['TRY=X'].dropna().iloc[-1])
        g_altin = (ons_v / 31.1034768) * usd_v
        altin_df_data = pd.DataFrame({
            "Altın Türü 🪙": ["Gram Altın", "Çeyrek Altın", "Yarım Altın", "Tam Altın"],
            "Fiyat (TL) 💰": [f"{g_altin:,.2f}", f"{g_altin*1.75:,.2f}", f"{g_altin*3.5:,.2f}", f"{g_altin*7.01:,.2f}"]
        })
    except:
        pass
    st.table(altin_df_data)
