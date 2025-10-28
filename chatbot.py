import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables from .env.chatbot file
load_dotenv(dotenv_path='.env.chatbot')

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

if not MCP_SERVER_URL:
    print("Error: MCP_SERVER_URL not found in .env.chatbot")
    exit(1)

def execute_mcp_query(table_name: str, query_params: dict):
    """Executes a query against the MCP server's /query/{table_name} endpoint."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/query/{table_name}", params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error executing query: {e}"}

def main():
    print("Initializing MCP Chatbot...")
    print(f"Connected to MCP server at {MCP_SERVER_URL}")
    print("Type your command, 'help' for commands, 'exit' to quit.")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'help':
            print("\nAvailable commands:")
            print("  list tables - List all available tables from the MCP server.")
            print("  list schemas - List all available tables and their schemas from the MCP server.")
            print("  get schema [table_name] - Get the schema for a specific table.")
            print("  query [columns] [table_name] [column1=value1] ... [limit=X] [offset=Y] [order_by=Z] - Query records from a table. Columns can be comma-separated (e.g., 'col1,col2').")
            print("  exit - Quit the chatbot.")
            print("\nExample Query: query device_table ne_ip_address=10.82.192.4 status=active limit=5 columns=DEVICE_ID,STATUS")
            print("Example Query: query email,name user_table limit=3")
            print("Example Query: query user_table limit=10 order_by=username DESC")
            continue
        elif user_input.lower() == 'list schemas':
            try:
                response = requests.get(f"{MCP_SERVER_URL}/tables")
                response.raise_for_status()
                tables = response.json()
                print("\n--- Available Tables and their Schemas ---")
                for table in tables:
                    print(f"\nTable: {table}")
                    schema_response = requests.get(f"{MCP_SERVER_URL}/tables/{table}/schema")
                    schema_response.raise_for_status()
                    schema = schema_response.json()
                    for col, typ in schema.items():
                        print(f"  - {col} ({typ})")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching table schemas: {e}")
            continue
        elif user_input.lower() == 'list tables':
            try:
                response = requests.get(f"{MCP_SERVER_URL}/tables")
                response.raise_for_status()
                tables = response.json()
                print("\nAvailable Tables:")
                for table in tables:
                    print(f"- {table}")
            except requests.exceptions.RequestException as e:
                print(f"Error listing tables: {e}")
            continue
        elif user_input.lower().startswith('get schema '):
            parts = user_input.split(' ', 2)
            if len(parts) == 3:
                table_name = parts[2]
                try:
                    response = requests.get(f"{MCP_SERVER_URL}/tables/{table_name}/schema")
                    response.raise_for_status()
                    schema = response.json()
                    print(f"\nSchema for {table_name}:")
                    for col, typ in schema.items():
                        print(f"  {col}: {typ}")
                except requests.exceptions.RequestException as e:
                    print(f"Error getting schema for {table_name}: {e}")
            else:
                print("Invalid command. Usage: get schema [table_name]")
            continue
        elif user_input.lower().startswith('query'):
            parts = user_input.split(' ')
            
            if len(parts) > 1: # Direct command mode
                table_name = None
                query_params = {}
                potential_columns = None

                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        query_params[key] = value
                    elif ',' in part and potential_columns is None: # Assume first comma-separated is columns
                        potential_columns = part
                    elif table_name is None:
                        table_name = part
                    else:
                        print(f"Invalid or unexpected argument: {part}. Skipping.")
                        continue
                
                if potential_columns and 'columns' not in query_params:
                    query_params['columns'] = potential_columns

                if not table_name:
                    print("Table name is required for direct query.")
                    continue

                results = execute_mcp_query(table_name, query_params)
                if "error" in results:
                    print(f"Error executing query: {results['error']}")
                else:
                    if results:
                        print(json.dumps(results, indent=2))
                    else:
                        print("No results found.")
            else: # Interactive query mode
                while True:
                    table_name = input("Enter table name (or 'switch table' to change, 'exit query' to quit): ").strip()
                    if table_name.lower() == 'exit query':
                        break
                    elif table_name.lower() == 'switch table':
                        continue # Go back to prompting for table name
                    elif not table_name:
                        print("Table name cannot be empty.")
                        continue

                    # Validate table name (optional, but good practice)
                    try:
                        response = requests.get(f"{MCP_SERVER_URL}/tables")
                        response.raise_for_status()
                        available_tables = response.json()
                        if table_name not in available_tables:
                            print(f"Table '{table_name}' not found. Available tables: {', '.join(available_tables)}")
                            continue
                    except requests.exceptions.RequestException as e:
                        print(f"Error checking available tables: {e}")
                        continue

                    while True:
                        query_params = {}
                        filters_input = input(f"Enter filters for {table_name} (e.g., key=value, separated by spaces, optional, or 'switch table', 'exit query'): ").strip()
                        if filters_input.lower() == 'exit query':
                            break # Exit interactive query mode
                        elif filters_input.lower() == 'switch table':
                            break # Go back to prompting for table name
                        
                        if filters_input:
                            for param_pair in filters_input.split(' '):
                                if '=' in param_pair:
                                    key, value = param_pair.split('=', 1)
                                    query_params[key] = value
                                else:
                                    print(f"Invalid filter format: {param_pair}. Skipping.")

                        columns_input = input(f"Enter columns to display for {table_name} (e.g., col1,col2, or leave empty for all, or 'switch table', 'exit query'): ").strip()
                        if columns_input.lower() == 'exit query':
                            break # Exit interactive query mode
                        elif columns_input.lower() == 'switch table':
                            break # Go back to prompting for table name
                        
                        if columns_input:
                            query_params['columns'] = columns_input

                        results = execute_mcp_query(table_name, query_params)
                        if "error" in results:
                            print(f"Error executing query: {results['error']}")
                        else:
                            if results:
                                print(json.dumps(results, indent=2))
                            else:
                                print("No results found.")
                        
                        # After displaying results, ask if they want to query again for the same table or switch
                        action = input("Query again for this table, 'switch table', or 'exit query'? ").strip().lower()
                        if action == 'exit query':
                            break # Exit interactive query mode
                        elif action == 'switch table':
                            break # Go back to prompting for table name
                        # else: continue the inner loop for the same table
                    if table_name.lower() == 'exit query': # Check if inner loop broke due to exit query
                        break
        else:
            print("Unknown command. Type 'help' for available commands.")

if __name__ == "__main__":
    main()