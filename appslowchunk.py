import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import time
st.title("Welcome, I am ur AI assistant")

SECRET_CODE = 'Jay9920'
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "message_hist" not in st.session_state:
    st.session_state.message_hist = []

if not st.session_state.authenticated:
    code = st.text_input("Enter Code", type="password")
    if code == SECRET_CODE:
        st.session_state.authenticated = True
        st.success("Code correct! Access granted ✅")
        st.rerun()
else:
    st.write("🎉 You are logged in!")
    
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.session_state.message_hist = []
        st.rerun()

    # LLM
    for message in st.session_state['message_hist']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    user_input = st.chat_input("Type here...")

    if user_input:
        st.session_state['message_hist'].append({'role':'user','content':user_input})
        with st.chat_message('user'):
            st.markdown(user_input)

        config = {'configurable':{'thread_id':1}}

        with st.spinner("Thinking..."):
            with st.chat_message("assistant"):
                placeholder = st.empty()
                ai_message = ""
                for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=config,
                stream_mode='messages'
                ):
                    if message_chunk.content:
                        ai_message += message_chunk.content
                        placeholder.markdown(ai_message)
                        time.sleep(0.10)
        st.session_state['message_hist'].append({'role':"assistant",'content':ai_message})
            
