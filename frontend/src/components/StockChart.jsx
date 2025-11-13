import { useState, useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import './StockChart.css';

export default function StockChart({ ticker }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const [timeframe, setTimeframe] = useState('1M');
  const [chartType, setChartType] = useState('candlestick');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const timeframes = [
    { label: '1D', value: '1D' },
    { label: '1W', value: '1W' },
    { label: '1M', value: '1M' },
    { label: '3M', value: '3M' },
    { label: '1Y', value: '1Y' },
    { label: '5Y', value: '5Y' }
  ];

  useEffect(() => {
    if (!ticker || !chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
      },
    });

    chartRef.current = chart;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Fetch and render data
    fetchChartData();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [ticker, timeframe, chartType]);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/stock/chart/${ticker}?timeframe=${timeframe}`
      );

      if (!response.ok) throw new Error('Failed to fetch chart data');

      const data = await response.json();
      renderChart(data);
    } catch (err) {
      console.error('Chart fetch error:', err);
      setError('Chart data unavailable');
    } finally {
      setLoading(false);
    }
  };

  const renderChart = (data) => {
    if (!chartRef.current || !data.prices || data.prices.length === 0) return;

    // Clear existing series
    chartRef.current.remove();
    
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
      },
    });

    chartRef.current = chart;

    // Add price series
    if (chartType === 'candlestick') {
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      });
      candlestickSeries.setData(data.prices);
    } else {
      const lineSeries = chart.addLineSeries({
        color: '#2962FF',
        lineWidth: 2,
      });
      const lineData = data.prices.map(p => ({
        time: p.time,
        value: p.close
      }));
      lineSeries.setData(lineData);
    }

    // Add volume series
    if (data.volumes && data.volumes.length > 0) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });
      volumeSeries.setData(data.volumes);
    }

    chart.timeScale().fitContent();
  };

  if (!ticker) return null;

  return (
    <div className="stock-chart-container">
      <div className="chart-controls">
        <div className="chart-type-selector">
          <button
            className={chartType === 'candlestick' ? 'active' : ''}
            onClick={() => setChartType('candlestick')}
          >
            📊 Candlestick
          </button>
          <button
            className={chartType === 'line' ? 'active' : ''}
            onClick={() => setChartType('line')}
          >
            📈 Line
          </button>
        </div>

        <div className="timeframe-selector">
          {timeframes.map(tf => (
            <button
              key={tf.value}
              className={timeframe === tf.value ? 'active' : ''}
              onClick={() => setTimeframe(tf.value)}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="chart-loading">
          <div className="spinner"></div>
          <p>Loading chart...</p>
        </div>
      )}

      {error && (
        <div className="chart-error">
          <p>{error}</p>
        </div>
      )}

      <div ref={chartContainerRef} className="chart-canvas" />
    </div>
  );
}
