import pandas as pd
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_unstructured import UnstructuredLoader


def extract_text_from_file(file_path):
    text_data = []
    try:
        loader = UnstructuredLoader(file_path)
        docs = loader.load()
        text_data.append("\n\n".join([doc.page_content for doc in docs]))
    except Exception as e:
        print(f"⚠️ Ошибка при обработке {file_path}: {e}")

    return "\n\n".join(text_data)

def checker_init():
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    return llm

def rag_init():
    template = """
    Ты – эксперт по подбору и производству спецодежды. 
    Ты получаешь на вход следующие JSON-структуры, которые надо дополнить недостоющими параметрами(статусы, аналоги):
    {question}
    1. **Общая характеристика заявки**:
        ```json
        [
            {{
                "номер заявки": "UUID",    // Генерируй уникальный UUID v4
                "дата": "datetime",       // Дата поступления заявки
                "товары": [int],           // Список уникальных ID товаров в этой заявке
                "статус": string            // Определяется по правилам ниже
            }}
        ]
        ```

    2. **Детализация каждого товара в заявке**:
        ```json
        [
            {{
                "номер заявки": "UUID",    // номер заявки из общий хаарктеристики заявки(нужно повторить для каждого товара в таблице)
                "ID": int,                    // ID товара из первого JSON
                "описание": "string",         // Описание товара (если нет, оставь пустым)
                "наименование": "string",     // Наименование товара
                "размеры": ["string/int"],    // Доступные размеры (если нет, укажи [])
                "кол-во": ["int"],            // Количество по размерам или общее (если размеров нет, укажи [общее число])
                "статус": "string",           // Определяется по правилам ниже
                "аналоги": ["string"]         // Перечисли найденные аналоги (если нет аналогов, укажи [])
            }}
        ]
        ```

    ### Логика определения **"статуса"** для товаров:
    - `"ШИТЬ"` → Если товар является спецодеждой.
    - `"КОМПЛЕМЕНТАРНОЕ"` → Если товар не является одеждой (например, ботинки, кепки, очки).
    - `"НЕРЕЛЕВАНТНО"` → Если товар не относится к спецодежде и СИЗ.

    ### Заполнение поля **"аналоги"**:
    - Подбирай аналоги товара из `{retrieved_products}`.
    - Если есть подходящие аналоги, укажи их наименования в массиве.
    - Если аналогов нет, укажи `[]`.

    ### Логика определения **"статуса"** заявки:
    - `"АНАЛОГИ"` → Если у всех товаров со статусом `"ШИТЬ"` в столбце "аналоги" не [].
    - `"ШИТЬ"` → Если хотя бы один товар в JSON 2 имеет статус `"ШИТЬ"` и при этом "аналоги" = []. 
    - `"НЕРЕЛЕВАНТНО"` → Если хотя бы один товар имеет статус `"НЕРЕЛЕВАНТНО"`.

    ### Формат ответа:
    Ответ должен содержать **два массива**, разделенных словом `next`, не пиши ```json```:


    [ ... ]  // JSON 1
    next
    [ ... ]  // JSON 2
    """
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Chroma(embedding_function=embedding_model, collection_name = "products", persist_directory="../chroma_langchain_db_price")
    retriever = vector_store.as_retriever(search_type = "mmr")
    llm = ChatOpenAI(model_name = "gpt-4o-mini")
    prompt = PromptTemplate(input_variables=["retrieved_products", "question"], template=template)
    llm_chain = prompt | llm | StrOutputParser()
    rag_chain = {"retrieved_products":retriever , "question": RunnablePassthrough()} | llm_chain
    
    return rag_chain
    

def convert_to_json(llm, text):
    prompt = f"""
        Ты получишь текстовые данные с описанием товаров. Они могут быть как табличными так и текст с описанием товаров.  
        Верни два списка со следующими структурами. 
        1. Общая характеристика заявки со струткурой:
        [
        {{
            "номер заявки": int,         // используй UUID v4 для генерации уникального номера заявки
            "дата": datetime,  // дата прихода заявки
            "товары": [int]        // уникальные id для каждого товара в этой заявке 
        }}
        ]
        2.
        [
        {{
            "ID": int,         // id-товара из первого json файла
            "описание": "string" // описание товара, если нет оставь пустым 
            "наименование": "string",  // наименование товара
            "размеры": ["string/int"],      // Список доступных размеров (если нет, укажи []), размеры могут иметь следующий вид: l70-176;48-50;S/M/L
            "кол-во": ["int"]         // Количество товаров для каждого размера или общее количество (если размеров нет, укажи [общее число]), количество часто это число перед шт. : 5 шт.
        }}
        ]
        Правила обработки данных:
        Извлекай только нужные данные: игнорируй любые другие колонки и текст.
        "размеры" – если размеры указаны, представь их в виде списка ["S", "M", "L"] или ["44", "56"], если их нет — укажи ["one-size"].
        "кол-во" – Если есть размеры, указывай количество товаров для каждого размера в том же порядке, что и "размеры". 
        Если размеров нет, но указано общее количество, записывай его как список с одним числом ["количество"]. 
        
        Важно:
        Если есть таблицы: анализируй заголовки таблиц и извлекай данные корректно.
        Соблюдай указанную структуру без лишний слов. Ответ должен содержать два массива через запятую.

        Вот данные:
        {text}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip("```json").strip("```")



def process_file(file_path, llm, rag_chain):
    text_data = extract_text_from_file(file_path)
    json_data = convert_to_json(llm, text_data)
    
    request, products = rag_chain.invoke(json_data).split("next")
    df_zayavki = pd.DataFrame(json.loads(request))
    df_tovary = pd.DataFrame(json.loads(products))

    return df_zayavki, df_tovary

