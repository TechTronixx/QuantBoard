# QuantBoard

I built this cryptocurrency analysis dashboard with Streamlit because I didn't have time to go through and check what's going on in the markets while working. I wanted everything in one place - market insights, technical indicators,

The dashboard includes all the indicators and metrics I've relied on throughout my trading journey. These aren't just random technical tools - they're the ones I've found most useful from my own experience in the markets.

The indicators and results aren't 100% accurate, nor do I claim them to be. Crypto is volatile and unpredictable - this is just a tool to help get a quick overview of market conditions based on technical analysis.

I made this for traders like me who want to quickly assess market conditions without spending hours analyzing different sources. Sometimes you just need that one-shot view to understand what's happening and make informed decisions fast.

The whole idea was simple: save time, get better insights, and have everything I need in a single dashboard.

## Features

- **Real-time Market Data**: Live cryptocurrency prices, market caps, and trading volumes from CoinGecko API
- **Advanced Technical Analysis**: RSI, MACD, Bollinger Bands, Ichimoku Cloud, Fibonacci retracements, and 20+ technical indicators
- **AI-Powered Predictions**: Machine learning models using Random Forest regression for price forecasting
- **Economic Indicators**: Integration with FRED API for S&P 500, VIX, Treasury rates, unemployment data, and Fed rates
- **Fear & Greed Index**: Market sentiment analysis with visual indicators
- **Portfolio Analytics**: Risk assessment, Monte Carlo simulations, and volatility analysis
- **Interactive Charts**: Dynamic Plotly visualizations with zoom, pan, and hover capabilities
- **Dark Glassmorphism UI**: Modern, professional interface with smooth animations and responsive design
- **Commodity Data**: COT (Commitment of Traders) data integration for market sentiment
- **Quantitative Metrics**: GARCH volatility modeling, Sharpe ratios, and advanced risk calculations

## Demo

Demo - [Link](https://quantboard.streamlit.app/)


## Install

1. Clone the repository:

```bash
git clone https://github.com/TechTronixx/QuantBoard.git
cd crypto-dashboard
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up API keys :

```bash
python setup.py
```

4. Run the application:

```bash
streamlit run app.py
```
or 
```bash
py -m streamlit run app.py
```

## Tech Used

- **Frontend**: Streamlit, Custom CSS, HTML5
- **Data Processing**: Pandas, NumPy, SciPy
- **Machine Learning**: Scikit-learn, Random Forest Regression
- **Data Sources**: CoinGecko API, FRED API, Yahoo Finance
- **Visualization**: Plotly, Interactive Charts
- **Technical Analysis**: TA-Lib, Custom indicators
- **Backend**: Python 3.8+, Requests, AsyncIO
- **Deployment**: Streamlit Cloud ready

## Troubleshooting

### Debug Mode

The application includes a built-in debug mode to help diagnose API issues and connectivity problems:

1. **Enable Debug Mode**: Check the "Debug Mode" checkbox in the sidebar settings
2. **API Testing**: Debug mode automatically tests CoinGecko API connectivity on startup
3. **Status Indicators**: Shows real-time API status, rate limits, and connection details
4. **Error Details**: Provides detailed error messages for failed API calls
5. **Validation**: Tests cryptocurrency ID validation and data fetching

### Common Issues

**API Rate Limiting**

- Free CoinGecko tier: 10-50 calls/minute
- Enable debug mode to monitor API usage
- Wait a few minutes before retrying
- Consider upgrading to paid API plan

**Data Loading Issues**

- Check internet connection
- Verify API keys in `.streamlit/secrets.toml`
- Use debug mode to test API connectivity
- Ensure cryptocurrency ID is valid (e.g., "bitcoin" not "BTC")

**Performance Issues**

- Large datasets may take time to load
- Debug mode shows loading progress

### Getting Help

- Enable debug mode for detailed error information
- Check the console for error messages
- Verify all dependencies are installed correctly
- Ensure API keys are properly configured

## Credits

Built with modern web technologies and financial data APIs. Special thanks to CoinGecko and FRED for providing comprehensive market data and economic indicators.

- https://docs.coingecko.com/reference/introduction
- https://fred.stlouisfed.org/docs/api/fred/
