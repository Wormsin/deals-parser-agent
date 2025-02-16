from dotenv import load_dotenv
import os
import time
from classification_agent import process_file, checker_init, rag_init
from datetime import datetime

load_dotenv()


# Define CSV file paths
DEALS_CSV = "data/deals.csv"
PRODUCTS_CSV = "data/products.csv"

def save_to_csv(df, file_path):
    """Appends a DataFrame to an existing CSV file, or creates a new one if it doesn't exist."""
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)  # Append without headers
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)  # Create new file


def monitor_folder(folder_path):
    """Monitors a folder and updates the Streamlit session with new data."""
    llm = checker_init()
    rag_chain = rag_init()
    while True:
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                df_zayavki, df_tovary = process_file(file_path, llm, rag_chain)
                
                df_zayavki['дата'] = datetime.now().date()
                
                 # Save data to CSV files (append mode)
                save_to_csv(df_zayavki, DEALS_CSV)
                save_to_csv(df_tovary, PRODUCTS_CSV)
                
                os.remove(file_path)
                print(f"Processed and deleted file: {file_path}")
        
        time.sleep(1)  # Adjust as needed
        

if __name__ == "__main__":
    monitor_folder("emails")