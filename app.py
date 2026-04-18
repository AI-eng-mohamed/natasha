import streamlit as st
from langchain_groq import ChatGroq
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from gtts import gTTS
import io
import os

# 1. إعداد المفاتيح (حذفنا ElevenLabs)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# 2. إعداد العملاء
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.7, groq_api_key=GROQ_API_KEY)
dg_client = DeepgramClient(DEEPGRAM_API_KEY)

st.set_page_config(page_title="Natasha AI", page_icon="👩‍💻")
st.title("👩‍💻 ناتاشا: نسخة الاستقرار المجانية")

persona = "أنتِ ناتاشا، مساعدة ذكية ومرحة. إجاباتكِ قصيرة جداً (جملة أو جملتين)."

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. المايك
audio_value = st.audio_input("🎙️ احجي ويا ناتاشا")

if audio_value:
    try:
        # أ. السمع (Deepgram)
        with st.spinner("ناتاشا تسمعك..."):
            buffer_data = audio_value.read()
            payload: FileSource = {"buffer": buffer_data}
            options = PrerecordedOptions(model="nova-3", language="ar", smart_format=True)
            response = dg_client.listen.rest.v("1").transcribe_file(payload, options)
            user_text = response.results.channels[0].alternatives[0].transcript

        if user_text and user_text.strip():
            with st.chat_message("user"):
                st.markdown(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})

            # ب. التفكير (Groq)
            with st.spinner("ناتاشا تفكر..."):
                ai_response = llm.invoke([("system", persona)] + [("human", user_text)])
                ans_text = ai_response.content

            # ج. النطق (Google TTS - البديل المجاني المضمون)
            with st.spinner("ناتاشا تجيب..."):
                tts = gTTS(text=ans_text, lang='ar')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_bytes = audio_fp.getvalue()
                
                with st.chat_message("assistant"):
                    st.markdown(ans_text)
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                
                st.session_state.messages.append({"role": "assistant", "content": ans_text})
                
    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
