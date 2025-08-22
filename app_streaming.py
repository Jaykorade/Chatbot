import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
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
        st.experimental_rerun()

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
   
        with st.chat_message("assistant"):

            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
               {'messages': [HumanMessage(content=user_input)]},
               config=config,
               stream_mode='messages'
               )  
            )
        st.session_state['message_hist'].append({'role':"assistant",'content':ai_message})
        
