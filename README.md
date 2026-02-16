# 📊 Competitive Intelligence Dashboard

> Pipeline automatisé de veille concurrentielle avec analyse IA et dashboards Excel

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Objectif

Automatiser la collecte, l'analyse et la visualisation de données concurrentielles pour faciliter la prise de décision business.

## ✨ Fonctionnalités

- 📡 **Collecte automatisée** de données via API REST
- 🧹 **Nettoyage intelligent** avec gestion des valeurs manquantes et doublons
- 🤖 **Analyse IA** : sentiment analysis sur les descriptions de produits
- 📊 **Dashboard Excel** professionnel avec KPIs et graphiques interactifs
- 📝 **Logging complet** pour traçabilité et debugging
- ⚙️ **Configuration flexible** via fichiers YAML

## 🛠️ Technologies utilisées

- **Python 3.10+**
- **Pandas** : Manipulation de données
- **Transformers (Hugging Face)** : Analyse de sentiment (NLP)
- **XlsxWriter** : Génération de dashboards Excel
- **Requests** : Requêtes HTTP/API
- **PyYAML** : Gestion de configuration

## 📦 Installation
```bash
# Cloner le projet
git clone https://github.com/monkamnicole_-lab/competitive-intelligence-dashboard.git
cd competitive-intelligence-dashboard

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancer le pipeline complet
```bash
python main.py
```

Le pipeline exécute automatiquement :
1. Collecte de données via API
2. Nettoyage et validation
3. Analyse IA (sentiment analysis)
4. Génération du dashboard Excel

### Modules individuels
```bash
# Collecte uniquement
python src/scraper.py

# Nettoyage uniquement
python src/cleaner.py

# Analyse IA uniquement
python src/analyzer.py

# Dashboard Excel uniquement
python src/visualizer.py
```

## 📁 Structure du projet
```
competitive-intelligence-dashboard/
├── config/
│   └── config.yaml          # Configuration centralisée
├── data/
│   ├── raw/                 # Données brutes collectées
│   ├── processed/           # Données nettoyées et analysées
│   └── output/              # Dashboards Excel générés
├── logs/                    # Fichiers de logs
├── src/
│   ├── scraper.py          # Module de collecte
│   ├── cleaner.py          # Module de nettoyage
│   ├── analyzer.py         # Module d'analyse IA
│   ├── visualizer.py       # Module de visualisation
│   └── logger.py           # Système de logging
├── main.py                 # Pipeline principal
├── requirements.txt        # Dépendances Python
└── README.md
```

## 📊 Exemple de sortie

Le pipeline génère :
- ✅ Fichier CSV avec données brutes
- ✅ Fichier CSV avec données nettoyées
- ✅ Fichier CSV avec analyse de sentiment
- ✅ Dashboard Excel avec 3 onglets :
  - **Résumé** : KPIs et insights business
  - **Données** : Tableau formaté et filtrable
  - **Graphiques** : Visualisations interactives

## 🎓 Compétences démontrées

- **Data Engineering** : ETL, nettoyage de données, gestion de pipelines
- **Machine Learning** : NLP, sentiment analysis, utilisation de modèles pré-entraînés
- **DevOps** : Logging, gestion d'erreurs, configuration externalisée
- **Business Intelligence** : Visualisation, KPIs, insights business
- **Bonnes pratiques** : Code modulaire, documentation, versioning Git

## 👤 Auteur

**[Ton Nom]**  
En recherche d'alternance   
📧 [monkamnicole8@gmail.com]  

---

⭐ **N'hésitez pas à star le projet si vous le trouvez utile !**