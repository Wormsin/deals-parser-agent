from dotenv import load_dotenv
import time
import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classification_rag.classification_agent import llm_rag_init, init_vectore_store
from datetime import datetime
from process_request import process_file
from product_parser.json_agent import checker_init


load_dotenv()


# Define CSV file paths
DEALS_CSV = "classification_rag/data/deals.csv"
PRODUCTS_CSV = "classification_rag/data/products.csv"

def save_to_csv(df, file_path):
    """Appends a DataFrame to an existing CSV file, or creates a new one if it doesn't exist."""
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)  # Append without headers
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)  # Create new file
        
        

def monitor_folder(folder_path):
    """Monitors a folder and updates the Streamlit session with new data."""
    llm = checker_init()
    llm_chain = llm_rag_init()
    vector_store = init_vectore_store()
    while True:
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                df_zayavki, df_tovary = process_file(file_path, llm, llm_chain, vector_store)
                
                df_zayavki['дата'] = datetime.now().date()
                df_zayavki['attachments'] = Path(file_path).name
                
                 # Save data to CSV files (append mode)
                save_to_csv(df_zayavki, DEALS_CSV)
                save_to_csv(df_tovary, PRODUCTS_CSV)
                
                os.remove(file_path)
                print(f"Processed and deleted file: {file_path}")
        
        time.sleep(1)  # Adjust as neededclassification/
        

if __name__ == "__main__":
    monitor_folder("classification_rag/emails")