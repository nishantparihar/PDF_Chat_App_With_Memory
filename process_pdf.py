
import streamlit as st
import os
from dotenv import load_dotenv
import time
import pickle

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

import pytesseract
from pdf2image import convert_from_bytes
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

@st.cache_data
def get_text_chunks(pdf):
    pdf = convert_from_bytes(pdf.read())
    text = ""

    for page in pdf:
        text += pytesseract.image_to_string(page,lang='eng')
    #st.write(text)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_text(text=text)
    return chunks



@st.cache_data
def get_vector_store(store_name, chunks):
    if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                VectorStore = pickle.load(f)
            
    else:
        embeddings = OpenAIEmbeddings()
        VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
        with open(f"{store_name}.pkl", "wb") as f:
            pickle.dump(VectorStore, f)

    return VectorStore

