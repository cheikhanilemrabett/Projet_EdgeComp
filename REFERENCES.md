---

```markdown
# 📚 Références et Ressources

Ce document regroupe les sources de données, les outils technologiques et les références académiques utilisées pour la réalisation du projet de détection de fraude distribuée.

## 💾 Dataset (Jeu de Données)

Le projet utilise un jeu de données synthétique simulant des transactions financières mobiles (Mobile Money), idéal pour la détection de fraude financière.

* **Nom** : Synthetic Mobile Money Transaction Dataset
* **Source** : Kaggle
* **Lien** : [https://www.kaggle.com/datasets/denishazamuke/synthetic-mobile-money-transaction-dataset](https://www.kaggle.com/datasets/denishazamuke/synthetic-mobile-money-transaction-dataset)
* **Description** : Contient des logs de transactions (CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER) avec une étiquette `isFraud`.

## 🛠 Stack Technologique

* **Langage** : Python 3.9
* **Machine Learning** : Scikit-learn (Logistic Regression)
* **Messaging / Fog Layer** : Apache Kafka (Confluent Image)
* **Virtualisation** : Docker & Docker Compose
* **Monitoring** : Streamlit (pour le Dashboard)

## 📖 Références Académiques & Concepts

1.  **Federated Learning (Apprentissage Fédéré)**
    * *McMahan, B., et al. (2017).* "Communication-Efficient Learning of Deep Networks from Decentralized Data".
    * Concept clé : `FedAvg` (Weighted Averaging).

2.  **Edge Computing**
    * Principe du traitement des données à la source pour réduire la latence et préserver la bande passante.

3.  **Architecture Data-to-Code**
    * Paradigme consistant à envoyer l'algorithme vers les données plutôt que l'inverse, essentiel pour la conformité RGPD et BCM.