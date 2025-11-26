import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime
import PyPDF2
from docx import Document

# إعدادات الصفحة
st.set_page_config(page_title="نظام التقييم الآلي للحقائب التدريبية", layout="wide", page_icon="🤖")

# تنسيق CSS
st.markdown("""
<style>
    .main {direction: rtl;}
    h1, h2, h3, p, div, label {text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    .stAlert {text-align: right;}
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# دالة استخراج النص من PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"خطأ في قراءة PDF: {str(e)}"

# دالة استخراج النص من Word
def extract_text_from_word(file):
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"خطأ في قراءة Word: {str(e)}"

# دالة التقييم الذكي
def auto_evaluate(text, criterion):
    text_lower = text.lower()
    
    rules = {
        "الهدف العام": ["الهدف العام", "يهدف البرنامج", "غرض البرنامج"],
        "نواتج التعلم": ["نواتج التعلم", "الأهداف التعليمية", "يتوقع من المتدرب", "في نهاية"],
        "المحتوى": ["المحتوى", "الموضوعات", "المواد التدريبية", "الوحدات"],
        "الأنشطة": ["نشاط", "تمرين", "تطبيق عملي", "ورشة عمل", "دراسة حالة"],
        "التقييم": ["اختبار", "تقييم", "قياس", "استبيان", "بطاقة ملاحظة"],
        "المراجع": ["المراجع", "المصادر", "المراجع العلمية", "قائمة المراجع"],
        "دليل المدرب": ["دليل المدرب", "إرشادات المدرب", "ملاحظات للميسر"],
        "دليل المتدرب": ["دليل المتدرب", "كتيب المتدرب", "مذكرة المتدرب"]
    }
    
    found_keywords = []
    for category, keywords in rules.items():
        if criterion.find(category) != -1 or any(kw in criterion for kw in keywords):
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                found_keywords.append((category, matches))
    
    total_matches = sum(m[1] for m in found_keywords)
    
    if total_matches >= 3:
        return "متحقق", "✓ وجدت أدلة قوية على تحقق المعيار"
    elif total_matches >= 1:
        return "متحقق جزئياً", "◐ وجدت بعض المؤشرات"
    else:
        return "غير متحقق", "✗ لم يتم العثور على دليل واضح"

@st.cache_data
def load_standards():
    standards = {
        "المجال الأول: الأهداف": [
            "يحدد الهدف العام ما يسعى البرنامج إلى تحقيقه",
            "نواتج التعلم واضحة وقابلة للقياس",
            "تتناسب الأهداف مع الزمن المتاح",
            "تتنوع نواتج التعلم (معرفية، مهارية، وجدانية)"
        ],
        "المجال الثاني: المحتوى": [
            "المحتوى حديث ومواكب للمستجدات",
            "التسلسل المنطقي للموضوعات سليم",
            "خلو المحتوى من الأخطاء العلمية",
            "يرتبط المحتوى بالأهداف المحددة"
        ],
        "المجال الثالث: الوسائل والأنشطة": [
            "توجد أنشطة تفاعلية متنوعة",
            "الوسائل البصرية واضحة وجذابة",
            "الأنشطة مرتبطة بنواتج التعلم",
            "توجد تعليمات واضحة لتنفيذ الأنشطة"
        ],
        "المجال الرابع: المادة التدريبية": [
            "يتوفر دليل للمدرب شامل",
            "يتوفر دليل للمتدرب واضح",
            "توجد مادة مرجعية داعمة",
            "توجد أوراق عمل وعروض تقديمية"
        ],
        "المجال الخامس: التقييم": [
            "توجد أدوات تقييم قبلي وبعدي",
            "أدوات التقييم مرتبطة بالأهداف",
            "توجد استمارة تقييم رضا المتدربين",
            "معايير التقييم واضحة ومحددة"
        ]
    }
    return standards

st.title("🤖 نظام التقييم الآلي الذكي للحقائب التدريبية")
st.markdown("### 📤 قم برفع ملف الحقيبة التدريبية للحصول على تقييم فوري ذكي")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "اختر ملف الحقيبة التدريبية (PDF, Word)",
        type=['pdf', 'docx', 'doc'],
        help="يدعم التطبيق: دليل المدرب، دليل المتدرب، أو الحقيبة الكاملة"
    )

with col2:
    st.info("💡 **نصيحة:**\nلأفضل النتائج، ارفع ملف الحقيبة الكامل")

if uploaded_file is not None:
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("⏳ جاري قراءة الملف...")
    progress_bar.progress(20)
    
    file_text = ""
    if uploaded_file.name.endswith('.pdf'):
        file_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(('.docx', '.doc')):
        file_text = extract_text_from_word(uploaded_file)
    else:
        st.warning("نوع الملف غير مدعوم")
        st.stop()
    
    progress_bar.progress(40)
    
    status_text.text("🔍 جاري التحليل الذكي للمحتوى...")
    progress_bar.progress(60)
    
    standards = load_standards()
    results = []
    
    for domain, criteria_list in standards.items():
        for criterion in criteria_list:
            status, note = auto_evaluate(file_text, criterion)
            results.append({
                "المجال": domain,
                "المعيار": criterion,
                "النتيجة": status,
                "الدرجة": 2 if status == "متحقق" else (1 if status == "متحقق جزئياً" else 0),
                "ملاحظة النظام": note
            })
    
    progress_bar.progress(100)
    status_text.text("✅ اكتمل التحليل!")
    
    st.success(f"✓ تم تحليل الملف بنجاح: **{uploaded_file.name}**")
    
    df_results = pd.DataFrame(results)
    
    total_score = df_results['الدرجة'].sum()
    max_score = len(df_results) * 2
    percentage = (total_score / max_score) * 100
    
    achieved = len(df_results[df_results['النتيجة'] == 'متحقق'])
    partial = len(df_results[df_results['النتيجة'] == 'متحقق جزئياً'])
    not_achieved = len(df_results[df_results['النتيجة'] == 'غير متحقق'])
    
    st.markdown("---")
    st.header("📊 نتائج التقييم الآلي")
    
    c1, c2, c3, c4 = st.columns(4)
    
    c1.markdown(f"""
    <div class="metric-card">
        <h2 style="color: white; margin: 0;">{percentage:.1f}%</h2>
        <p style="margin: 5px 0; opacity: 0.9;">نسبة المطابقة</p>
    </div>
    """, unsafe_allow_html=True)
    
    c2.metric("✅ متحقق كلياً", achieved)
    c3.metric("◐ متحقق جزئياً", partial)
    c4.metric("❌ غير متحقق", not_achieved)
    
    st.subheader("📈 توزيع النتائج")
    fig = go.Figure(data=[go.Pie(
        labels=['متحقق', 'متحقق جزئياً', 'غير متحقق'],
        values=[achieved, partial, not_achieved],
        hole=.4,
        marker_colors=['#10b981', '#f59e0b', '#ef4444']
    )])
    fig.update_layout(showlegend=True, height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 الأداء حسب المجالات")
    domain_scores = df_results.groupby('المجال')['الدرجة'].sum().reset_index()
    
    fig2 = px.bar(domain_scores, x='المجال', y='الدرجة', color='الدرجة', text='الدرجة')
    fig2.update_traces(textposition='outside')
    fig2.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("📋 التفاصيل الكاملة")
    
    filter_status = st.multiselect(
        "فلترة حسب الحالة:",
        ['متحقق', 'متحقق جزئياً', 'غير متحقق'],
        default=['غير متحقق', 'متحقق جزئياً']
    )
    
    filtered_df = df_results[df_results['النتيجة'].isin(filter_status)]
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    st.subheader("💡 اقتراحات التحسين الذكية")
    
    improvements = df_results[df_results['النتيجة'] != 'متحقق']
    
    if not improvements.empty:
        for domain in improvements['المجال'].unique():
            with st.expander(f"🔹 {domain}"):
                domain_issues = improvements[improvements['المجال'] == domain]
                for _, row in domain_issues.iterrows():
                    st.markdown(f"**❗ {row['المعيار']}**")
                    st.markdown(f"- الحالة: `{row['النتيجة']}`")
                    st.markdown(f"- التوصية: أضف أو وضح هذا العنصر")
                    st.markdown("---")
    else:
        st.success("🎉 ممتاز! جميع المعايير متحققة")
    
    st.sub
