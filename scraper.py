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
    
    # URLs - Usando o endpoint /all que costuma ser mais resiliente
    url_cambio = "https://economia.awesomeapi.com.br/all/USD-BRL,EUR-BRL"
    url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=brl"
    
    # Headers para simular um navegador real e evitar bloqueios (429)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    max_tentativas = 3
    espera_segundos = 30 
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Coleta de Câmbio
            res_cambio_obj = requests.get(url_cambio, headers=headers, timeout=20)
            
            if res_cambio_obj.status_code == 429:
                logger.warning(f"⚠️ Limite atingido (429). Tentativa {tentativa}/{max_tentativas}. Aguardando {espera_segundos}s...")
                time.sleep(espera_segundos)
                continue
            
            res_cambio = res_cambio_obj.json()
            
            # 2. Coleta de Crypto
            res_crypto = requests.get(url_crypto, headers=headers, timeout=20).json()
            
            # Extração dos dados (Tratando possíveis variações de nomes na API de câmbio)
            usd = res_cambio.get("USD", {}).get("bid")
            eur = res_cambio.get("EUR", {}).get("bid")
            btc = res_crypto.get("bitcoin", {}).get("brl")
            eth = res_crypto.get("ethereum", {}).get("brl")

            # Validação básica: se algum dado essencial falhou, força o erro para tentar de novo
            if not all([usd, eur, btc, eth]):
                raise ValueError("Dados incompletos recebidos das APIs")

            results = [
                {"timestamp": timestamp, "asset": "Dólar", "price": float(usd)},
                {"timestamp": timestamp, "asset": "Euro", "price": float(eur)},
                {"timestamp": timestamp, "asset": "Bitcoin", "price": float(btc)},
                {"timestamp": timestamp, "asset": "Ethereum", "price": float(eth)}
            ]
            
            for r in results:
                logger.info(f" ✓ {r['asset']}: R$ {r['price']:.2f}")
                
            return results
            
        except Exception as e:
            logger.error(f"Erro na tentativa {tentativa}: {e}")
            if tentativa < max_tentativas:
                time.sleep(espera_segundos)
            else:
                logger.critical("❌ Todas as tentativas falharam. API pode estar fora do ar ou bloqueio persistente.")
    
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