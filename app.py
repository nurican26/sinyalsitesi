# ==========================================
# 📊 SAĞ TARAF: ANLIK BORSA KÖŞESİ & TOPLULUK PANELİ
# ==========================================
with sag_taraf:
    st.subheader("🎯 Canlı Takip & Topluluk Paneli")
    
    # ==========================================
    # 🏦 YENİ EKLEMEYEN SABİT ANLIK BORSA KÖŞESİ
    # ==========================================
    st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
    with st.spinner("Anlık borsa fiyatları çekiliyor..."):
        canli_borsa_listesi = []
        for hisse in BORSA_HISSELERI:
            try:
                # Yahoo Finance üzerinden tüm listenin anlık fiyatını ve günlük değişimini çekiyoruz
                hisse_obj = yf.Ticker(f"{hisse}.IS")
                hisse_data = hisse_obj.history(period="2d") # Son 2 günü çekerek dünkü kapanışa göre değişim hesaplıyoruz
                if len(hisse_data) >= 2:
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    onceki_kapanis = hisse_data['Close'].iloc[-2]
                    gunluk_degisim = ((guncel_fiy - onceki_kapanis) / onceki_kapanis) * 100
                    
                    canli_borsa_listesi.append({
                        "Hisse Kodu": hisse,
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Günlük Değişim": f"🟢 %+{gunluk_degisim:.2f}" if gunluk_degisim >= 0 else f"🔴 %{gunluk_degisim:.2f}"
                    })
                elif not hisse_data.empty:
                    # Tek gün verisi varsa sadece fiyatı basıyoruz
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    canli_borsa_listesi.append({
                        "Hisse Kodu": hisse,
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Günlük Değişim": "🔄 Veri Yok"
                    })
            except:
                pass
        
        if canli_borsa_listesi:
            # Tüm hisselerin canlı fiyat tablosunu basıyoruz (Arama ve sıralama yapılabilir)
            st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)
        else:
            st.error("Borsa canlı verileri şu anda çekilemedi.")

    st.divider()

    # 📌 Özel Takip Kutusu Listeleme (Yeşil butondan tetiklenenler)
    st.markdown("#### 🌟 Sinyal Havuzuna Alınan Hisseler")
    if st.session_state["ozel_takip_kutusu"]:
        takip_listesi = []
        for hisse, bilgi in list(st.session_state["ozel_takip_kutusu"].items()):
            try:
                hisse_data = yf.Ticker(f"{hisse}.IS").history(period="1d")
                if not hisse_data.empty:
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    ilkesel_fiy = bilgi["kayit_fiyati"]
                    degisim = ((guncel_fiy - ilkesel_fiy) / ilkesel_fiy) * 100
                    
                    takip_listesi.append({
                        "Hisse Kodu": hisse,
                        "Giriş Fiyatı": f"{ilkesel_fiy:.2f} TL",
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Performans": f"🟢 %{degisim:.2f}" if degisim >= 0 else f"🔴 %{degisim:.2f}",
                        "Kayıt Zamanı": bilgi["kayit_zamani"]
                    })
            except:
                pass
        
        if takip_listesi:
            st.dataframe(pd.DataFrame(takip_listesi), use_container_width=True, hide_index=True)
            
            if st.button("🗑️ Takip Listesini Temizle", use_container_width=True):
                st.session_state["ozel_takip_kutusu"] = {}
                st.rerun()
        else:
            st.info("Takip listesindeki veriler güncellenemedi.")
    else:
        st.info("Henüz yeşil buton tetiklenerek takibe alınan dinamik bir hisse bulunmuyor.")

    st.divider()

    # ⭐ Topluluk Değerlendirme Sistemi
    st.markdown("#### 🗳️ Paneli Değerlendir")
    with st.form("oylama_formu", clear_on_submit=True):
        secilen_puan = st.slider("Panele Puan Verin:", min_value=1, max_value=5, value=5, step=1)
        oy_ver_butonu = st.form_submit_button("Oyu Gönder", use_container_width=True)
        
        if oy_ver_butonu:
            st.session_state["topham_oy_sayisi"] += 1
            st.session_state["topham_yildiz_puani"] += secilen_puan
            st.success("Oyunuz başarıyla kaydedildi! Panel puanı güncellendi.")
            st.rerun()
