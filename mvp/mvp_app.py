import streamlit as st
import time
import pandas as pd
import os

DEALS_CSV = "data/deals.csv"
PRODUCTS_CSV = "data/products.csv"

def load_data():
    """Loads deals and products from CSV if available."""
    deals = pd.read_csv(DEALS_CSV) if os.path.exists(DEALS_CSV) else pd.DataFrame(columns=["номер заявки", "дата", "статус", "товары"])
    products = pd.read_csv(PRODUCTS_CSV) if os.path.exists(PRODUCTS_CSV) else pd.DataFrame(columns=["номер заявки", "ID", "описание", "наименование", "размеры", "кол-во", "статус", "аналоги"])
    return deals, products

# Streamlit UI
st.title("📊 Заявки")

# Auto-refresh every 2 seconds
while True:
    # Load latest data from CSV
    deals, products = load_data()

    if not deals.empty:
        # Dropdown for selecting deals
        selected_deal = st.selectbox("Выберете заявку", deals["номер заявки"].unique(), key="deal_select")

        # Display selected deal info
        st.subheader("📝 Информация по заявке")
        st.write(deals[deals["номер заявки"] == selected_deal])

        # Display related products
        st.subheader("📦 Информация по товарам в заявке")
        st.write(products[products["номер заявки"] == selected_deal])
    else:
        st.warning("Пока нет заявок...")

    time.sleep(2)
    st.rerun()  # Forces the UI to refresh
