import requests
import csv
import os
import logging
import time
from datetime import datetime
import requests
from datetime import datetime, timedelta

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
    
    data_cotacao = (datetime.now() - timedelta(days=1)).strftime('%m-%d-%Y')
    
    # URLs
    url_usd = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='USD'&@dataCotacao='{data_cotacao}'&$format=json"
    url_eur = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='EUR'&@dataCotacao='{data_cotacao}'&$format=json"
    url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=brl"
    
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Coletar USD e EUR do Banco Central
    for moeda, url in [("Dólar", url_usd), ("Euro", url_eur)]:
        try:
            res = requests.get(url, timeout=15)
            dados = res.json()
            if dados.get('value'):
                preco = dados['value'][0]['cotacaoVenda']
                results.append({"timestamp": timestamp, "asset": moeda, "price": round(float(preco), 2)})
                logger.info(f" ✓ {moeda} coletado via BC.")
            else:
                logger.warning(f"⚠️ Sem cotação de {moeda} para a data {data_cotacao} (Fim de semana/Feriado?)")
        except Exception as e:
            logger.error(f"Erro no câmbio BC ({moeda}): {e}")

    # 2. Coletar Cripto (CoinGecko)
    try:
        res_crypto = requests.get(url_crypto, timeout=15)
        dados_c = res_crypto.json()
        results.append({"timestamp": timestamp, "asset": "Bitcoin", "price": float(dados_c['bitcoin']['brl'])})
        results.append({"timestamp": timestamp, "asset": "Ethereum", "price": float(dados_c['ethereum']['brl'])})
        logger.info(" ✓ Criptos coletadas.")
    except Exception as e:
        logger.error(f"Erro Cripto: {e}")

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