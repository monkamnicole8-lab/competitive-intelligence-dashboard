"""
Module d'analyse IA - Sentiment analysis et statistiques avancées
"""

"""
Module d'analyse IA - Sentiment analysis et statistiques avancées
"""

import pandas as pd
import numpy as np
from transformers import pipeline
from tqdm import tqdm
import warnings
import sys
import os

# Ajouter les dossiers au path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from src.logger import get_logger

# Désactiver les warnings de transformers (pour un affichage propre)
warnings.filterwarnings('ignore')

logger = get_logger(__name__)


class ProductAnalyzer:
    """
    Classe pour analyser les produits avec IA
    """
    
    def __init__(self):
        """
        Initialise l'analyseur avec un modèle de sentiment
        """
        logger.info("🤖 Initialisation du modèle d'analyse de sentiment...")
        
        try:
            # Charge un modèle pré-entraîné pour l'analyse de sentiment
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # -1 = CPU, 0 = GPU
            )
            logger.info("✅ Modèle chargé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle : {e}")
            self.sentiment_analyzer = None
    
    
    def analyze_sentiment(self, text):
        """
        Analyse le sentiment d'un texte
        
        Args:
            text (str): Texte à analyser
            
        Returns:
            dict: {'label': 'POSITIVE'/'NEGATIVE', 'score': 0.95}
        """
        if not self.sentiment_analyzer:
            return {'label': 'UNKNOWN', 'score': 0.0}
        
        try:
            # Limite à 512 caractères (limite du modèle)
            text = str(text)[:512]
            result = self.sentiment_analyzer(text)[0]
            return result
        except Exception as e:
            logger.warning(f"⚠️  Erreur d'analyse pour '{text[:30]}...': {e}")
            return {'label': 'UNKNOWN', 'score': 0.0}
    
    
    def analyze_products_dataframe(self, df):
        """
        Analyse tous les produits d'un DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame avec les produits
            
        Returns:
            pd.DataFrame: DataFrame enrichi avec analyse de sentiment
        """
        logger.info(f"🔍 Analyse de sentiment sur {len(df)} produits...")
        
        if self.sentiment_analyzer is None:
            logger.error("❌ Modèle non disponible, analyse annulée")
            return df
        
        # Copie pour ne pas modifier l'original
        df_analyzed = df.copy()
        
        # Listes pour stocker les résultats
        sentiments = []
        scores = []
        
        # Barre de progression
        for idx, row in tqdm(df_analyzed.iterrows(), total=len(df_analyzed), desc="Analyse IA"):
            result = self.analyze_sentiment(row['title'])
            sentiments.append(result['label'])
            scores.append(result['score'])
        
        # Ajouter les colonnes au DataFrame
        df_analyzed['sentiment'] = sentiments
        df_analyzed['sentiment_score'] = scores
        
        logger.info("✅ Analyse de sentiment terminée")
        
        return df_analyzed
    
    
    def compute_statistics(self, df):
        """
        Calcule des statistiques avancées
        
        Args:
            df (pd.DataFrame): DataFrame analysé
            
        Returns:
            dict: Statistiques calculées
        """
        logger.info("📊 Calcul des statistiques...")
        
        stats = {
            'total_products': len(df),
            'avg_price': df['price'].mean(),
            'median_price': df['price'].median(),
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'std_price': df['price'].std(),
        }
        
        # Statistiques par catégorie
        if 'category' in df.columns:
            stats['categories'] = df['category'].value_counts().to_dict()
            stats['avg_price_by_category'] = df.groupby('category')['price'].mean().to_dict()
        
        # Statistiques de sentiment
        if 'sentiment' in df.columns:
            stats['sentiment_distribution'] = df['sentiment'].value_counts().to_dict()
            stats['avg_sentiment_score'] = df['sentiment_score'].mean()
            
            # Sentiment par catégorie
            sentiment_by_cat = df.groupby('category')['sentiment'].value_counts().unstack(fill_value=0)
            stats['sentiment_by_category'] = sentiment_by_cat.to_dict()
        
        logger.info("✅ Statistiques calculées")
        
        return stats
    
    
    def generate_insights(self, df, stats):
        """
        Génère des insights business à partir des données
        
        Args:
            df (pd.DataFrame): DataFrame analysé
            stats (dict): Statistiques calculées
            
        Returns:
            list: Liste d'insights
        """
        logger.info("💡 Génération d'insights...")
        
        insights = []
        
        # Insight 1 : Prix
        if stats['avg_price'] > stats['median_price']:
            insights.append(
                f"⚠️  Le prix moyen (${stats['avg_price']:.2f}) est supérieur au prix médian "
                f"(${stats['median_price']:.2f}), indiquant quelques produits très chers."
            )
        
        # Insight 2 : Catégorie dominante
        if 'categories' in stats:
            top_category = max(stats['categories'].items(), key=lambda x: x[1])
            insights.append(
                f"📦 Catégorie dominante : '{top_category[0]}' avec {top_category[1]} produits "
                f"({(top_category[1]/stats['total_products']*100):.1f}%)"
            )
        
        # Insight 3 : Sentiment
        if 'sentiment_distribution' in stats:
            positive_pct = stats['sentiment_distribution'].get('POSITIVE', 0) / stats['total_products'] * 100
            negative_pct = stats['sentiment_distribution'].get('NEGATIVE', 0) / stats['total_products'] * 100
            
            if positive_pct > 70:
                insights.append(
                    f"😊 Excellent ! {positive_pct:.1f}% des produits ont un titre positif"
                )
            elif negative_pct > 30:
                insights.append(
                    f"⚠️  Attention : {negative_pct:.1f}% des produits ont un titre négatif"
                )
        
        # Insight 4 : Produit le plus cher
        most_expensive = df.loc[df['price'].idxmax()]
        insights.append(
            f"💰 Produit le plus cher : '{most_expensive['title'][:50]}...' à ${most_expensive['price']:.2f}"
        )
        
        # Insight 5 : Produit le moins cher
        cheapest = df.loc[df['price'].idxmin()]
        insights.append(
            f"💵 Produit le moins cher : '{cheapest['title'][:50]}...' à ${cheapest['price']:.2f}"
        )
        
        logger.info(f"✅ {len(insights)} insights générés")
        
        return insights


def analyze_products(input_file, output_file, config):
    """
    Fonction principale d'analyse
    
    Args:
        input_file (str): Fichier CSV à analyser
        output_file (str): Fichier de sortie
        config (dict): Configuration
        
    Returns:
        tuple: (DataFrame analysé, statistiques, insights)
    """
    logger.info("=" * 60)
    logger.info("🤖 DÉMARRAGE DE L'ANALYSE IA")
    logger.info("=" * 60)
    
    # Charger les données
    logger.info(f"📂 Chargement depuis {input_file}...")
    df = pd.read_csv(input_file, encoding='utf-8')
    logger.info(f"✅ {len(df)} produits chargés")
    
    # Initialiser l'analyseur
    analyzer = ProductAnalyzer()
    
    # Analyser le sentiment
    df_analyzed = analyzer.analyze_products_dataframe(df)
    
    # Calculer les statistiques
    stats = analyzer.compute_statistics(df_analyzed)
    
    # Générer les insights
    insights = analyzer.generate_insights(df_analyzed, stats)
    
    # Afficher les insights
    logger.info("\n" + "=" * 60)
    logger.info("💡 INSIGHTS BUSINESS")
    logger.info("=" * 60)
    for insight in insights:
        logger.info(insight)
    logger.info("=" * 60 + "\n")
    
    # Sauvegarder
    df_analyzed.to_csv(output_file, index=False, encoding='utf-8')
    logger.info(f"✅ Résultats sauvegardés : {output_file}")
    
    return df_analyzed, stats, insights


# Point d'entrée si exécuté directement
if __name__ == "__main__":
    from src.logger import load_config
    
    config = load_config()
    
    # Analyser le dernier fichier nettoyé
    import glob
    import os
    
    processed_files = glob.glob(f"{config['paths']['processed_data']}/products_clean_*.csv")
    
    if processed_files:
        latest_file = max(processed_files, key=os.path.getctime)
        output_file = latest_file.replace('_clean_', '_analyzed_')
        
        analyze_products(latest_file, output_file, config)
    else:
        logger.error("❌ Aucun fichier nettoyé trouvé")