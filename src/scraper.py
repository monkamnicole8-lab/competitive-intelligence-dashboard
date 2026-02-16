"""
Module de collecte de données depuis des APIs et sites web
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Ajouter les dossiers au path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from src.logger import get_logger, load_config

# Créer le logger
logger = get_logger(__name__)


def test_api_connection(config):
    """
    Teste la connexion à une API publique
    """
    base_url = config['api']['base_url']
    endpoint = config['api']['endpoints']['products']
    url = f"{base_url}{endpoint}"
    timeout = config['api']['timeout']
    
    logger.info(f"Envoi de la requête à l'API : {url}")
    
    try:
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            logger.info(f"✅ Connexion réussie (code {response.status_code})")
            data = response.json()
            logger.info(f"📊 {len(data)} produits récupérés")
            return data
        else:
            logger.error(f"❌ Erreur HTTP : code {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"⏱️  Timeout après {timeout} secondes")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("🔌 Erreur de connexion réseau")
        return None
    except Exception as e:
        logger.critical(f"❌ Erreur inattendue : {e}", exc_info=True)
        return None


def save_products_to_csv(products, config, filename=None):
    """
    Transforme les données JSON en DataFrame et sauvegarde en CSV
    """
    if not products:
        logger.warning("⚠️  Aucune donnée à sauvegarder")
        return None
    
    logger.info("🔄 Transformation des données en DataFrame...")
    
    df = pd.DataFrame(products)
    df = df[['id', 'title', 'price', 'category']]
    
    logger.info(f"📊 DataFrame créé : {df.shape[0]} lignes × {df.shape[1]} colonnes")
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config['paths']['raw_data']}/products_{timestamp}.csv"
    
    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"✅ Données sauvegardées : {filename}")
    
    return df


def run_scraper(config):
    """
    Exécute le pipeline complet de collecte
    """
    logger.info("=" * 60)
    logger.info("🚀 DÉMARRAGE DU SCRAPER")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    products = test_api_connection(config)
    
    if not products:
        logger.error("❌ Échec de la collecte de données")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{config['paths']['raw_data']}/products_{timestamp}.csv"
    df = save_products_to_csv(products, config, filename)
    
    elapsed_time = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"✅ SCRAPER TERMINÉ en {elapsed_time:.2f} secondes")
    logger.info(f"📂 Fichier créé : {filename}")
    logger.info("=" * 60)
    
    return filename


if __name__ == "__main__":
    config = load_config()
    run_scraper(config)