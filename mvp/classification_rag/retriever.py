from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
import os 
import json
import sys
from langchain.vectorstores import VectorStore
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def init_bm25():
    docs = []
    for file_name in os.listdir("classification_rag/json_price_full"):
        file_path = "classification_rag/json_price_full/" + file_name
        with open(file_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        for product in products:
            metadata = product["metadata"]

            # Create a LangChain Document object
            doc = Document(page_content=product["text"], metadata=metadata)
            docs.append(doc)
    bm25_retriever = BM25Retriever.from_documents(documents=docs)
    return bm25_retriever
    

def retriever_init(vector_store, metadata, description):
    filter_data = []
    for key in metadata:
        filter_data.append({key: {'$eq': metadata[key]}})
    filters = {'$and': filter_data}
    retriever = vector_store.as_retriever(search_kwargs={'filter':filters})
    ensemble_retriever = EnsembleRetriever(retrievers=[init_bm25(), retriever],
                                       weights=[0.7, 0.3])
    retrieved_products = ensemble_retriever.invoke(description)
    #print(filters)
    
    return retrieved_products

def get_retrieved_products(products, vector_store):
    retrieved_products = []
    for product in products:
        metadata = product["metadata"]
        del metadata["material"]
        if metadata["category"] == "Комплементарное":
            del metadata["season"]
    
        retrieved_product = retriever_init(vector_store, metadata, product["наименование"]+product["описание"])
        product["аналоги"] = retrieved_product
        retrieved_products.append(retrieved_product)
    return retrieved_products
    