"""
Stock-related API routes
Handles stock prices, charts, alerts, and market data
"""
from flask import Blueprint, request, jsonify
from services.stock_price_service import stock_price_service
from chart_service import chart_service
from price_alerts_service import price_alerts_service
from market_overview_service import market_overview_service
from auth_service import require_auth
import logging

logger = logging.getLogger(__name__)

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/api/stock/price/<ticker>', methods=['GET'])
def get_stock_price(ticker):
    """Get current price for a single stock"""
    try:
        price_data = stock_price_service.get_stock_price(ticker)
        
        if not price_data:
            return jsonify({'error': 'Price data not available'}), 404
        
        return jsonify(price_data)
        
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/stock/prices', methods=['GET'])
def get_multiple_prices():
    """Get prices for multiple stocks"""
    try:
        tickers_param = request.args.get('tickers', '')
        
        if not tickers_param:
            return jsonify({'error': 'No tickers provided'}), 400
        
        tickers = [t.strip().upper() for t in tickers_param.split(',')]
        
        if len(tickers) > 20:
            return jsonify({'error': 'Too many tickers (max 20)'}), 400
        
        prices = stock_price_service.get_multiple_prices(tickers)
        
        return jsonify({'prices': prices})
        
    except Exception as e:
        logger.error(f"Error fetching multiple prices: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/stock/chart/<ticker>', methods=['GET'])
def get_chart_data(ticker):
    """Get historical chart data for a stock"""
    try:
        timeframe = request.args.get('timeframe', '1M')
        
        chart_data = chart_service.get_chart_data(ticker, timeframe)
        
        if not chart_data:
            return jsonify({'error': 'Chart data not available'}), 404
        
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error fetching chart for {ticker}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/alerts', methods=['GET'])
@require_auth
def get_alerts(user_id):
    """Get all alerts for the authenticated user"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        alerts = price_alerts_service.get_user_alerts(user_id, active_only)
        
        return jsonify({'alerts': alerts})
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/alerts', methods=['POST'])
@require_auth
def create_alert(user_id):
    """Create a new price alert"""
    try:
        data = request.get_json()
        
        ticker = data.get('ticker', '').upper()
        alert_type = data.get('alert_type', 'price')
        target_price = data.get('target_price')
        percentage_change = data.get('percentage_change')
        condition = data.get('condition', 'above')
        
        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400
        
        if alert_type == 'price' and not target_price:
            return jsonify({'error': 'Target price is required'}), 400
        
        if alert_type == 'percentage' and not percentage_change:
            return jsonify({'error': 'Percentage change is required'}), 400
        
        alert_id = price_alerts_service.create_alert(
            user_id=user_id,
            ticker=ticker,
            alert_type=alert_type,
            target_price=float(target_price) if target_price else None,
            percentage_change=float(percentage_change) if percentage_change else None,
            condition=condition
        )
        
        if not alert_id:
            return jsonify({'error': 'Failed to create alert'}), 500
        
        return jsonify({'alert_id': alert_id, 'message': 'Alert created successfully'})
        
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
@require_auth
def delete_alert(user_id, alert_id):
    """Delete a price alert"""
    try:
        success = price_alerts_service.delete_alert(alert_id, user_id)
        
        if not success:
            return jsonify({'error': 'Failed to delete alert'}), 500
        
        return jsonify({'message': 'Alert deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/market/overview', methods=['GET'])
def get_market_overview():
    """Get market overview data"""
    try:
        market_data = market_overview_service.get_market_overview()
        
        if not market_data:
            return jsonify({'error': 'Market data not available'}), 404
        
        return jsonify(market_data)
        
    except Exception as e:
        logger.error(f"Error fetching market overview: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/portfolio/doctor', methods=['GET'])
@require_auth
def get_portfolio_doctor(user_id):
    """Get AI portfolio doctor recommendations"""
    try:
        from portfolio_doctor_service import portfolio_doctor
        from portfolio_service import portfolio_service
        
        # Get portfolio data
        portfolio_data = portfolio_service.get_portfolio_summary(user_id)
        
        # Generate recommendations
        recommendations = portfolio_doctor.get_daily_recommendations(portfolio_data)
        
        return jsonify(recommendations)
        
    except Exception as e:
        logger.error(f"Error getting portfolio doctor: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@stock_bp.route('/api/portfolio/rebalance', methods=['GET'])
@require_auth
def get_rebalancing_plan(user_id):
    """Get smart rebalancing suggestions"""
    try:
        from rebalancing_service import rebalancing_service
        from portfolio_service import portfolio_service
        
        # Get portfolio data
        portfolio_data = portfolio_service.get_portfolio_summary(user_id)
        
        # Generate rebalancing plan
        plan = rebalancing_service.generate_rebalancing_plan(portfolio_data)
        
        return jsonify(plan)
        
    except Exception as e:
        logger.error(f"Error generating rebalancing plan: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
