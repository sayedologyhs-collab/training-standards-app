import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime
import PyPDF2
from docx import Document
from PIL import Image
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المستشار الذكي لتقييم الأدلة التدريبية - مؤسسة علمني", layout="wide", page_icon="🎓")

# --- تنسيق CSS ---
st.markdown("""
<style>
    .main {direction: rtl;}
    h1, h2, h3, p, div, label, li {text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    .stAlert {text-align: right; direction: rtl;}
    .metric-card {background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); 
                  color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .recommendation-box {background-color: #fff3cd; border-right: 5px solid #ffc107; padding: 15px; margin-bottom: 10px; border-radius: 5px; color: #856404;}
    .example-box {background-color: #e2e8f0; border-right: 5px solid #4a5568; padding: 10px; margin-top: 5px; border-radius: 5px; font-size: 0.9em; color: #2d3748;}
    .report-container {background-color: #f8f9fa; padding: 25px; border-radius: 10px; border: 1px solid #ddd; margin-top: 20px;}
    .logo-text {font-size: 1.5rem; font-weight: bold; color: #2c3e50; margin-top: 10px;}
    .sub-logo-text {font-size: 1.1rem; color: #7f8c8d;}
</style>
""", unsafe_allow_html=True)

# --- دوال استخراج النصوص ---
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return ""

def extract_text_from_word(file):
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return ""

# --- قاعدة المعرفة (الخبير التربوي) ---
@st.cache_data
def get_expert_knowledge():
    return {
        "المجال الأول: الأهداف ونواتج التعلم": [
            {
                "criterion": "وضوح الهدف العام للبرنامج",
                "keywords": ["الهدف العام", "يهدف البرنامج", "الغرض من البرنامج", "الهدف الرئيس"],
                "advice": "قم بصياغة هدف عام يصف النتيجة النهائية للبرنامج بدقة.",
                "example": "مثال صحيح: 'تنمية مهارات المشاركين في استخدام لغة بايثون لتحليل البيانات.' \nمثال خاطئ: 'أن يعرف المتدرب لغة بايثون.'"
            },
            {
                "criterion": "صياغة نواتج التعلم (SMART)",
                "keywords": ["نواتج التعلم", "الأهداف التفصيلية", "يتوقع من المتدرب", "قادر على أن", "الأهداف السلوكية"],
                "advice": "تأكد أن الأهداف تتبع معيار SMART. استخدم أفعالاً سلوكية قابلة للقياس.",
                "example": "نموذج: 'في نهاية الجلسة، سيكون المتدرب قادراً على صياغة 3 أهداف ذكية دون أخطاء.'"
            },
            {
                "criterion": "شمولية الأهداف (معرفي/مهاري/وجداني)",
                "keywords": ["المعرفة", "المهارات", "الاتجاهات", "القيم", "السلوكيات", "الجوانب الوجدانية"],
                "advice": "البرنامج يركز على جانب واحد. أضف أهدافاً وجدانية ومهارية.",
                "example": "هدف وجداني: 'أن يبدي المتدرب اهتماماً بتطبيق معايير السلامة.' \nهدف مهاري: 'أن يفكك الجهاز في أقل من 5 دقائق.'"
            }
        ],
        "المجال الثاني: المحتوى التدريبي": [
            {
                "criterion": "حداثة المراجع والمصادر",
                "keywords": ["المراجع", "المصادر", "قائمة المراجع", "2023", "2024", "2025", "الدراسات الحديثة"],
                "advice": "لم يتم رصد مراجع حديثة. ادعم المحتوى بإحصائيات ودراسات من آخر 3 سنوات.",
                "example": "يمكنك الاستشهاد بتقارير: المنتدى الاقتصادي العالمي 2024، أو دراسات هارفارد الحديثة ذات الصلة بموضوعك."
            },
            {
                "criterion": "تنظيم وتسلسل الوحدات",
                "keywords": ["الوحدة الأولى", "الجلسة التدريبية", "جدول زمني", "خطة البرنامج", "التسلسل"],
                "advice": "أعد هيكلة المحتوى ليبدأ من الأساسيات وصولاً للتطبيقات المعقدة (Scaffolding).",
                "example": "مقترح تسلسل: 1. المفاهيم الأساسية -> 2. الأدوات والتقنيات -> 3. التطبيق العملي -> 4. مشروع التخرج."
            }
        ],
        "المجال الثالث: الأنشطة والأساليب": [
            {
                "criterion": "تنوع أساليب التدريب",
                "keywords": ["ورشة عمل", "عصف ذهني", "تمثيل أدوار", "دراسة حالة", "نقاش جماعي", "تطبيق عملي"],
                "advice": "الحقيبة تعتمد على السرد النظري. أضف أنشطة تفاعلية لكل 45 دقيقة تدريب.",
                "example": "فكرة نشاط: قسم المتدربين لمجموعات، واطلب منهم حل مشكلة واقعية (Case Study) وعرض الحل في 5 دقائق."
            },
            {
                "criterion": "تعليمات الأنشطة",
                "keywords": ["زمن النشاط", "خطوات النشاط", "المطلوب من المتدرب", "آلية التنفيذ"],
                "advice": "حدد بوضوح لكل نشاط: (الزمن، الهدف، الأدوات المطلوبة، وآلية التنفيذ).",
                "example": "نموذج تعليمات: 'الزمن: 15 دقيقة. الهدف: تطبيق المعادلة. الأدوات: ورقة وقلم. الآلية: عمل فردي ثم نقاش ثنائي.'"
            }
        ],
        "المجال الرابع: أدوات التقييم": [
            {
                "criterion": "أدوات قياس الأثر (قبلي/بعدي)",
                "keywords": ["الاختبار القبلي", "الاختبار البعدي", "قياس الأثر", "Pre-test", "Post-test"],
                "advice": "صمم اختباراً قبلياً وبعدياً متطابقاً لقياس نسبة التحسن في المعرفة.",
                "example": "نموذج: اختبار من 10 أسئلة (اختيار من متعدد) يغطي المفاهيم الأساسية، يطبق في أول وآخر يوم."
            },
            {
                "criterion": "قياس رضا المتدربين",
                "keywords": ["استمارة تقييم", "راي المتدرب", "استبيان", "تقييم البرنامج"],
                "advice": "أرفق نموذجاً لتقييم بيئة التدريب وأداء المدرب.",
                "example": "عناصر التقييم الأساسية: وضوح المادة، تمكن المدرب، جودة القاعة، ملاءمة الوقت."
            }
        ]
    }

# --- دالة التقييم الذكي ---
def evaluate_content(text, knowledge_base):
    results = []
    text_lower = text.lower()
    
    for domain, items in knowledge_base.items():
        for item in items:
            matches = [kw for kw in item['keywords'] if kw in text or kw in text_lower]
            score = len(matches)
            
            status = "غير متحقق"
            if score >= 2:
                status = "متحقق"
            elif score == 1:
                status = "متحقق جزئياً"
            
            results.append({
                "المجال": domain,
                "المعيار": item['criterion'],
                "النتيجة": status,
                "الدرجة": 2 if status == "متحقق" else (1 if status == "متحقق جزئياً" else 0),
                "التوصية": item['advice'],
                "مثال تطبيقي": item['example'],
                "الأدلة": ", ".join(matches) if matches else "لا يوجد"
            })
    return results

# --- مولد التقرير السردي ---
def generate_smart_narrative(df, prog_name):
    score = (df['الدرجة'].sum() / (len(df) * 2)) * 100
    
    report = f"### 📑 التقرير الاستشاري للبرنامج التدريبي: {prog_name}\n\n"
    
    if score >= 85:
        report += "بناءً على التحليل الفني، يظهر البرنامج **جاهزية عالية** ومطابقة ممتازة للمعايير التدريبية."
    elif score >= 50:
        report += "البرنامج يمتلك **بنية أساسية جيدة**، ولكنه يحتاج إلى تدخلات جوهرية في جوانب التصميم التعليمي."
    else:
        report += "يحتاج البرنامج إلى **إعادة هيكلة شاملة**، حيث يفتقر للعديد من العناصر الأساسية."

    report += "\n\n#### ⚠️ أولويات التطوير والمقترحات:\n"
    weaknesses = df[df['النتيجة'] != 'متحقق']
    
    if not weaknesses.empty:
        for domain in weaknesses['المجال'].unique():
            domain_issues = weaknesses[weaknesses['المجال'] == domain]
            report += f"\n**في {domain}:**\n"
            for _, row in domain_issues.iterrows():
                report += f"- **المعيار:** {row['المعيار']}\n  - **التوصية:** {row['التوصية']}\n"
    else:
        report += "لا توجد ملاحظات جوهرية، البرنامج مكتمل.\n"
        
    return report

# --- الواجهة الرئيسية ---
col_header1, col_header2 = st.columns([1, 4])

with col_header1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=130)
    else:
        st.info("📷 (ارفع ملف logo.png)")

with col_header2:
    st.markdown('<div class="logo-text">الاستشاري الافتراضي لتقييم الأدلة التدريبية</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-logo-text">مؤسسة علمني</div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("ارفع ملف الحقيبة (PDF/Word) للتحليل الشامل:", type=['pdf', 'docx', 'doc'])

if uploaded_file:
    with st.spinner('جاري تحليل المحتوى وتوليد النماذج المقترحة...'):
        file_text = ""
        if uploaded_file.name.endswith('.pdf'):
            file_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith('.docx'):
            file_text = extract_text_from_word(uploaded_file)
        
        if len(file_text) < 50:
            st.error("عذراً، الملف يبدو فارغاً أو لا يمكن استخراج النص منه.")
        else:
            # التحليل
            kb = get_expert_knowledge()
            results_list = evaluate_content(file_text, kb)
            df_res = pd.DataFrame(results_list)
            
            # الحسابات
            total_score = df_res['الدرجة'].sum()
            max_score = len(df_res) * 2
            percentage = (total_score / max_score) * 100 if max_score > 0 else 0
            
            st.success("✅ تم الانتهاء من التحليل بنجاح!")
            
            # 1. لوحة القيادة
            st.markdown("### 📊 مؤشرات الجودة")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("نسبة الجودة", f"{percentage:.1f}%")
            m2.metric("نقاط القوة", len(df_res[df_res['النتيجة']=='متحقق']))
            m3.metric("تحتاج تحسين", len(df_res[df_res['النتيجة']=='متحقق جزئياً']))
            m4.metric("نواقص حادة", len(df_res[df_res['النتيجة']=='غير متحقق']))
            
            st.progress(int(percentage))
            
            # الرسوم البيانية
            st.markdown("---")
            st.header("📈 التحليل البصري للأداء")
            
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                st.subheader("توازن مجالات الحقيبة")
                radar_data = df_res.groupby('المجال')['الدرجة'].mean().reset_index()
                radar_data['النسبة'] = (radar_data['الدرجة'] / 2) * 100
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=radar_data['النسبة'],
                    theta=radar_data['المجال'],
                    fill='toself',
                    name='أداء الحقيبة'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                
            with col_graph2:
                st.subheader("تفاصيل الأداء")
                fig_bar = px.bar(df_res, x='المعيار', y='الدرجة', color='النتيجة',
                                 color_discrete_map={'متحقق': '#4ade80', 'متحقق جزئياً': '#facc15', 'غير متحقق': '#f87171'})
                st.plotly_chart(fig_bar, use_container_width=True)

            # التقرير السردي
            st.markdown("---")
            st.header("📝 التقرير الاستشاري")
            smart_report = generate_smart_narrative(df_res, uploaded_file.name)
            st.markdown(f"""<div class="report-container">{smart_report}</div>""", unsafe_allow_html=True)
            
            # التوصيات
            st.markdown("---")
            st.header("💡 التوصيات والنماذج المقترحة")
            
            issues = df_res[df_res['النتيجة'] != 'متحقق']
            if not issues.empty:
                for i, row in issues.iterrows():
                    with st.expander(f"⭕ {row['المعيار']} ({row['النتيجة']})"):
                        st.markdown(f"""
                        <div class="recommendation-box">
                            <strong>💡 توصية الخبير:</strong><br>
                            {row['التوصية']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="example-box">
                            <strong>📌 نموذج تطبيقي مقترح:</strong><br>
                            {row['مثال تطبيقي']}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("الحقيبة مكتملة ومثالية!")

            # التحميل
            st.markdown("---")
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df_res.to_excel(writer, sheet_name='التحليل', index=False)
                wb = writer.book
                ws = wb.add_worksheet('التقرير')
                ws.write(0, 0, smart_report)
                
            st.download_button(
                label="📥 تحميل التقرير الشامل (Excel)",
                data=excel_buffer.getvalue(),
                file_name="EduTrain_Report.xlsx",
                mime="application/vnd.ms-excel"
            )
