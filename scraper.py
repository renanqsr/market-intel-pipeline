import requests
import csv
import os
import logging
import time
from datetime import datetime

# Configuração de pastas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR  = os.path.join(BASE_DIR, "logs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

CSV_FILE = os.path.join(DATA_DIR, "market_trends.csv")
LOG_FILE = os.path.join(LOG_DIR, "monitor.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def fetch_market_data():
    logger.info("Iniciando coleta de dados financeiros...")
    
    url_cambio = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
    url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=brl"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Tentar Câmbio (AwesomeAPI)
    try:
        res = requests.get(url_cambio, headers=headers, timeout=15)
        if res.status_code == 200:
            dados = res.json()
            results.append({"timestamp": timestamp, "asset": "Dólar", "price": float(dados['USDBRL']['bid'])})
            results.append({"timestamp": timestamp, "asset": "Euro", "price": float(dados['EURBRL']['bid'])})
            logger.info(" ✓ Câmbio coletado com sucesso.")
        else:
            logger.warning(f"⚠️ Falha no câmbio (Status {res.status_code}). Pulando...")
    except Exception as e:
        logger.error(f"Erro ao acessar AwesomeAPI: {e}")

    # 2. Tentar Cripto (CoinGecko)
    try:
        res_crypto = requests.get(url_crypto, headers=headers, timeout=15)
        if res_crypto.status_code == 200:
            dados_c = res_crypto.json()
            results.append({"timestamp": timestamp, "asset": "Bitcoin", "price": float(dados_c['bitcoin']['brl'])})
            results.append({"timestamp": timestamp, "asset": "Ethereum", "price": float(dados_c['ethereum']['brl'])})
            logger.info(" ✓ Cripto coletada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao acessar CoinGecko: {e}")

    return results

def save_csv(records):
    if not records: return
    headers = ["timestamp", "asset", "price"]
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerows(records)
        logger.info(f"Dados persistidos em CSV com sucesso.")

if __name__ == "__main__":
    data = fetch_market_data()
    save_csv(data)