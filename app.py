import streamlit as st
from langchain_groq import ChatGroq
from elevenlabs.client import ElevenLabs
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os

# 1. إعداد المفاتيح من الـ Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# 2. إعداد العملاء (الذكاء، الصوت، السمع)
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.7, groq_api_key=GROQ_API_KEY)
client_eleven = ElevenLabs(api_key=ELEVENLABS_API_KEY)
dg_client = DeepgramClient(DEEPGRAM_API_KEY)

st.set_page_config(page_title="Natasha AI", page_icon="👩‍💻")

# تصميم واجهة ناتاشا
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👩‍💻 ناتاشا: الوضع الصوتي الاحترافي")

# تعريف شخصية ناتاشا
persona = "أنتِ ناتاشا، مساعدة ذكية ومرحة. بما أننا في حوار صوتي، اجعلي إجاباتكِ قصيرة جداً ومباشرة (جملة أو جملتين فقط)."

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. واجهة التسجيل (المايك)
audio_value = st.audio_input("🎙️ اضغط للتحدث مع ناتاشا")

if audio_value:
    try:
        # أ. تحويل الصوت لنص (Deepgram)
        with st.spinner("ناتاشا تسمعك..."):
            buffer_data = audio_value.read()
            payload: FileSource = {"buffer": buffer_data}
            options = PrerecordedOptions(
                model="nova-3",
                language="ar",
                smart_format=True,
            )
            
            # استدعاء التحويل عبر REST API (النسخة الأكثر استقراراً)
            response = dg_client.listen.rest.v("1").transcribe_file(payload, options)
            user_text = response.results.channels[0].alternatives[0].transcript

        if user_text and user_text.strip():
            # عرض كلام المستخدم
            with st.chat_message("user"):
                st.markdown(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})

            # ب. تفكير ناتاشا (Groq)
            with st.spinner("ناتاشا تفكر..."):
                ai_response = llm.invoke([("system", persona)] + [("human", user_text)])
                ans_text = ai_response.content

            # ج. توليد الصوت البشري (التحديث النهائي 2026)
         with st.spinner("ناتاشا تجيب..."):
             audio_gen = client_eleven.text_to_speech.convert(
                 voice_id="21m00Tcm4TlvDq8ikWAM", # هذا هو كود صوت Bella الشهير
                 text=ans_text,
                 model_id="eleven_multilingual_v2",
                 output_format="mp3_44100_128",
             )
            
             # تجميع البيانات الصوتية
              audio_bytes = b"".join(list(audio_gen))
            
              with st.chat_message("assistant"):
                 st.markdown(ans_text)
                 st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                
                 st.session_state.messages.append({"role": "assistant", "content": ans_text})
                
    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
