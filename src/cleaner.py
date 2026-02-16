"""
Module de nettoyage et de préparation des données
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_raw_data(filepath="data/raw/products.csv"):
    """
    Charge les données brutes depuis un fichier CSV
    
    Args:
        filepath (str): Chemin du fichier CSV
        
    Returns:
        pd.DataFrame: DataFrame chargé
    """
    print(f"📂 Chargement des données depuis {filepath}...")
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        print(f"✅ {len(df)} lignes chargées\n")
        return df
    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {filepath}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None


def inspect_data(df):
    """
    Affiche un diagnostic complet du DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame à inspecter
    """
    print("=" * 60)
    print("🔍 DIAGNOSTIC DES DONNÉES")
    print("=" * 60)
    
    # 1. Dimensions
    print(f"\n📊 Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")
    
    # 2. Aperçu des premières lignes
    print("\n📋 Aperçu des données :")
    print(df.head())
    
    # 3. Types de données
    print("\n🏷️ Types de données :")
    print(df.dtypes)
    
    # 4. Valeurs manquantes
    print("\n❓ Valeurs manquantes :")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Colonnes': missing.index,
        'Manquantes': missing.values,
        'Pourcentage': missing_pct.values
    })
    print(missing_df[missing_df['Manquantes'] > 0])
    
    # 5. Doublons
    duplicates = df.duplicated().sum()
    print(f"\n🔁 Nombre de doublons : {duplicates}")
    
    # 6. Statistiques descriptives (colonnes numériques)
    print("\n📈 Statistiques descriptives :")
    print(df.describe())
    
    print("\n" + "=" * 60)


def clean_data(df):
    """
    Nettoie le DataFrame selon les règles métier
    
    Args:
        df (pd.DataFrame): DataFrame brut
        
    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    print("\n🧹 NETTOYAGE DES DONNÉES")
    print("=" * 60)
    
    # Copie pour ne pas modifier l'original
    df_clean = df.copy()
    
    initial_rows = len(df_clean)
    
    # 1️⃣ Suppression des doublons
    print("\n1️⃣ Suppression des doublons...")
    duplicates_before = df_clean.duplicated().sum()
    df_clean = df_clean.drop_duplicates()
    duplicates_removed = duplicates_before - df_clean.duplicated().sum()
    print(f"   ✅ {duplicates_removed} doublons supprimés")
    
    # 2️⃣ Gestion des valeurs manquantes
    print("\n2️⃣ Gestion des valeurs manquantes...")
    
    # Pour le prix : on supprime les lignes sans prix (info critique)
    missing_price_before = df_clean['price'].isnull().sum()
    df_clean = df_clean.dropna(subset=['price'])
    missing_price_removed = missing_price_before - df_clean['price'].isnull().sum()
    print(f"   ✅ {missing_price_removed} lignes sans prix supprimées")
    
    # Pour le titre : on supprime aussi (info critique)
    missing_title_before = df_clean['title'].isnull().sum()
    df_clean = df_clean.dropna(subset=['title'])
    missing_title_removed = missing_title_before - df_clean['title'].isnull().sum()
    print(f"   ✅ {missing_title_removed} lignes sans titre supprimées")
    
    # Pour la catégorie : on remplace par "Uncategorized"
    missing_category = df_clean['category'].isnull().sum()
    df_clean['category'] = df_clean['category'].fillna('Uncategorized')
    print(f"   ✅ {missing_category} catégories manquantes remplacées par 'Uncategorized'")
    
    # 3️⃣ Nettoyage des prix
    print("\n3️⃣ Nettoyage des prix...")
    # S'assurer que les prix sont bien numériques
    df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')
    # Supprimer les prix <= 0 ou aberrants (> 10000)
    invalid_prices = ((df_clean['price'] <= 0) | (df_clean['price'] > 10000)).sum()
    df_clean = df_clean[(df_clean['price'] > 0) & (df_clean['price'] <= 10000)]
    print(f"   ✅ {invalid_prices} prix invalides supprimés")
    
    # 4️⃣ Standardisation des catégories
    print("\n4️⃣ Standardisation des catégories...")
    # Mettre en title case et enlever les espaces
    df_clean['category'] = df_clean['category'].str.strip().str.title()
    unique_categories = df_clean['category'].nunique()
    print(f"   ✅ Catégories standardisées ({unique_categories} catégories uniques)")
    
    # 5️⃣ Nettoyage des titres
    print("\n5️⃣ Nettoyage des titres...")
    # Enlever les espaces en début/fin
    df_clean['title'] = df_clean['title'].str.strip()
    # Limiter la longueur à 100 caractères pour l'affichage
    df_clean['title_short'] = df_clean['title'].str[:100]
    print(f"   ✅ Titres nettoyés")
    
    # 6️⃣ Ajout de métadonnées
    print("\n6️⃣ Ajout de métadonnées...")
    df_clean['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_clean['data_quality'] = 'clean'
    print(f"   ✅ Métadonnées ajoutées")
    
    final_rows = len(df_clean)
    rows_removed = initial_rows - final_rows
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSUMÉ DU NETTOYAGE")
    print("=" * 60)
    print(f"Lignes initiales : {initial_rows}")
    print(f"Lignes finales   : {final_rows}")
    print(f"Lignes supprimées: {rows_removed} ({(rows_removed/initial_rows)*100:.1f}%)")
    print("=" * 60 + "\n")
    
    return df_clean


def save_clean_data(df, filepath="data/processed/products_clean.csv"):
    """
    Sauvegarde le DataFrame nettoyé
    
    Args:
        df (pd.DataFrame): DataFrame nettoyé
        filepath (str): Chemin de sauvegarde
    """
    print(f"💾 Sauvegarde des données nettoyées dans {filepath}...")
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"✅ Sauvegarde réussie !\n")


# Point d'entrée du script
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧹 PIPELINE DE NETTOYAGE DE DONNÉES")
    print("=" * 60 + "\n")
    
    # 1. Charger les données brutes
    df_raw = load_raw_data()
    
    if df_raw is not None:
        # 2. Inspecter les données
        inspect_data(df_raw)
        
        # 3. Nettoyer les données
        df_clean = clean_data(df_raw)
        
        # 4. Inspecter les données nettoyées
        print("\n📊 INSPECTION DES DONNÉES NETTOYÉES")
        inspect_data(df_clean)
        
        # 5. Sauvegarder
        save_clean_data(df_clean)
        
        print("✅ Pipeline de nettoyage terminé avec succès !")
    else:
        print("❌ Impossible de continuer sans données.")