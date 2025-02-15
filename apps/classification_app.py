import os 
import streamlit as st 
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import json
from langchain.schema import Document

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = Chroma(embedding_function=embedding_model, collection_name = "products", persist_directory="./chroma_langchain_db_price")

retriever = vector_store.as_retriever(search_type = "mmr")

llm = ChatOpenAI(model_name = "gpt-4o-mini")

template = """
Ты – эксперт по подбору и производству спецодежды.  
Твоя задача – анализировать запросы клиентов и предлагать им подходящие товары или возможности пошива.  

### 🔹 Входные данные от пользователя:
{question}

### 🔹 Контекст: Найденные аналоги из базы данных:
{retrieved_products}
---
### Твоя задача:
 **Оценить наличие аналогов**  
   - Если в базе есть товары, соответствующие запросу, **перечисли их с размерами и количеством**.  
   - Если каких-то размеров не хватает, **укажи, сколько и какого размера нужно пошить**.  

 **Если аналогов нет – оценить возможность пошива**  
   - Мы производим **спецодежду**. Если товар подходит под нашу категорию, **оцени возможность пошива**.  
   - Если пошив возможен, **укажи, что мы можем пошить нужный вам товар**.  
   - Если товар не относится к спецодежде, напиши, что мы не можем его изготовить.  
---
### Формат ответа:
 **Если есть аналоги в наличии:**  
 Мы можем предложить следующие аналоги:

Название аналога 1: размеры, в наличии количество
Название аналога 2: размеры, в наличии количество
 
**Только если Не хватает(число в наличии < числа требуемого):**
Размер X: требуется количество, в наличии сколько есть → Нужно пошить недостающее количество
Размер Y: требуется количество, но нет в наличии → Нужно пошить количество

**Если аналогов нет, но можем пошить:**  
В базе нет подходящих аналогов, но мы можем сшить этот товар.

**Если аналогов нет и пошив невозможен:** 
К сожалению, в нашей базе нет аналогов, и мы не можем изготовить этот товар,
так как он не относится к категории спецодежды.

"""

prompt = PromptTemplate(input_variables=["retrieved_products", "question"], template=template)

llm_chain = prompt | llm | StrOutputParser()

rag_chain = {"retrieved_products":retriever , "question": RunnablePassthrough()} | llm_chain

st.title("Классификация заявок")
input_text = st.text_area(label = "Введите описание товара", height=200)


if input_text:
    st.write(rag_chain.invoke(input_text))