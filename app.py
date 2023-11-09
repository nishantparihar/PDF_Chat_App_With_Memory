import streamlit as st
import os
from dotenv import load_dotenv
import time


from streamlit_extras.add_vertical_space import add_vertical_space

from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory


from database_connect import *
from process_pdf import *


if "pdf" not in st.session_state:
     st.session_state.pdf = False

if "hflag1" not in st.session_state:
     st.session_state.hflag1 = False


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")




def handle_button_click(conversation_id):


    if st.session_state.hflag1 == False and st.session_state.messages :
        saveIntoDatabase(st.session_state.title, st.session_state.messages)


    st.session_state.hflag1 = True
    
    engine = getConnection()

    with engine.connect() as connection:
        result = connection.execute(sa.text(f"SELECT content FROM chats WHERE conversation_id = {conversation_id}"))

        conversation_content = []
        for row in result:
            conversation_content.append(row[0])


        st.session_state.messages.clear()
        count = 0

        if conversation_content:
            for message in conversation_content:
                if(count%2 == 0):
                    st.session_state.messages.append({"role": "human", "content": message})
                    
                    count += 1
                else:
                    st.session_state.messages.append({"role": "ai", "content": message})
                    count += 1
        
      
            
                    


def main():
        
    if "messages" not in st.session_state:
                st.session_state.messages = []

    if "title" not in st.session_state:
        st.session_state.title = "New Chat"

    st.title('🤗💬 LLM Chat App')
    st.header("Chat with PDF 💬")

    tab1, tab2, tab3 = st.tabs(["Try it!!", "How to??", "About"])

    with tab1:
        # upload a PDF file
        pdf = st.file_uploader("Upload your PDF", type='pdf')   

    with tab2:
        st.markdown('''
        ## How to Use ChatPDF App

        1. Upload a PDF.
        2. Ask questions in the "Ask a query" field.
        3. Enjoy the conversation.

        The app provides answers based on the PDF content.
        ''')

    with tab3:
        st.markdown('''
            ## About
            This app is an LLM-powered chatbot built using:
            - [Streamlit](https://streamlit.io/)
            - [LangChain](https://python.langchain.com/)
            - [OpenAI](https://platform.openai.com/docs/models) LLM model
            ''')

        st.markdown('''
            ## Developed by [Nishant Singh Parihar](https://nishantparihar.github.io/)
            ''')

    
    with st.chat_message('assistant'):
                st.markdown("Hi. . . Upload File Lets Talk!!!")

    # Initialize Streamlit chat UI
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    load_dotenv()

    # if pdf is None:
    #     if st.session_state.messages :
    #          saveIntoDatabase(st.session_state.title, st.session_state.messages)
    #     #st.session_state.clear()

    if pdf is None and st.session_state.pdf == True:
        if st.session_state.hflag1 == False and st.session_state.messages :
             saveIntoDatabase(st.session_state.title, st.session_state.messages)
        st.session_state.messages.clear()

    
    if pdf is not None:
        st.session_state.pdf = True
        store_name = pdf.name[:-4]

        chunks = get_text_chunks(pdf)
        VectorStore = get_vector_store(store_name, chunks)
        
            
        if prompt := st.chat_input("Ask a query about your PDF:"):

            if st.session_state.title ==  "New Chat":
                 st.session_state.title = prompt[0:21]
            
            with st.chat_message("Human"):
                st.markdown(prompt)
            
            llm = OpenAI(model_name='gpt-3.5-turbo')
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            chain = ConversationalRetrievalChain.from_llm(llm, VectorStore.as_retriever(), memory=memory)

            with get_openai_callback() as cb:
                #response = chain({"input_documents": docs, "human_input": query}, return_only_outputs=True)
                response = chain({'question':prompt})
                print(cb)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                for chunk in response["answer"].split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            for msg in response["chat_history"]:
                st.session_state.messages.append({"role": msg.type, "content": msg.content})
            


            



with st.sidebar:
        if "messages" not in st.session_state:
            st.session_state.messages = []


        if st.button('New Chat', key=0):
            if st.session_state.hflag1 == False and st.session_state.messages :
                saveIntoDatabase(st.session_state.title, st.session_state.messages)
            
            st.session_state.hflag1 = False
            st.session_state.messages.clear()
            st.session_state.title = ""

        if "title" not in st.session_state or st.session_state.title == "":
            st.session_state.title = "New Chat"

        if st.session_state.title != "New Chat":
             st.button('#### ' + st.session_state.title)


        conversation_data = getTitles()

        
        if conversation_data:
            for conversation_id, title in conversation_data:
                clicked = st.button('#### ' + title, key=conversation_id)
                if clicked:
                    handle_button_click(conversation_id)
                    st.session_state.rerun = True
                
  

if __name__ == '__main__':
    main()
