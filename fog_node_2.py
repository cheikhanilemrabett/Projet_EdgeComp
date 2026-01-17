import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, ArrayType
from kafka import KafkaProducer
from sklearn.linear_model import LinearRegression
import numpy as np

# إعدادات العقدة (يمكنك تغييرها عند التشغيل للعقدة الثانية)
TOPIC_NAME = "sensor-data-node-2" # غيّر هذا إلى sensor-data-node-2 للعقدة الثانية
KAFKA_BOOTSTRAP = "localhost:9092"

# إعداد Spark
spark = SparkSession.builder \
    .appName("FogNode-Trainer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# إعداد Producer لإرسال الأوزان
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# دالة التدريب التي ستعمل على كل حزمة بيانات (Micro-batch)
def train_and_send_weights(batch_df, batch_id):
    if batch_df.count() == 0:
        return
    
    # تحويل بيانات Spark إلى Pandas للتدريب السريع
    pdf = batch_df.toPandas()
    
    # تجهيز البيانات للتدريب
    # ملاحظة: الميزات تأتي كمصفوفة، نحتاج لتسطيحها
    X = np.array(pdf['features'].tolist())
    y = np.array(pdf['label'].tolist())
    
    # تدريب نموذج محلي (Scikit-Learn أسرع للحزم الصغيرة)
    model = LinearRegression()
    model.fit(X, y)
    
    # استخراج الأوزان
    weights = {
        'node_id': pdf['node_id'].iloc[0],
        'batch_id': batch_id,
        'coef': model.coef_[0],     # الميل (Slope)
        'intercept': model.intercept_ # التقاطع (Bias)
    }
    
    # إرسال الأوزان إلى السحابة
    print(f"📦 Sending Weights from Batch {batch_id}: {weights}")
    producer.send('model-weights', value=weights)
    producer.flush()

# تعريف Schema للبيانات القادمة JSON
schema = StructType([
    StructField("node_id", StringType()),
    StructField("features", ArrayType(DoubleType())),
    StructField("label", DoubleType())
])

# 1. القراءة من Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", TOPIC_NAME) \
    .option("startingOffsets", "latest") \
    .load()

# 2. فك تشفير البيانات
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 3. تشغيل الـ Stream وتطبيق دالة التدريب
query = parsed_df.writeStream \
    .foreachBatch(train_and_send_weights) \
    .trigger(processingTime='5 seconds') \
    .start()

query.awaitTermination()