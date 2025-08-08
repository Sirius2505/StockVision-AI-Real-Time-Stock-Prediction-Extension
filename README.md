# 📈 Global Stock Analysis Panel

This project is a **web browser extension** that provides a comprehensive platform for **real-time stock market analysis**. It is designed to offer investors and enthusiasts instant access to key financial data, technical indicators, and visualizations for a wide range of stocks across multiple global markets. The extension combines a robust Python backend with a modern, responsive frontend to deliver a seamless user experience directly in the browser.

---

## 🚀 Key Features

* **Multi-Market Data:** Access live and historical data for stocks listed on **Borsa İstanbul (BIST)**, major **US markets**, and popular **cryptocurrencies**. The extension provides a unified view of these diverse markets.
* **Advanced Technical Indicators:** Analyze stock performance using essential technical indicators such as **Simple Moving Average (SMA)**, **Relative Strength Index (RSI)**, and **MACD**. These indicators are calculated and presented in an easy-to-understand format.
* **Interactive Charts:** Visualize stock price movements and technical indicators with dynamic charts powered by **Chart.js**. Users can switch between different chart types (e.g., line, candlestick) to suit their analysis needs.
* **Modern & Intuitive UI:** The extension features a clean, minimalist, and responsive user interface with a sleek dark theme. The design is optimized for efficiency, allowing users to quickly navigate and find the information they need.
* **Efficient Data Handling:** A dedicated Python backend server built with **Flask** handles all data fetching from the **Finnhub API**. This data is then stored and managed in a local **SQLite3** database, ensuring fast access and reduced API call overhead.

---

## 🖼 Preview

| Dashboard View | Stock Detail View |
| :---: | :---: |
| ![Dashboard Screenshot](https://via.placeholder.com/400x300.png?text=Dashboard+Screenshot) | ![Stock Detail Screenshot](https://via.placeholder.com/400x300.png?text=Stock+Detail+Screenshot) |

(Projenin arayüzünü gösteren gerçek görsellerle bu placeholder'ları değiştirmeyi unutmayın.)

---

## 📦 Installation

To get this project up and running, you need to set up both the backend server and the browser extension.

### 1. Backend Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/KullaniciAdin/ProjeAdin.git](https://github.com/KullaniciAdin/ProjeAdin.git)
    cd ProjeAdin
    ```
2.  **Install Dependencies:** All necessary Python packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Server:**
    ```bash
    python app.py
    ```
    The server will start on `http://localhost:5000`. It will automatically initialize the database and begin fetching data for the default stock list.

### 2. Browser Extension Setup

1.  Open your browser (e.g., Chrome, Edge, Brave).
2.  Navigate to the extensions management page (e.g., `chrome://extensions`).
3.  Enable **Developer Mode** in the top right corner.
4.  Click **Load unpacked** and select the project directory where your `manifest.json` file is located. The extension icon will now appear in your toolbar.

---

## ⚙️ How It Works

The project's architecture is divided into two parts:

* **Backend (`app.py`):** A Flask server that acts as a data provider. It uses the Finnhub API to retrieve real-time stock prices and historical data. It also performs technical analysis calculations and stores all the information in a local SQLite3 database for quick retrieval. A background thread ensures data is updated periodically.
* **Frontend (`popup.html`, `popup.js`):** The browser extension's user interface. It communicates with the local Flask server to fetch stock data. The `popup.js` script handles all user interactions, data filtering, and rendering of the charts using the Chart.js library.

⚙️ Setup
Sign up for a market data API service:

Alpha Vantage

Yahoo Finance API

Finnhub

Get your API key from the provider.

Open the extension’s settings page.

Paste your API key and save.

[Browser Extension UI] 
        ↓
[API Request] → [Live Market Data Provider]
        ↓
[Feature Extraction: RSI, MACD, SMA, EMA]
        ↓
[Machine Learning Model (Pre-trained)]
        ↓
[Prediction: UP or DOWN]
        ↓
[Render in UI]

🛠 Technologies Used
Frontend & Extension
HTML5 / CSS3 / JavaScript (ES6+)

Browser Extension APIs (Chrome/Edge/Brave)

Machine Learning
Python (Scikit-learn / TensorFlow for training)

TensorFlow.js (for in-browser prediction) or model inference via API

APIs
Alpha Vantage / Yahoo Finance / Finnhub 



## 🛠 Technologies Used

* **Backend:** Python, Flask, SQLite3, Requests, NumPy
* **Frontend & Extension:** HTML5, CSS3, JavaScript (ES6+), Chart.js
* **APIs:** Finnhub API for financial data.
* **Development Tools:** Git, Browser Extension APIs (Manifest V3)

---

## 🤝 Contributing

We welcome contributions, bug reports, and feature requests. Please feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the **Apache License 2.0**. For more details, please see the included `Apache-Licence.txt` file.

---

## 📬 Contact

For any questions, suggestions, or feedback, you can reach out by opening an issue on the GitHub repository.

2. Load the Extension
Open your browser’s Extensions page.

Enable Developer Mode.

Click Load unpacked.

Select the project folder.

⚙️ Setup
Sign up for a market data API service:

Alpha Vantage

Yahoo Finance API

Finnhub

Get your API key from the provider.

Open the extension’s settings page.

Paste your API key and save.

[Browser Extension UI] 
        ↓
[API Request] → [Live Market Data Provider]
        ↓
[Feature Extraction: RSI, MACD, SMA, EMA]
        ↓
[Machine Learning Model (Pre-trained)]
        ↓
[Prediction: UP or DOWN]
        ↓
[Render in UI]

🛠 Technologies Used
Frontend & Extension
HTML5 / CSS3 / JavaScript (ES6+)

Browser Extension APIs (Chrome/Edge/Brave)

Machine Learning
Python (Scikit-learn / TensorFlow for training)

TensorFlow.js (for in-browser prediction) or model inference via API

APIs
Alpha Vantage / Yahoo Finance / Finnhub

<img width="439" height="848" alt="Ekran görüntüsü 2025-08-08 163614" src="https://github.com/user-attachments/assets/b78c44b8-f6c6-49a2-a02c-d87fc628d159" />

<img width="411" height="736" alt="Ekran görüntüsü 2025-08-08 163625" src="https://github.com/user-attachments/assets/9e3b0cfb-e2d6-4e32-8fc0-5a556a00bc85" />

<img width="313" height="883" alt="Ekran görüntüsü 2025-08-08 163652" src="https://github.com/user-attachments/assets/eb0f8937-56cd-44ce-972e-9eb3e808648d" />



