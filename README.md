# MCP DB Server and Chatbot

This project provides a FastAPI-based server for interacting with a MySQL database and a simplified command-line chatbot to query the database.

## Project Idea
The core idea is to offer a user-friendly interface to access and retrieve data from a MySQL database without requiring direct SQL knowledge. The FastAPI server exposes a robust API, and the chatbot acts as a client, translating user commands into API calls.

## Functionality

### FastAPI Server (`main.py`, `database.py`)
The FastAPI server provides a RESTful API for database operations:

-   **`database.py`**: Handles MySQL database connection using SQLAlchemy, manages sessions, retrieves table schemas, lists table names, and executes raw SQL queries.

-   **`main.py`**: Defines the FastAPI application with the following endpoints:
    -   `GET /tables`: Lists all available table names in the connected database.
    -   `GET /tables/{table_name}/schema`: Returns the schema (column names and types) for a specified table.
    -   `POST /sql`: Allows execution of raw SQL queries (primarily for advanced/internal use).
    -   `GET /query/{table_name}`: The main data retrieval endpoint. It supports:
        -   Filtering records by column values (e.g., `status=active`).
        -   Limiting the number of results (`limit=X`).
        -   Offsetting results for pagination (`offset=Y`).
        -   Ordering results (`order_by=column DESC/ASC`).
        -   **Selecting specific columns** (`columns=col1,col2`).
        -   Case-insensitive column name matching for filters.

### Chatbot (`chatbot.py`)
The command-line chatbot acts as a client for the FastAPI server, enabling interactive database querying:

-   **Simplified Interaction**: The chatbot operates purely on explicit commands, without Natural Language Processing (NLP) or LLM integration.
-   **Commands**:
    -   `help`: Displays a list of all available commands and their usage.
    -   `list tables`: Shows all table names in the database.
    -   `list schemas`: Displays all table names along with their full schemas (columns and types).
    -   `get schema [table_name]`: Provides the schema for a specific table.
    -   `query`: The primary command for data retrieval, offering two modes:
        -   **Interactive Mode**: Typing `query` without arguments initiates a guided process to select a table, apply filters, and choose specific columns. It also allows switching tables or exiting the query session.
        -   **Direct Command Mode**: Allows users to specify all query parameters in a single line. Supports flexible column selection (e.g., `query email,name user_table limit=3` or `query user_table columns=email,name limit=3`).

## Setup and Running

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ARehman-Nets/mcp_server_from_db.git
    cd mcp_server_from_db
    ```

2.  **Set up Python Virtual Environment**:
    ```bash
    python -m venv venv
    ./venv/Scripts/activate # On Windows
    # source venv/bin/activate # On Linux/macOS
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    -   Create a `.env` file in the project root with your MySQL database credentials:
        ```
        DB_HOST=your_db_host
        DB_PORT=your_db_port
        DB_USER=your_db_user
        DB_PASSWORD=your_db_password
        DB_NAME=your_db_name
        ```
    -   Create a `.env.chatbot` file in the project root with the FastAPI server URL:
        ```
        MCP_SERVER_URL=http://localhost:8000
        ```

5.  **Run the FastAPI Server**:
    ```bash
    uvicorn main:app --reload
    ```
    The server will typically run on `http://127.0.0.1:8000`.

6.  **Run the Chatbot**:
    ```bash
    python chatbot.py
    ```
    You can then use the commands like `help`, `list tables`, `list schemas`, `get schema [table_name]`, and `query` to interact with your database. 

## Future Enhancements

-   Re-integrate LLM for natural language querying, potentially using a more robust tool-calling framework.
-   Add support for more complex analytical queries and reporting features in the FastAPI server.
-   Implement data modification (INSERT, UPDATE, DELETE) capabilities with appropriate access controls.

