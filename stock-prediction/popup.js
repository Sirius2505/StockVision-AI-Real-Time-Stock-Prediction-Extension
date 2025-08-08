// Mock data for the application
const mockStocks = [
    { symbol: 'THYAO.IS', name: 'Turkish Airlines', market: 'BIST', price: 249.75, change: 1.25, currency: '₺' },
    { symbol: 'AKBNK.IS', name: 'Akbank', market: 'BIST', price: 56.30, change: 0.75, currency: '₺' },
    { symbol: 'GARAN.IS', name: 'Garanti BBVA', market: 'BIST', price: 89.45, change: -0.45, currency: '₺' },
    { symbol: 'SISE.IS', name: 'Şişe Cam', market: 'BIST', price: 42.80, change: 2.10, currency: '₺' },
    { symbol: 'ASELS.IS', name: 'Aselsan', market: 'BIST', price: 65.20, change: 1.80, currency: '₺' },
    { symbol: 'KCHOL.IS', name: 'Koç Holding', market: 'BIST', price: 320.50, change: -1.20, currency: '₺' },
    { symbol: 'TCELL.IS', name: 'Turkcell', market: 'BIST', price: 98.75, change: 0.35, currency: '₺' },
    { symbol: 'EREGL.IS', name: 'Ereğli Iron Steel', market: 'BIST', price: 56.90, change: 2.75, currency: '₺' },
    { symbol: 'AAPL', name: 'Apple Inc.', market: 'US', price: 175.25, change: 0.92, currency: '$' },
    { symbol: 'MSFT', name: 'Microsoft', market: 'US', price: 330.45, change: 1.15, currency: '$' },
    { symbol: 'GOOGL', name: 'Alphabet', market: 'US', price: 145.80, change: -0.25, currency: '$' },
    { symbol: 'TSLA', name: 'Tesla Inc.', market: 'US', price: 210.75, change: 3.20, currency: '$' },
    { symbol: 'AMZN', name: 'Amazon', market: 'US', price: 185.30, change: 0.65, currency: '$' },
    { symbol: 'META', name: 'Meta Platforms', market: 'US', price: 495.60, change: -0.85, currency: '$' },
    { symbol: 'JPM', name: 'JPMorgan Chase', market: 'US', price: 198.45, change: 1.25, currency: '$' },
    { symbol: 'NVDA', name: 'NVIDIA', market: 'US', price: 950.75, change: 4.50, currency: '$' },
    { symbol: 'BTC-USD', name: 'Bitcoin', market: 'Crypto', price: 63450, change: -1.25, currency: '$' },
    { symbol: 'ETH-USD', name: 'Ethereum', market: 'Crypto', price: 3250, change: 0.75, currency: '$' },
    { symbol: 'BNB-USD', name: 'Binance Coin', market: 'Crypto', price: 585.30, change: 2.10, currency: '$' },
    { symbol: 'SOL-USD', name: 'Solana', market: 'Crypto', price: 142.80, change: 5.25, currency: '$' },
    { symbol: 'XRP-USD', name: 'Ripple', market: 'Crypto', price: 0.52, change: -0.35, currency: '$' },
    { symbol: 'ADA-USD', name: 'Cardano', market: 'Crypto', price: 0.46, change: 1.20, currency: '$' }
];

// DOM elements
const stockList = document.getElementById('stockList');
const updateTime = document.getElementById('updateTime');
const stockChartCtx = document.getElementById('stockChart').getContext('2d');
const refreshBtn = document.getElementById('refreshBtn');
const addStockBtn = document.getElementById('addStockBtn');
const searchBtn = document.getElementById('searchBtn');
const searchInput = document.getElementById('searchInput');
const chartTypeBtn = document.getElementById('chartTypeBtn');
const notification = document.getElementById('notification');
const trendAnalysis = document.getElementById('trendAnalysis');
const stockStats = document.getElementById('stockStats');
const predictionContainer = document.getElementById('predictionContainer');
const logoutBtn = document.getElementById('logoutBtn');
const expandChartBtn = document.getElementById('expandChartBtn');

// Global variables
let stockChart;
let currentStock = null;
let chartType = 'line';
let filteredStocks = [...mockStocks];

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initStockChart();
    renderStockList(filteredStocks);
    updateClock();
    setInterval(updateClock, 1000);

    // Select first stock by default
    if (filteredStocks.length > 0) {
        setTimeout(() => {
            const firstStock = document.querySelector('.stock-item');
            if (firstStock) {
                firstStock.classList.add('active');
                updateStockDetails(filteredStocks[0]);
            }
        }, 300);
    }
    
    // Add event listeners
    refreshBtn.addEventListener('click', () => {
        showNotification('Stock data refreshed');
        renderStockList(filteredStocks);
    });

    addStockBtn.addEventListener('click', addNewStock);
    searchBtn.addEventListener('click', searchStocks);

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchStocks();
        }
    });

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            filterStocks(filter);
        });
    });

    // Chart type button
    chartTypeBtn.addEventListener('click', () => {
        chartType = chartType === 'line' ? 'candle' : 'line';
        if (currentStock) {
            updateStockDetails(currentStock);
            showNotification(`Chart type: ${chartType === 'line' ? 'Line' : 'Candlestick'}`);
        }
    });

    // Logout button
    logoutBtn.addEventListener('click', () => {
        showNotification('Logging out...');
        setTimeout(() => {
            window.close();
        }, 1000);
    });

    // Expand chart button
    expandChartBtn.addEventListener('click', () => {
        showNotification('Full screen chart activated');
    });
});

// Render stock list
function renderStockList(stocks) {
    stockList.innerHTML = '';

    if (stocks.length === 0) {
        stockList.innerHTML = '<div class="loading"><i class="fas fa-exclamation-circle"></i> No stocks found</div>';
        return;
    }

    stocks.forEach((stock, index) => {
        const changeClass = stock.change >= 0 ? 'positive' : 'negative';
        const changeSign = stock.change >= 0 ? '+' : '';

        const stockItem = document.createElement('div');
        stockItem.className = 'stock-item';
        stockItem.innerHTML = `
            <div class="stock-logo">${stock.symbol.charAt(0)}</div>
            <div class="stock-info">
                <div class="stock-symbol">${stock.symbol}</div>
                <div class="stock-name">${stock.name}</div>
            </div>
            <div>
                <div class="stock-price">${stock.price.toFixed(2)} ${stock.currency}</div>
                <div class="stock-change ${changeClass}">
                    ${changeSign}${stock.change.toFixed(2)}%
                </div>
            </div>
        `;

        stockItem.addEventListener('click', () => {
            // Highlight selected stock
            document.querySelectorAll('.stock-item').forEach(item => {
                item.classList.remove('active');
            });
            stockItem.classList.add('active');

            // Update stock details
            updateStockDetails(stock);
        });

        stockList.appendChild(stockItem);
    });
}

// Initialize stock chart
function initStockChart() {
    stockChart = new Chart(stockChartCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                data: [],
                borderColor: '#2a9df4',
                backgroundColor: 'rgba(42, 157, 244, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(26, 37, 47, 0.9)',
                    titleFont: { size: 14 },
                    bodyFont: { size: 13 },
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#ecf0f1',
                        callback: function (value) { return value.toFixed(2); }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: {
                        color: '#ecf0f1',
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 8
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Update stock chart
function updateStockChart(stock) {
    if (!stockChart) return;

    // Generate random chart data
    const hours = ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];
    const prices = [];

    // Start from the stock price
    let currentPrice = stock.price;
    prices.push(currentPrice);

    // Generate random price movements
    for (let i = 1; i < hours.length; i++) {
        const change = (Math.random() * 4 - 2) * (stock.price / 100);
        currentPrice += change;
        prices.push(currentPrice);
    }

    stockChart.data.labels = hours;
    stockChart.data.datasets[0].data = prices;
    stockChart.update();
}

// Update stock details
function updateStockDetails(stock) {
    currentStock = stock;

    // Update chart
    updateStockChart(stock);

    // Update trend analysis
    const trendScore = Math.floor(Math.random() * 100);
    let trendIndicator, trendText;

    if (trendScore > 70) {
        trendIndicator = 'trend-positive';
        trendText = 'Strong Uptrend';
    } else if (trendScore > 55) {
        trendIndicator = 'trend-positive';
        trendText = 'Uptrend';
    } else if (trendScore > 45) {
        trendIndicator = 'trend-neutral';
        trendText = 'Neutral';
    } else if (trendScore > 30) {
        trendIndicator = 'trend-negative';
        trendText = 'Downtrend';
    } else {
        trendIndicator = 'trend-negative';
        trendText = 'Strong Downtrend';
    }

    trendAnalysis.innerHTML = `
        <div class="trend-indicator ${trendIndicator}"></div>
        <div class="trend-text">${trendText} (Score: ${trendScore})</div>
    `;

    // Update stats
    const openPrice = stock.price * (1 + (Math.random() * 0.02 - 0.01));
    const prevClose = stock.price * (1 + (Math.random() * 0.03 - 0.015));
    const high = stock.price * (1 + Math.random() * 0.03);
    const low = stock.price * (1 - Math.random() * 0.02);

    stockStats.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Daily Change</div>
            <div class="stat-value ${stock.change >= 0 ? 'positive' : 'negative'}">
                ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Price</div>
            <div class="stat-value">${stock.price.toFixed(2)} ${stock.currency}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Open</div>
            <div class="stat-value">${openPrice.toFixed(2)} ${stock.currency}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Prev Close</div>
            <div class="stat-value">${prevClose.toFixed(2)} ${stock.currency}</div>
        </div>
    `;

    // Update predictions
    const predictionChange = (Math.random() * 8 - 2);
    const predictionClass = predictionChange >= 0 ? 'prediction-positive' : 'prediction-negative';
    const predictionSign = predictionChange >= 0 ? '+' : '';

    predictionContainer.innerHTML = `
        <div class="prediction-item">
            <span class="prediction-label">AI Prediction</span>
            <span class="prediction-value ${predictionClass}">${predictionSign}${predictionChange.toFixed(2)}%</span>
        </div>
        <div class="prediction-item">
            <span class="prediction-label">Technical Analysis</span>
            <span class="prediction-value">${trendText}</span>
        </div>
        <div class="prediction-item">
            <span class="prediction-label">Market Sentiment</span>
            <span class="prediction-value">${trendScore > 70 ? 'Strong Buy' : trendScore > 55 ? 'Buy' : trendScore > 45 ? 'Neutral' : trendScore > 30 ? 'Sell' : 'Strong Sell'}</span>
        </div>
        <div class="prediction-item">
            <span class="prediction-label">Avg. Prediction</span>
            <span class="prediction-value prediction-positive">+${(Math.random() * 4 + 1).toFixed(2)}%</span>
        </div>
    `;
}

// Update time function
function updateClock() {
    const now = new Date();
    updateTime.textContent = now.toLocaleTimeString('en-US');
}

// Show notification
function showNotification(message, isError = false) {
    notification.innerHTML = `<i class="fas ${isError ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i><span>${message}</span>`;
    notification.className = `notification show ${isError ? 'error' : ''}`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Add new stock
function addNewStock() {
    const symbol = prompt('Enter stock symbol to add (e.g. AAPL):');
    if (symbol && symbol.trim() !== '') {
        const newStock = {
            symbol: symbol.toUpperCase(),
            name: `${symbol} Stock`,
            market: symbol.includes('.IS') ? 'BIST' : symbol.includes('-') ? 'Crypto' : 'US',
            price: Math.random() * 300 + 20,
            change: (Math.random() * 6 - 3),
            currency: symbol.includes('.IS') ? '₺' : '$'
        };

        mockStocks.push(newStock);
        filteredStocks.push(newStock);
        renderStockList(filteredStocks);
        showNotification(`${symbol} added successfully`);
    }
}

// Search stocks
function searchStocks() {
    const searchTerm = searchInput.value.trim().toLowerCase();
    if (searchTerm) {
        filteredStocks = mockStocks.filter(stock =>
            stock.symbol.toLowerCase().includes(searchTerm) ||
            stock.name.toLowerCase().includes(searchTerm)
        );
        renderStockList(filteredStocks);
    } else {
        filteredStocks = [...mockStocks];
        renderStockList(filteredStocks);
    }
}

// Filter stocks
function filterStocks(filter) {
    if (filter === 'all') {
        filteredStocks = [...mockStocks];
    } else {
        filteredStocks = mockStocks.filter(stock =>
            stock.market.toLowerCase() === filter
        );
    }
    renderStockList(filteredStocks);
}