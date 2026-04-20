import streamlit as st
from langchain_groq import ChatGroq

# 1. إعداد المفتاح من الـ Secrets (نحتاج فقط مفتاح Groq حالياً)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# 2. إعداد محرك الذكاء (الدماغ)
llm = ChatGroq(
    model_name="openai/gpt-oss-120b", 
    temperature=0.9, 
    groq_api_key=GROQ_API_KEY
)

st.set_page_config(page_title="Natasha Chat", page_icon="👩‍💻")

st.title("هلو اني ناتاشا")
st.info("مرحباً محمد.")

# تعريف الشخصية
persona = "أنتِ ناتاشا، مساعدة ذكية، مرحة، انثى، واني اسمي محمد (ذكر) تكلمي معي بصيغة المذكر وانا اتكلم معكِ بصيغة الانثى لأن انتِ انثى وانا ذكر، وتتحدثين بلهجة عراقية خفيفة ومحببة."

# نظام الذاكرة للمحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. صندوق الكتابة (Input)
if prompt := st.chat_input("اكتبلي شعندك هنا !..."):
    # أ. عرض رسالة المستخدم
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ب. طلب الرد من ناتاشا
    with st.spinner("ناتاشا تكتب..."):
        try:
            full_prompt = [("system", persona)] + [
                (m["role"], m["content"]) for m in st.session_state.messages
            ]
            response = llm.invoke(full_prompt)
            ans_text = response.content

            # ج. عرض رد ناتاشا
            with st.chat_message("assistant"):
                st.markdown(ans_text)
            st.session_state.messages.append({"role": "assistant", "content": ans_text})
            
        except Exception as e:
            st.error(f"استاذي العزيز دتواجهني مشكلة حلها وتعال غرد: {str(e)}")
