        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
                    if len(h_detay_veri) > 0:
                        # Gerekli fiyat verilerini çekiyoruz
                        guncel_fiyat = float(h_detay_veri['Close'].iloc[-1])
                        en_yuksek = float(h_detay_veri['High'].iloc[-1])
                        en_dusuk = float(h_detay_veri['Low'].iloc[-1])
                        
                        # Yan yana 3 sütun halinde gösteriyoruz
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("Güncel Fiyat", f"{guncel_fiyat:,.2f} TL")
                        m_col2.metric("En Yüksek Fiyat", f"{en_yuksek:,.2f} TL")
                        m_col3.metric("En Düşük Fiyat", f"{en_dusuk:,.2f} TL")
