import streamlit as st
import yfinance as yf

st.title("📈 Gelişmiş Borsa & Sohbet Paneli")

# 1. Borsa Kısmı
hisse = st.text_input("Hisse Kodu Girin (Örn: THYAO.IS veya AAPL):", "THYAO.IS")
data = yf.Ticker(hisse).history(period="1d")
st.write(f"{hisse} Anlık Fiyatı:", data['Close'].iloc[-1] if not data.empty else "Veri bulunamadı")

# Beğeni (Like) Butonu
if st.button("❤️ Bu Hisseyi Beğen / Takip Listesine Ekle"):
    st.success(f"{hisse} başarıyla beğenildi ve listenize eklendi!")

st.divider()

# 2. Canlı Sohbet Salonu (Chat Room)
st.subheader("💬 Hissedarlar Sohbet Odası")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları listele
for msg in st.session_state.messages:
    st.text(f"👤 {msg['user']}: {msg['text']}")

# Yeni mesaj gönderme
yeni_mesaj = st.text_input("Mesajınızı yazın:")
if st.button("Gönder"):
    st.session_state.messages.append({"user": "Yatırımcı", "text": yeni_mesaj})
    st.rerun()
