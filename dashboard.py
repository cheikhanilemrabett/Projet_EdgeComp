import streamlit as st
import pandas as pd
import json
import time
import os
import plotly.express as px

# إعداد الصفحة
st.set_page_config(page_title="Système de Détection de Fraude", layout="wide")

st.title("🏦 Tableau de Bord : Apprentissage Fédéré")
st.markdown("Surveillance de la fraude bancaire en temps réel - (Projet 3.3)")

# اسم الملف (يجب أن يكون مطابقاً لملف السيرفر)
HISTORY_FILE = 'historique_modele_global.json'

def load_data():
    """وظيفة لتحميل البيانات من ملف JSON"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []

# تحميل البيانات
data = load_data()

if not data:
    # رسالة تنبيه في حال عدم وجود بيانات
    st.warning("⏳ En attente de mises à jour des nœuds (Agencies)...")
    # إعادة المحاولة بعد 3 ثواني
    time.sleep(3)
    st.rerun()
else:
    df = pd.DataFrame(data)
    latest = df.iloc[-1]

    # --- القسم الأول: المؤشرات الرئيسية (KPIs) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Round Actuel", value=f"#{latest['round']}")
    
    with col2:
        # عرض الدقة كنسبة مئوية
        accuracy_val = f"{latest['accuracy']:.2%}"
        st.metric(label="Précision Globale", value=accuracy_val)
    
    with col3:
        # حساب عدد الوكالات المشاركة
        nodes_count = len(latest['participating_nodes'])
        st.metric(label="Agencies Participantes", value=nodes_count)

    st.divider()

    # --- القسم الثاني: الرسم البياني وتطور الدقة ---
    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        st.subheader("📈 Évolution de la Précision")
        fig = px.line(
            df, 
            x='round', 
            y='accuracy', 
            markers=True,
            title="Précision du Modèle Global par Round",
            labels={'round': 'Round', 'accuracy': 'Précision'}
        )
        fig.update_yaxes(range=[0, 1.0])
        
        # حل مشكلة الـ ID: إضافة مفتاح فريد يعتمد على عدد السجلات
        st.plotly_chart(fig, use_container_width=True, key=f"plot_round_{len(df)}")

    with col_table:
        # --- القسم الثالث: سجل التحديثات الأخير ---
        st.subheader("📋 Dernières Mises à Jour")
        recent_df = df[['round', 'accuracy']].sort_values(by='round', ascending=False)
        st.table(recent_df.head(5))

    # --- القسم الرابع: تفاصيل العقد المشاركة ---
    with st.expander("Voir les détails des nœuds par round"):
        st.dataframe(df[['round', 'participating_nodes', 'timestamp']], use_container_width=True)

    # تحديث تلقائي للصفحة كل 5 ثوانٍ
    time.sleep(5)
    st.rerun()