import json
import numpy as np
from kafka import KafkaConsumer
import os

# إعدادات كافكا
SUJET_KAFKA = 'fraud-model-updates'
SERVEUR_KAFKA = 'localhost:9092'
FICHIER_HISTORIQUE = 'historique_modele_global.json'

def moyennage_federe(tampon_modeles):
    """
    تطبيق خوارزمية FedAvg:
    Global_Weight = Sum(Local_Weight * num_samples) / Total_Samples
    """
    total_echantillons = sum(m['num_samples'] for m in tampon_modeles)
    
    # حساب مجموع الأوزان الموزونة
    poids_ponderes = [np.array(m['weights']) * m['num_samples'] for m in tampon_modeles]
    biais_ponderes = [m['intercept'] * m['num_samples'] for m in tampon_modeles]
    
    # التجميع والقسمة على العدد الكلي
    poids_globaux = np.sum(poids_ponderes, axis=0) / total_echantillons
    biais_global = sum(biais_ponderes) / total_echantillons
    
    # حساب متوسط الدقة (للعرض فقط)
    precision_moyenne = sum(m['accuracy'] * m['num_samples'] for m in tampon_modeles) / total_echantillons
    
    return poids_globaux.tolist(), biais_global, precision_moyenne

def demarrer_serveur():
    print(f"📡 Le serveur central est en cours d'exécution... Écoute sur le sujet : {SUJET_KAFKA}")
    
    consommateur = KafkaConsumer(
        SUJET_KAFKA,
        bootstrap_servers=SERVEUR_KAFKA,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )

    tampon_modeles = []
    num_round = 1
    
    # التأكد من وجود ملف فارغ للسجل
    with open(FICHIER_HISTORIQUE, 'w') as f:
        json.dump([], f)

    print("⏳ En attente de mises à jour des nœuds (Agencies)...")
    
    for message in consommateur:
        donnees = message.value
        print(f"   📥 Mise à jour reçue de : {donnees['node_id']} (Précision locale : {donnees['accuracy']:.2%})")
        
        tampon_modeles.append(donnees)
        
        # لنفترض أننا ندمج النماذج كلما وصلنا تحديثين أو أكثر
        if len(tampon_modeles) >= 2:
            print(f"\n⚙️  Début du processus de fusion (Round {num_round})...")
            
            # 1. حساب النموذج العالمي الجديد
            p_globaux, b_global, precision_g = moyennage_federe(tampon_modeles)
            
            print(f"   ✅ Nouveau modèle global généré !")
            print(f"   📊 Précision globale agrégée : {precision_g:.2%}")
            
            # 2. حفظ النتائج في ملف لعرضها في لوحة التحكم
            enregistrement = {
                'round': num_round,
                'accuracy': precision_g,
                'participating_nodes': [m['node_id'] for m in tampon_modeles],
                'timestamp': message.timestamp
            }
            
            # قراءة السجل القديم وتحديثه
            try:
                with open(FICHIER_HISTORIQUE, 'r') as f:
                    historique = json.load(f)
            except:
                historique = []
                
            historique.append(enregistrement)
            
            with open(FICHIER_HISTORIQUE, 'w') as f:
                json.dump(historique, f)
            
            # تنظيف الذاكرة المؤقتة للجولة القادمة
            tampon_modeles = []
            num_round += 1
            print("------------------------------------------------")

if __name__ == "__main__":
    demarrer_serveur()