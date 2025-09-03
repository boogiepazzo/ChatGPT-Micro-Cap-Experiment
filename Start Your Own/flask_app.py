from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import json
import logging

# Add the parent directory to path to import the trading script
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import functions from the main trading script
from trading_script import (
    download_price_data, 
    process_portfolio, 
    daily_results, 
    load_latest_portfolio_state,
    set_data_dir,
    PORTFOLIO_CSV,
    TRADE_LOG_CSV,
    last_trading_date,
    check_weekend
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class PortfolioPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    cost_basis = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, default=0.0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
class TradeLogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # BUY, SELL
    shares = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    pnl = db.Column(db.Float, default=0.0)
    reason = db.Column(db.String(200))
    
class PortfolioSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    cash_balance = db.Column(db.Float, nullable=False)
    total_equity = db.Column(db.Float, nullable=False)
    pnl = db.Column(db.Float, default=0.0)

# Set data directory to current folder
DATA_DIR = Path(__file__).resolve().parent
set_data_dir(DATA_DIR)

def get_current_price(ticker):
    """Get current price for a ticker using the trading script's data fetching"""
    try:
        today = last_trading_date()
        start_date = today - timedelta(days=1)
        end_date = today + timedelta(days=1)
        
        fetch_result = download_price_data(
            ticker, 
            start=start_date, 
            end=end_date, 
            progress=False
        )
        
        if not fetch_result.df.empty:
            return float(fetch_result.df['Close'].iloc[-1])
        return None
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        return None

def load_portfolio_from_csv():
    """Load portfolio from CSV file"""
    try:
        if PORTFOLIO_CSV.exists():
            portfolio, cash = load_latest_portfolio_state(str(PORTFOLIO_CSV))
            # Convert list to DataFrame if necessary
            if isinstance(portfolio, list):
                if portfolio:
                    portfolio = pd.DataFrame(portfolio)
                else:
                    portfolio = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
            elif portfolio is None:
                portfolio = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
            return portfolio, cash
        else:
            return pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"]), 10000.0  # Default starting cash
    except Exception as e:
        logger.error(f"Error loading portfolio: {e}")
        return pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"]), 10000.0

def save_portfolio_to_csv(portfolio_df, cash):
    """Save portfolio to CSV file"""
    try:
        # Create a snapshot row for today
        today = check_weekend()
        total_value = 0
        total_pnl = 0
        
        results = []
        
        # Handle empty portfolio
        if portfolio_df is None or portfolio_df.empty:
            # Just add total row for empty portfolio
            total_row = {
                "Date": today, "Ticker": "TOTAL", "Shares": "", "Buy Price": "",
                "Cost Basis": "", "Stop Loss": "", "Current Price": "",
                "Total Value": round(total_value, 2), "PnL": round(total_pnl, 2),
                "Action": "", "Cash Balance": round(cash, 2),
                "Total Equity": round(total_value + cash, 2),
            }
            results.append(total_row)
        else:
            # Process portfolio positions
            for _, stock in portfolio_df.iterrows():
                ticker = str(stock["ticker"]).upper()
                shares = float(stock["shares"]) if not pd.isna(stock["shares"]) else 0
                cost = float(stock["buy_price"]) if not pd.isna(stock["buy_price"]) else 0.0
                cost_basis = float(stock["cost_basis"]) if not pd.isna(stock["cost_basis"]) else cost * shares
                stop = float(stock["stop_loss"]) if not pd.isna(stock["stop_loss"]) else 0.0
                
                current_price = get_current_price(ticker)
                if current_price:
                    price = round(current_price, 2)
                    value = round(price * shares, 2)
                    pnl = round((price - cost) * shares, 2)
                    total_value += value
                    total_pnl += pnl
                    action = "HOLD"
                else:
                    price = ""
                    value = ""
                    pnl = ""
                    action = "NO DATA"
                
                row = {
                    "Date": today, "Ticker": ticker, "Shares": shares,
                    "Buy Price": cost, "Cost Basis": cost_basis, "Stop Loss": stop,
                    "Current Price": price, "Total Value": value, "PnL": pnl,
                    "Action": action, "Cash Balance": "", "Total Equity": "",
                }
                results.append(row)
            
            # Add total row
            total_row = {
                "Date": today, "Ticker": "TOTAL", "Shares": "", "Buy Price": "",
                "Cost Basis": "", "Stop Loss": "", "Current Price": "",
                "Total Value": round(total_value, 2), "PnL": round(total_pnl, 2),
                "Action": "", "Cash Balance": round(cash, 2),
                "Total Equity": round(total_value + cash, 2),
            }
            results.append(total_row)
        
        df_out = pd.DataFrame(results)
        
        # Append to existing CSV or create new
        if PORTFOLIO_CSV.exists():
            existing = pd.read_csv(PORTFOLIO_CSV)
            existing = existing[existing["Date"] != str(today)]
            df_out = pd.concat([existing, df_out], ignore_index=True)
        
        df_out.to_csv(PORTFOLIO_CSV, index=False)
        return True
    except Exception as e:
        logger.error(f"Error saving portfolio: {e}")
        return False

def is_first_time_setup():
    """Check if this is the first time setup (no portfolio file exists)"""
    return not PORTFOLIO_CSV.exists()

@app.route('/')
def index():
    """Main entry point - redirect to setup or dashboard"""
    if is_first_time_setup():
        return redirect(url_for('setup'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup page for portfolio value"""
    if request.method == 'POST':
        try:
            initial_cash = float(request.form['initial_cash'])
            if initial_cash <= 0:
                flash('Initial portfolio value must be greater than 0', 'error')
                return render_template('setup.html')
            
            # Create initial portfolio with just cash
            today = check_weekend()
            initial_row = {
                "Date": today, "Ticker": "TOTAL", "Shares": "", "Buy Price": "",
                "Cost Basis": "", "Stop Loss": "", "Current Price": "",
                "Total Value": 0.0, "PnL": 0.0,
                "Action": "", "Cash Balance": round(initial_cash, 2),
                "Total Equity": round(initial_cash, 2),
            }
            
            df_out = pd.DataFrame([initial_row])
            df_out.to_csv(PORTFOLIO_CSV, index=False)
            
            flash(f'Portfolio initialized with ${initial_cash:,.2f}', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError:
            flash('Please enter a valid number for initial portfolio value', 'error')
            return render_template('setup.html')
    
    return render_template('setup.html')

@app.route('/reset_portfolio', methods=['GET', 'POST'])
def reset_portfolio():
    """Reset portfolio - clear all positions but keep logs"""
    if request.method == 'POST':
        try:
            # Get current cash balance
            portfolio_df, cash = load_portfolio_from_csv()
            
            # Create new portfolio with just cash
            today = check_weekend()
            reset_row = {
                "Date": today, "Ticker": "TOTAL", "Shares": "", "Buy Price": "",
                "Cost Basis": "", "Stop Loss": "", "Current Price": "",
                "Total Value": 0.0, "PnL": 0.0,
                "Action": "RESET", "Cash Balance": round(cash, 2),
                "Total Equity": round(cash, 2),
            }
            
            # Append reset row to existing portfolio history
            if PORTFOLIO_CSV.exists():
                existing = pd.read_csv(PORTFOLIO_CSV)
                df_out = pd.concat([existing, pd.DataFrame([reset_row])], ignore_index=True)
            else:
                df_out = pd.DataFrame([reset_row])
            
            df_out.to_csv(PORTFOLIO_CSV, index=False)
            
            flash('Portfolio reset successfully. All positions cleared, logs preserved.', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Error resetting portfolio: {e}")
            flash(f'Error resetting portfolio: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    return render_template('reset_portfolio.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard showing portfolio overview"""
    portfolio_df, cash = load_portfolio_from_csv()
    
    # Calculate current portfolio value
    total_value = 0
    portfolio_data = []
    
    # Handle case where portfolio_df might be a list or None
    if isinstance(portfolio_df, list):
        if portfolio_df:
            portfolio_df = pd.DataFrame(portfolio_df)
        else:
            portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
    elif portfolio_df is None:
        portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
    
    # Only process if portfolio_df is not empty
    if not portfolio_df.empty:
        for _, stock in portfolio_df.iterrows():
            ticker = str(stock["ticker"]).upper()
            shares = float(stock["shares"]) if not pd.isna(stock["shares"]) else 0
            cost = float(stock["buy_price"]) if not pd.isna(stock["buy_price"]) else 0.0
            cost_basis = float(stock["cost_basis"]) if not pd.isna(stock["cost_basis"]) else cost * shares
            stop = float(stock["stop_loss"]) if not pd.isna(stock["stop_loss"]) else 0.0
            
            current_price = get_current_price(ticker)
            if current_price:
                current_value = current_price * shares
                current_pnl = (current_price - cost) * shares
                total_value += current_value
            else:
                current_price = 0
                current_value = 0
                current_pnl = 0
            
            portfolio_data.append({
                'ticker': ticker,
                'shares': shares,
                'buy_price': cost,
                'cost_basis': cost_basis,
                'stop_loss': stop,
                'current_price': current_price,
                'current_value': current_value,
                'current_pnl': current_pnl
            })
    
    total_equity = total_value + cash
    
    return render_template('dashboard.html', 
                         portfolio=portfolio_data,
                         total_value=total_value,
                         cash_balance=cash,
                         total_equity=total_equity)

@app.route('/trade', methods=['GET', 'POST'])
def trade():
    """Execute trades"""
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        action = request.form['action']
        shares = float(request.form['shares'])
        price = float(request.form['price'])
        stop_loss = float(request.form.get('stop_loss', 0))
        
        portfolio_df, cash = load_portfolio_from_csv()
        
        if action == 'BUY':
            # Check if we have enough cash
            cost = shares * price
            if cost > cash:
                flash(f'Insufficient cash. Need ${cost:.2f}, have ${cash:.2f}', 'error')
                return redirect(url_for('trade'))
            
            # Add to portfolio
            if isinstance(portfolio_df, list) or portfolio_df.empty:
                portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
            
            existing_rows = portfolio_df[portfolio_df["ticker"].astype(str).str.upper() == ticker.upper()]
            
            if existing_rows.empty:
                new_position = {
                    "ticker": ticker,
                    "shares": shares,
                    "stop_loss": stop_loss,
                    "buy_price": price,
                    "cost_basis": cost
                }
                portfolio_df = pd.concat([portfolio_df, pd.DataFrame([new_position])], ignore_index=True)
            else:
                # Update existing position
                idx = existing_rows.index[0]
                cur_shares = float(portfolio_df.at[idx, "shares"])
                cur_cost = float(portfolio_df.at[idx, "cost_basis"])
                new_shares = cur_shares + shares
                new_cost = cur_cost + cost
                avg_price = new_cost / new_shares
                
                portfolio_df.at[idx, "shares"] = new_shares
                portfolio_df.at[idx, "cost_basis"] = new_cost
                portfolio_df.at[idx, "buy_price"] = avg_price
                portfolio_df.at[idx, "stop_loss"] = max(portfolio_df.at[idx, "stop_loss"], stop_loss)
            
            cash -= cost
            flash(f'Bought {shares} shares of {ticker} at ${price:.2f}', 'success')
            
        elif action == 'SELL':
            # Handle case where portfolio_df might be a list
            if isinstance(portfolio_df, list):
                portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
            
            existing_rows = portfolio_df[portfolio_df["ticker"].astype(str).str.upper() == ticker.upper()]
            
            if existing_rows.empty:
                flash(f'No position in {ticker}', 'error')
                return redirect(url_for('trade'))
            
            current_shares = float(existing_rows.iloc[0]["shares"])
            if shares > current_shares:
                flash(f'Insufficient shares. Have {current_shares}, trying to sell {shares}', 'error')
                return redirect(url_for('trade'))
            
            # Calculate P&L
            buy_price = float(existing_rows.iloc[0]["buy_price"])
            pnl = (price - buy_price) * shares
            
            # Update position
            idx = existing_rows.index[0]
            if shares == current_shares:
                # Sell entire position
                portfolio_df = portfolio_df[portfolio_df["ticker"] != ticker]
            else:
                # Partial sell
                portfolio_df.at[idx, "shares"] = current_shares - shares
                portfolio_df.at[idx, "cost_basis"] = portfolio_df.at[idx, "shares"] * buy_price
            
            cash += shares * price
            flash(f'Sold {shares} shares of {ticker} at ${price:.2f}. P&L: ${pnl:.2f}', 'success')
        
        # Save updated portfolio
        save_portfolio_to_csv(portfolio_df, cash)
        return redirect(url_for('dashboard'))
    
    # Load current portfolio for display
    portfolio_df, cash = load_portfolio_from_csv()
    total_value = 0
    portfolio_data = []
    
    # Handle case where portfolio_df might be a list or None
    if isinstance(portfolio_df, list):
        if portfolio_df:
            portfolio_df = pd.DataFrame(portfolio_df)
        else:
            portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
    elif portfolio_df is None:
        portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
    
    # Only process if portfolio_df is not empty
    if not portfolio_df.empty:
        for _, stock in portfolio_df.iterrows():
            ticker = str(stock["ticker"]).upper()
            shares = float(stock["shares"]) if not pd.isna(stock["shares"]) else 0
            cost = float(stock["buy_price"]) if not pd.isna(stock["buy_price"]) else 0.0
            cost_basis = float(stock["cost_basis"]) if not pd.isna(stock["cost_basis"]) else cost * shares
            stop = float(stock["stop_loss"]) if not pd.isna(stock["stop_loss"]) else 0.0
            
            current_price = get_current_price(ticker)
            if current_price:
                current_value = current_price * shares
                current_pnl = (current_price - cost) * shares
                total_value += current_value
            else:
                current_price = 0
                current_value = 0
                current_pnl = 0
            
            portfolio_data.append({
                'ticker': ticker,
                'shares': shares,
                'buy_price': cost,
                'cost_basis': cost_basis,
                'stop_loss': stop,
                'current_price': current_price,
                'current_value': current_value,
                'current_pnl': current_pnl
            })
    
    return render_template('trade.html', 
                         portfolio=portfolio_data,
                         total_value=total_value,
                         cash_balance=cash)

@app.route('/api/price/<ticker>')
def get_price_api(ticker):
    """API endpoint for current price"""
    price = get_current_price(ticker)
    return jsonify({'ticker': ticker, 'price': price})

@app.route('/api/search_tickers')
def search_tickers_api():
    """API endpoint for ticker search"""
    query = request.args.get('q', '').upper()
    if len(query) < 1:
        return jsonify({'tickers': []})
    
    # Common stock tickers for suggestions
    common_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
        'JPM', 'BAC', 'WMT', 'DIS', 'KO', 'PEP', 'ABT', 'JNJ', 'PG', 'V',
        'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'GLD', 'SLV',
        'TQQQ', 'SQQQ', 'UVXY', 'VIXY', 'TLT', 'LQD', 'HYG', 'EMB', 'EFA', 'EEM'
    ]
    
    # Filter tickers that match the query
    matching_tickers = [ticker for ticker in common_tickers if query in ticker]
    
    # Limit results to 10 suggestions
    suggestions = matching_tickers[:10]
    
    return jsonify({'tickers': suggestions})

@app.route('/api/ticker_info/<ticker>')
def ticker_info_api(ticker):
    """API endpoint for ticker information including current price"""
    try:
        current_price = get_current_price(ticker)
        
        # Get additional info from yfinance
        import yfinance as yf
        ticker_info = yf.Ticker(ticker)
        info = ticker_info.info
        
        ticker_data = {
            'ticker': ticker,
            'current_price': current_price,
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'volume': info.get('volume', 0),
            'previous_close': info.get('previousClose', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0)
        }
        
        return jsonify(ticker_data)
    except Exception as e:
        logger.error(f"Error getting ticker info for {ticker}: {e}")
        return jsonify({
            'ticker': ticker,
            'current_price': get_current_price(ticker),
            'name': ticker,
            'sector': 'Unknown',
            'market_cap': 0,
            'volume': 0,
            'previous_close': 0,
            'day_high': 0,
            'day_low': 0
        })

@app.route('/analytics')
def analytics():
    """Performance analytics page"""
    try:
        if PORTFOLIO_CSV.exists():
            df = pd.read_csv(PORTFOLIO_CSV)
            totals = df[df["Ticker"] == "TOTAL"].copy()
            
            if not totals.empty:
                totals["Date"] = pd.to_datetime(totals["Date"])
                totals = totals.sort_values("Date")
                
                # Calculate basic metrics
                final_equity = float(totals.iloc[-1]["Total Equity"])
                initial_equity = float(totals.iloc[0]["Total Equity"])
                total_return = (final_equity - initial_equity) / initial_equity
                
                # Calculate daily returns
                equity_series = totals.set_index("Date")["Total Equity"].astype(float)
                daily_returns = equity_series.pct_change().dropna()
                
                if len(daily_returns) > 1:
                    volatility = daily_returns.std() * np.sqrt(252)  # Annualized
                    sharpe_ratio = (daily_returns.mean() * 252) / volatility if volatility > 0 else 0
                    
                    # Max drawdown
                    running_max = equity_series.cummax()
                    drawdowns = (equity_series / running_max) - 1.0
                    max_drawdown = float(drawdowns.min())
                    
                    metrics = {
                        'total_return': total_return,
                        'volatility': volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'max_drawdown': max_drawdown,
                        'final_equity': final_equity,
                        'initial_equity': initial_equity
                    }
                else:
                    metrics = {'message': 'Insufficient data for analytics'}
            else:
                metrics = {'message': 'No portfolio data available'}
        else:
            metrics = {'message': 'No portfolio file found'}
            
    except Exception as e:
        logger.error(f"Error calculating analytics: {e}")
        metrics = {'error': str(e)}
    
    return render_template('analytics.html', metrics=metrics)

@app.route('/run_daily_update')
def run_daily_update():
    """Run the daily portfolio update process"""
    try:
        portfolio_df, cash = load_portfolio_from_csv()
        
        # Handle case where portfolio_df might be a list or None
        if isinstance(portfolio_df, list):
            if portfolio_df:
                portfolio_df = pd.DataFrame(portfolio_df)
            else:
                portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
        elif portfolio_df is None:
            portfolio_df = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
        
        # Run the portfolio processing (non-interactive)
        updated_portfolio, updated_cash = process_portfolio(
            portfolio_df, 
            cash, 
            interactive=False
        )
        
        # Save the results
        save_portfolio_to_csv(updated_portfolio, updated_cash)
        
        flash('Daily portfolio update completed successfully', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error in daily update: {e}")
        flash(f'Error during daily update: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/portfolio_history')
def portfolio_history():
    """Show portfolio history"""
    try:
        if PORTFOLIO_CSV.exists():
            df = pd.read_csv(PORTFOLIO_CSV)
            totals = df[df["Ticker"] == "TOTAL"].copy()
            
            if not totals.empty:
                totals["Date"] = pd.to_datetime(totals["Date"])
                totals = totals.sort_values("Date")
                
                history_data = []
                for _, row in totals.iterrows():
                    history_data.append({
                        'date': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                        'total_value': row['Total Value'],
                        'cash_balance': row['Cash Balance'],
                        'total_equity': row['Total Equity'],
                        'pnl': row['PnL']
                    })
            else:
                history_data = []
        else:
            history_data = []
            
    except Exception as e:
        logger.error(f"Error loading portfolio history: {e}")
        history_data = []
    
    return render_template('portfolio_history.html', history=history_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
