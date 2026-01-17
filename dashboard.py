import streamlit as st
import json
import pandas as pd
from kafka import KafkaConsumer
import matplotlib.pyplot as plt
import time

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="IoT Federated Learning Monitor",
    layout="wide",
    page_icon="☁️"
)

st.title("☁️ Cloud Aggregator & Live Monitoring")
st.markdown("---")

# --- تهيئة المتغيرات (Session State) ---
# نحتاج لتخزين البيانات في الذاكرة لكي لا تختفي عند تحديث الصفحة
if 'data_history' not in st.session_state:
    st.session_state['data_history'] = []

# --- إعداد Kafka Consumer ---
# نستخدم @st.cache_resource لكي لا يعيد الاتصال بـ Kafka مع كل تحديث للصفحة
@st.cache_resource
def init_consumer():
    return KafkaConsumer(
        'model-weights',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',  # اقرأ البيانات القديمة أولاً
        enable_auto_commit=True,
        group_id='dashboard-group-v2', # تغيير الجروب لضمان قراءة كل شيء من جديد
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

consumer = init_consumer()

# --- تخطيط الصفحة (Layout) ---
# ننشئ أماكن فارغة (Placeholders) سنقوم بتحديثها لاحقاً
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Global Model Metrics")
    metrics_placeholder = st.empty()
    logs_placeholder = st.empty()

with col2:
    st.subheader("📈 Weights Convergence")
    chart_placeholder = st.empty()

# --- حلقة التحديث الرئيسية ---
st.toast("Listening for Spark updates...", icon="📡")

# زر لإيقاف المراقبة يدوياً
stop_button = st.button("Stop Monitoring")

while not stop_button:
    # 1. محاولة سحب رسائل جديدة (لمدة 0.5 ثانية فقط)
    # هذا هو السر: poll لا تجمد الشاشة للأبد مثل for loop
    msg_pack = consumer.poll(timeout_ms=500)

    # 2. إذا وجدنا رسائل، نضيفها للقائمة
    if msg_pack:
        for tp, messages in msg_pack.items():
            for message in messages:
                data = message.value
                st.session_state['data_history'].append(data)
    
    # 3. معالجة البيانات وعرضها (إذا كانت القائمة غير فارغة)
    if len(st.session_state['data_history']) > 0:
        df = pd.DataFrame(st.session_state['data_history'])
        
        # --- الحسابات (Federated Averaging) ---
        # نأخذ آخر 20 تحديثاً لنكون أكثر دقة
        recent_df = df.tail(20)
        global_coef = recent_df['coef'].mean()
        global_intercept = recent_df['intercept'].mean()
        total_updates = len(df)
        last_node = df.iloc[-1]['node_id']

        # --- تحديث الأرقام (Metrics) ---
        with metrics_placeholder.container():
            kpi1, kpi2 = st.columns(2)
            kpi1.metric("Global Slope (Weights)", f"{global_coef:.4f}")
            kpi2.metric("Global Bias (Intercept)", f"{global_intercept:.4f}")
            st.info(f"Last update from: **{last_node}** | Total Packets: {total_updates}")
            st.success(f"Final Model Equation:\n\n $y = {global_coef:.2f}x + {global_intercept:.2f}$")

        # --- تحديث الرسم البياني ---
        with chart_placeholder.container():
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # رسم نقاط كل عقدة بلون مختلف
            groups = recent_df.groupby('node_id')
            for name, group in groups:
                ax.plot(group.index, group['coef'], marker='o', linestyle='', label=name, alpha=0.6)
            
            # رسم الخط المتوسط (Global Model)
            ax.axhline(y=global_coef, color='red', linestyle='--', linewidth=2, label='Global Model')
            
            ax.set_title("Live Weight Updates (FedAvg)")
            ax.set_ylabel("Coefficient Value")
            ax.set_xlabel("Update Sequence")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            plt.close(fig) # تنظيف الذاكرة

        # --- عرض السجلات ---
        with logs_placeholder.container():
            st.write("Recent Raw Data:")
            st.dataframe(recent_df[['node_id', 'batch_id', 'coef', 'intercept']].tail(5), hide_index=True)

    else:
        # شاشة انتظار إذا لم تصل بيانات بعد
        with metrics_placeholder.container():
            st.warning("Waiting for data from Kafka...")

    # 4. توقف لحظي لتخفيف الحمل على المعالج
    time.sleep(1) 
    # لا نحتاج st.rerun هنا لأننا نستخدم while loop وتحديث الـ Placeholders