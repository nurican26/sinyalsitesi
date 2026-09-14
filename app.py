import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# Sayfa Genişlik Ayarları (Profesyonel Görünüm İçin Geniş Ekran)
st.set_page_config(page_title="ProStock - Finans & Sosyal Panel", layout="wide", page_icon="📈")

# ──── BAŞLIK VE KULLANICI BİLGİSİ ────
st.title("📈 ProStock Professional Trading & Chat Center")
st.caption("Canlı Veriler, İndikatörler, Hisse Özel Sohbet Odaları ve Sosyal Etkileşim Paneli")

# Sol Menü - Hisse Seçimi ve Portföy Durumu
with st.sidebar:
    st.header("🔍 Piyasa Takibi")
    hisse_turu = st.selectbox("Piyasa Seçin", ["BIST (Borsa İstanbul)", "Kripto Para", "ABD Borsaları"])
    
    if hisse_turu == "BIST (Borsa İstanbul)":
        hisse_kodu = st.text_input("Hisse Kodu (Örn: THYAO.IS, EREGL.IS)", "THYAO.IS")
    elif hisse_turu == "Kripto Para":
        hisse_kodu = st.text_input("Kripto Kodu (Örn: BTC-USD, ETH-USD)", "BTC-USD")
    else:
        hisse_kodu = st.text_input("Hisse Kodu (Örn: AAPL, TSLA)", "AAPL")

    st.divider()
    st.markdown("### 💼 Sanal Portföyüm (Paper Trading)")
    st.metric(label="Toplam Bakiye", value="150,000 TL", delta="+4,250 TL (Bugün)")

# ──── VERİ ÇEKME MOTORU ────
@st.cache_data(ttl=60) # Verileri her 60 saniyede bir günceller, sistemi yormaz
def veri_getir(sembol):
    ticker = yf.Ticker(sembol)
    df = ticker.history(period="1mo", interval="1d")
    info = ticker.info
    return df, info

try:
    df, info = veri_getir(hisse_kodu)
    
    # Ana Ekranı İkiye Bölüyoruz: Sol Taraf Grafikler ve Veri, Sağ Taraf Canlı Chat
    col_grafik, col_sohbet = st.columns([2.2, 1])

    # ──── SOL TARAF: BORSA VE GRAFİK MODÜLÜ ────
    with col_grafik:
        # Canlı Fiyat Kartları
        guncel_fiyat = df['Close'].iloc[-1]
        onceki_fiyat = df['Close'].iloc[-2]
        degisim = ((guncel_fiyat - onceki_fiyat) / onceki_fiyat) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric(label=f"{hisse_kodu} Son Fiyat", value=f"{guncel_fiyat:.2f}", delta=f"{degisim:.2f}%")
        c2.metric(label="En Yüksek (24s)", value=f"{df['High'].iloc[-1]:.2f}")
        c3.metric(label="İşlem Hacmi", value=f"{df['Volume'].iloc[-1]:,}")

        # Gelişmiş Mum (Candlestick) Grafiği
        st.subheader("📊 İnteraktif Teknik Analiz Grafiği")
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name="Mumlar"
        )])
        
        # Hareketli Ortalama İndikatörü (SMA 20) Ekleme
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], mode='lines', name='SMA 20', line=dict(color='orange')))
        
        fig.update_layout(xaxis_rangeslider_visible=False, height=450, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Sosyal Etkileşim (Beğeniler ve Duygu Analizi)
        st.subheader("💬 Topluluk Duygusu (Sentiment)")
        col_like, col_bull, col_bear = st.columns(3)
        
        with col_like:
            if st.button("❤️ Takip Listeme Ekle / Beğen"):
                st.toast(f"{hisse_kodu} favorilerinize eklendi!", icon="❤️")
        with col_bull:
            if st.button("🚀 Boğa (Yükseliş Bekliyorum)"):
                st.success("Yükseliş oyunuz kaydedildi!")
        with col_bear:
            if st.button("🐻 Ayı (Düşüş Bekliyorum)"):
                st.error("Düşüş oyunuz kaydedildi!")

    # ──── SAĞ TARAF: HİSSEYE ÖZEL SOHBET SALONU ────
    with col_sohbet:
        st.subheader(f"💬 {hisse_kodu} Özel Odası")
        st.caption("Sadece bu hisseyi tutanların anlık yazışma alanı")
        
        # Sohbet Geçmişi Hafızası (Gerçek uygulamada veritabanından çekilir)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = {
                hisse_kodu: [
                    {"user": "Ahmet_Trader", "text": "Destek noktasına yaklaştı, buralardan tepki gelebilir.", "time": "19:30"},
                    {"user": "Elif_K", "text": "Hacim çok düştü, bilanço bekleniyor herhalde.", "time": "19:32"}
                ]
            }
        
        if hisse_kodu not in st.session_state.chat_history:
            st.session_state.chat_history[hisse_kodu] = []

        # Mesaj kutusu kutusu ve listeleme arayüzü
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.chat_history[hisse_kodu]:
                st.markdown(f"**👤 {msg['user']}** <span style='font-size:11px; color:gray;'>{msg['time']}</span>", unsafe_allow_html=True)
                st.info(msg['text'])

        # Mesaj Gönderme Formu
        with st.form(key="mesaj_formu", clear_on_submit=True):
            kullanici = st.text_input("Kullanıcı Adınız", value="Yatırımcı_X")
            mesaj_metni = st.text_area("Mesajınız (En fazla 200 karakter)", max_chars=200, height=70)
            gonder_btn = st.form_submit_with_clicks(label="Odaya Gönder")
            
            if gonder_btn and mesaj_metni:
                simdi = datetime.now().strftime("%H:%M")
                st.session_state.chat_history[hisse_kodu].append({
                    "user": kullanici,
                    "text": mesaj_metni,
                    "time": simdi
                })
                st.rerun()

except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu veya geçersiz kod girdiniz. Hata: {e}")
