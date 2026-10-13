import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai

# تحميل متغيرات البيئة محلياً
load_dotenv()

# قراءة مفتاح API بأمان من Streamlit Cloud أو ملف البيئة المحلي
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

# إعداد وتكوين مفتاح الربط للمكتبة بالطريقة الصحيحة
genai.configure(api_key=api_key)

# إعداد تصميم وتخطيط الصفحة
st.set_page_config(
    page_title="Digital Forensics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# عنوان التطبيق والترحيب
st.title("🛡️ Digital Forensics & LensTrace Dashboard")
st.markdown("منصة متقدمة لتحليل الصور الرقمية، استخراج بيانات الـ EXIF، والتحليل الجغرافي الذكي باستخدام الذكاء الاصطناعي.")

# رفع الصور
uploaded_file = st.file_uploader("اختر صورة للتحليل...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة التي تم رفعها للفحص", use_container_width=True)
    
    # قسم التحليل البصري الذكي
    st.subheader("📍 التحليل البصري الذكي للمكان")
    st.markdown("فحص تفاصيل ومعالم البيئة والخلفية لتخمين الموقع الجغرافي بصرياً.")
    
    if st.button("بدء التحليل الجغرافي البصري"):
        with st.spinner("جاري تحليل المعالم والبيئة عبر الذكاء الاصطناعي..."):
            try:
                # استخدام النموذج الصحيح للتحليل البصري
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "قم بتحليل هذه الصورة بدقة لتحديد المعالم الجغرافية، طبيعة البيئة، المدينة المحتملة، أو أي أدلة بصرية تدل على الموقع."
                response = model.generate_content([prompt, image])
                
                st.success("تم الانتهاء من التحليل بنجاح!")
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث تنبيه: {e}")

    # قسم استخراج بيانات الـ EXIF
    st.subheader("🔍 استخراج بيانات الـ EXIF والبيانات الوصفية")
    if st.button("استخراج بيانات EXIF"):
        exif_data = image.getexif()
        if exif_data:
            exif_list = []
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_list.append({"Tag": tag, "Value": str(value)})
            
            df = pd.DataFrame(exif_list)
            st.table(df)
        else:
            st.info("لا توجد بيانات EXIF متاحة في هذه الصورة.")