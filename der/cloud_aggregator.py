# cloud_aggregator.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType, IntegerType
import json
import time
from kafka import KafkaProducer

# 1. Créer la session Spark
print("☁️ Démarrage Cloud Aggregator...")
spark = SparkSession.builder \
    .appName("CloudAggregator") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint_cloud") \
    .getOrCreate()

# 2. Définir le schéma des poids
schema_poids = StructType([
    StructField("node_id", StringType()),
    StructField("batch_id", IntegerType()),
    StructField("weights", ArrayType(DoubleType())),
    StructField("intercept", DoubleType()),
    StructField("num_samples", IntegerType()),
    StructField("timestamp", StringType()),
    StructField("type", StringType())
])

# 3. Producer Kafka
kafka_producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 4. Lire les poids de Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "model-weights") \
    .option("startingOffsets", "earliest") \
    .load()

# 5. Convertir JSON
parsed_df = df.select(
    from_json(col("value").cast("string"), schema_poids).alias("data")
).select("data.*")

# 6. Fonction Federated Averaging
def aggreg_federree(batch_df, batch_id):
    lignes = batch_df.collect()
    
    if len(lignes) > 0:
        print(f"\n{'='*60}")
        print(f"☁️ Cloud Aggregator - Batch {batch_id}")
        print(f"   Nœuds: {len(lignes)}")
        
        # Afficher chaque nœud
        for i, ligne in enumerate(lignes):
            print(f"   Nœud {ligne['node_id']}: {ligne['num_samples']} échantillons")
        
        # Calculer total échantillons
        total_echantillons = sum([ligne['num_samples'] for ligne in lignes])
        print(f"   Total échantillons: {total_echantillons}")
        
        if total_echantillons > 0:
            # Appliquer FedAvg
            nb_features = len(lignes[0]['weights'])
            poids_moyens = [0.0] * nb_features
            intercept_moyen = 0.0
            
            for ligne in lignes:
                facteur = ligne['num_samples'] / total_echantillons
                
                # Poids pondérés
                for i in range(nb_features):
                    poids_moyens[i] += ligne['weights'][i] * facteur
                
                # Intercept pondéré
                intercept_moyen += ligne['intercept'] * facteur
            
            # Créer modèle global
            modele_global = {
                "model_id": f"global_model_{batch_id}",
                "weights": poids_moyens,
                "intercept": float(intercept_moyen),
                "total_samples": int(total_echantillons),
                "num_nodes": len(lignes),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "global_model"  # Important pour le dashboard
            }
            
            print(f"   ✅ Modèle global créé:")
            print(f"      - Poids moyens: {[round(p, 4) for p in poids_moyens]}")
            print(f"      - Intercept: {round(intercept_moyen, 4)}")
            
            # Envoyer au topic global-model
            kafka_producer.send("global-model", value=modele_global)
            kafka_producer.flush()
            print(f"   📤 Envoyé → global-model")
        
        print(f"{'='*60}")

# 7. Démarrer l'agrégation
query = parsed_df \
    .writeStream \
    .foreachBatch(aggreg_federree) \
    .trigger(processingTime='15 seconds') \
    .option("checkpointLocation", "/tmp/checkpoint_cloud_agg") \
    .start()

print("✅ Cloud Aggregator prêt - En attente de poids...")
query.awaitTermination()