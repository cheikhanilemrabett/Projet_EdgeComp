# dashboard_simple.py
import streamlit as st
from kafka import KafkaConsumer
import json

st.set_page_config(page_title="Dashboard Simple", layout="wide")
st.title("📊 Dashboard Simple - Lecture Directe")

topic = st.selectbox(
    "Sélectionner un Topic:",
    ['sensor-data-node-1', 'sensor-data-node-2', 'model-weights', 'global-model']
)

if st.button("Lire les messages"):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=5000
        )
        
        messages = []
        for msg in consumer:
            messages.append({
                'offset': msg.offset,
                'timestamp': msg.timestamp,
                'value': msg.value
            })
            if len(messages) >= 5:  # نأخذ 5 رسائل كحد أقصى
                break
        
        consumer.close()
        
        if messages:
            st.success(f"✅ {len(messages)} messages trouvés dans {topic}")
            
            for i, msg in enumerate(messages):
                with st.expander(f"Message {i+1} (Offset: {msg['offset']})"):
                    st.json(msg['value'])
        else:
            st.warning(f"⚠️ Aucun message dans {topic}")
            
    except Exception as e:
        st.error(f"❌ Erreur: {e}")