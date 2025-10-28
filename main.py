from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database import get_db, get_all_table_names, get_table_schema, execute_sql_query
from sqlalchemy import text

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "MCP DB Server is running!"}

@app.get("/tables", response_model=List[str])
async def list_tables():
    """List all table names in the connected database."""
    try:
        table_names = get_all_table_names()
        return table_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tables: {e}")

@app.get("/tables/{table_name}/schema", response_model=Dict[str, str])
async def get_table_details(table_name: str):
    """Get the schema (column names and types) for a specific table."""
    try:
        schema = get_table_schema(table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found or no schema available.")
        return schema
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting schema for table '{table_name}': {e}")

@app.post("/sql", response_model=List[Dict[str, Any]])
async def execute_raw_sql(sql_query: Dict[str, str]):
    """Execute a raw SQL query and return the results."""
    query = sql_query.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="'query' field is required in the request body.")
    try:
        results = execute_sql_query(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {e}")

from fastapi import Request # Add this import at the top

@app.get("/query/{table_name}", response_model=List[Dict[str, Any]])
async def query_table(
    table_name: str,
    request: Request, # Add Request parameter
    db: Session = Depends(get_db),
    columns: Optional[str] = Query(None, description="Comma-separated list of columns to retrieve (e.g., 'column1,column2')"),
):
    """Query records from a specific table with filtering, limit, offset, and ordering."""
    try:
        # Check if table exists
        if table_name not in get_all_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")

        table_schema = get_table_schema(table_name)
        if not table_schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found or no schema available.")

        select_columns = "*"
        if columns:
            requested_columns = [col.strip() for col in columns.split(',')]
            # Validate requested columns against the actual table schema
            invalid_columns = [col for col in requested_columns if col not in table_schema]
            if invalid_columns:
                raise HTTPException(status_code=400, detail=f"Invalid column(s) requested: {', '.join(invalid_columns)}")
            select_columns = ", ".join(requested_columns)

        query_str = f"SELECT {select_columns} FROM {table_name}"
        where_clauses = []
        params = {}

        # Extract query parameters
        query_params = dict(request.query_params)

        limit = query_params.pop("limit", None)
        offset = query_params.pop("offset", None)
        order_by = query_params.pop("order_by", None)

        # Convert limit and offset to int if they exist
        if limit:
            try:
                limit = int(limit)
                if limit < 1:
                    raise ValueError("Limit must be a positive integer.")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid limit parameter. Must be an integer >= 1.")
        
        if offset:
            try:
                offset = int(offset)
                if offset < 0:
                    raise ValueError("Offset must be a non-negative integer.")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid offset parameter. Must be an integer >= 0.")

        # Build WHERE clauses from remaining query_params (filters)
        table_schema = get_table_schema(table_name)
        schema_col_map = {col.lower(): col for col in table_schema.keys()}

        for col_param, value in query_params.items():
            col_lower = col_param.lower()
            if col_lower not in schema_col_map:
                raise HTTPException(status_code=400, detail=f"Invalid filter column: {col_param}")
            
            actual_col_name = schema_col_map[col_lower]
            where_clauses.append(f"TRIM({actual_col_name}) = TRIM(:{actual_col_name})")
            params[actual_col_name] = value

        if where_clauses:
            query_str += " WHERE " + " AND ".join(where_clauses)

        # Add ORDER BY clause
        if order_by:
            # Basic sanitization for order_by to prevent SQL injection
            # This is a very basic example, a more robust solution would parse and validate
            # column names and ASC/DESC keywords.
            parts = order_by.split()
            if len(parts) == 1 and parts[0] in table_schema:
                query_str += f" ORDER BY {order_by}"
            elif len(parts) == 2 and parts[0] in table_schema and parts[1].upper() in ["ASC", "DESC"]:
                query_str += f" ORDER BY {order_by}"
            else:
                raise HTTPException(status_code=400, detail=f"Invalid order_by parameter: {order_by}")

        # Add LIMIT and OFFSET
        if limit is not None:
            query_str += f" LIMIT :limit"
            params["limit"] = limit
        if offset is not None:
            query_str += f" OFFSET :offset"
            params["offset"] = offset

        results = db.execute(text(query_str), params).fetchall()
        return [row._asdict() for row in results]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying table '{table_name}': {e}")
