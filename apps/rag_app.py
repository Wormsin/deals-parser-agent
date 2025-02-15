import os 
import streamlit as st 
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama.llms import OllamaLLM

load_dotenv()

def format_docs(docs):
    return "\n\n".join([f"Date: {doc.metadata['date']}\nPrice: {doc.metadata['price'] + doc.metadata['currency']}\nContent: {doc.page_content}" for doc in docs])


embedding_model = HuggingFaceEmbeddings(model_name = "intfloat/multilingual-e5-base")
vector_store = Chroma(embedding_function=embedding_model, collection_name = "json_collection", persist_directory="./chroma_langchain_db")

retriever = vector_store.as_retriever(search_type = "mmr", search_kwargs={"filter": {"type": "костюм"}})

llm = ChatOpenAI(model_name = "o1-mini")
#llm = OllamaLLM(model="deepseek-r1")

template = """
Задача:
Оценить цену нового продукта на основе предоставленного контекста.

Инструкции:
Сейчас февраль 2025 года. 
Пользователь предоставит описание нового продукта. 
Вам нужно будет использовать цены существующих продуктов из поля "Price" и их описания из поля "Content".
Поле "Date" указывает, когда продукт был предложен по указанной цене.
Если указана дата, скорректируйте цену с учётом инфляции, увеличив цену на 10% за каждый год в зависимости от разницы между текущей датой и датой контекста.
Если поле "Date" отсутствует или пустое, не вносите изменений в цену.
Чётко объясните, какие параметры повлияли на оценочную цену(перечисли определенные характеристика изделия(виды ткани и т.д.), если таковые есть и их влияние) 
и как (например, увеличили или уменьшили стоимость).
Предоставьте конкретную числовую цену, если это возможно, с учётом инфляции, если это применимо.
Если точную цену определить невозможно, чётко объясните, почему, какие дополнительные данные нужны и какие параметры отсутствуют.
Не выдумывайте информацию. Если в контексте нет релевантных данных, просто ответьте: "Я не знаю." с указанием причины. 


<context>
{context}
</context>

question: {question}

"""
prompt = PromptTemplate(input_variables=["context", "question"], template=template)

llm_chain = prompt | llm | StrOutputParser()

rag_chain = {"context":retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()} | llm_chain


st.title("CPQ RAG DEMO")
input_text = st.text_area(label = "Введите описание товара", height=200)


if input_text:
    st.write(rag_chain.invoke(input_text))