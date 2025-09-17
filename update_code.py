import streamlit as st
import uuid
from langchain_core.messages import HumanMessage
from backend import chatbot  # Make sure backend.py contains the compiled chatbot

# ------------------ Utility Functions ------------------ #

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_hist'] = []
    st.session_state['generated_summary'][thread_id] = False
    add_thread(thread_id)

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def load_summary(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('summary', f"Chat {str(thread_id)[:8]}")

def get_last_message_preview(thread_id):
    messages = load_conversation(thread_id)
    if messages:
        last_msg = messages[-1].content
        return last_msg[:30] + "..." if len(last_msg) > 30 else last_msg
    return "No messages yet."

# ------------------ Session Initialization ------------------ #

st.title("🤖 Welcome, I am your AI Assistant")

SECRET_CODE = 'Jay9920'

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "message_hist" not in st.session_state:
    st.session_state['message_hist'] = []

if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = []

if "chat_summaries" not in st.session_state:
    st.session_state['chat_summaries'] = {}

if "generated_summary" not in st.session_state:
    st.session_state['generated_summary'] = {}

if "rename_mode" not in st.session_state:
    st.session_state['rename_mode'] = False

# Add current thread to threads list
add_thread(st.session_state['thread_id'])

# ------------------ Sidebar ------------------ #

st.sidebar.title("📚 My Conversations")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.markdown("---")

# Toggle Rename Mode
if st.sidebar.checkbox("✏️ Rename Chat Titles", key="rename_toggle"):
    st.session_state['rename_mode'] = True
else:
    st.session_state['rename_mode'] = False

# Display all chat threads
for thread_id in st.session_state['chat_threads'][::-1]:
    # Get LLM summary title (or load it if not present)
    summary = st.session_state['chat_summaries'].get(thread_id)

    if not summary:
        summary = load_summary(thread_id)
        if summary:
            st.session_state['chat_summaries'][thread_id] = summary

    if not summary:
        summary = f"Chat {str(thread_id)[:8]}"  # Fallback

    preview = get_last_message_preview(thread_id)

    col1, col2 = st.sidebar.columns([0.75, 0.25])

    if st.session_state['rename_mode']:
        # Editable title
        new_title = col1.text_input("Rename", value=summary, key=f"rename_{thread_id}")
        if new_title != summary:
            st.session_state.chat_summaries[thread_id] = new_title
        col2.write("")
    else:
        # Select chat thread
        if col1.button(summary, key=f"chat_{thread_id}"):
            st.session_state['thread_id'] = thread_id
            messages = load_conversation(thread_id)
            temp_messages = []
            for msg in messages:
                role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
                temp_messages.append({'role': role, 'content': msg.content})
            st.session_state['message_hist'] = temp_messages

        col2.caption(f"💬 {preview}")

st.sidebar.markdown("---")

# ------------------ Main Chat Area ------------------ #

if not st.session_state.authenticated:
    code = st.text_input("🔐 Enter Access Code", type="password")
    if code == SECRET_CODE:
        st.session_state.authenticated = True
        st.success("✅ Access granted!")
        st.rerun()
else:
    st.write("🎉 You are logged in.")

    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.session_state.message_hist = []
        st.experimental_rerun()

    # Display message history
    for message in st.session_state['message_hist']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Show user message
        st.session_state.message_hist.append({'role': 'user', 'content': user_input})
        with st.chat_message('user'):
            st.markdown(user_input)

        # Send to backend
        config = {'configurable': {'thread_id': st.session_state['thread_id']}}
        stream = chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages"
        )

        # Stream assistant response
        ai_message = ""
        with st.chat_message("assistant"):
            for chunk, _ in stream:
                st.write(chunk.content, end="")
                ai_message += chunk.content

        # Save assistant response
        st.session_state['message_hist'].append({'role': 'assistant', 'content': ai_message})

        # Generate summary only once per thread
        thread_id = st.session_state['thread_id']
        if not st.session_state['generated_summary'].get(thread_id, False):
            final_state = chatbot.get_state(config=config)
            summary = final_state.values.get("summary", None)
            if summary:
                st.session_state.chat_summaries[thread_id] = summary
            st.session_state['generated_summary'][thread_id] = True
