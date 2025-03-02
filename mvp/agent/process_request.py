from product_parser.json_agent import extract_text_from_file, convert_to_json
from classification_rag.retriever import get_retrieved_products
import json
import pandas as pd

def process_file(file_path, llm, llm_chain, vector_store):
    text_data = extract_text_from_file(file_path)
    json_data = convert_to_json(llm, text_data)
    
    products = json.loads(json_data)[1:]
    retrieved_products = get_retrieved_products(products, vector_store)
    request, products = llm_chain.invoke({
        "retrieved_products": retrieved_products,  
        "question": json_data
        }).split("next")
    df_zayavki = pd.DataFrame(json.loads(request))
    df_tovary = pd.DataFrame(json.loads(products))

    return df_zayavki, df_tovary
