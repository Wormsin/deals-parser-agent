


def retriever_init(vector_store, metadata, description):
    filter_data = []
    for key in metadata:
        filter_data.append({key: {'$eq': metadata[key]}})
    filters = {'$and': filter_data}
    retriever = vector_store.as_retriever(search_kwargs={'filter':filters})
    
    retrieved_products = retriever.invoke(description)
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
    