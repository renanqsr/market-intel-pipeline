# 📊 Market Intel Pipeline

[![Market Data Monitor](https://github.com/renanqsr/market-intel-pipeline/actions/workflows/scraper.yml/badge.svg)](https://github.com/renanqsr/market-intel-pipeline/actions/workflows/scraper.yml)

Automated **ETL (Extract, Transform, Load)** system for monitoring financial assets (Forex and Crypto). The project uses Python for data collection and processing, with fully serverless orchestration via **GitHub Actions**.

---

## 🚀 Problem vs Solution

Financial data analysis often depends on manual exports or paid tools.  
This project solves that by creating a **free, automated historical dataset**.

The system runs daily, fetches fresh data, processes it, and stores it — building a consistent historical dataset with **zero manual intervention** and no infrastructure costs (**Git-as-a-Database approach**).

---

## 📁 Project Structure

```text
.
├── scraper.py             # Main data collection script (Python)
├── requirements.txt       # Project dependencies
├── data/
│   └── market_trends.csv  # Historical dataset (auto-generated)
├── logs/
│   └── monitor.log        # Execution logs (auto-generated)
└── .github/
    └── workflows/
        └── scraper.yml    # CI/CD pipeline (Cron Job: 09:00 BRT)
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.12
- **Libraries:**
  - `requests`: API consumption
  - `csv`: Data persistence (standard library)
  - `logging`: Monitoring and debugging (standard library)
  - `beautifulsoup4` & `lxml`: Web scraping capabilities (pre-configured)
- **Orchestration:** GitHub Actions (Automated Workflow)
- **Architecture:** Event-driven Automation / ETL Pipeline

---

## ⚙️ How the Pipeline Works

1.  **Trigger:** GitHub Actions runs the workflow daily via Cron Job at `12:00 UTC` (`09:00 BRT`).
2.  **Extraction:** Fetches real-time data from:
    - **AwesomeAPI:** USD/BRL and EUR/BRL exchange rates.
    - **CoinGecko:** Bitcoin and Ethereum prices in BRL.
3.  **Transformation:**
    - Validates raw data.
    - Converts values to float.
    - Adds timestamps.
4.  **Load:** Automatically commits updated data to `data/market_trends.csv`.

---

## 💻 Run Locally

To run the project on your machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/renanqsr/market-intel-pipeline.git
    cd market-intel-pipeline
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the pipeline:**
    ```bash
    python scraper.py
    ```

---

## 🔍 Monitoring & Logs

- **Local Logs:** Stored in `logs/monitor.log` for request debugging.
- **GitHub Artifacts:** Each Actions run generates downloadable execution logs.
- **Transparency:** The badge at the top of this README shows real-time pipeline status.

---

## 👨‍💻 Author

Developed by **Renan Queiroz**.
