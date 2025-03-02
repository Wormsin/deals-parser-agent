import streamlit as st
import pandas as pd
import os
import time
import os, sys, subprocess
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


DEALS_CSV = "classification_rag/data/deals.csv"
PRODUCTS_CSV = "classification_rag/data/products.csv"

def load_data():
    """Loads deals and products from CSV if available."""
    deals = pd.read_csv(DEALS_CSV) if os.path.exists(DEALS_CSV) else pd.DataFrame(columns=["номер заявки", "дата", "статус", "товары"])
    products = pd.read_csv(PRODUCTS_CSV) if os.path.exists(PRODUCTS_CSV) else pd.DataFrame(columns=["номер заявки", "описание", "наименование", "размеры", "кол-во", "статус", "аналоги"])
    return deals, products

def open_file(filename):
    try:
        if sys.platform.startswith("win"):  # Windows
            os.startfile(filename)
        elif sys.platform.startswith("darwin"):  # macOS
            subprocess.call(["open", filename])
        else:  # Linux
            subprocess.call(["xdg-open", filename])
    except Exception as e:
        st.error(f"Ошибка: {e}")

# Streamlit UI
st.set_page_config(page_title="Order Viewer", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #1A2335;
    }
    .stTitle, .stTabs {
        color: #d84315;
    }
    .stRadio label {
        color: #d84315;
        font-weight: bold;
    }
    .stMarkdown {
        color: white;
    }
    .stTabs [data-baseweb="tab"] {
        color: #D84315;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Order Viewer 💰")
# Layout
col1, col2 = st.columns([3, 5], gap="large")

while True:
    # Load latest data from CSV
    deals, products = load_data()

    if not deals.empty:
        
        with col1:
            # Order selection
            order_ids = deals["номер заявки"].unique()
            selected_order = st.radio("📌 Select an Order ID", order_ids)

        order_info = deals[deals["номер заявки"] == selected_order]

        with col2:
            # Tabs for details
            tab1, tab2 = st.tabs(["📋 General Info", "📦 Products"])

            with tab1:
                st.write("#### General Order Information")
                #st.dataframe(order_info)
                for index, row in order_info.iterrows():
                    st.write(f"**📅 Дата:** {row['дата']}")
                    st.write(f"**✅ Статус:** {row['статус']}")
                    st.write(f"**📦 Товары:** {row['товары']}")
                    st.write("---")
                if st.button("Открыть файл"):
                    open_file(f"mail_agent/attachments/{row['attachments']}")

            with tab2:
                st.write("#### Products in Order")
                order_products = products[products["номер заявки"] == selected_order]
                #st.dataframe(order_products)
                for index, row in order_products.iterrows():
                    st.write(f"**🐱 Название:** {row['наименование']}")
                    st.write(f"**Описание:** {row['описание']}")
                    st.write(f"**Размеры:** {row['размеры'].replace('[', '').replace(']', '')}")
                    st.write(f"**Количество:** {row['кол-во'].replace('[', '').replace(']', '')}")
                    st.write(f"**Статус:** {row['статус']}")
                    st.write(f"**Аналоги:** {row['аналоги'].replace('[', '').replace(']', '')}")
                    st.write("---")
                    
    else:
        st.warning("Пока нет заявок...")

    time.sleep(5)
    st.rerun()  # Forces the UI to refresh
