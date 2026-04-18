import streamlit as st
from langchain_groq import ChatGroq
from elevenlabs import generate, set_api_key
from deepgram import DeepgramClient, PrerecordedOptions
import os
import io

# 1. جلب المفاتيح من الـ Secrets (الخزنة السريّة)
set_api_key(st.secrets["ELEVENLABS_API_KEY"])
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# 2. إعداد محرك الذكاء (ناتاشا)
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.7, groq_api_key=GROQ_API_KEY)

st.set_page_config(page_title="Natasha Voice", page_icon="👩‍💻")
st.title("👩‍💻 ناتاشا: الوضع الصوتي الاحترافي")

# تصميم ناتاشا للردود الصوتية (قصيرة وذكية)
persona = "أنتِ ناتاشا، مساعدة ذكية جداً. أنتِ الآن في وضع الحوار الصوتي، لذا اجعلي إجاباتكِ قصيرة ومباشرة (جملة أو جملتين فقط) ليكون الحوار طبيعياً."

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الشات القديم
for msg in st.session_state.messages:
    with st.chat_message("user" if msg['role'] == 'user' else 'assistant'):
        st.write(msg['content'])

# 3. واجهة السمع (زر المايك الذكي)
# سنستخدم هنا تقنية تسجيل بسيطة ومستقرة للمتصفح
audio_value = st.audio_input("🎙️ اضغط للتحدث مع ناتاشا")

if audio_value:
    # أ. تحويل الصوت لنص باستخدام Deepgram (الأذن الذكية)
    dg_client = DeepgramClient(DEEPGRAM_API_KEY)
    
    with st.spinner("ناتاشا تسمعك..."):
        buffer_data = audio_value.read()
        payload = {"buffer": buffer_data}
        options = PrerecordedOptions(model="nova-2", language="ar", smart_format=True)
        
        response = dg_client.listen.prerecorded.v("1").transcribe_file(payload, options)
        user_text = response.results.channels[0].alternatives[0].transcript

    if user_text:
        st.chat_message("user").write(user_text)
        st.session_state.messages.append({"role": "user", "content": user_text})

        # ب. تفكير ناتاشا (الدماغ)
        with st.spinner("ناتاشا تفكر..."):
            ai_response = llm.invoke([("system", persona)] + [("human", user_text)])
            ans_text = ai_response.content

        # ج. تحويل الرد لصوت بشري (الحنجرة) من ElevenLabs
        with st.spinner("ناتاشا تجيب..."):
            audio_gen = generate(
                text=ans_text,
                voice="Bella", # صوت أنثوي رقيق، تقدر تغيره لاحقاً
                model="eleven_multilingual_v2"
            )
            
            st.chat_message("assistant").write(ans_text)
            st.audio(audio_gen, format="audio/mp3", autoplay=True)
            st.session_state.messages.append({"role": "assistant", "content": ans_text})
