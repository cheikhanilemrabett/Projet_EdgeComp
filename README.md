> README.md << 'EOF'
# Système de Détection de Fraude Bancaire Distribué 🛡️💸

![Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-Streaming-black)

Ce projet implémente une architecture **Edge Computing** et **Federated Learning** pour détecter la fraude dans les transactions de mobile money (type Bankily/Masrivi) en Mauritanie. L'objectif est de créer un modèle d'IA global sans jamais déplacer les données privées des clients hors des agences locales.

---

## 📑 Table des Matières
- [Contexte et Problématique](#-contexte-et-problématique)
- [Architecture Technique](#-architecture-technique)
- [Installation et Utilisation](#-installation-et-utilisation)
- [Résultats](#-résultats)
- [Auteurs](#-auteurs)

---

## 🧐 Contexte et Problématique
Les systèmes centralisés classiques ("Code-to-Data") posent des risques de sécurité majeurs et violent souvent les régulations de confidentialité (BCM). Ce projet adopte l'approche **"Data-to-Code"** :
1. Les données restent dans l'agence (Edge).
2. Le code se déplace vers les données pour l'entraînement.
3. Seuls les **poids mathématiques** (connaissance) sont partagés via un canal sécurisé.

---

## 🏗 Architecture Technique

Le système repose sur trois couches logiques :

### 1. Edge Layer (Les Agences) 🏦
- **Technologie :** Python, Scikit-learn.
- **Rôle :** Entraînement local des modèles `LogisticRegression`.
- **Confidentialité :** Aucune donnée brute (CSV) ne sort du conteneur Docker de l'agence.

### 2. Fog Layer (Le Transport) ☁️
- **Technologie :** Apache Kafka, Zookeeper.
- **Rôle :** Decoupling et buffering. Assure que les mises à jour de modèles ne sont jamais perdues, même si le serveur central est hors ligne.

### 3. Cloud Layer (Le Cerveau) 🧠
- **Technologie :** Python (Custom Aggregator).
- **Algorithme :** `FedAvg` (Federated Averaging).
- **Rôle :** Agrégation des poids reçus pour créer un "Modèle National".

---

## 🚀 Installation et Utilisation

### Prérequis
- Docker & Docker Compose
- Python 3.8+

### Démarrage Rapide (Simulation)

1. **Lancer l'infrastructure (Kafka & Zookeeper)**
   ```bash
   docker-compose up -d

2. **Démarrer le Serveur Central (Cloud) Le serveur se met en mode écoute sur le topic fraud-model-updates**
    ```bash
   python cloud_server.py

3. **Lancer les Nœuds Edge (Agences) Dans de nouveaux terminaux, simulez les agences (Agence 1, Agence 2, Agence 3) :**
     ```bash
    # Agence 1
    python edge_node.py 1

    # Agence 2
    python edge_node.py 2
        

