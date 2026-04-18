import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import os

st.set_page_config(page_title="Natasha Voice", page_icon="🎙️")
st.title("🎙️ ناتاشا الصوتية")

# إعداد الموديل
api_key = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.8, groq_api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# وظيفة تحويل النص إلى صوت (مجانية)
def speak_text(text):
    tts = gTTS(text=text, lang='ar', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

# إضافة المايك في الجانب
st.sidebar.title("التحكم الصوتي")
audio_input = mic_recorder(start_prompt="🎙️ إبدأ الكلام", stop_prompt="🛑 توقف", key='recorder')

user_input = st.chat_input("أو اكتب هنا...")

# إذا المستخدم حجي بالمايك
if audio_input:
    # ملاحظة: لتحويل الصوت لنص مجاناً نستخدم خاصية الترجمة المدمجة بالمتصفح 
    # أو نعتمد على نص المايك إذا كانت المكتبة تدعم الترجمة الفورية
    # للتسهيل هسة، سنركز على أن ناتاشا "تجيب بصوتها" على ما تكتبه أو تسجله
    prompt = audio_input['text'] if 'text' in audio_input else None
else:
    prompt = user_input

if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = llm.invoke(st.session_state.messages[-5:])
        st.markdown(response.content)
        
        # نطق الجواب
        audio_fp = speak_text(response.content)
        st.audio(audio_fp, format='audio/mp3', autoplay=True)
        
        st.session_state.messages.append(AIMessage(content=response.content))
