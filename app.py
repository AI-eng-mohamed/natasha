import streamlit as st
from langchain_groq import ChatGroq
from elevenlabs.client import ElevenLabs
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import io

# 1. جلب المفاتيح
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# 2. إعداد العملاء
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.7, groq_api_key=GROQ_API_KEY)
client_eleven = ElevenLabs(api_key=ELEVENLABS_API_KEY)
# التأكد من تمرير المفتاح مباشرة للعميل
dg_client = DeepgramClient(DEEPGRAM_API_KEY)

st.set_page_config(page_title="Natasha AI", page_icon="👩‍💻")
st.title("👩‍💻 ناتاشا: النسخة الاحترافية")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 3. المايك الجديد
audio_value = st.audio_input("🎙️ احجي ويا ناتاشا")

if audio_value:
    try:
        with st.spinner("ناتاشا تسمعك..."):
            buffer_data = audio_value.read()
            # صياغة الطلب بشكل يتوافق مع النسخة المستقرة
            payload = {"buffer": buffer_data}
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                language="ar"
            )
            
            # محاولة استخدام الـ rest client مباشرة لتجنب أخطاء النسخ
            response = dg_client.listen.rest.v("1").transcribe_file(payload, options)
            user_text = response.results.channels[0].alternatives[0].transcript

        if user_text and user_text.strip():
            st.chat_message("user").write(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})

            with st.spinner("ناتاشا تفكر..."):
                persona = "أنتِ ناتاشا، مساعدة ذكية. إجاباتكِ قصيرة جداً (جملة واحدة)."
                ai_response = llm.invoke([("system", persona), ("human", user_text)])
                ans_text = ai_response.content

            with st.spinner("ناتاشا تجيب..."):
                audio_gen = client_eleven.generate(
                    text=ans_text,
                    voice="Bella",
                    model="eleven_multilingual_v2"
                )
                audio_bytes = b"".join(list(audio_gen))
                
                st.chat_message("assistant").write(ans_text)
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                st.session_state.messages.append({"role": "assistant", "content": ans_text})
    
    except Exception as e:
        st.error(f"اكو مشكلة صغيرة بالاتصال: {str(e)}")
