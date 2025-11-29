import streamlit as st
from datetime import date
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# إعدادات البريد
SENDER_EMAIL = "your.email@example.com"  # بريدك الإلكتروني لإرسال الرسائل
SENDER_PASSWORD = "your-email-password"  # كلمة المرور أو App Password
SMTP_SERVER = "smtp.example.com"         # SMTP server مثل smtp.gmail.com
SMTP_PORT = 465                          # رقم المنفذ (مثلاً 465 للبريد المشفر SSL)
MANAGER_EMAIL = "ahmedkashkoush@educateme-foundation.org"  # بريد مدير البرامج

# دالة لتوليد ملف PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "تقرير المهام الأسبوعي", 0, 1, "C")
    
    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(3)
    
    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

def create_pdf_report(data):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("قائد/مدير الفريق: " + data["user"])
    pdf.chapter_title("تاريخ التقرير: " + data["date"])
    pdf.chapter_title("ملخص المهام المنجزة")
    pdf.chapter_body(data["completed"])
    pdf.chapter_title("خطة المهام المتوقعة")
    pdf.chapter_body(data["planned"])
    pdf.chapter_title("نقاط الدعم المطلوبة")
    pdf.chapter_body(data["support"])

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# دالة لإرسال البريد الإلكتروني مع المرفق
def send_email_report(pdf_bytes, recipient_email, user_name):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = f"تقرير مهام أسبوعي من {user_name}"

    body = f"""مرحبًا،

تم إكمال تقرير المهام الأسبوعي من قبل {user_name}، الرجاء الاطلاع على الملف المرفق.

مع التحية."""
    msg.attach(MIMEText(body, "plain"))

    attach = MIMEApplication(pdf_bytes.read(), _subtype="pdf")
    attach.add_header('Content-Disposition', 'attachment', filename="تقرير_المهام_الأسبوعي.pdf")
    msg.attach(attach)
    pdf_bytes.seek(0)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

# واجهة Streamlit
st.title("نظام تقارير المهام الأسبوعية لقادة ومديري الفرق")

user_name = st.text_input("اسم قائد/مدير الفريق")
report_date = st.date_input("تاريخ التقرير", date.today())

completed_tasks = st.text_area("ملخص المهام المنجزة خلال الأسبوع السابق")
planned_tasks = st.text_area("خطة المهام المتوقعة للأسبوع التالي")
support_points = st.text_area("نقاط الدعم المطلوبة من الفريق ومن مدير البرامج")

if st.button("حفظ وإرسال التقرير"):
    if not user_name.strip():
        st.error("يرجى إدخال اسم قائد/مدير الفريق")
    else:
        report_data = {
            "user": user_name,
            "date": str(report_date),
            "completed": completed_tasks,
            "planned": planned_tasks,
            "support": support_points
        }

        # إنشاء التقرير بصيغة PDF
        pdf_output = create_pdf_report(report_data)

        # إرسال التقرير إلى مدير البرامج
        try:
            send_email_report(pdf_output, MANAGER_EMAIL, user_name)
            st.success("تم حفظ التقرير وإرساله إلى مدير البرامج بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء إرسال البريد: {e}")

        # عرض التقرير تفاعليًا
        st.header("ملخص التقرير التفاعلي")

        # عرض نصي مبسط
        st.subheader("ملخص المهام المنجزة")
        st.write(completed_tasks)

        st.subheader("خطة المهام المتوقعة")
        st.write(planned_tasks)

        st.subheader("نقاط الدعم المطلوبة")
        st.write(support_points)

        # إنشاء بيانات إحصائية بسيطة للرسوم البيانية
        counts = {
            "المهام المنجزة": len(completed_tasks.split("\n")),
            "المهام المستقبلية": len(planned_tasks.split("\n")),
            "نقاط الدعم": len(support_points.split("\n")),
        }
        fig = px.bar(
            x=list(counts.keys()),
            y=list(counts.values()),
            labels={"x": "فئة التقرير", "y": "عدد البنود"},
            title="تحليل بنود التقرير"
        )
        st.plotly_chart(fig)
