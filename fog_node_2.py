from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import json
import time
import traceback
from kafka import KafkaProducer

def main():
    try:
        print("🚀 Démarrage de Fog Node 2...")
        
        # 1. إنشاء Spark Session
        spark = SparkSession.builder \
            .appName("FogNode-2") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint_node2") \
            .getOrCreate()
        
        print("✅ Spark Session créée")
        
        # 2. تعريف مخطط البيانات
        schema = StructType([
            StructField("node_id", StringType()),
            StructField("timestamp", StringType()),
            StructField("temperature", DoubleType()),
            StructField("vibration", DoubleType()),
            StructField("pressure", DoubleType()),
            StructField("anomaly", DoubleType())
        ])
        
        # 3. Kafka Producer
        print("🔌 Tentative de connexion à Kafka...")
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Connexion au Kafka Producer")
        except Exception as e:
            print(f"❌ Échec de la connexion à Kafka: {e}")
            spark.stop()
            return
        
        # 4. قراءة البيانات من Kafka
        print("📖 Lecture du topic sensor-data-node-2...")
        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "sensor-data-node-2") \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        # 5. تحويل JSON
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # 6. دالة المعالجة
        def process_batch(batch_df, batch_id):
            try:
                count = batch_df.count()
                print(f"\n{'='*50}")
                print(f"🔧 Fog Node 2 - Batch {batch_id}")
                print(f"   Échantillons: {count}")
                
                if count > 0:
                    # حساب المتوسطات
                    avg_temp = batch_df.selectExpr("avg(temperature)").first()[0]
                    avg_vibration = batch_df.selectExpr("avg(vibration)").first()[0]
                    
                    # أوزان محاكاة
                    weights = [avg_temp, avg_vibration, 0.5]
                    
                    # رسالة الأوزان
                    weights_msg = {
                        "node_id": "node-2",
                        "batch_id": int(batch_id),
                        "weights": weights,
                        "intercept": 1.0,
                        "num_samples": int(count),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "node_update"
                    }
                    
                    # إرسال إلى model-weights
                    kafka_producer.send("model-weights", value=weights_msg)
                    kafka_producer.flush()
                    
                    print("📤 Poids envoyés → model-weights")
                    print(f"   Poids: {[round(w, 2) for w in weights]}")
                else:
                    print("⚠️ Pas de données dans ce batch")
                
                print(f"{'='*50}")
                
            except Exception as e:
                print(f"❌ Erreur dans process_batch: {e}")
                traceback.print_exc()
        
        # 7. بدء المعالجة
        print("🎬 Démarrage du Streaming Query...")
        
        query = parsed_df \
            .writeStream \
            .foreachBatch(process_batch) \
            .trigger(processingTime='10 seconds') \
            .option("checkpointLocation", "/tmp/checkpoint_fog_node_2") \
            .start()
        
        print("✅ Fog Node 2 fonctionne et attend les données...")
        print("   Appuyez sur Ctrl+C pour arrêter\n")
        
        # انتظار حتى الإنهاء
        query.awaitTermination()
        
    except KeyboardInterrupt:
        print("\n⏹️ Fog Node 2 arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur principale : {e}")
        traceback.print_exc()
    finally:
        print("\n🧹 Nettoyage des ressources...")
        try:
            spark.stop()
        except:
            pass

if __name__ == "__main__":
    main()
