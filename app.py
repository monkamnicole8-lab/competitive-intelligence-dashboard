"""
Application web Streamlit pour le dashboard de veille concurrentielle
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import glob
import sys
import time

# Ajouter après st.set_page_config()
# Auto-refresh toutes les 5 minutes (optionnel)
if st.sidebar.checkbox("🔄 Auto-refresh (5 min)"):
    st.sidebar.info("La page se rafraîchira automatiquement toutes les 5 minutes")
    time.sleep(300)  # 300 secondes = 5 minutes
    st.rerun()

# Configuration de la page (doit être en premier)
st.set_page_config(
    page_title="Veille Concurrentielle",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le dossier au path
sys.path.insert(0, os.path.dirname(__file__))

from src.logger import load_config


# ═══════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_latest_data(folder_path, pattern):
    """
    Charge le fichier le plus récent correspondant au pattern
    """
    files = glob.glob(os.path.join(folder_path, pattern))
    if not files:
        return None
    
    latest_file = max(files, key=os.path.getctime)
    df = pd.read_csv(latest_file, encoding='utf-8')
    return df, latest_file


def calculate_stats(df):
    """
    Calcule les statistiques à partir du DataFrame
    """
    stats = {
        'total_products': len(df),
        'avg_price': df['price'].mean(),
        'median_price': df['price'].median(),
        'min_price': df['price'].min(),
        'max_price': df['price'].max(),
        'std_price': df['price'].std(),
    }
    
    if 'category' in df.columns:
        stats['categories'] = df['category'].value_counts().to_dict()
        stats['avg_price_by_category'] = df.groupby('category')['price'].mean().to_dict()
    
    if 'sentiment' in df.columns:
        stats['sentiment_distribution'] = df['sentiment'].value_counts().to_dict()
        stats['avg_sentiment_score'] = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0
    
    return stats


# ═══════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION
# ═══════════════════════════════════════════════════════

st.sidebar.title("📊 Veille Concurrentielle")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🚀 Exécuter Pipeline", "📁 Données", "⚙️ Configuration"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Application développée avec**\n\n"
    "- Python 🐍\n"
    "- Streamlit 🌐\n"
    "- Transformers 🤖\n"
    "- Plotly 📊"
)


# ═══════════════════════════════════════════════════════
# PAGE 1 : DASHBOARD
# ═══════════════════════════════════════════════════════

if page == "🏠 Dashboard":
    st.title("📊 Dashboard de Veille Concurrentielle")
    st.markdown("---")
    
    # Charger les données
    config = load_config()
    
    result = load_latest_data(
        config['paths']['processed_data'],
        'products_analyzed_*.csv'
    )
    
    if result is None:
        st.warning("⚠️ Aucune donnée disponible. Veuillez exécuter le pipeline d'abord.")
        st.info("👉 Allez dans la section **🚀 Exécuter Pipeline** pour lancer la collecte de données.")
    else:
        df, filepath = result
        stats = calculate_stats(df)
        
        # Afficher la date de dernière mise à jour
        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
        st.caption(f"📅 Dernière mise à jour : {file_time.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # ═══════════════════════════════════════════════════════
        # KPIs (Indicateurs clés)
        # ═══════════════════════════════════════════════════════
        
        st.subheader("📈 Indicateurs Clés")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Produits analysés",
                value=stats['total_products'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="Prix moyen",
                value=f"${stats['avg_price']:.2f}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Prix médian",
                value=f"${stats['median_price']:.2f}",
                delta=None
            )
        
        with col4:
            if 'sentiment_distribution' in stats and stats['sentiment_distribution']:
                positive_count = stats['sentiment_distribution'].get('POSITIVE', 0)
                positive_pct = (positive_count / stats['total_products']) * 100
                st.metric(
                    label="Sentiment positif",
                    value=f"{positive_pct:.0f}%",
                    delta=None
                )
            else:
                st.metric(
                    label="Catégories",
                    value=len(stats.get('categories', {})),
                    delta=None
                )
        
        st.markdown("---")
        
        # ═══════════════════════════════════════════════════════
        # GRAPHIQUES
        # ═══════════════════════════════════════════════════════
        
        st.subheader("📊 Visualisations")
        
        # Layout en colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique 1 : Prix moyen par catégorie
            if 'avg_price_by_category' in stats:
                st.markdown("#### Prix moyen par catégorie")
                
                fig1 = px.bar(
                    x=list(stats['avg_price_by_category'].keys()),
                    y=list(stats['avg_price_by_category'].values()),
                    labels={'x': 'Catégorie', 'y': 'Prix moyen ($)'},
                    color=list(stats['avg_price_by_category'].values()),
                    color_continuous_scale='Blues'
                )
                
                fig1.update_layout(
                    showlegend=False,
                    height=400,
                    xaxis_title="Catégorie",
                    yaxis_title="Prix moyen ($)"
                )
                
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Graphique 2 : Distribution des sentiments
            if 'sentiment_distribution' in stats and stats['sentiment_distribution']:
                st.markdown("#### Distribution des sentiments")
                
                colors = {
                    'POSITIVE': '#70AD47',
                    'NEGATIVE': '#FF6B6B',
                    'NEUTRAL': '#FFC107'
                }
                
                sentiments = list(stats['sentiment_distribution'].keys())
                values = list(stats['sentiment_distribution'].values())
                color_list = [colors.get(s, '#999999') for s in sentiments]
                
                fig2 = go.Figure(data=[go.Pie(
                    labels=sentiments,
                    values=values,
                    marker=dict(colors=color_list),
                    hole=0.3
                )])
                
                fig2.update_layout(height=400)
                
                st.plotly_chart(fig2, use_container_width=True)
        
        # Graphique 3 : Distribution des prix (histogramme)
        st.markdown("#### Distribution des prix")
        
        fig3 = px.histogram(
            df,
            x='price',
            nbins=20,
            labels={'price': 'Prix ($)', 'count': 'Nombre de produits'},
            color_discrete_sequence=['#2E75B6']
        )
        
        fig3.update_layout(
            showlegend=False,
            height=300,
            xaxis_title="Prix ($)",
            yaxis_title="Nombre de produits"
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")

        # Graphique 4 : Corrélation Prix vs Sentiment Score
        if 'sentiment_score' in df.columns:
            st.markdown("#### Relation Prix / Score de Sentiment")
            
            fig4 = px.scatter(
                df,
                x='sentiment_score',
                y='price',
                color='sentiment' if 'sentiment' in df.columns else None,
                hover_data=['title', 'category'],
                labels={
                    'sentiment_score': 'Score de sentiment',
                    'price': 'Prix ($)',
                    'sentiment': 'Sentiment'
                },
                color_discrete_map={
                    'POSITIVE': '#70AD47',
                    'NEGATIVE': '#FF6B6B',
                    'NEUTRAL': '#FFC107'
                }
            )
            
            fig4.update_layout(height=400)
            
            st.plotly_chart(fig4, use_container_width=True)
        
        # ═══════════════════════════════════════════════════════
        # TABLEAU DE DONNÉES
        # ═══════════════════════════════════════════════════════
        
        st.subheader("📋 Aperçu des données")
        
        # Filtres
        col1, col2 = st.columns(2)
        
        with col1:
            if 'category' in df.columns:
                categories = ['Toutes'] + sorted(df['category'].unique().tolist())
                selected_category = st.selectbox("Filtrer par catégorie", categories)
        
        with col2:
            if 'sentiment' in df.columns:
                sentiments = ['Tous'] + sorted(df['sentiment'].unique().tolist())
                selected_sentiment = st.selectbox("Filtrer par sentiment", sentiments)
        
        # Appliquer les filtres
        filtered_df = df.copy()
        
        if 'category' in df.columns and selected_category != 'Toutes':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        if 'sentiment' in df.columns and selected_sentiment != 'Tous':
            filtered_df = filtered_df[filtered_df['sentiment'] == selected_sentiment]
        
        # Afficher le tableau
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        
        # Statistiques du tableau filtré
        st.caption(f"📊 {len(filtered_df)} produits affichés sur {len(df)} au total")


# ═══════════════════════════════════════════════════════
# PAGE 2 : EXÉCUTER PIPELINE
# ═══════════════════════════════════════════════════════

elif page == "🚀 Exécuter Pipeline":
    st.title("🚀 Exécuter le Pipeline")
    st.markdown("---")
    
    st.info(
        "**Cette section permet de lancer manuellement le pipeline complet :**\n\n"
        "1. 📡 Collecte de données via API\n"
        "2. 🧹 Nettoyage et validation\n"
        "3. 🤖 Analyse IA (sentiment analysis)\n"
        "4. 📊 Génération du dashboard Excel"
    )
    
    st.markdown("---")
    
    if st.button("▶️ Lancer le pipeline", type="primary", use_container_width=True):
        
        with st.spinner("🔄 Exécution du pipeline en cours..."):
            
            # Conteneur pour les logs
            log_container = st.empty()
            
            try:
                # Import des modules
                from src.scraper import run_scraper
                from src.cleaner import load_raw_data, clean_data, save_clean_data
                from src.analyzer import analyze_products
                from src.visualizer import create_dashboard
                
                config = load_config()
                
                # Étape 1 : Collecte
                log_container.info("📡 Étape 1/4 : Collecte de données...")
                raw_file = run_scraper(config)
                
                if not raw_file:
                    st.error("❌ Échec de la collecte de données")
                    st.stop()
                
                log_container.success(f"✅ Collecte terminée : {os.path.basename(raw_file)}")
                
                # Étape 2 : Nettoyage
                log_container.info("🧹 Étape 2/4 : Nettoyage des données...")
                df_raw = load_raw_data(raw_file)
                df_clean = clean_data(df_raw)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                clean_file = f"{config['paths']['processed_data']}/products_clean_{timestamp}.csv"
                save_clean_data(df_clean, clean_file)
                
                log_container.success(f"✅ Nettoyage terminé : {os.path.basename(clean_file)}")
                
                # Étape 3 : Analyse IA
                log_container.info("🤖 Étape 3/4 : Analyse IA...")
                analyzed_file = clean_file.replace('_clean_', '_analyzed_')
                df_analyzed, stats, insights = analyze_products(clean_file, analyzed_file, config)
                
                log_container.success(f"✅ Analyse terminée : {os.path.basename(analyzed_file)}")
                
                # Étape 4 : Dashboard Excel
                log_container.info("📊 Étape 4/4 : Génération du dashboard Excel...")
                dashboard_file = f"{config['paths']['output_data']}/dashboard_{timestamp}.xlsx"
                create_dashboard(df_analyzed, stats, insights, dashboard_file)
                
                log_container.success(f"✅ Dashboard créé : {os.path.basename(dashboard_file)}")
                
                # Afficher le résumé
                st.success("🎉 Pipeline exécuté avec succès !")
                
                st.markdown("---")
                st.subheader("📊 Résumé")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Produits analysés", len(df_analyzed))
                    st.metric("Prix moyen", f"${stats['avg_price']:.2f}")
                
                with col2:
                    st.metric("Insights générés", len(insights))
                    if 'sentiment_distribution' in stats:
                        positive_pct = stats['sentiment_distribution'].get('POSITIVE', 0) / len(df_analyzed) * 100
                        st.metric("Sentiment positif", f"{positive_pct:.0f}%")
                
                # Téléchargement du dashboard
                st.markdown("---")
                st.subheader("📥 Téléchargement")
                
                with open(dashboard_file, 'rb') as f:
                    st.download_button(
                        label="📊 Télécharger le dashboard Excel",
                        data=f,
                        file_name=os.path.basename(dashboard_file),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"💥 Erreur lors de l'exécution : {str(e)}")
                st.exception(e)


# ═══════════════════════════════════════════════════════
# PAGE 3 : DONNÉES
# ═══════════════════════════════════════════════════════

elif page == "📁 Données":
    st.title("📁 Gestion des Données")
    st.markdown("---")
    
    config = load_config()
    
    # Liste des fichiers disponibles
    st.subheader("📂 Fichiers disponibles")
    
    tabs = st.tabs(["Données brutes", "Données nettoyées", "Données analysées", "Dashboards"])
    
    with tabs[0]:
        files = glob.glob(f"{config['paths']['raw_data']}/products_*.csv")
        if files:
            for f in sorted(files, key=os.path.getctime, reverse=True)[:10]:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(os.path.basename(f))
                with col2:
                    file_time = datetime.fromtimestamp(os.path.getctime(f))
                    st.caption(file_time.strftime('%d/%m/%Y %H:%M'))
                with col3:
                    file_size = os.path.getsize(f) / 1024
                    st.caption(f"{file_size:.1f} KB")
        else:
            st.info("Aucun fichier brut disponible")
    
    with tabs[1]:
        files = glob.glob(f"{config['paths']['processed_data']}/products_clean_*.csv")
        if files:
            for f in sorted(files, key=os.path.getctime, reverse=True)[:10]:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(os.path.basename(f))
                with col2:
                    file_time = datetime.fromtimestamp(os.path.getctime(f))
                    st.caption(file_time.strftime('%d/%m/%Y %H:%M'))
                with col3:
                    file_size = os.path.getsize(f) / 1024
                    st.caption(f"{file_size:.1f} KB")
        else:
            st.info("Aucun fichier nettoyé disponible")
    
    with tabs[2]:
        files = glob.glob(f"{config['paths']['processed_data']}/products_analyzed_*.csv")
        if files:
            for f in sorted(files, key=os.path.getctime, reverse=True)[:10]:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(os.path.basename(f))
                with col2:
                    file_time = datetime.fromtimestamp(os.path.getctime(f))
                    st.caption(file_time.strftime('%d/%m/%Y %H:%M'))
                with col3:
                    file_size = os.path.getsize(f) / 1024
                    st.caption(f"{file_size:.1f} KB")
        else:
            st.info("Aucun fichier analysé disponible")
    
    with tabs[3]:
        files = glob.glob(f"{config['paths']['output_data']}/dashboard_*.xlsx")
        if files:
            for f in sorted(files, key=os.path.getctime, reverse=True)[:10]:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                with col1:
                    st.text(os.path.basename(f))
                with col2:
                    file_time = datetime.fromtimestamp(os.path.getctime(f))
                    st.caption(file_time.strftime('%d/%m/%Y %H:%M'))
                with col3:
                    file_size = os.path.getsize(f) / 1024
                    st.caption(f"{file_size:.1f} KB")
                with col4:
                    with open(f, 'rb') as file:
                        st.download_button(
                            "📥",
                            data=file,
                            file_name=os.path.basename(f),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_{os.path.basename(f)}"
                        )
        else:
            st.info("Aucun dashboard disponible")


# ═══════════════════════════════════════════════════════
# PAGE 4 : CONFIGURATION
# ═══════════════════════════════════════════════════════

elif page == "⚙️ Configuration":
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    config = load_config()
    
    st.subheader("🔧 Paramètres actuels")
    
    with st.expander("📡 API Configuration"):
        st.json(config['api'])
    
    with st.expander("🧹 Data Processing"):
        st.json(config['processing'])
    
    with st.expander("📁 Paths"):
        st.json(config['paths'])
    
    st.markdown("---")
    
    st.info(
        "💡 **Pour modifier la configuration :**\n\n"
        "Éditez le fichier `config/config.yaml` et relancez l'application."
    )