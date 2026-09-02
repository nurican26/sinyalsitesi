# 💬 TOPLULUK SOHBET ODASI
    st.subheader("💬 Topluluk Sohbet Odası")
    with st.form("mesaj_formu", clear_on_submit=True):
        kullanici_mesaji = st.text_input("Mesajınızı yazın:", placeholder="Buraya yazın...")
        mesaj_gonder = st.form_submit_button("Gönder", use_container_width=True)
        
        if mesaj_gonder and kullanici_mesaji:
            mesaj_temiz = kullanici_mesaji.lower()
            if any(kufur in mesaj_temiz for kufur in st.session_state["engellenen_kelimeler"]):
                st.error("⚠️ Mesajınız uygunsuz kelimeler içerdiği için engellendi.")
            else:
                zaman = datetime.datetime.now().strftime("%H:%M")
                st.session_state["chat_history"].insert(0, f"[{zaman}] Kullanıcı: {kullanici_mesaji}")
                st.rerun()

    if st.session_state["chat_history"]:
        for msg in st.session_state["chat_history"]:
            st.write(msg)
    else:
        st.info("Henüz mesaj yazılmamış. İlk mesajı siz yazın!")

# ------------------------------------------
# 🎯 SAĞ TARAF: CANLI TAKİP & OYLAMA PANELİ
# ------------------------------------------
with sag_taraf:
    st.subheader("🎯 Canlı Takip")
    
    # ⚡ TÜM HİSSELERE AİT SABİT CANLI KÖŞE
    st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
    with st.spinner("Anlık borsa fiyatları çekiliyor..."):
        canli_borsa_listesi = []
        for hisse in BORSA_HISSELERI:
            try:
                hisse_obj = yf.Ticker(f"{hisse}.IS")
                hisse_data = hisse_obj.history(period="2d")
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
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    canli_borsa_listesi.append({
                        "Hisse Kodu": hisse,
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Günlük Değişim": "🔄 Veri Yok"
                    })
            except:
                pass
        
        if canli_borsa_listesi:
            st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)
        else:
            st.error("Borsa canlı verileri şu anda çekilemedi.")

    st.divider()

    # 🌟 SİNYAL HAVUZUNA ALINAN HİSSELER
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
        st.info("Henüz takibe alınan dinamik bir hisse bulunmuyor.")

    st.divider()

    # ⭐ EN ALTA EKLENEN PUANLAMA VE BEĞENİ SİSTEMİ
    st.markdown("#### 🗳️ Paneli Değerlendir")
    with st.form("oylama_formu", clear_on_submit=True):
        secilen_puan = st.slider("Panele Yıldız Verin (1-5):", min_value=1, max_value=5, value=5, step=1)
        oy_ver_butonu = st.form_submit_button("Beğen ve Gönder", use_container_width=True)
        
        if oy_ver_butonu:
            st.session_state["topham_oy_sayisi"] += 1
            st.session_state["topham_yildiz_puani"] += secilen_puan
            st.success("Beğeniniz ve puanınız başarıyla kaydedildi! Üst panel güncellendi.")
            st.rerun()
