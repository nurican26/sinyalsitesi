from flask import Flask, jsonify, render_template, request
import yfinance as yf

app = Flask(__name__)

# Varsayılan takip listesi sembolleri
# BIST hisselerinin sonuna .IS eklemeyi unutmayın (Örn: THYAO.IS)
WATCHLIST = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "AAPL", "TSLA"]

def fetch_stock_data(ticker_symbol):
    """
    Yahoo Finance üzerinden tek bir hissenin canlı verilerini çeker.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # Güncel gün içi verileri çekmek için en kararlı aralık
        todays_data = ticker.history(period="1d", interval="1m")
        
        if todays_data.empty:
            todays_data = ticker.history(period="2d")
            
        if not todays_data.empty:
            current_price = todays_data['Close'].iloc[-1]
            day_high = todays_data['High'].max()
            day_low = todays_data['Low'].min()
            
            # Önceki kapanış fiyatını güvenli bir şekilde alma
            info = ticker.info
            previous_close = info.get('previousClose', current_price)
            
            price_change = current_price - previous_close
            pct_change = (price_change / previous_close) * 100
            company_name = info.get('longName', ticker_symbol)
            
            return {
                "symbol": ticker_symbol,
                "name": company_name,
                "price": round(current_price, 2),
                "change": round(pct_change, 2),
                "high": round(day_high, 2),
                "low": round(day_low, 2),
                "status": "success"
            }
    except Exception as e:
        print(f"Veri çekme hatası ({ticker_symbol}): {str(e)}")
        
    return {
        "symbol": ticker_symbol,
        "name": "Veri Alınamadı",
        "price": 0.0,
        "change": 0.0,
        "high": 0.0,
        "low": 0.0,
        "status": "error"
    }

@app.route('/')
def home():
    return "Borsa API Backend Sistemi Aktif. Canlı veriler için /api/stocks adresini sorgulayın."

@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """Takip listesindeki tüm verileri JSON formatında basar."""
    data_list = []
    for ticker in WATCHLIST:
        stock_info = fetch_stock_data(ticker)
        data_list.append(stock_info)
    return jsonify(data_list)

@app.route('/api/add', methods=['POST'])
def add_to_watchlist():
    """Hata veren toUpperCase() yerine düzeltilmiş Python .upper() fonksiyonu"""
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Geçersiz parametre."}), 400
        
    # Python uyumlu .upper() düzeltmesi yapıldı
    new_ticker = data['ticker'].strip().upper()
    
    if new_ticker not in WATCHLIST:
        WATCHLIST.append(new_ticker)
        return jsonify({"message": f"{new_ticker} listeye eklendi.", "watchlist": WATCHLIST}), 200
    return jsonify({"message": "Zaten listede var."}), 200

@app.route('/api/delete', methods=['POST'])
def delete_from_watchlist():
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Geçersiz parametre."}), 400
        
    ticker_to_delete = data['ticker'].strip().upper()
    
    if ticker_to_delete in WATCHLIST:
        WATCHLIST.remove(ticker_to_delete)
        return jsonify({"message": f"{ticker_to_delete} silindi.", "watchlist": WATCHLIST}), 200
    return jsonify({"error": "Bulunamadı."}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
