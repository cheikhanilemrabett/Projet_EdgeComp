import time
import json
import random
import numpy as np
from kafka import KafkaProducer

# إعداد Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def generate_data(node_id):
    # محاكاة معادلة خطية: y = 2*x + 5 + noise
    x = random.uniform(0, 100)
    noise = np.random.normal(0, 2) # تشويش بسيط
    y = (2 * x) + 5 + noise
    
    data = {
        'node_id': node_id,
        'timestamp': time.time(),
        'features': [x], # البيانات المدخلة
        'label': y       # القيمة المراد التنبؤ بها
    }
    return data

print("🚀 Sensors started sending data...")

try:
    while True:
        # إرسال بيانات الحساس 1
        data1 = generate_data(node_id="node-1")
        producer.send('sensor-data-node-1', value=data1)
        print(f"Sent Node 1: {data1}")

        # إرسال بيانات الحساس 2
        data2 = generate_data(node_id="node-2")
        producer.send('sensor-data-node-2', value=data2)
        print(f"Sent Node 2: {data2}")

        # انتظار ثانية واحدة
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping sensors...")