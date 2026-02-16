"""
Pipeline principal - Orchestre toutes les étapes du projet
Version finale avec dashboard Excel automatique
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.logger import get_logger, load_config
from src.scraper import run_scraper
from src.cleaner import load_raw_data, inspect_data, clean_data, save_clean_data
from src.analyzer import analyze_products
from src.visualizer import create_dashboard

logger = get_logger(__name__)


def run_full_pipeline():
    """
    Exécute le pipeline complet : collecte → nettoyage → analyse → dashboard
    """
    logger.info("\n" + "=" * 70)
    logger.info("🚀 DÉMARRAGE DU PIPELINE COMPLET - VEILLE CONCURRENTIELLE")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    logger.info(f"⏰ Heure de démarrage : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Charger la configuration
    config = load_config()
    logger.info("✅ Configuration chargée")
    
    # Variables pour stocker les chemins de fichiers
    files_created = {
        'raw': None,
        'clean': None,
        'analyzed': None,
        'dashboard': None
    }
    
    try:
        # ═══════════════════════════════════════════════════════
        # ÉTAPE 1 : COLLECTE DES DONNÉES
        # ═══════════════════════════════════════════════════════
        logger.info("\n" + "─" * 70)
        logger.info("📡 ÉTAPE 1/4 : COLLECTE DES DONNÉES")
        logger.info("─" * 70)
        
        raw_file = run_scraper(config)
        
        if not raw_file:
            logger.error("❌ Échec de la collecte - Arrêt du pipeline")
            return False, files_created
        
        files_created['raw'] = raw_file
        logger.info(f"✅ Collecte terminée : {raw_file}")
        
        # ═══════════════════════════════════════════════════════
        # ÉTAPE 2 : NETTOYAGE DES DONNÉES
        # ═══════════════════════════════════════════════════════
        logger.info("\n" + "─" * 70)
        logger.info("🧹 ÉTAPE 2/4 : NETTOYAGE DES DONNÉES")
        logger.info("─" * 70)
        
        df_raw = load_raw_data(raw_file)
        
        if df_raw is None:
            logger.error("❌ Impossible de charger les données - Arrêt du pipeline")
            return False, files_created
        
        logger.info("\n📊 Inspection des données brutes :")
        inspect_data(df_raw)
        
        df_clean = clean_data(df_raw)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_file = f"{config['paths']['processed_data']}/products_clean_{timestamp}.csv"
        save_clean_data(df_clean, clean_file)
        
        files_created['clean'] = clean_file
        logger.info(f"✅ Nettoyage terminé : {clean_file}")
        
        # ═══════════════════════════════════════════════════════
        # ÉTAPE 3 : ANALYSE IA
        # ═══════════════════════════════════════════════════════
        logger.info("\n" + "─" * 70)
        logger.info("🤖 ÉTAPE 3/4 : ANALYSE IA ET INSIGHTS")
        logger.info("─" * 70)
        
        analyzed_file = clean_file.replace('_clean_', '_analyzed_')
        df_analyzed, stats, insights = analyze_products(clean_file, analyzed_file, config)
        
        files_created['analyzed'] = analyzed_file
        logger.info(f"✅ Analyse terminée : {analyzed_file}")
        
        # ═══════════════════════════════════════════════════════
        # ÉTAPE 4 : GÉNÉRATION DU DASHBOARD EXCEL
        # ═══════════════════════════════════════════════════════
        logger.info("\n" + "─" * 70)
        logger.info("📊 ÉTAPE 4/4 : GÉNÉRATION DU DASHBOARD EXCEL")
        logger.info("─" * 70)
        
        dashboard_file = f"{config['paths']['output_data']}/dashboard_{timestamp}.xlsx"
        create_dashboard(df_analyzed, stats, insights, dashboard_file)
        
        files_created['dashboard'] = dashboard_file
        logger.info(f"✅ Dashboard créé : {dashboard_file}")
        
        # ═══════════════════════════════════════════════════════
        # RÉSUMÉ FINAL
        # ═══════════════════════════════════════════════════════
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ PIPELINE TERMINÉ AVEC SUCCÈS")
        logger.info("=" * 70)
        logger.info(f"⏱️  Durée totale : {duration:.2f} secondes ({duration/60:.1f} minutes)")
        logger.info(f"📊 Nombre de produits traités : {len(df_analyzed)}")
        logger.info(f"💡 Nombre d'insights générés : {len(insights)}")
        logger.info("")
        logger.info("📂 FICHIERS CRÉÉS :")
        logger.info(f"   • Données brutes      : {files_created['raw']}")
        logger.info(f"   • Données nettoyées   : {files_created['clean']}")
        logger.info(f"   • Données analysées   : {files_created['analyzed']}")
        logger.info(f"   • Dashboard Excel     : {files_created['dashboard']}")
        logger.info("=" * 70 + "\n")
        
        # Afficher un résumé des insights
        logger.info("💡 RÉSUMÉ DES INSIGHTS :")
        for i, insight in enumerate(insights, 1):
            logger.info(f"   {i}. {insight}")
        logger.info("")
        
        return True, files_created
        
    except Exception as e:
        logger.critical(f"💥 ERREUR CRITIQUE DANS LE PIPELINE : {e}", exc_info=True)
        return False, files_created


def print_summary(success, files_created):
    """
    Affiche un résumé visuel dans la console
    
    Args:
        success (bool): Succès du pipeline
        files_created (dict): Dictionnaire des fichiers créés
    """
    print("\n" + "=" * 70)
    
    if success:
        print("✅ PIPELINE TERMINÉ AVEC SUCCÈS")
        print("=" * 70)
        print("\n📁 Fichiers générés :")
        
        for file_type, filepath in files_created.items():
            if filepath:
                filename = os.path.basename(filepath)
                print(f"   • {file_type.upper():12} : {filename}")
        
        print("\n🎯 Prochaines étapes :")
        print("   1. Ouvrir le dashboard Excel dans data/output/")
        print("   2. Consulter les logs détaillés dans logs/")
        print("   3. Partager le dashboard avec votre équipe")
        
    else:
        print("❌ LE PIPELINE A RENCONTRÉ DES ERREURS")
        print("=" * 70)
        print("\n🔍 Actions recommandées :")
        print("   1. Consulter les logs dans logs/")
        print("   2. Vérifier la connexion réseau")
        print("   3. Vérifier les fichiers de configuration")
    
    print("=" * 70 + "\n")


def main():
    """
    Point d'entrée principal
    """
    # Banner de démarrage
    print("\n" + "=" * 70)
    print("🤖 PIPELINE DE VEILLE CONCURRENTIELLE AUTOMATISÉ")
    print("=" * 70)
    print("Collecte → Nettoyage → Analyse IA → Dashboard Excel")
    print("=" * 70 + "\n")
    
    # Exécuter le pipeline
    success, files_created = run_full_pipeline()
    
    # Afficher le résumé
    print_summary(success, files_created)
    
    # Code de sortie
    if success:
        logger.info("👍 Le pipeline s'est terminé sans erreur")
        sys.exit(0)  # Code de sortie 0 = succès
    else:
        logger.error("👎 Le pipeline a rencontré des erreurs")
        sys.exit(1)  # Code de sortie 1 = erreur


if __name__ == "__main__":
    main()