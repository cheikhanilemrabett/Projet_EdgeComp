<div align="center">

# 📚 Ressources et Références

**Sources de données • Outils technologiques • Références académiques**

</div>

---

Ce document regroupe les sources de données, les outils technologiques et les références académiques utilisées pour la réalisation du projet de détection de fraude distribuée.

---

## 💾 Dataset (Jeu de Données)

Le projet utilise un jeu de données synthétique simulant des transactions financières mobiles (Mobile Money), idéal pour la détection de fraude financière.

<div align="center">

| Propriété | Détail |
|-----------|--------|
| **Nom** | Synthetic Mobile Money Transaction Dataset |
| **Source** | Kaggle |
| **Lien** | [📥 Télécharger le dataset](https://www.kaggle.com/datasets/denishazamuke/synthetic-mobile-money-transaction-dataset) |
| **Description** | Contient des logs de transactions (`CASH_IN`, `CASH_OUT`, `DEBIT`, `PAYMENT`, `TRANSFER`) avec une étiquette `isFraud` |

</div>

---

## 🛠 Stack Technologique

<div align="center">

| Catégorie | Technologie | Version/Détails |
|-----------|-------------|-----------------|
| **Langage** | ![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white) | Python 3.9 |
| **Machine Learning** | ![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Logistic%20Regression-orange?logo=scikitlearn) | Logistic Regression |
| **Messaging / Fog Layer** | ![Kafka](https://img.shields.io/badge/Apache%20Kafka-Confluent-black?logo=apachekafka) | Confluent Image |
| **Virtualisation** | ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white) | Docker & Docker Compose |
| **Monitoring** | ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white) | Dashboard interactif |

</div>

---

## 📖 Références Académiques & Concepts

### 1. **Federated Learning (Apprentissage Fédéré)**
```
McMahan, B., et al. (2017)
"Communication-Efficient Learning of Deep Networks from Decentralized Data"
```

> **Concept clé :** `FedAvg` (Weighted Averaging)

---

### 2. **Edge Computing**
```
Principe du traitement des données à la source pour réduire 
la latence et préserver la bande passante
```

---

### 3. **Architecture Data-to-Code**
```
Paradigme consistant à envoyer l'algorithme vers les données 
plutôt que l'inverse, essentiel pour la conformité RGPD et BCM
```

---

<div align="center">



</div>
