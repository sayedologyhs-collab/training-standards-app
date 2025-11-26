import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام تقييم الحقائب التدريبية", layout="wide", page_icon="📊")

# --- تنسيق CSS مخصص للغة العربية والجمالية ---
st.markdown("""
<style>
    .main {direction: rtl;}
    h1, h2, h3, p, div {text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    .stRadio > label {display: none;}
    .stSelectbox > label {display: none;}
    div[data-testid="stExpander"] details summary p {font-size: 1.2rem; font-weight: bold;}
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;}
    div[data-testid="stMarkdownContainer"] ul {list-style-position: inside; padding-right: 20px;}
</style>
""", unsafe_allow_html=True)

# --- تحميل البيانات (هيكل المعايير) ---
@st.cache_data
def load_data():
    data = {
        "المجال الأول: الأهداف": {
            "المعيار 1: وضوح الأهداف": [
                "هل الهدف العام يصيغ ما يسعى البرنامج لتحقيقه بدقة؟",
                "هل نواتج التعلم قابلة للقياس والملاحظة؟",
                "هل تتناسب الأهداف مع الزمن المتاح؟"
            ],
            "المعيار 2: شمولية الأهداف": [
                "هل تغطي الأهداف الجوانب المعرفية والمهارية والوجدانية؟"
            ]
        },
        "المجال الثاني: المحتوى": {
            "المعيار 1: ملاءمة المحتوى": [
                "هل المحتوى حديث ومواكب للمستجدات؟",
                "هل التسلسل المنطقي للموضوعات سليم؟"
            ],
            "المعيار 2: صحة المحتوى": [
                "خلو المحتوى من الأخطاء العلمية.",
                "خلو المحتوى من الأخطاء اللغوية والإملائية."
            ]
        },
         "المجال الثالث: الوسائل والأنشطة": {
            "المعيار 1: تنوع الأنشطة": [
                "هل توجد أنشطة تفاعلية تشرك المتدربين؟",
                "هل الوسائل البصرية واضحة وذات جودة عالية؟"
            ]
        },
         "المجال الرابع: الإخراج الفني": {
            "المعيار 1: التصميم": [
                "هل الغلاف جذاب ويحتوي على البيانات الأساسية؟",
                "هل التنسيق الداخلي مريح للقراءة؟"
            ]
        },
         "المجال الخامس: التقييم": {
            "المعيار 1: أدوات القياس": [
                "هل توجد اختبارات قبلية وبعدية؟",
                "هل توجد استمارة لتقييم رضا المتدربين؟"
            ]
        }
    }
    return data

# --- الواجهة الرئيسية ---
st.title("📊 نظام التقييم الذكي للحقائب التدريبية")
st.markdown("---")

# بيانات الحقيبة
with st.expander("📝 بيانات البرنامج التدريبي", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        prog_name = st.text_input("اسم البرنامج التدريبي")
        trainer_name = st.text_input("اسم المدرب / المعد")
    with col2:
        date = st.date_input("تاريخ التقييم")
        evaluator = st.text_input("اسم المقيم")

# تحميل البيانات
structure = load_data()
scores = {"متحقق": 2, "متحقق جزئياً": 1, "غير متحقق": 0}
results = []

st.header("📋 قائمة التحقق من المعايير")

# إنشاء Tabs للمجالات
tabs = st.tabs(list(structure.keys()))

# حلقة تكرارية لبناء الواجهة ديناميكياً
for i, (domain, standards) in enumerate(structure.items()):
    with tabs[i]:
        st.subheader(domain)
        for standard, criteria_list in standards.items():
            with st.container():
                st.markdown(f"#### 📌 {standard}")
                for criterion in criteria_list:
                    c1, c2, c3 = st.columns()
                    with c1:
                        st.write(f"- {criterion}")
                    with c2:
                        key = f"{domain}_{standard}_{criterion}"
                        status = st.radio(
                            "الحالة", 
                            ["متحقق", "متحقق جزئياً", "غير متحقق"], 
                            horizontal=True, 
                            key=key,
                            index=2 # الافتراضي غير متحقق
                        )
                    with c3:
                        notes = st.text_input("ملاحظات", key=f"notes_{key}", placeholder="أضف ملاحظة...")
                    
                    # حفظ النتيجة
                    results.append({
                        "المجال": domain,
                        "المعيار": standard,
                        "المؤشر": criterion,
                        "النتيجة": status,
                        "الدرجة": scores[status],
                        "الملاحظات": notes
                    })
                st.markdown("---")

# --- قسم النتائج والتقرير ---
st.header("📈 تقرير النتائج")

if st.button("إصدار التقرير النهائي"):
    if not prog_name:
        st.warning("يرجى إدخال اسم البرنامج التدريبي أولاً.")
    else:
        df_res = pd.DataFrame(results)
        
        # حسابات النسب
        total_score = df_res['الدرجة'].sum()
        max_score = len(df_res) * 2
        percentage = (total_score / max_score) * 100
        
        # عرض المؤشرات العلوية
        c1, c2, c3 = st.columns(3)
        c1.metric("نسبة المطابقة العامة", f"{percentage:.1f}%")
        c2.metric("عدد المعايير المتحققة", len(df_res[df_res['النتيجة']=="متحقق"]))
        c3.metric("نقاط تحتاج تحسين", len(df_res[df_res['النتيجة']!="متحقق"]))
        
        # رسم بياني بسيط
        st.subheader("الأداء حسب المجالات")
        domain_scores = df_res.groupby("المجال")['الدرجة'].sum().reset_index()
        st.bar_chart(domain_scores.set_index("المجال"))
        
        # جدول التفاصيل (فلترة للغير متحقق فقط)
        st.subheader("⚠️ فرص التحسين (المعايير غير المتحققة)")
        improvement_df = df_res[df_res['النتيجة'] != "متحقق"][['المجال', 'المعيار', 'المؤشر', 'النتيجة', 'الملاحظات']]
        
        if not improvement_df.empty:
            st.table(improvement_df)
        else:
            st.success("🎉 تهانينا! جميع المعايير متحققة.")

        # تصدير النتائج
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False, sheet_name='التقرير التفصيلي')
            
        st.download_button(
            label="📥 تحميل التقرير (Excel)",
            data=excel_buffer.getvalue(),
            file_name=f"Evaluation_Report.xlsx",
            mime="application/vnd.ms-excel"
        )
