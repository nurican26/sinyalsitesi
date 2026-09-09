# ===================================================================== #
# 4. GÜVENLİ SOHBET FORMU VE YEREL SES SİNYALİ (GARANTİLİ SES)
# ===================================================================== #
st.write("---")
st.markdown(f'<div class="kucuk-baslik">Sohbet (<span style="color:#00ffcc;">Odadaki Kişi: {gercek_kisi_sayisi}</span>)</div>', unsafe_allow_html=True)

yasakli = ["orosu", "orospu", "amk", "oç", "oc", "siktir", "piç", "salak", "sik", "göt", "amına"]

garantili_bip_html = """
<script>
    (function() {
        try {
            var AudioContext = window.AudioContext || window.webkitAudioContext;
            var context = new AudioContext();
            var osc = context.createOscillator();
            var gain = context.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(600, context.currentTime);
            gain.gain.setValueAtTime(0.1, context.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.2);
            osc.connect(gain);
            gain.connect(context.destination);
            osc.start();
            osc.stop(context.currentTime + 0.2);
        } catch(e) { console.log(e); }
    })();
</script>
"""

# Sohbet Giriş Formu
with st.form("sohbet_formu", clear_on_submit=True):
    kullanici_adi = st.text_input("İsminiz", max_chars=20, value="Anonim")
    mesaj = st.text_area("Yorumunuz", max_chars=150)
    gonder = st.form_submit_button("Gönder")

    if gonder and mesaj.strip():
        temiz_mesaj = mesaj.lower()
        if not any(kelime in temiz_mesaj for kelime in yasakli):
            try:
                yeni_mesaj = pd.DataFrame([{"isim": kullanici_adi, "saat": datetime.datetime.now().strftime("%H:%M:%S"), "yorum": mesaj.strip()}])
                yeni_mesaj.to_csv(db_sohbet, mode='a', header=not os.path.exists(db_sohbet), index=False)
                
                # Ses tetikleyici HTML'i ekrana basıyoruz
                st.markdown(garantili_bip_html, unsafe_allow_html=True)
                st.success("Mesaj gönderildi!")
                st.rerun()
            except Exception as e:
                st.error("Mesaj gönderilirken bir hata oluştu, lütfen tekrar deneyin.")
        else:
            st.warning("Mesajınız uygunsuz kelimeler içeriyor.")

# Mesajları Ekrana Okuma ve Yazma Alanı
if os.path.exists(db_sohbet):
    try:
        df_sohbet_oku = pd.read_csv(db_sohbet)
        if not df_sohbet_oku.empty:
            # En son yazılan 10 mesajı listeler
            for idx, row in df_sohbet_oku.tail(10).iterrows():
                st.markdown(f"**[{row['saat']}] {row['isim']}:** {row['yorum']}")
    except:
        pass
