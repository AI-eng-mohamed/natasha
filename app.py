import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from gtts import gTTS
import io

st.set_page_config(page_title="Natasha AI", page_icon="👩‍💻")

# ثيم خفيف لناتاشا
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👩‍💻 ناتاشا العبقرية")

# إعداد الموديل
api_key = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.8, groq_api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# وظيفة تحويل النص إلى صوت
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='ar', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

# مدخل النص (استخدم علامة المايك الموجودة بالكيبورد مالت موبايلك)
if prompt := st.chat_input("احجي وياي يا محمد..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # إرسال المحادثة
        full_response = llm.invoke(st.session_state.messages[-5:])
        content = full_response.content
        st.markdown(content)
        
        # نطق الجواب تلقائياً
        audio_data = speak_text(content)
        if audio_data:
            st.audio(audio_data, format='audio/mp3', autoplay=True)
            
        st.session_state.messages.append(AIMessage(content=content))
