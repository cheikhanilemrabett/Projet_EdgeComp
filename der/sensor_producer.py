# producer_capteurs.py
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# Configuration du Producer Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generer_donnees_capteur(node_id):
    """Générer des données de capteur aléatoires"""
    return {
        'node_id': node_id,
        'timestamp': datetime.now().isoformat(),
        'temperature': round(random.uniform(20.0, 100.0), 2),
        'vibration': round(random.uniform(0.0, 10.0), 2),
        'pressure': round(random.uniform(50.0, 150.0), 2),
        'anomaly': random.choice([0, 0, 0, 0, 1])  # 20% d'anomalie
    }

# Envoi continu de données
try:
    print("🚀 Producer démarré - Envoi de données de capteurs...")
    while True:
        # Données Node 1
        data_node1 = generer_donnees_capteur('node-1')
        producer.send('sensor-data-node-1', value=data_node1)
        print(f"📤 Node 1 → Température: {data_node1['temperature']:.2f}°C")
        
        # Données Node 2
        data_node2 = generer_donnees_capteur('node-2')
        producer.send('sensor-data-node-2', value=data_node2)
        print(f"📤 Node 2 → Température: {data_node2['temperature']:.2f}°C")
        
        time.sleep(1)  # Pause d'une seconde
        
except KeyboardInterrupt:
    print("\n⏹️ Arrêt du Producer")
finally:
    producer.close()