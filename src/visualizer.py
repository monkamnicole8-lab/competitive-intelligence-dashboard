"""
Module de visualisation - Génération de dashboards Excel automatiques
"""

import pandas as pd
import xlsxwriter
from datetime import datetime
import sys
import os

# Ajouter les dossiers au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from src.logger import get_logger

logger = get_logger(__name__)


class ExcelDashboard:
    """
    Classe pour créer des dashboards Excel professionnels
    """
    
    def __init__(self, output_file):
        """
        Initialise le dashboard
        
        Args:
            output_file (str): Chemin du fichier Excel de sortie
        """
        self.output_file = output_file
        self.workbook = xlsxwriter.Workbook(output_file)
        
        # Définir des formats réutilisables
        self.formats = {
            'title': self.workbook.add_format({
                'bold': True,
                'font_size': 16,
                'font_color': 'white',
                'bg_color': '#2E75B6',
                'align': 'center',
                'valign': 'vcenter'
            }),
            'header': self.workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#D9E1F2',
                'border': 1,
                'align': 'center'
            }),
            'cell': self.workbook.add_format({
                'border': 1,
                'align': 'left'
            }),
            'cell_center': self.workbook.add_format({
                'border': 1,
                'align': 'center'
            }),
            'currency': self.workbook.add_format({
                'border': 1,
                'num_format': '$#,##0.00'
            }),
            'percent': self.workbook.add_format({
                'border': 1,
                'num_format': '0.0%'
            }),
            'metric': self.workbook.add_format({
                'bold': True,
                'font_size': 24,
                'font_color': '#2E75B6',
                'align': 'center'
            }),
            'metric_label': self.workbook.add_format({
                'font_size': 10,
                'font_color': '#666666',
                'align': 'center'
            })
        }
        
        logger.info(f"📊 Dashboard Excel initialisé : {output_file}")
    
    
    def create_summary_sheet(self, df, stats, insights):
        """
        Crée la feuille de résumé avec KPIs
        
        Args:
            df (pd.DataFrame): Données analysées
            stats (dict): Statistiques calculées
            insights (list): Liste d'insights
        """
        logger.info("📋 Création de la feuille Résumé...")
        
        worksheet = self.workbook.add_worksheet('Résumé')
        
        # Titre
        worksheet.merge_range('A1:F1', '📊 DASHBOARD VEILLE CONCURRENTIELLE', self.formats['title'])
        worksheet.set_row(0, 30)
        
        # Date de génération
        worksheet.write('A2', f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # KPIs (Indicateurs clés)
        row = 4
        
        # KPI 1 : Nombre de produits
        worksheet.merge_range(row, 0, row, 1, stats['total_products'], self.formats['metric'])
        worksheet.merge_range(row+1, 0, row+1, 1, 'Produits analysés', self.formats['metric_label'])
        
        # KPI 2 : Prix moyen
        worksheet.merge_range(row, 2, row, 3, f"${stats['avg_price']:.2f}", self.formats['metric'])
        worksheet.merge_range(row+1, 2, row+1, 3, 'Prix moyen', self.formats['metric_label'])
        
        # KPI 3 : Sentiment positif
        if 'sentiment_distribution' in stats:
            positive_pct = stats['sentiment_distribution'].get('POSITIVE', 0) / stats['total_products']
            worksheet.merge_range(row, 4, row, 5, f"{positive_pct:.0%}", self.formats['metric'])
            worksheet.merge_range(row+1, 4, row+1, 5, 'Sentiment positif', self.formats['metric_label'])
        
        # Statistiques détaillées
        row = 8
        worksheet.write(row, 0, 'STATISTIQUES DÉTAILLÉES', self.formats['header'])
        row += 1
        
        stats_data = [
            ['Nombre de produits', stats['total_products']],
            ['Prix moyen', f"${stats['avg_price']:.2f}"],
            ['Prix médian', f"${stats['median_price']:.2f}"],
            ['Prix minimum', f"${stats['min_price']:.2f}"],
            ['Prix maximum', f"${stats['max_price']:.2f}"],
            ['Écart-type', f"${stats['std_price']:.2f}"],
        ]
        
        for label, value in stats_data:
            worksheet.write(row, 0, label, self.formats['cell'])
            if isinstance(value, str) and value.startswith('$'):
                worksheet.write(row, 1, float(value.replace('$', '').replace(',', '')), self.formats['currency'])
            else:
                worksheet.write(row, 1, value, self.formats['cell_center'])
            row += 1
        
        # Insights
        row += 2
        worksheet.write(row, 0, '💡 INSIGHTS BUSINESS', self.formats['header'])
        row += 1
        
        for insight in insights:
            worksheet.write(row, 0, insight)
            row += 1
        
        # Ajuster les largeurs de colonnes
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:F', 12)
        
        logger.info("✅ Feuille Résumé créée")
    
    
    def create_data_sheet(self, df):
        """
        Crée la feuille avec les données brutes
        
        Args:
            df (pd.DataFrame): Données à afficher
        """
        logger.info("📋 Création de la feuille Données...")
        
        worksheet = self.workbook.add_worksheet('Données')
        
        # Titre
        worksheet.merge_range('A1:F1', 'DONNÉES ANALYSÉES', self.formats['title'])
        worksheet.set_row(0, 25)
        
        # En-têtes
        for col_num, column in enumerate(df.columns):
            worksheet.write(2, col_num, column, self.formats['header'])
        
        # Données
        for row_num, row_data in enumerate(df.values):
            for col_num, cell_data in enumerate(row_data):
                if df.columns[col_num] == 'price':
                    worksheet.write(row_num + 3, col_num, cell_data, self.formats['currency'])
                elif df.columns[col_num] == 'sentiment_score':
                    worksheet.write(row_num + 3, col_num, cell_data, self.formats['percent'])
                else:
                    worksheet.write(row_num + 3, col_num, cell_data, self.formats['cell'])
        
        # Ajuster les colonnes
        worksheet.set_column('A:A', 8)   # id
        worksheet.set_column('B:B', 50)  # title
        worksheet.set_column('C:C', 12)  # price
        worksheet.set_column('D:D', 20)  # category
        worksheet.set_column('E:E', 15)  # sentiment
        worksheet.set_column('F:F', 15)  # sentiment_score
        
        logger.info("✅ Feuille Données créée")
    
    
    def create_charts_sheet(self, df, stats):
        """
        Crée la feuille avec les graphiques
        
        Args:
            df (pd.DataFrame): Données
            stats (dict): Statistiques
        """
        logger.info("📊 Création de la feuille Graphiques...")
        
        worksheet = self.workbook.add_worksheet('Graphiques')
        
        # Titre
        worksheet.merge_range('A1:L1', 'VISUALISATIONS', self.formats['title'])
        worksheet.set_row(0, 25)
        
        # ═══════════════════════════════════════════════════════
        # GRAPHIQUE 1 : Prix moyen par catégorie (Barres)
        # ═══════════════════════════════════════════════════════
        if 'avg_price_by_category' in stats:
            # Préparer les données
            categories = list(stats['avg_price_by_category'].keys())
            prices = list(stats['avg_price_by_category'].values())
            
            # Écrire les données dans le sheet (invisible pour l'utilisateur)
            row = 2
            worksheet.write(row, 0, 'Catégorie', self.formats['header'])
            worksheet.write(row, 1, 'Prix moyen', self.formats['header'])
            
            for i, (cat, price) in enumerate(zip(categories, prices)):
                worksheet.write(row + 1 + i, 0, cat)
                worksheet.write(row + 1 + i, 1, price)
            
            # Créer le graphique
            chart1 = self.workbook.add_chart({'type': 'column'})
            chart1.add_series({
                'name': 'Prix moyen',
                'categories': f'=Graphiques!$A${row+2}:$A${row+1+len(categories)}',
                'values': f'=Graphiques!$B${row+2}:$B${row+1+len(categories)}',
                'fill': {'color': '#2E75B6'},
            })
            
            chart1.set_title({'name': 'Prix moyen par catégorie'})
            chart1.set_x_axis({'name': 'Catégorie'})
            chart1.set_y_axis({'name': 'Prix ($)'})
            chart1.set_style(10)
            
            worksheet.insert_chart('D3', chart1, {'x_scale': 1.5, 'y_scale': 1.2})
        
        # ═══════════════════════════════════════════════════════
        # GRAPHIQUE 2 : Distribution des sentiments (Camembert)
        # ═══════════════════════════════════════════════════════
        if 'sentiment_distribution' in stats:
            sentiments = list(stats['sentiment_distribution'].keys())
            counts = list(stats['sentiment_distribution'].values())
            
            # Écrire les données
            row = 15
            worksheet.write(row, 0, 'Sentiment', self.formats['header'])
            worksheet.write(row, 1, 'Nombre', self.formats['header'])
            
            for i, (sent, count) in enumerate(zip(sentiments, counts)):
                worksheet.write(row + 1 + i, 0, sent)
                worksheet.write(row + 1 + i, 1, count)
            
            # Créer le graphique
            chart2 = self.workbook.add_chart({'type': 'pie'})
            chart2.add_series({
                'name': 'Distribution des sentiments',
                'categories': f'=Graphiques!$A${row+2}:$A${row+1+len(sentiments)}',
                'values': f'=Graphiques!$B${row+2}:$B${row+1+len(sentiments)}',
                'points': [
                    {'fill': {'color': '#70AD47'}},  # POSITIVE = vert
                    {'fill': {'color': '#FF6B6B'}},  # NEGATIVE = rouge
                ],
            })
            
            chart2.set_title({'name': 'Distribution des sentiments'})
            chart2.set_style(10)
            
            worksheet.insert_chart('D20', chart2, {'x_scale': 1.5, 'y_scale': 1.2})
        
        logger.info("✅ Feuille Graphiques créée")
    
    
    def close(self):
        """
        Ferme et sauvegarde le workbook
        """
        self.workbook.close()
        logger.info(f"✅ Dashboard Excel sauvegardé : {self.output_file}")


def create_dashboard(df, stats, insights, output_file):
    """
    Fonction principale pour créer un dashboard Excel complet
    
    Args:
        df (pd.DataFrame): Données analysées
        stats (dict): Statistiques
        insights (list): Insights
        output_file (str): Fichier de sortie
    """
    logger.info("=" * 60)
    logger.info("📊 CRÉATION DU DASHBOARD EXCEL")
    logger.info("=" * 60)
    
    # Créer le dashboard
    dashboard = ExcelDashboard(output_file)
    
    # Créer les feuilles
    dashboard.create_summary_sheet(df, stats, insights)
    dashboard.create_data_sheet(df)
    dashboard.create_charts_sheet(df, stats)
    
    # Sauvegarder
    dashboard.close()
    
    logger.info("=" * 60)
    logger.info(f"✅ Dashboard Excel créé : {output_file}")
    logger.info("=" * 60)
    
    return output_file


# Point d'entrée si exécuté directement
if __name__ == "__main__":
    from src.logger import load_config
    import glob
    
    config = load_config()
    
    # Trouver le dernier fichier analysé
    analyzed_files = glob.glob(f"{config['paths']['processed_data']}/products_analyzed_*.csv")
    
    if analyzed_files:
        latest_file = max(analyzed_files, key=os.path.getctime)
        
        logger.info(f"📂 Chargement : {latest_file}")
        df = pd.read_csv(latest_file, encoding='utf-8')
        
        # Recalculer les stats (simplifié pour le test)
        stats = {
            'total_products': len(df),
            'avg_price': df['price'].mean(),
            'median_price': df['price'].median(),
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'std_price': df['price'].std(),
            'avg_price_by_category': df.groupby('category')['price'].mean().to_dict(),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict() if 'sentiment' in df.columns else {}
        }
        
        insights = [
            "Dashboard généré automatiquement",
            f"Analyse de {len(df)} produits",
            f"Prix moyen : ${stats['avg_price']:.2f}"
        ]
        
        # Créer le dashboard
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{config['paths']['output_data']}/dashboard_{timestamp}.xlsx"
        
        create_dashboard(df, stats, insights, output_file)
        
    else:
        logger.error("❌ Aucun fichier analysé trouvé")