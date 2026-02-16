"""
Planificateur autonome - Exécute le pipeline automatiquement
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

# Ajouter le dossier au path
sys.path.insert(0, os.path.dirname(__file__))

from src.logger import get_logger

logger = get_logger(__name__)


def run_pipeline_job():
    """
    Fonction qui sera exécutée par le scheduler
    """
    logger.info("=" * 70)
    logger.info(f"🕐 EXÉCUTION PLANIFIÉE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    try:
        # Lancer main.py dans un subprocess
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            logger.info("✅ Pipeline exécuté avec succès")
        else:
            logger.error(f"❌ Pipeline terminé avec erreur (code {result.returncode})")
            logger.error(f"Sortie d'erreur : {result.stderr}")
        
    except Exception as e:
        logger.critical(f"💥 Erreur lors de l'exécution : {e}", exc_info=True)


def main():
    """
    Configure et démarre le scheduler
    """
    print("\n" + "=" * 70)
    print("🕐 PLANIFICATEUR AUTOMATIQUE DÉMARRÉ")
    print("=" * 70)
    print(f"Heure de démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📅 Planification configurée :")
    print("   • Tous les jours à 08:00")
    print("   • Appuyez sur Ctrl+C pour arrêter")
    print("=" * 70 + "\n")
    
    logger.info("🕐 Planificateur démarré")
    
    # Configure la planification
    schedule.every().day.at("08:00").do(run_pipeline_job)
    
    # Option : ajouter d'autres horaires
    # schedule.every().hour.do(run_pipeline_job)  # Toutes les heures
    # schedule.every().monday.at("09:00").do(run_pipeline_job)  # Tous les lundis
    
    # Boucle infinie
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les minutes
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("⏹️  ARRÊT DU PLANIFICATEUR")
        print("=" * 70)
        logger.info("⏹️  Planificateur arrêté par l'utilisateur")


if __name__ == "__main__":
    main()