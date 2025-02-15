import os 
import streamlit as st 
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
)


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional product manager"),
    ("human", "Question:{question}")
])
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

st.title("CPQ RAG DEMO")
input_text = st.text_input("Enter your question to our product manager")

if input_text:
    st.write(chain.invoke({'question':input_text}))