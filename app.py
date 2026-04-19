import streamlit as st
from langchain_groq import ChatGroq

# 1. إعداد المفتاح من الـ Secrets (نحتاج فقط مفتاح Groq حالياً)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# 2. إعداد محرك الذكاء (الدماغ)
llm = ChatGroq(
    model_name="openai/gpt-oss-120b", 
    temperature=0.7, 
    groq_api_key=GROQ_API_KEY
)

st.set_page_config(page_title="Natasha Chat", page_icon="👩‍💻")

st.title("👩‍💻 ناتاشا: نسخة الدردشة الذكية")
st.info("مرحباً محمد! هذي النسخة تركز على الدردشة الكتابية المستقرة.")

# تعريف الشخصية
persona = "أنتِ ناتاشا، مساعدة ذكية، مرحة، وتتحدثين بلهجة عراقية خفيفة ومحببة."

# نظام الذاكرة للمحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. صندوق الكتابة (Input)
if prompt := st.chat_input("اكتب رسالتك لناتاشا هنا..."):
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
            st.error(f"اكو مشكلة بالاتصال بالدماغ: {str(e)}")
