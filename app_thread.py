import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid 

#-------------utility functions-----------------
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id =generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_hist']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
    return state.values.get('messages',[])
#--------------session setup-----------------------------
st.title("Welcome, I am ur AI assistant")

SECRET_CODE = 'Jay9920'
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "message_hist" not in st.session_state:
    st.session_state.message_hist = []

if "thread_id" not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])


#------------Sidebar UI------------------------------------
st.sidebar.title("Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()
    
st.sidebar.header("My Conversations")
for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages = load_conversation(thread_id)

        temp_messages =[]


        for msg in messages:
            if isinstance(msg,HumanMessage):
                role='user'
            else:
                role ='assistant'
            temp_messages.append({'role':role,'content':msg.content})

        st.session_state['message_hist']=temp_messages



#---------------------------------------------------------

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

        config = {'configurable':{'thread_id':st.session_state['thread_id']}}
   
        with st.chat_message("assistant"):

            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
               {'messages': [HumanMessage(content=user_input)]},
               config=config,
               stream_mode='messages'
               )  
            )
        st.session_state['message_hist'].append({'role':"assistant",'content':ai_message})
        
