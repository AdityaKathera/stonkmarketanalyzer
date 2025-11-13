# 🌍 International Stocks Support

## Overview

Stonk Market Analyzer now supports international stocks from major exchanges worldwide!

## How to Add International Stocks

### Format: `TICKER.EXCHANGE`

Add the exchange suffix to your ticker symbol:

### Supported Exchanges

| Country | Exchange | Suffix | Example |
|---------|----------|--------|---------|
| 🇮🇳 India (NSE) | National Stock Exchange | `.NS` | `ITC.NS`, `RELIANCE.NS` |
| 🇮🇳 India (BSE) | Bombay Stock Exchange | `.BO` | `ITC.BO`, `RELIANCE.BO` |
| 🇬🇧 UK | London Stock Exchange | `.L` | `BP.L`, `HSBA.L` |
| 🇨🇦 Canada | Toronto Stock Exchange | `.TO` | `SHOP.TO`, `TD.TO` |
| 🇭🇰 Hong Kong | Hong Kong Stock Exchange | `.HK` | `0700.HK`, `0005.HK` |
| 🇯🇵 Japan | Tokyo Stock Exchange | `.T` | `7203.T`, `9984.T` |
| 🇦🇺 Australia | Australian Securities Exchange | `.AX` | `BHP.AX`, `CBA.AX` |
| 🇩🇪 Germany | Frankfurt Stock Exchange | `.DE` | `VOW3.DE`, `SAP.DE` |
| 🇫🇷 France | Euronext Paris | `.PA` | `MC.PA`, `OR.PA` |
| 🇺🇸 USA | NASDAQ/NYSE | (none) | `AAPL`, `TSLA` |

## Popular Indian Stocks

### How to Add

For Indian stocks, use the `.NS` suffix (NSE is more liquid):

```
ITC.NS          - ITC Limited
RELIANCE.NS     - Reliance Industries
TCS.NS          - Tata Consultancy Services
INFY.NS         - Infosys
HDFCBANK.NS     - HDFC Bank
ICICIBANK.NS    - ICICI Bank
SBIN.NS         - State Bank of India
BHARTIARTL.NS   - Bharti Airtel
HINDUNILVR.NS   - Hindustan Unilever
KOTAKBANK.NS    - Kotak Mahindra Bank
```

### Alternative: BSE

You can also use `.BO` for BSE:
```
ITC.BO
RELIANCE.BO
```

## Features That Work

All features work with international stocks:

✅ **Portfolio Tracking** - Add holdings with purchase price  
✅ **Real-time Prices** - Yahoo Finance provides global data  
✅ **News Feed** - AI-powered news summaries  
✅ **Social Sentiment** - Community sentiment analysis  
✅ **Portfolio Insights** - AI-powered recommendations  

## How It Works

### 1. Price Data
- Uses Yahoo Finance API (supports 100+ exchanges)
- Real-time quotes for most major markets
- Automatic currency conversion

### 2. News & Sentiment
- AI analyzes global news sources
- Perplexity API provides market insights
- Fallback links to Google Finance (exchange-aware)

### 3. Exchange Detection
The system automatically detects the exchange:
- Checks ticker suffix (`.NS`, `.L`, etc.)
- Recognizes popular Indian stocks (ITC, RELIANCE, etc.)
- Provides appropriate links for each market

## Examples

### Adding ITC (Indian Stock)

**Step 1**: Go to Portfolio tab  
**Step 2**: Click "Add Holding"  
**Step 3**: Enter:
- Ticker: `ITC.NS`
- Shares: `100`
- Purchase Price: `450.00`

**Step 4**: Save

### Viewing News

The News tab will show:
- AI-generated summaries
- Links to NSE/BSE data
- Google Finance India links

### Checking Sentiment

The Sentiment tab will analyze:
- Indian market discussions
- Local news sentiment
- Community mood

## Troubleshooting

### "No price data available"

**Solution**: Make sure you're using the correct exchange suffix:
- ✅ `ITC.NS` (correct)
- ❌ `ITC` (won't work for Indian stocks)

### "News not loading"

**Solution**: 
- News API has limited coverage for some markets
- System will provide fallback links to Google Finance
- AI will still generate market insights

### "Wrong currency"

**Note**: Yahoo Finance returns prices in local currency:
- Indian stocks: INR (₹)
- UK stocks: GBP (£)
- US stocks: USD ($)

## Best Practices

1. **Use NSE for Indian stocks** (`.NS`) - more liquid than BSE
2. **Check Yahoo Finance** first to verify ticker format
3. **Add exchange suffix** for all non-US stocks
4. **Use local currency** when entering purchase price

## Future Enhancements

Coming soon:
- 🔄 Automatic currency conversion
- 📊 Exchange-specific market hours
- 🌐 Multi-language support
- 📈 Regional market indices

## Need Help?

Can't find your stock? Check:
1. **Yahoo Finance**: https://finance.yahoo.com
2. **Google Finance**: https://www.google.com/finance
3. Look for the ticker symbol with exchange suffix

---

**Last Updated**: November 13, 2024  
**Status**: ✅ International stocks fully supported
