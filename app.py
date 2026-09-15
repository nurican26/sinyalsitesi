import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Sinyal Sitesi", layout="wide")

# ==========================================
# 1. CANLI BİST VERİLERİNİ ÇEKEN FONKSİYON
# ==========================================
@st.cache_data(ttl=60)  # Verileri 60 saniyede bir otomatik günceller
def get_bist_live_data():
    # Tüm BIST hisselerinin listesi
    bist_symbols = [
        "A1CAP.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "AGHOL.IS", "AGROT.IS", "AKBNK.IS", "AKCNS.IS", 
        "AKFGY.IS", "AKFYE.IS", "AKMGH.IS", "AKSA.IS", "AKSEN.IS", "AKSUE.IS", "ALARK.IS", "ALBRK.IS", 
        "ALCAR.IS", "ALCTL.IS", "ALARK.IS", "ALMAD.IS", "ALTNY.IS", "ALVES.IS", "ANSGR.IS", "ARCLK.IS", 
        "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ASELS.IS", "ASTOR.IS", "ATAKP.IS", "ATEKS.IS", "ATSYH.IS", 
        "AVOD.IS", "AYCES.IS", "AYDEM.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", 
        "BANVT.IS", "BARMA.IS", "BASGZ.IS", "BAYRK.IS", "BEVT.IS", "BERA.IS", "BEYAZ.IS", "BFREN.IS", 
        "BIENP.IS", "BIGCHEFS.IS", "BIMAS.IS", "BIOEN.IS", "BRKSN.IS", "BRLSM.IS", "BRSAN.IS", "BRYAT.IS", 
        "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS", "BURVA.IS", "CANTE.IS", "CASA.IS", "CATES.IS", 
        "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "CVKMD.IS", 
        "CWENE.IS", "DAPGM.IS", "DARDL.IS", "DGATE.IS", "DGGYO.IS", "DITAS.IS", "DMSAS.IS", "DNISI.IS", 
        "DOAS.IS", "DOBUR.IS", "DOCO.IS", "DOHOL.IS", "DOKTA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", 
        "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDATA.IS", "EDIP.IS", "EGEEN.IS", "EGGUB.IS", "EGPRO.IS", 
        "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS", "ENERY.IS", "ENJSA.IS", 
        "ENKAI.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "EUPWR.IS", "EUREK.IS", "EYGYO.IS", "FMIZP.IS", 
        "FONET.IS", "FORMT.IS", "FORTE.IS", "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", 
        "GENTS.IS", "GEREL.IS", "GESAN.IS", "GOKNR.IS", "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRSEL.IS", 
        "GSDHO.IS", "GSDE.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HATEK.IS", "HEKTS.IS", "HKTM.IS", 
        "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "IEYHO.IS", "IHAAS.IS", 
        "IHEVA.IS", "IHGTT.IS", "IHLGM.IS", "IHYAY.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS", 
        "INTEM.IS", "INVEO.IS", "INVES.IS", "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISFIN.IS", "ISGSY.IS", 
        "ISGYO.IS", "ISKPL.IS", "ISMEN.IS", "ISSEN.IS", "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS", 
        "KAREL.IS", "KARSN.IS", "KARTN.IS", "KATMR.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS", "KLGYO.IS", 
        "KLMSN.IS", "KLSER.IS", "KLRHO.IS", "KMPUR.IS", "KONTR.IS", "KONYA.IS", "KORDS.IS", "KOZAA.IS", 
        "KOZAL.IS", "KRDMD.IS", "KRONT.IS", "KRPLS.IS", "KRVGD.IS", "KSTUR.IS", "KTLEV.IS", "KUYAŞ.IS", 
        "LIDER.IS", "LKMNH.IS", "LOGO.IS", "LRVGY.IS", "LUKSK.IS", "MAALT.IS", "MACKO.IS", "MAKIM.IS", 
        "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEPET.IS", "MERCN.IS", 
        "MERKO.IS", "METRO.IS", "MHRGY.IS", "MIATK.IS", "MIPAZ.IS", "MPARK.IS", "MRGYO.IS", "MSGYO.IS", 
        "MTRKS.IS", "MTURG.IS", "NAVTK.IS", "NTGAZ.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", 
        "OBASE.IS", "ODAS.IS", "ONCSM.IS", "ORGE.IS", "ORMA.IS", "OTKAR.IS", "OYYAT.IS", "OZKGY.IS", 
        "OZSUB.IS", "PAGYO.IS", "PAMEL.IS", "PATEK.IS", "PAPIL.IS", "PARSN.IS", "PASEU.IS", "PENCW.IS", 
        "PENTA.IS", "PETKM.IS", "PKART.IS", "PLTUR.IS", "POLHO.IS", "POLTK.IS", "PRKAB.IS", "PRKME.IS", 
        "PRDGS.IS", "PSAOL.IS", "PSGYO.IS", "QUAGR.IS", "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RGYAS.IS", 
        "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS", "RYSAS.IS", "SAHOL.IS", 
        "SAMAT.IS", "SANEL.IS", "SANFM.IS", "SANGS.IS", "SANKO.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", 
        "SDTTR.IS", "SEGMN.IS", "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", 
        "SISE.IS", "SKBNK.IS", "SMART.IS", "SMRTG.IS", "SNAAM.IS", "SNET.IS", "SOKM.IS", "SOPAT.IS", 
        "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TCELL.IS", 
        "TDGYO.IS", "TEKTN.IS", "TEZOL.IS", "TETMT.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TLMAN.IS", 
        "TMSN.IS", "TNZTP.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS", "TRILC.IS", "TSKB.IS", "TSPOR.IS", 
        "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TURGG.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS", 
        "ULKER.IS", "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKKO.IS", "VANGD.IS", "VBTYZ.IS", "VERTU.IS", 
        "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", 
        "YGGYO.IS", "YGYO.IS", "YEOTK.IS", "YKBNK.IS", "YONGA.IS", "YUNSA.IS", "YYLGD.IS", "ZOREN.IS"
    ]
    
    data_list = []
    # Verileri toplu şekilde çekiyoruz
    tickers = yf.Tickers(" ".join(bist_symbols))
    
    for symbol in bist_symbols:
        try:
            ticker = tickers.tickers[symbol]
            info = ticker.fast_info
            
            last_price = info.last_price
            prev_close = info.previous_close
            
            if last_price and prev_close:
                change_pct = ((last_price - prev_close) / prev_close) * 100
                volume = (info.last_volume * last_price / 1_000_000) if info.last_volume else 0
                
                clean_symbol = symbol.replace(".IS", "")
                data_list.append({
                    "symbol": clean_symbol,
                    "price": f"{last_price:,.2f}",
                    "change_num": change_pct,
                    "change": f"{change_pct:+.2f} %",
                    "volume_num": volume,
                    "volume": f"{volume:,.2f}"
                })
        except Exception:
            continue
            
    return pd.DataFrame(data_list)

# ==========================================
# 2. ANA SAYFA VE İKON SEÇİMİ (SEKMELER)
# ==========================================
st.title("🚀 Sinyal Sitesi")

# Sayfanıza eklenen yeni ikon grubu
tab1, tab2, tab3 = st.tabs([
    "📹 Canlı Yayın / YouTube", 
    "📈 BIST Canlı (Yükselen/Düşen)", 
    "⚙️ Diğer Ayarlar"
])

# ------------------------------------------
# SEKME 1: MEVCUT CANLI YAYIN SAYFANIZ
# ------------------------------------------
with tab1:
    st.info("Yayın takibi yapmak veya doğrudan yayına katılmak için aşağıdaki butona tıklayabilir ya da yayını doğrudan izleyebilirsiniz.")
    url_input = st.text_input("Canlı Yayın URL (YouTube, Kick vb.):", value="https://www.youtube.com")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button("🎥 CANLI YAYINA KATIL / İZLE", url_input, use_container_width=True)
    
    st.subheader("📺 Yayın Ekranı")
    # YouTube / Video Oynatıcı Alanı
    st.video(url_input if "youtube.com" in url_input or "youtu.be" in url_input else "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    st.warning("⚠️ SPK YASAL UYARI: Bu platformda yer alan veriler yalnızca genel bilgilendirme amacıyla sunulmaktadır. Borsa verileri en az 15 dakika gecikmeli olabilir.")

# ------------------------------------------
# SEKME 2: CANLI YÜKSELEN / DÜŞEN BİST HİSSELERİ (YENİ EKİ)
# ------------------------------------------
with tab2:
    st.subheader("📊 Borsa İstanbul Canlı Veriler")
    
    if st.button("🔄 Verileri Şimdi Yenile"):
        st.cache_data.clear()

    with st.spinner("Tüm BIST hisseleri taranıyor, lütfen bekleyin..."):
        df = get_bist_live_data()

    if not df.empty:
        # En Çok Yükselenler, Düşenler ve Hacimliler sıralamaları
        yukselenler = df.sort_values(by="change_num", ascending=False).head(10).to_dict('records')
        dusenler = df.sort_values(by="change_num", ascending=True).head(10).to_dict('records')
        hacimliler = df.sort_values(by="volume_num", ascending=False).head(10).to_dict('records')

        # Görseldeki Tasarım HTML/CSS Kod Bileşeni
        widget_html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
          <meta charset="UTF-8">
          <style>
            * {{ box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            body {{ background-color: transparent; display: flex; justify-content: center; padding: 5px; }}
            .widget-container {{ width: 100%; max-width: 450px; background: #fff; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .header-title {{ background-color: #2ed599; color: #000; text-align: center; padding: 12px; font-weight: bold; font-size: 16px; }}
            .tabs {{ display: flex; background-color: #f9f9f9; border-bottom: 1px solid #ddd; }}
            .tab-btn {{ flex: 1; padding: 10px 5px; text-align: center; background: none; border: none; border-right: 1px solid #ddd; font-size: 14px; font-weight: bold; color: #333; cursor: pointer; }}
            .tab-btn:last-child {{ border-right: none; }}
            .tab-btn.active {{ background-color: #fff; border-top: 3px solid #2ed599; color: #000; }}
            .stock-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            .stock-table th {{ text-align: left; padding: 8px; background-color: #fff; border-bottom: 1px solid #ddd; color: #000; font-weight: bold; }}
            .stock-table th:nth-child(2), .stock-table th:nth-child(3), .stock-table th:nth-child(4) {{ text-align: right; }}
            .stock-table td {{ padding: 8px; border-bottom: 1px dashed #e0e0e0; }}
            .stock-table tr:nth-child(even) {{ background-color: #fdfdfd; }}
            .stock-table td:nth-child(2), .stock-table td:nth-child(3), .stock-table td:nth-child(4) {{ text-align: right; }}
            .pos-change {{ color: #2ed599; font-weight: bold; }}
            .neg-change {{ color: #e74c3c; font-weight: bold; }}
            .symbol {{ font-weight: bold; }}
          </style>
        </head>
        <body>

        <div class="widget-container">
          <div class="header-title">Endeks/Dönem Seçimi</div>
          
          <div class="tabs">
            <button class="tab-btn active" onclick="showTab('yukselenler', event)">Yükselenler</button>
            <button class="tab-btn" onclick="showTab('dusenler', event)">Düşenler</button>
            <button class="tab-btn" onclick="showTab('hacimliler', event)">Hacimliler</button>
          </div>

          <table class="stock-table">
            <thead>
              <tr>
                <th>HİSSE</th>
                <th>SON</th>
                <th>DEĞİŞİM</th>
                <th>HACİM (mTL)</th>
              </tr>
            </thead>
            <tbody id="table-body"></tbody>
          </table>
        </div>

        <script>
          const data = {{
            yukselenler: {yukselenler},
            dusenler: {dusenler},
            hacimliler: {hacimliler}
          }};

          function showTab(type, evt) {{
            if (evt) {{
              document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
              evt.target.classList.add('active');
            }}

            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            data[type].forEach(item => {{
              const isNegative = item.change.includes('-');
              const changeClass = isNegative ? 'neg-change' : 'pos-change';

              const row = `
                <tr>
                  <td class="symbol">${{item.symbol}}</td>
                  <td>${{item.price}}</td>
                  <td class="${{changeClass}}">${{item.change}}</td>
                  <td>${{item.volume}}</td>
                </tr>
              `;
              tbody.innerHTML += row;
            }});
          }}

          showTab('yukselenler');
        </script>
        </body>
        </html>
        """
        
        st.components.v1.html(widget_html, height=500, scrolling=False)
    else:
        st.warning("Veriler şu an çekilemiyor. Lütfen yenile butonunu deneyin.")

# ------------------------------------------
# SEKME 3: DİĞER MODÜLLER İÇİN ALAN
# ------------------------------------------
with tab3:
    st.write("Sitenize ekleyeceğiniz diğer modüller veya ayarlar için bu alanı kullanabilirsiniz.")
