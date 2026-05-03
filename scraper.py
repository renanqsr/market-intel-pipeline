import requests
import csv
import os
import logging
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
    
    # URLs
    url_cambio = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
    url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=brl"
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Request Câmbio
        res_cambio = requests.get(url_cambio, timeout=20).json()
        # Ajuste aqui: a API pode retornar com ou sem hífen
        usd_data = res_cambio.get("USDBRL") or res_cambio.get("USD-BRL")
        eur_data = res_cambio.get("EURBRL") or res_cambio.get("EUR-BRL")
        
        # Request Crypto
        res_crypto = requests.get(url_crypto, timeout=20).json()
        
        results = [
            {"timestamp": timestamp, "asset": "Dólar", "price": float(usd_data["bid"])},
            {"timestamp": timestamp, "asset": "Euro", "price": float(eur_data["bid"])},
            {"timestamp": timestamp, "asset": "Bitcoin", "price": float(res_crypto["bitcoin"]["brl"])},
            {"timestamp": timestamp, "asset": "Ethereum", "price": float(res_crypto["ethereum"]["brl"])}
        ]
        
        for r in results:
            logger.info(f" ✓ {r['asset']}: R$ {r['price']:.2f}")
            
        return results
    except Exception as e:
        logger.error(f"Falha na coleta: {e}")
        # Log detalhado para debug se falhar de novo
        if 'res_cambio' in locals(): logger.error(f"Payload recebido: {res_cambio}")
        return []

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