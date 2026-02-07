import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder

# اسم ملف البيانات الأصلي
NOM_FICHIER_SOURCE = 'MoMTSim_20240722202413_1000_dataset.csv'
DOSSIER_SORTIE = 'donnees_edge'

def preparer_et_distribuer_donnees():
    # التأكد من وجود الملف الأصلي قبل البدء
    if not os.path.exists(NOM_FICHIER_SOURCE):
        print(f"❌ Erreur: Le fichier '{NOM_FICHIER_SOURCE}' est introuvable.")
        return

    print(">>> Chargement et nettoyage des données...")
    
    # قراءة البيانات
    df = pd.read_csv(NOM_FICHIER_SOURCE)
    
    # 1. تنظيف البيانات: حذف أي سطر يحتوي على قيم فارغة (NaN)
    # هذا السطر يحل مشكلة ValueError: Input X contains NaN التي واجهتها سابقاً
    df.dropna(inplace=True)
    
    # 2. اختيار الأعمدة المالية الهامة فقط للنموذج
    colonnes_utiles = [
        'transactionType', 'amount', 'oldBalInitiator', 
        'newBalInitiator', 'oldBalRecipient', 'newBalRecipient', 'isFraud'
    ]
    
    # التأكد من وجود الأعمدة المطلوبة في الملف
    df = df[[col for col in colonnes_utiles if col in df.columns]]

    # 3. تحويل البيانات النصية (النوع) إلى أرقام لتسهيل معالجتها رياضياً
    if 'transactionType' in df.columns:
        encodeur = LabelEncoder()
        df['transactionType'] = encodeur.fit_transform(df['transactionType'].astype(str))
        print("✅ Encodage des types de transactions terminé.")

    # 4. خلط البيانات عشوائياً لضمان توزيع عادل بين الوكالات (Nodes)
    df_melange = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 5. تقسيم البيانات إلى 3 أجزاء متساوية (تمثل 3 وكالات)
    segments = np.array_split(df_melange, 3)

    # إنشاء المجلد إذا لم يكن موجوداً
    if not os.path.exists(DOSSIER_SORTIE):
        os.makedirs(DOSSIER_SORTIE)

    print(f">>> Distribution des données dans le dossier '{DOSSIER_SORTIE}':")
    
    for i, segment in enumerate(segments):
        # تسمية ملف كل وكالة
        nom_csv = f"{DOSSIER_SORTIE}/node_{i+1}.csv"
        
        # حفظ الملف
        segment.to_csv(nom_csv, index=False)
        
        # حساب نسبة الاحتيال في كل جزء للتأكد من جودة التوزيع
        nb_fraudes = segment['isFraud'].sum()
        print(f"   📍 Node {i+1}: {len(segment)} lignes | Fraudes détectées: {nb_fraudes}")

    print("\n🚀 Simulation terminée avec succès. Les nœuds sont prêts pour le Federated Learning.")

if __name__ == "__main__":
    preparer_et_distribuer_donnees()