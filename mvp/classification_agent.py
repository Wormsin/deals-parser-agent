from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


def llm_rag_init():
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
                "ID": int,                   
                "описание": "string",         
                "наименование": "string",
                "размеры": ["string/int"],    
                "кол-во": ["int"],            
                "статус": "string",           // Определяется по правилам ниже
                "аналоги": ["string"]         // Перечисли найденные аналоги (если нет аналогов, укажи [])
                "metadata": {{
                    "category": "string",   
                    "season": "string",     
                    "gender": "string",      
                    "material": ["string"]
                    }}
            }}
        ]
        ```

    ### Заполнение поля **"аналоги"**:
    - Выбери подходящие аналоги для каждого товара из списка `{retrieved_products}` (релевантность аналога определяй по описанию), укажи их котороткое наименование.
    - Если аналогов нет, укажи `[]`.

    ### Логика определения **"статуса"** для товаров:
    - `"ШИТЬ"` → Если "category" == Костюм / Куртка / Брюки.
    - `"КОМПЛЕМЕНТАРНОЕ"` → Если category == Обувь / Комплементарное и товар ялвяется спецодеждой(определи по описанию и наименованию) или у него есть аналоги.
    - `"НЕРЕЛЕВАНТНО"` → Если category == Комплементарное, но товар явно не относится к спецодежде(пример: платье)(определи по описанию и наименованию), также если описание не четкое и нет аналогов.

    ### Логика определения **"статуса"** заявки:
    - `"АНАЛОГИ"` → Если у всех товаров со статусом `"ШИТЬ"` в столбце "аналоги" не [].
    - `"ШИТЬ"` → Если хотя бы один товар в JSON 2 имеет статус `"ШИТЬ"` и при этом его "аналоги" = []. 
    - `"НЕРЕЛЕВАНТНО"` → Если хотя бы один товар имеет статус `"НЕРЕЛЕВАНТНО"`.

    ### Формат ответа:
    Ответ должен содержать **два массива**, разделенных словом `next`, не пиши ```json```:


    [ ... ]  // JSON 1
    next
    [ ... ]  // JSON 2
    """
   
    llm = ChatOpenAI(model_name = "gpt-4o-mini")
    prompt = PromptTemplate(input_variables=["retrieved_products", "question"], template=template)
    llm_chain = prompt | llm | StrOutputParser()
    
    return llm_chain

def init_vectore_store():  
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma(embedding_function=embedding_model, collection_name = "products", persist_directory="../chroma_db_price")
    return vector_store










