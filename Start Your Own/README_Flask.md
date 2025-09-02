# Flask Trading Portfolio Web Application

This is a web-based interface for the ChatGPT Micro-Cap Trading Experiment, built with Flask. It provides a modern, user-friendly way to manage your trading portfolio through a web browser.

## Features

- **Dashboard**: Real-time portfolio overview with current positions and performance
- **Trading Interface**: Easy-to-use forms for buying and selling stocks
- **Analytics**: Performance metrics including Sharpe ratio, volatility, and drawdown
- **Portfolio History**: Historical performance data with charts
- **Real-time Price Updates**: Live stock price fetching
- **CSV Integration**: Works with existing CSV files from the original trading script

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_flask.txt
   ```

2. **Set up environment variables (optional):**
   Create a `.env` file in the "Start Your Own" directory:
   ```
   SECRET_KEY=your-secret-key-here
   ```

## Usage

1. **Start the Flask application:**
   ```bash
   cd "Start Your Own"
   python flask_app.py
   ```

2. **Access the web interface:**
   Open your browser and go to `http://localhost:5000`

3. **Navigate the application:**
   - **Dashboard**: View your current portfolio and performance
   - **Trade**: Execute buy/sell orders
   - **Analytics**: View performance metrics and charts
   - **History**: See historical portfolio data

## Web Interface Features

### Dashboard
- Real-time portfolio value and cash balance
- Current positions with live pricing
- Quick action buttons for common tasks
- Auto-refresh every 30 seconds

### Trading
- Simple forms for buy/sell orders
- Real-time price fetching
- Trade confirmation modals
- Portfolio summary sidebar

### Analytics
- Performance metrics (Sharpe ratio, volatility, drawdown)
- Interactive charts using Chart.js
- Risk assessment indicators
- Performance interpretation guide

### Portfolio History
- Historical performance table
- Equity growth charts
- Export functionality (CSV, PDF)
- Summary statistics

## Integration with Original Script

The Flask app integrates seamlessly with the original trading script:

- **Uses the same CSV files**: `chatgpt_portfolio_update.csv` and `chatgpt_trade_log.csv`
- **Same data fetching**: Uses the original script's `download_price_data` function
- **Compatible data format**: Maintains the same CSV structure
- **Can run alongside**: You can still use the original command-line script

## API Endpoints

- `GET /`: Dashboard
- `GET /trade`: Trading interface
- `POST /trade`: Execute trades
- `GET /analytics`: Performance analytics
- `GET /portfolio_history`: Historical data
- `GET /api/price/<ticker>`: Get current price for a ticker
- `GET /run_daily_update`: Run the daily portfolio update

## Data Flow

1. **Portfolio Loading**: Reads from `chatgpt_portfolio_update.csv`
2. **Price Updates**: Fetches current prices using the original script's data sources
3. **Trade Execution**: Updates portfolio and saves to CSV
4. **Analytics**: Calculates performance metrics from historical data
5. **Charts**: Displays interactive charts using Chart.js

## Security Notes

- The app runs in debug mode by default (for development)
- Set a proper `SECRET_KEY` for production use
- Consider adding authentication for multi-user environments
- The app binds to `0.0.0.0:5000` by default

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running from the "Start Your Own" directory
2. **CSV not found**: Ensure `chatgpt_portfolio_update.csv` exists in the directory
3. **Price fetching fails**: Check internet connection and ticker symbols
4. **Database errors**: The SQLite database will be created automatically

### Debug Mode

The app runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Future Enhancements

- User authentication and multi-user support
- Real-time WebSocket updates
- Advanced charting with more indicators
- Email notifications for stop-loss triggers
- Mobile-responsive design improvements
- Integration with additional data sources (Tiingo, Alpha Vantage)

## Contributing

Feel free to modify and enhance the Flask application. The modular design makes it easy to add new features while maintaining compatibility with the original trading script.
