import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

st.title("Welcome I am ur AI assistant")
if 'message_hist' not in st.session_state:
     st.session_state['message_hist']=[]

st.secrets["OPENAI_API_KEY"]

# LLM
for message in st.session_state['message_hist']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type here")

if user_input:
    st.session_state['message_hist'].append({'role':'user','content':user_input})

    with st.chat_message('user'):
        st.text(user_input)
    config = {'configurable':{'thread_id':1}}
    response = chatbot.invoke({'messages': [HumanMessage(content = user_input)]},config=config)
    ai_message = response['messages'][-1].content

    st.session_state['message_hist'].append({'role':'AI','content':ai_message})
    with st.chat_message('AI'):
            st.text(ai_message)

