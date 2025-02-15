# LLM Agent Based on RAG System

## Description

This project involves the development of an **LLM (Large Language Model) agent** powered by a **RAG (Retrieval-Augmented Generation)** system. The primary goal of this system is to facilitate efficient handling and analysis of customer requests by extracting useful information from the received data in any format. The agent processes customer data, finds analogous products using the RAG system, and stores relevant information in a **Django database** for further use. 

Additionally, the project includes a **apps/rag_app.py** that leverages the **OpenAI reasoning model** to analyze customer requests, generate product recommendations, and offer price estimates based on historical data and previous interactions.

Currently, this project is in its **MVP (Minimum Viable Product)** stage, showcasing the core functionality and potential of the system.

## Motivation

The motivation behind this project is to improve the efficiency and accuracy of product recommendation systems by combining the power of large language models and retrieval-augmented generation. Traditional systems rely on static data, but by incorporating dynamic querying and reasoning capabilities, this project enables businesses to provide more personalized and relevant product recommendations in response to customer requests.

Moreover, by storing extracted data in a structured database and utilizing AI-powered analysis, businesses can gain insights into trends, customer preferences, and optimize their pricing strategies.

## Features

- **Data Extraction classification.ipynb**: The system can process customer data in various formats and extract useful information for further analysis and action.
- **Product Recommendation (RAG) classification.ipynb**: Using the RAG system, the agent can retrieve analogues for products based on received data and provide appropriate recommendations.
- **Django Database Storage classification.ipynb**: All useful data and processed information are stored in a structured **Django database** for easy management and future analysis.
- **Price Offering apps/rag_app.py**: Based on previous data and historical trends, the system can generate price offers for recommended products.
- **OpenAI Reasoning apps/rag_app.py**: The integrated **OpenAI reasoning model** enables intelligent analysis of customer requests, allowing for better decision-making and personalized responses.


## Current Status

This project is currently in the **MVP (Minimum Viable Product)** stage. The core functionality, including the LLM agent, RAG system, and Django database integration, is implemented, but there are plans to further enhance the system by:

- Expanding the types of data that can be processed by the system.
- Refining the product recommendation and price offering algorithms.
- Improving the integration with OpenAI models for better reasoning and customer interaction handling.

## Conclusion

This project combines the power of **LLMs**, **RAG systems**, and **Django databases** to create a flexible and intelligent product recommendation and pricing system. The MVP is already capable of extracting useful data from customer requests, recommending analogous products, and storing relevant information for future analysis. With further enhancements, this system has the potential to significantly improve how businesses respond to customer inquiries and optimize their pricing strategies.

