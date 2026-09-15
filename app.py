import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Borsa Takibi", page_icon="📈", layout="centered")

# 1. Takip Edilecek BIST Hisse Listesi (Sistemin canlı verisini toplayacağı hisseler)
BIST_SYMBOLS = [
    "PATEK.IS", "TKFEN.IS", "ZOREN.IS", "DSTKF.IS", "ENERY.IS", 
    "REEDR.IS", "ASELS.IS", "ANSGR.IS", "THYAO.IS", "GARAN.IS", 
    "EREGL.IS", "AKBNK.IS", "KCHOL.IS", "TUPRS.IS", "SAHOL.IS",
    "SASA.IS", "HEKTS.IS", "BIMAS.IS", "SISE.IS", "EKGYO.IS"
]

@st.cache_data(ttl=60)  # Veriyi 60 saniyede bir otomatik yeniler
def get_live_bist_data():
    data_list = []
    
    # yfinance ile tüm hisselerin son durumunu çekiyoruz
    tickers = yf.Tickers(" ".join(BIST_SYMBOLS))
    
    for symbol in BIST_SYMBOLS:
        try:
            ticker = tickers.tickers[symbol]
            info = ticker.fast_info
            
            last_price = info.last_price
            prev_close = info.previous_close
            
            if last_price and prev_close:
                # Yüzdelik Değişim Hesabı
                change_pct = ((last_price - prev_close) / prev_close) * 100
                # Hacim Hesabı (Tahmini mTL cinsinden)
                volume = info.last_volume * last_price / 1_000_000 if info.last_volume else 0
                
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

# Yan Menü (Sidebar) Veya Sayfa Başına Yenileme Butonu
st.sidebar.title("Kontrol Paneli")
if st.sidebar.button("🔄 Verileri Canlı Yenile"):
    st.cache_data.clear()

st.title("📈 Canlı Borsa İstatistikleri")

# Canlı Veriyi Çek
with st.spinner("Borsa İstanbul canlı verileri çekiliyor..."):
    df = get_live_bist_data()

if not df.empty:
    # Verileri Kriterlere Göre Filtrele
    yukselenler = df.sort_values(by="change_num", ascending=False).head(8).to_dict('records')
    dusenler = df.sort_values(by="change_num", ascending=True).head(8).to_dict('records')
    hacimliler = df.sort_values(by="volume_num", ascending=False).head(8).to_dict('records')

    # HTML & CSS Şablonu
    html_code = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
      <meta charset="UTF-8">
      <style>
        * {{ box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
        body {{ background-color: transparent; display: flex; justify-content: center; padding: 5px; }}
        .widget-container {{ width: 100%; max-width: 420px; background: #fff; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
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

    st.components.v1.html(html_code, height=450, scrolling=False)
else:
    st.error("Veriler çekilirken bir hata oluştu. Lütfen sayfayı yenileyin.")
