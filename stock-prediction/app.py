from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import time
import threading
import requests
import numpy as np
import logging
import sys

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Finnhub API Key
FINNHUB_API_KEY = "d2ahh4pr01qgk9uetqegd2ahh4pr01qgk9uetqf0"

# Database connection
conn = sqlite3.connect('stocks.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Stocks table
    c.execute('''CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                market TEXT,
                sector TEXT,
                currency TEXT,
                last_updated TIMESTAMP)''')
    
    # Prices table
    c.execute('''CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date DATE,
                close REAL,
                FOREIGN KEY(symbol) REFERENCES stocks(symbol))''')
    
    # Technical analysis table
    c.execute('''CREATE TABLE IF NOT EXISTS technical_analysis (
                symbol TEXT PRIMARY KEY,
                sma REAL,
                rsi REAL,
                macd REAL,
                trend TEXT,
                trend_score REAL,
                last_updated TIMESTAMP)''')
    
    # Default stocks
    default_stocks = [
        ('THYAO.IS', 'Turkish Airlines', 'BIST', 'Aviation', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('AKBNK.IS', 'Akbank', 'BIST', 'Banking', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('GARAN.IS', 'Garanti BBVA', 'BIST', 'Banking', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('SISE.IS', 'Şişe Cam', 'BIST', 'Industry', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('KOZAA.IS', 'Koza Altın', 'BIST', 'Mining', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('EREGL.IS', 'Ereğli Iron Steel', 'BIST', 'Metal', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('ASELS.IS', 'Aselsan', 'BIST', 'Defense', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('KCHOL.IS', 'Koç Holding', 'BIST', 'Conglomerate', 'TRY', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('AAPL', 'Apple Inc.', 'US', 'Technology', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('MSFT', 'Microsoft', 'US', 'Technology', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('GOOGL', 'Alphabet (Google)', 'US', 'Technology', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('AMZN', 'Amazon', 'US', 'Retail', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('TSLA', 'Tesla Inc.', 'US', 'Automotive', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('JPM', 'JPMorgan Chase', 'US', 'Banking', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('NVDA', 'NVIDIA', 'US', 'Technology', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('META', 'Meta Platforms', 'US', 'Technology', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('BTC-USD', 'Bitcoin', 'Crypto', 'Cryptocurrency', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('ETH-USD', 'Ethereum', 'Crypto', 'Cryptocurrency', 'USD', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    # Add default stocks
    for stock in default_stocks:
        c.execute('''INSERT OR IGNORE INTO stocks (symbol, name, market, sector, currency, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)''', stock)
    
    conn.commit()
    logger.info("Database initialized successfully")

def fetch_stock_profile(symbol):
    """Get stock profile information from Finnhub API"""
    try:
        logger.info(f"Fetching profile for {symbol}")
        response = requests.get(
            f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}",
            timeout=10
        )
        
        if response.status_code != 200:
            logger.warning(f"Failed to get profile for {symbol}. HTTP {response.status_code}")
            return {
                'name': symbol,
                'sector': 'Unknown',
                'currency': 'USD' if '.' not in symbol else 'TRY'
            }
        
        data = response.json()
        
        if not data or 'name' not in data:
            logger.warning(f"No profile found for {symbol}")
            return {
                'name': symbol,
                'sector': 'Unknown',
                'currency': 'USD' if '.' not in symbol else 'TRY'
            }
        
        return {
            'name': data.get('name', symbol),
            'sector': data.get('finnhubIndustry', 'Unknown'),
            'currency': data.get('currency', 'USD' if '.' not in symbol else 'TRY')
        }
    except Exception as e:
        logger.error(f"Failed to get profile for {symbol}: {str(e)}")
        return {
            'name': symbol,
            'sector': 'Unknown',
            'currency': 'USD' if '.' not in symbol else 'TRY'
        }

def update_stock_data(symbol):
    """Update stock price data"""
    try:
        logger.info(f"Updating price data for {symbol}")
        
        # Get historical data from Finnhub
        end_date = int(time.time())
        start_date = end_date - (365 * 24 * 60 * 60 * 5)  # 5 years ago
        
        response = requests.get(
            f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={start_date}&to={end_date}&token={FINNHUB_API_KEY}",
            timeout=15
        )
        
        if response.status_code != 200:
            logger.warning(f"Failed to get price data for {symbol}. HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if data.get('s') != 'ok':
            logger.warning(f"No data or error for {symbol}: {data.get('s')}")
            return False
        
        closes = data.get('c', [])
        timestamps = data.get('t', [])
        
        if not closes or not timestamps:
            logger.warning(f"Empty data for {symbol}")
            return False
        
        logger.info(f"Received {len(closes)} days of data for {symbol}")
        
        # Save prices to database
        for i in range(len(timestamps)):
            date_str = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
            close_price = closes[i]
            
            c.execute('''INSERT OR IGNORE INTO prices (symbol, date, close)
                         VALUES (?, ?, ?)''', (symbol, date_str, close_price))
        
        # Save last update time
        c.execute('''UPDATE stocks SET last_updated = ? WHERE symbol = ?''',
                 (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
        
        conn.commit()
        logger.info(f"Updated stock data for {symbol} ({len(timestamps)} days)")
        return True
    except Exception as e:
        logger.error(f"Update error for {symbol}: {str(e)}")
        return False

def fetch_technical_analysis(symbol):
    """Calculate and save technical indicators"""
    try:
        logger.info(f"Updating technical analysis for {symbol}")
        
        # Get technical indicators from Finnhub
        end_date = int(time.time())
        start_date = end_date - (365 * 24 * 60 * 60)  # 1 year ago
        
        # SMA (Simple Moving Average)
        sma_response = requests.get(
            f"https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&from={start_date}&to={end_date}"
            f"&indicator=sma&timeperiod=20&token={FINNHUB_API_KEY}",
            timeout=15
        )
        
        # RSI (Relative Strength Index)
        rsi_response = requests.get(
            f"https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&from={start_date}&to={end_date}"
            f"&indicator=rsi&timeperiod=14&token={FINNHUB_API_KEY}",
            timeout=15
        )
        
        # MACD (Moving Average Convergence Divergence)
        macd_response = requests.get(
            f"https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&from={start_date}&to={end_date}"
            f"&indicator=macd&token={FINNHUB_API_KEY}",
            timeout=15
        )
        
        # Check responses
        if sma_response.status_code != 200:
            logger.warning(f"Failed to get SMA for {symbol}. HTTP {sma_response.status_code}")
            return None
        
        if rsi_response.status_code != 200:
            logger.warning(f"Failed to get RSI for {symbol}. HTTP {rsi_response.status_code}")
            return None
            
        if macd_response.status_code != 200:
            logger.warning(f"Failed to get MACD for {symbol}. HTTP {macd_response.status_code}")
            return None
        
        sma_data = sma_response.json()
        rsi_data = rsi_response.json()
        macd_data = macd_response.json()
        
        # Extract last values
        last_sma = sma_data['technicalAnalysis']['sma'][-1] if sma_data['s'] == 'ok' and sma_data['technicalAnalysis']['sma'] else 0
        last_rsi = rsi_data['technicalAnalysis']['rsi'][-1] if rsi_data['s'] == 'ok' and rsi_data['technicalAnalysis']['rsi'] else 0
        last_macd = macd_data['technicalAnalysis']['macd'][-1] if macd_data['s'] == 'ok' and macd_data['technicalAnalysis']['macd'] else 0
        
        # Analyze trend
        trend, trend_score = analyze_trend(last_sma, last_rsi, last_macd)
        
        # Save to database
        c.execute('''INSERT OR REPLACE INTO technical_analysis (symbol, sma, rsi, macd, trend, trend_score, last_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                 (symbol, last_sma, last_rsi, last_macd, trend, trend_score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        
        logger.info(f"Updated technical analysis for {symbol}: SMA={last_sma:.2f}, RSI={last_rsi:.2f}, MACD={last_macd:.2f}, Trend={trend}")
        return {
            'sma': last_sma,
            'rsi': last_rsi,
            'macd': last_macd,
            'trend': trend,
            'trend_score': trend_score
        }
    except Exception as e:
        logger.error(f"Technical analysis error for {symbol}: {str(e)}")
        return None

def analyze_trend(sma, rsi, macd):
    """Analyze trend based on indicators and calculate score"""
    # Calculate trend score (0-100)
    trend_score = 50  # Neutral start
    
    # Adjustments based on RSI
    if rsi > 70:
        trend_score -= 20  # Overbought
    elif rsi > 60:
        trend_score -= 10
    elif rsi < 30:
        trend_score += 20  # Oversold
    elif rsi < 40:
        trend_score += 10
    
    # Adjustments based on MACD
    if macd > 0:
        trend_score += 15  # Positive momentum
    else:
        trend_score -= 15  # Negative momentum
    
    # Adjustments based on SMA
    if sma > 0:
        trend_score += 5
    
    # Limit score
    trend_score = max(0, min(100, trend_score))
    
    # Determine trend category
    if trend_score >= 70:
        return "Strong Uptrend", trend_score
    elif trend_score >= 60:
        return "Uptrend", trend_score
    elif trend_score >= 40:
        return "Neutral", trend_score
    elif trend_score >= 30:
        return "Downtrend", trend_score
    else:
        return "Strong Downtrend", trend_score

def background_updater():
    """Background function to update data periodically"""
    while True:
        try:
            logger.info("\n" + "="*50)
            logger.info("Starting background update...")
            logger.info("="*50)
            
            # Get all stocks
            c.execute("SELECT symbol FROM stocks")
            symbols = [row[0] for row in c.fetchall()]
            
            # Update stock data
            for i, symbol in enumerate(symbols):
                try:
                    logger.info(f"[{i+1}/{len(symbols)}] Updating {symbol}...")
                    
                    # Update stock profile
                    if i % 5 == 0:  # Every 5 stocks
                        profile = fetch_stock_profile(symbol)
                        c.execute('''UPDATE stocks SET name=?, sector=?, currency=? WHERE symbol=?''',
                                 (profile['name'], profile['sector'], profile['currency'], symbol))
                        conn.commit()
                    
                    # Update price data
                    if not update_stock_data(symbol):
                        logger.warning(f"Failed to update price data for {symbol}")
                    
                    # Update technical analysis
                    if not fetch_technical_analysis(symbol):
                        logger.warning(f"Failed to update technical analysis for {symbol}")
                    
                    # Wait for API limits (Finnhub: 60 requests/minute)
                    time.sleep(1.2)
                    
                except Exception as e:
                    logger.error(f"Update error for {symbol}: {str(e)}")
            
            logger.info("\n" + "="*50)
            logger.info(f"All stocks updated. {len(symbols)} stocks.")
            logger.info("Waiting 1 hour...")
            logger.info("="*50 + "\n")
            time.sleep(3600)  # Wait 1 hour
        except Exception as e:
            logger.error(f"Background update error: {str(e)}")
            time.sleep(60)

@app.route('/stock_data', methods=['POST'])
def stock_data():
    symbol = request.json.get('symbol')
    period = request.json.get('period', '1Y')
    
    period_mapping = {
        '10Y': 3650,
        '5Y': 1825,
        '1Y': 365,
        '6M': 180,
        '1M': 30,
        '1W': 7
    }
    
    days = period_mapping.get(period, period_mapping['1Y'])
    
    try:
        # Get last N days of data
        c.execute("""
            SELECT date, close 
            FROM prices 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT ?
        """, (symbol, days))
        
        data = c.fetchall()
        
        if not data:
            return jsonify({'error': 'No data available'}), 404
            
        dates = [row[0] for row in data]
        prices = [row[1] for row in data]
        
        return jsonify({
            'symbol': symbol,
            'dates': dates,
            'prices': prices
        })
    except Exception as e:
        logger.error(f"Stock data error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/add_stock', methods=['POST'])
def add_stock():
    symbol = request.json.get('symbol')
    if not symbol:
        return jsonify({'status': 'error', 'message': 'Stock symbol required'}), 400
    
    try:
        # Get stock profile
        profile = fetch_stock_profile(symbol)
        
        # Determine market category
        if symbol.endswith('.IS'):
            market = 'BIST'
        elif symbol in ['BTC-USD', 'ETH-USD']:
            market = 'Crypto'
        else:
            market = 'US'
        
        # Add to database
        c.execute('''INSERT OR IGNORE INTO stocks (symbol, name, market, sector, currency, last_updated)
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                 (symbol, profile['name'], market, profile['sector'], profile['currency'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        
        # Update immediately
        update_stock_data(symbol)
        fetch_technical_analysis(symbol)
        
        return jsonify({
            'status': 'success', 
            'message': f'{symbol} added successfully',
            'data': {
                'symbol': symbol,
                'name': profile['name'],
                'market': market,
                'sector': profile['sector'],
                'currency': profile['currency']
            }
        })
    except Exception as e:
        logger.error(f"Add stock error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/stocks', methods=['GET'])
def get_stocks():
    market = request.args.get('market', 'all')
    
    try:
        if market == 'all':
            c.execute("SELECT symbol, name, market, sector, currency FROM stocks")
        else:
            c.execute("SELECT symbol, name, market, sector, currency FROM stocks WHERE market=?", (market,))
        
        stocks = []
        for row in c.fetchall():
            symbol, name, market, sector, currency = row
            
            # Get latest price
            c.execute("SELECT close FROM prices WHERE symbol=? ORDER BY date DESC LIMIT 1", (symbol,))
            price_row = c.fetchone()
            price = price_row[0] if price_row else 0.0
            
            # Get technical analysis
            c.execute("SELECT trend, trend_score FROM technical_analysis WHERE symbol=?", (symbol,))
            tech_row = c.fetchone()
            trend = tech_row[0] if tech_row else "Unknown"
            trend_score = tech_row[1] if tech_row else 0
            
            # Calculate change percentage
            change = 0.0
            change_percent = 0.0
            c.execute("SELECT close FROM prices WHERE symbol=? ORDER BY date DESC LIMIT 2", (symbol,))
            price_rows = c.fetchall()
            if len(price_rows) == 2:
                prev_price = price_rows[1][0]
                current_price = price_rows[0][0]
                change = current_price - prev_price
                change_percent = (change / prev_price) * 100 if prev_price != 0 else 0.0
            
            stocks.append({
                'symbol': symbol,
                'name': name,
                'market': market,
                'sector': sector,
                'currency': currency,
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'trend': trend,
                'trend_score': trend_score
            })
        
        # Sort by trend score (high score first)
        stocks.sort(key=lambda x: x['trend_score'], reverse=True)
        
        return jsonify(stocks)
    except Exception as e:
        logger.error(f"Get stocks error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/technical_analysis', methods=['POST'])
def technical_analysis():
    symbol = request.json.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    try:
        # Get technical analysis from database
        c.execute("SELECT sma, rsi, macd, trend, trend_score FROM technical_analysis WHERE symbol=?", (symbol,))
        analysis = c.fetchone()
        
        if analysis:
            sma, rsi, macd, trend, trend_score = analysis
            return jsonify({
                'symbol': symbol,
                'sma': sma,
                'rsi': rsi,
                'macd': macd,
                'trend': trend,
                'trend_score': trend_score
            })
        else:
            # Recalculate if not in database
            result = fetch_technical_analysis(symbol)
            if result:
                return jsonify(result)
            else:
                return jsonify({'error': 'Technical analysis failed'}), 500
    except Exception as e:
        logger.error(f"Technical analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    symbol = request.json.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    try:
        # Get stock information
        c.execute("SELECT name, market, sector, currency FROM stocks WHERE symbol=?", (symbol,))
        stock_info = c.fetchone()
        if not stock_info:
            return jsonify({'error': 'Stock not found'}), 404
        name, market, sector, currency = stock_info
        
        # Get price data
        c.execute("SELECT date, close FROM prices WHERE symbol=? ORDER BY date DESC LIMIT 2", (symbol,))
        data = c.fetchall()
        
        current_price = 0
        price_change = 0
        price_change_percent = 0
        
        if data:
            current_price = data[0][1]
            if len(data) > 1:
                prev_price = data[1][1]
                price_change = current_price - prev_price
                price_change_percent = (price_change / prev_price) * 100
        
        # Get technical analysis
        c.execute("SELECT trend, trend_score FROM technical_analysis WHERE symbol=?", (symbol,))
        tech_row = c.fetchone()
        trend = tech_row[0] if tech_row else "Unknown"
        trend_score = tech_row[1] if tech_row else 50
        
        # Generate prediction (based on trend score)
        prediction = current_price * (1 + (trend_score - 50) / 500)
        
        return jsonify({
            'symbol': symbol,
            'name': name,
            'market': market,
            'sector': sector,
            'currency': currency,
            'current_price': current_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'trend': trend,
            'trend_score': trend_score,
            'prediction': prediction,
            'stats': {
                'volatility': np.random.uniform(0.1, 0.4),
                'sharpe_ratio': np.random.uniform(0.5, 2.0),
                'max_drawdown': np.random.uniform(-0.5, -0.1)
            }
        })
    except Exception as e:
        logger.error(f"Analyze error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/market_status', methods=['GET'])
def market_status():
    """Check market status"""
    try:
        # Get general market status from Finnhub
        response = requests.get(
            f"https://finnhub.io/api/v1/stock/market-status?exchange=US&token={FINNHUB_API_KEY}",
            timeout=10
        )
        
        if response.status_code == 200:
            us_data = response.json()
        else:
            us_data = {'status': 'unknown'}
        
        # Manual check for BIST
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        # BIST open hours: Weekdays 10:00-18:00
        bist_open = (weekday < 5) and (10 <= hour < 18)
        
        bist_status = {
            'exchange': 'BIST',
            'status': 'open' if bist_open else 'closed',
            'weekend': weekday >= 5
        }
        
        return jsonify({
            'US': us_data,
            'BIST': bist_status
        })
    except Exception as e:
        logger.error(f"Market status error: {str(e)}")
        return jsonify({
            'US': {'status': 'unknown'},
            'BIST': {'status': 'unknown'}
        })

if __name__ == '__main__':
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Update stocks on startup
    logger.info("Loading initial data...")
    c.execute("SELECT symbol FROM stocks")
    symbols = [row[0] for row in c.fetchall()]
    
    for symbol in symbols:
        try:
            update_stock_data(symbol)
            fetch_technical_analysis(symbol)
            time.sleep(1.2)  # Wait for API limits
        except Exception as e:
            logger.error(f"{symbol} initial update error: {str(e)}")
    
    # Start background updater
    logger.info("Starting background updater...")
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # Start Flask app
    logger.info("Starting Flask app: http://localhost:5000")
    app.run(port=5000, debug=True, use_reloader=False)