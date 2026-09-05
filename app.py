    "YAPRK", "YATAS", "YAYLA", "YBCLK", "YEOTK", "YGGYO", "YGYO", "YKBNK", "YLTEK"
]

# =========================================================================
# SEKME 1: 🔎 TÜM BIST ARAMA MOTORU
# =========================================================================
with sekme_arama:
    st.markdown("<div class='alsat-baslik'>🔍 BIST Hisse Analiz ve Veri Sorgulama</div>", unsafe_allow_html=True)
    
    # Kullanıcıdan hisse kodu seçimi (Telefon uyumlu arama kutusu)
    secilen_hisse = st.selectbox("Analiz etmek istediğiniz BIST hissesini seçin veya yazın:", bist_all, index=0)
    
    if secilen_hisse:
        # yfinance için BIST uzantısı (.IS) ekleniyor
        ticker_kod = f"{secilen_hisse}.IS"
        
        try:
            hisse_data = yf.Ticker(ticker_kod)
            # Son 1 aylık veriyi çekelim
            gecmis_veri = hisse_data.history(period="1mo")
            
            if not gecmis_veri.empty:
                son_fiyat = gecmis_veri['Close'].iloc[-1]
                onceki_fiyat = gecmis_veri['Close'].iloc[-2] if len(gecmis_veri) > 1 else son_fiyat
                degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
                
                # Özet Kartlar
                k1, k2, k3 = st.columns(3)
                with k1:
                    st.metric("Son Kapanış Fiyatı", f"{son_fiyat:.2f} TL")
                with k2:
                    st.metric("Günlük Değişim", f"{degisim:.2f}%", delta=f"{degisim:.2f}%")
                with k3:
                    st.metric("En Yüksek (Aylık)", f"{gecmis_veri['High'].max():.2f} TL")
                
                # Grafik Gösterimi
                st.markdown("### 📊 Son 1 Aylık Fiyat Hareketi")
                st.line_chart(gecmis_veri['Close'])
                
                # Detaylı Veri Tablosu
                with st.expander("📋 Son Dönem Detaylı Veri Tablosu"):
                    st.dataframe(gecmis_veri.tail(10), use_container_width=True)
            else:
                st.warning(f"⚠️ {secilen_hisse} için güncel veri çekilemedi. Lütfen piyasa saatlerini kontrol edin.")
                
        except Exception as e:
            st.error(f"❌ Veri çekilirken bir hata oluştu: {e}")

# =========================================================================
# SEKME 2: 🪙 CANLI ALTIN TAKİBİ
# =========================================================================
with sekme_altin:
    st.markdown("<div class='al-baslik'>🪙 Canlı Altın ve Küresel Emtia Fiyatları</div>", unsafe_allow_html=True)
    
    # Altın (Ons) ve USDTRY verilerini çekerek Gram Altın hesaplama
    try:
        ons_gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd_try = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
        
        # Gram Altın Hesaplama (Ons / 31.10347 * Dolar Kuru)
        gram_altin = (ons_gold / 31.10347) * usd_try
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gram Altın (Hesaplanan)", f"{gram_altin:.2f} TL")
        with col2:
            st.metric("Ons Altın ($)", f"{ons_gold:.2f} $")
        with col3:
            st.metric("USD / TRY Kuru", f"{usd_try:.4f} TL")
            
        st.info("💡 Not: Altın fiyatları uluslararası piyasalardan gecikmeli olarak hesaplanmaktadır.")
        
    except Exception as e:
        st.error(f"❌ Altın verisi yüklenirken hata oluştu: {e}")

# =========================================================================
# SEKME 3: 💬 SOHBET & NOT ALANI
# =========================================================================
with sekme_sohbet:
    st.markdown("<div class='alsat-baslik'>💬 Canlı Notlar ve Oda İçi Mesajlaşma</div>", unsafe_allow_html=True)
    
    # Yeni Mesaj Girişi
    with st.form("mesaj_formu", clear_on_submit=True):
        kullanici_adi = st.text_input("Takma Adınız (Rumuz):", placeholder="Örn: TraderAhmet")
        yeni_mesaj = st.text_area("Mesajınız veya Notunuz:", placeholder="Odaya iletmek istediğiniz not...")
        gonder_butonu = st.form_submit_group_button("Gönder / Kaydet")
        
        if gonder_butonu and yeni_mesaj:
            zaman_damgasi = datetime.datetime.now().strftime("%H:%M:%S")
            isim = kullanici_adi if kullanici_adi else "Anonim"
            
            # Geçmişe ekle
            st.session_state["sohbet_gecmisi"].append(f"[{zaman_damgasi}] **{isim}**: {yeni_mesaj}")
            st.toast("⚡ Not başarıyla odaya eklendi!")
            st.rerun()
            
    # Mesajları Ekranda Listeleme
    st.markdown("### 📌 Güncel Odanın Notları")
    if st.session_state["sohbet_gecmisi"]:
        for mesaj in reversed(st.session_state["sohbet_gecmisi"]):
            st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 4px; margin-bottom: 5px;'>{mesaj}</div>", unsafe_allow_html=True)
    else:
        st.caption("Henüz odaya bir not bırakılmamış.")
