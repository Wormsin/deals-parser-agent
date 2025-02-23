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


def convert_to_json(llm, text):
    prompt = f"""
        Ты получишь текстовые данные с описанием товаров. Они могут быть как табличными так и текст с описанием товаров.  
        Верни следующую JSON структур c Общей характеристикой заявки и Детализацией каждого товара в заявке:
        [
        {{
            "номер заявки": int,         // используй UUID v4 для генерации уникального номера заявки
            "дата": datetime,  // дата прихода заявки
            "товары": [int]        // уникальные id для каждого товара в этой заявке 
        }},
        {{
            "ID": int,         // id-товара из первого json файла
            "описание": "string" // описание товара, если нет оставь пустым 
            "наименование": "string",  // наименование товара
            "размеры": ["string/int"],      // Список доступных размеров (если нет, укажи []), размеры могут иметь следующий вид: l70-176;48-50;S/M/L
            "кол-во": ["int"]         // Количество товаров для каждого размера или общее количество (если размеров нет, укажи [общее число]), количество часто это число перед шт. : 5 шт.
            "metadata": {{
                "category": "Костюм / Куртка / Брюки / Обувь / Комплементарное (определи по названию и описанию, указывай Комплементарное если товар не является костюмом, курткой, брюками или обувью, не придумывай новые категории, указывай только из этого списка)",
                "season": "Зима / Лето / Демисезон (определи из описания)",
                "gender": "Мужской / Женский / Унисекс (если нет упоминаний пола, ставь унисекс)",
                "material":  "["список материалов (определи из описания)"]", //список переведи в строку без указания отсутопов или новой строки
                
            }}
        }}
        ]
        Правила обработки данных:
        Извлекай только нужные данные: игнорируй любые другие колонки и текст.
        "размеры" – если размеры указаны, представь их в виде списка ["S", "M", "L"] или ["44", "56"], если их нет — укажи ["one-size"].сделай строку из листа не изменяя сами данные без указания отсутопов или новой строки
        "кол-во" – Если есть размеры, указывай количество товаров для каждого размера в том же порядке, что и "размеры". сделай строку из листа не изменяя сами данные без указания отсутопов или новой строки
        Если размеров нет, но указано общее количество, записывай его как список с одним числом ["количество"]. 
        
        Важно:
        Если есть таблицы: анализируй заголовки таблиц и извлекай данные корректно.
        Соблюдай указанную структуру без лишний слов. Ответ должен содержать ТОЛЬКО JSON структуру вида: [{...}, {...}, {...}, ...]

        Вот данные:
        {text}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return response.content.strip("```json").strip("```")

