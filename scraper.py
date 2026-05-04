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
    
    timestamp_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []

    # 1. Coletar USD e EUR do Banco Central
    for moeda in ["USD", "EUR"]:
        nome_exibicao = "Dólar" if moeda == "USD" else "Euro"
        encontrou = False
        tentativas = 0
        
        # Tenta buscar a cotação de até 5 dias atrás
        while not encontrou and tentativas < 5:
            data_teste = (datetime.now() - timedelta(days=tentativas)).strftime('%m-%d-%Y')
            url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='{moeda}'&@dataCotacao='{data_teste}'&$format=json"
            
            try:
                res = requests.get(url, timeout=10)
                dados = res.json()
                if dados.get('value'):
                    preco = dados['value'][0]['cotacaoVenda']
                    results.append({"timestamp": timestamp_agora, "asset": nome_exibicao, "price": round(float(preco), 2)})
                    logger.info(f" ✓ {nome_exibicao} coletado (Data ref: {data_teste}).")
                    encontrou = True
                else:
                    tentativas += 1
            except Exception as e:
                logger.error(f"Erro ao acessar BC para {moeda}: {e}")
                break

    # 2. Coletar Cripto (CoinGecko)
    try:
        url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=brl"
        res_c = requests.get(url_crypto, timeout=10)
        dados_c = res_c.json()
        results.append({"timestamp": timestamp_agora, "asset": "Bitcoin", "price": float(dados_c['bitcoin']['brl'])})
        results.append({"timestamp": timestamp_agora, "asset": "Ethereum", "price": float(dados_c['ethereum']['brl'])})
        logger.info(" ✓ Criptos coletadas com sucesso.")
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