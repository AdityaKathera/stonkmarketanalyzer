"""Prompt templates for guided research flow"""

def overview_template(ticker, horizon, risk_level):
    return f"""You are an expert equity research analyst. Analyze {ticker} and provide a comprehensive business overview using the MOST RECENT and LATEST data available.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

Please provide:
1. **Business Model**: What does the company do? How does it make money?
2. **Industry Position**: Market share, competitive landscape, and key competitors
3. **Recent Performance**: Latest quarterly results and key metrics (use TODAY'S date as reference)
4. **Management Quality**: Leadership team and track record
5. **Growth Drivers**: Key catalysts and opportunities

IMPORTANT: Use real-time data and the most current information available. Include today's stock price and latest market data. Format your response with clear sections and cite all sources with dates."""

def financials_template(ticker, horizon, risk_level):
    return f"""You are an expert equity research analyst. Conduct a detailed financial analysis of {ticker} using the MOST RECENT financial data available.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

Please analyze:
1. **Revenue & Profitability**: Latest quarterly and annual growth trends, margins, and quality of earnings
2. **Balance Sheet Health**: Current debt levels, liquidity, and capital structure
3. **Cash Flow**: Most recent operating cash flow, free cash flow, and capital allocation
4. **Key Metrics**: Latest ROE, ROIC, P/E ratio, and other relevant financial ratios
5. **Historical Trends**: 3-5 year performance and consistency

IMPORTANT: Use the most current financial data available (latest quarter/year). Provide specific numbers with sources and dates. Highlight any red flags or strengths."""

def moat_template(ticker, horizon, risk_level):
    return f"""You are an expert equity research analyst. Evaluate the competitive moat and sustainable advantages of {ticker}.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

Analyze:
1. **Moat Type**: Network effects, switching costs, intangible assets, cost advantages, or scale
2. **Moat Strength**: Wide, narrow, or no moat? Is it widening or narrowing?
3. **Competitive Threats**: Who could disrupt this business?
4. **Pricing Power**: Can the company raise prices without losing customers?
5. **Durability**: Will these advantages persist over your {horizon} time horizon?

Be critical and evidence-based. Cite specific examples and data."""

def risks_template(ticker, horizon, risk_level):
    return f"""You are an expert equity research analyst. Identify and assess the key risks for {ticker}.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

Evaluate:
1. **Business Risks**: Operational, competitive, and execution risks
2. **Financial Risks**: Leverage, liquidity, and capital structure concerns
3. **Market Risks**: Cyclicality, macro sensitivity, and market dynamics
4. **Regulatory/Legal**: Compliance, litigation, or regulatory changes
5. **ESG Risks**: Environmental, social, and governance concerns

For each risk, assess:
- Probability (High/Medium/Low)
- Potential Impact (High/Medium/Low)
- Mitigation factors

Be thorough and cite recent examples or incidents."""

def valuation_template(ticker, horizon, risk_level):
    return f"""You are an expert equity research analyst. Perform a valuation analysis for {ticker} using REAL-TIME market data.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

Analyze:
1. **Current Valuation**: TODAY'S stock price, P/E, P/S, EV/EBITDA, and other relevant multiples
2. **Historical Context**: How does current valuation compare to historical ranges?
3. **Peer Comparison**: Valuation vs. comparable companies (use latest data)
4. **Growth Expectations**: What growth is priced in at current levels?
5. **Fair Value Range**: Based on multiple approaches (DCF, comps, precedents)

IMPORTANT: Start with the current stock price as of today. Use the most recent market data available. Provide specific numbers with dates and explain your reasoning. Is the stock cheap, fair, or expensive?"""

def memo_template(ticker, horizon, risk_level):
    return f"""You are an expert equity research analyst. Create a comprehensive, neutral investment memo for {ticker}.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

Structure your memo:
1. **Investment Thesis**: Bull and bear cases (balanced view)
2. **Business Quality**: Strengths and weaknesses
3. **Financial Health**: Key metrics and trends
4. **Competitive Position**: Moat assessment
5. **Valuation**: Current pricing and fair value estimate
6. **Key Risks**: Top 3-5 risks to monitor
7. **Catalysts**: Potential positive and negative triggers
8. **Conclusion**: Neutral summary without buy/sell recommendation

Be objective, data-driven, and cite all sources. This should be a professional-grade research report."""

def investment_advice_template(ticker, horizon, risk_level):
    return f"""You are an AI investment advisor analyzing {ticker}. Based on comprehensive analysis of the company's LATEST metrics, financials, competitive position, and CURRENT market conditions, provide a biased investment recommendation.

Investment Context:
- Time Horizon: {horizon}
- Risk Tolerance: {risk_level}

FIRST: State the CURRENT stock price as of TODAY with the exact date.

Then provide:
1. **Investment Recommendation**: Clear BUY, HOLD, or SELL recommendation with conviction level (High/Medium/Low)
2. **Price Prediction**: Predict potential stock price movement (% up or down) over the {horizon} timeframe with specific target price based on current price
3. **Key Drivers**: Top 3-5 factors supporting your prediction (use latest news and data)
4. **Financial Metrics Assessment**: Analyze LATEST P/E ratio, revenue growth, profit margins, debt levels, cash flow
5. **Market Position**: Evaluate competitive advantages and market share trends (current data)
6. **Risk Factors**: Acknowledge key risks that could invalidate your thesis
7. **Entry/Exit Strategy**: Suggested price points for entry and potential exit targets (based on current price)
8. **Confidence Level**: Rate your confidence in this prediction (1-10) with reasoning

CRITICAL: Use REAL-TIME data. Start with today's stock price. Be specific with numbers and percentages. Make a clear, biased call based on the most current data available. Cite all sources with dates.

IMPORTANT: This is AI-generated analysis and should not be considered professional financial advice."""

# Template registry
prompt_templates = {
    'overview': {
        'name': 'Business Overview',
        'template': overview_template
    },
    'financials': {
        'name': 'Financial Analysis',
        'template': financials_template
    },
    'moat': {
        'name': 'Competitive Moat',
        'template': moat_template
    },
    'risks': {
        'name': 'Risk Assessment',
        'template': risks_template
    },
    'valuation': {
        'name': 'Valuation Analysis',
        'template': valuation_template
    },
    'memo': {
        'name': 'Investment Memo',
        'template': memo_template
    },
    'investment_advice': {
        'name': 'Investment Advice by AI',
        'template': investment_advice_template
    }
}

def free_chat_template(ticker, question):
    """Template for free-form chat queries"""
    return f"""You are an expert equity research analyst. Answer the following question about {ticker}:

{question}

Provide a detailed, data-driven response with citations. Be objective and thorough."""
