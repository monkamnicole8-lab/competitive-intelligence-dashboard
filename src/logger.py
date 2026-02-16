"""
Module de configuration du système de logging
"""

import logging
import logging.handlers
import os
from datetime import datetime
import yaml


def load_config(config_path="config/config.yaml"):
    """
    Charge la configuration depuis le fichier YAML
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"⚠️  Fichier de config introuvable : {config_path}")
        print("📝 Utilisation de la configuration par défaut")
        return {
            'paths': {'logs': 'logs'},
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }


def setup_logger(name, config=None):
    """
    Configure un logger avec rotation de fichiers
    """
    if config is None:
        config = load_config()
    
    # Créer le dossier logs s'il n'existe pas
    log_dir = config['paths']['logs']
    os.makedirs(log_dir, exist_ok=True)
    
    # Créer le logger
    logger = logging.getLogger(name)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Niveau de log
    log_level = getattr(logging, config['logging']['level'], logging.INFO)
    logger.setLevel(log_level)
    
    # Format du log
    formatter = logging.Formatter(config['logging']['format'])
    
    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier
    log_filename = os.path.join(
        log_dir, 
        f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=config['logging'].get('file_max_bytes', 10485760),
        backupCount=config['logging'].get('backup_count', 5),
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name):
    """
    Raccourci pour obtenir un logger configuré
    """
    config = load_config()
    return setup_logger(name, config)