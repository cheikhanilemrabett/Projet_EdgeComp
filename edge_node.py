import pandas as pd
import json
import time
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from kafka import KafkaProducer

# إعدادات كافكا
SUJET_KAFKA = 'fraud-model-updates'
SERVEUR_KAFKA = 'localhost:9092'

def entrainer_et_envoyer(id_noeud, chemin_fichier):
    print(f"\n🚀 Démarrage du nœud : {id_noeud}")
    
    # 1. تحميل البيانات المحلية
    try:
        df = pd.read_csv(chemin_fichier)
    except FileNotFoundError:
        print(f"❌ Le fichier {chemin_fichier} est introuvable. Assurez-vous de lancer la simulation d'abord.")
        return

    # فصل الهدف (isFraud) عن الميزات
    X = df.drop('isFraud', axis=1)
    y = df['isFraud']

    # 2. التدريب المحلي (Local Training)
    print(f"   🛠️  Entraînement local du modèle sur {len(df)} transactions...")
    modele = LogisticRegression(max_iter=1000)
    modele.fit(X, y)
    
    precision = modele.score(X, y)
    print(f"   ✅ Entraînement terminé. Précision du modèle local : {precision:.2%}")

    # 3. تجهيز الأوزان للإرسال (Federated Learning Update)
    # نستخرج المعاملات (coef) والقاطع (intercept)
    poids = modele.coef_.tolist()[0]
    biais = modele.intercept_.tolist()[0]
    
    message = {
        'node_id': id_noeud,
        'weights': poids,        # ما تعلمه النموذج
        'intercept': biais,
        'num_samples': len(df),  # وزن العقدة في التجميع (تم تعديله ليتوافق مع السيرفر)
        'accuracy': precision
    }

    # 4. الإرسال عبر Kafka Producer
    producteur = KafkaProducer(
        bootstrap_servers=SERVEUR_KAFKA,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print(f"   📡 Envoi des poids au cloud (Kafka Topic: {SUJET_KAFKA})...")
    producteur.send(SUJET_KAFKA, message)
    producteur.flush()
    print("   ✅ Envoi réussi !")
    producteur.close()

if __name__ == "__main__":
    # يمكن تمرير رقم العقدة كمعامل (argument)
    # مثال للتشغيل: python edge_node.py 1
    if len(sys.argv) > 1:
        num_noeud = sys.argv[1]
    else:
        num_noeud = "1" # الافتراضي
        
    fichier_donnees = f"donnees_edge/node_{num_noeud}.csv"
    entrainer_et_envoyer(f"Agency_{num_noeud}", fichier_donnees)