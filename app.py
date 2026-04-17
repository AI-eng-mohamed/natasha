import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os

st.set_page_config(page_title="Natasha AI", page_icon="👩‍💻")
st.title("👩‍💻 ناتاشا العبقرية")

# جلب المفتاح من إعدادات السيرفر (للأمان)
api_key = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.8, groq_api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

if prompt := st.chat_input("تكلمي معي يا ناتاشا..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = llm.invoke(st.session_state.messages[-5:]) 
        st.markdown(response.content)
        st.session_state.messages.append(AIMessage(content=response.content))
