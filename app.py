import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai

# تحميل متغيرات البيئة من ملف .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# إعداد الصفحة وتفعيل تصميم الواجهة واتجاه النص
st.set_page_config(
    page_title="Digital Forensics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- تنسيقات CSS مخصصة لتنظيم الواجهة وإعدادات الطباعة النظيفة ---
st.markdown("""
    <style>
    .main {
        direction: rtl;
        text-align: right;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #0f172a;
        font-weight: 700;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
        background-color: #2563eb;
        color: white;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    div.stAlert {
        border-radius: 8px;
    }
    
    /* إخفاء القوائم والأزرار عند الطباعة */
    @media print {
        [data-testid="stSidebar"], 
        header, 
        .stFileUploader, 
        .stButton,
        [data-testid="stToolbar"] {
            display: none !important;
        }
        body {
            background-color: white !important;
        }
        .main {
            direction: rtl;
            text-align: right;
            padding: 0px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# عنوان الواجهة الرئيسي
st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>لوحة تحكم التحقيق الجنائي الرقمي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>استخراج بيانات EXIF، التحليل البصري الجغرافي، والتعرف على الشخصيات بالذكاء الاصطناعي</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("إعدادات الأدوات")
uploaded_file = st.file_uploader("اختر أو اسحب صورة للفحص الجنائي...", type=["jpg", "jpeg", "png"])

def get_decimal_from_dms(dms, ref):
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.subheader("معاينة الصورة")
        st.image(image, caption="الصورة التي تم رفعها للفحص", use_container_width=True)
        
    with col2:
        st.subheader("بيانات الـ EXIF الوصفية")
        exif_data = image._getexif()
        
        if exif_data:
            metadata_list = []
            gps_info = {}
            
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    for t in value:
                        gps_decoded = GPSTAGS.get(t, t)
                        gps_info[gps_decoded] = value[t]
                else:
                    metadata_list.append({"الوسم البرمجي (Tag)": str(tag), "القيمة (Value)": str(value)})
            
            df = pd.DataFrame(metadata_list)
            st.dataframe(df, use_container_width=True, height=300)
            
            if gps_info:
                st.markdown("---")
                st.subheader("إحداثيات موقع الالتقاط (GPS)")
                try:
                    lat_data = gps_info.get("GPSLatitude")
                    lat_ref = gps_info.get("GPSLatitudeRef")
                    lon_data = gps_info.get("GPSLongitude")
                    lon_ref = gps_info.get("GPSLongitudeRef")
                    
                    if lat_data and lon_data and lat_ref and lon_ref:
                        lat = get_decimal_from_dms(lat_data, lat_ref)
                        lon = get_decimal_from_dms(lon_data, lon_ref)
                        
                        st.success(f"خط العرض: {lat} | خط الطول: {lon}")
                        df_map = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                        st.map(df_map)
                    else:
                        st.info("توجد بيانات GPS جزئية ولكن تعذر حساب الإحداثيات بدقة.")
                except Exception as e:
                    st.warning(f"تعذر استخراج خريطة الإحداثيات: {e}")
            else:
                st.info("لا توجد بيانات GPS تقليدية داخل هذه الصورة.")
        else:
            st.warning("الصورة لا تحتوي على بيانات EXIF وصفية (تمت إزالتها غالباً بواسطة منصات التواصل الاجتماعي).")

    # --- القسم الأول: التحليل البصري الذكي للمكان ---
    st.markdown("---")
    st.subheader("التحليل البصري الذكي للمكان")
    st.info("فحص تفاصيل ومعالم البيئة والخلفية لتخمين الموقع الجغرافي بصرياً.")
    
    if st.button("بدء التحليل الجغرافي البصري"):
        if not api_key:
            st.error("عذراً، لم يتم العثور على مفتاح API داخل ملف .env")
        else:
            with st.spinner("جاري تحليل المعالم البصرية والمكان..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "أنت خبير محقق جنائي رقمي. قم بتحليل خلفية ومعالم هذه الصورة واستخرج الآتي باللغة العربية:\n"
                        "1. نوع البيئة أو الموقع.\n"
                        "2. المعالم البارزة أو اللوحات أو طراز المباني.\n"
                        "3. تخمين الدولة أو المدينة المحتملة."
                    )
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=[image, prompt]
                    )
                    st.success("تم التحليل الجغرافي بنجاح!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"تنبيه: {e}")

    # --- القسم الثاني: التعرف على الشخصيات العامة والمشاهير ---
    st.markdown("---")
    st.subheader("التعرف على الشخصيات العامة والمشاهير")
    st.info("فحص وجه الشخص الظاهر في الصورة وتحديد ما إذا كان شخصية مشهورة، يوتيوبر، سياسياً، أو وزيراً.")
    
    if st.button("فحص والتعرف على الشخصية في الصورة"):
        if not api_key:
            st.error("عذراً، لم يتم العثور على مفتاح API داخل ملف .env")
        else:
            with st.spinner("جاري فحص ملامح الوجه والبحث عن الشخصية..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "أنت محقق جنائي وخبير في تحليل الهويات البصرية. "
                        "قم بفحص الوجه والشخصية الظاهرة في هذه الصورة وأجبني باللغة العربية عن الآتي:\n"
                        "1. هل الشخصية الظاهرة تعتبر شخصية عامة، مشهور، يوتيوبر، وزير، أو سياسي معروف؟ إذا نعم، من هو؟\n"
                        "2. ما هي تفاصيل هويته أو سبب شهرته؟\n"
                        "3. أية ملاحظات تحليلية بصرية حول ملامح الوجه أو المظهر الظاهر."
                    )
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=[image, prompt]
                    )
                    st.success("تم فحص الشخصية بنجاح!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"تنبيه: {e}")
                    # --- تذييل الصفحة (Footer) ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>تم تطوير لوحة تحكم التحقيق الجنائي الرقمي | فكرة وتنفيذ: علي حسن</p>", 
    unsafe_allow_html=True
)