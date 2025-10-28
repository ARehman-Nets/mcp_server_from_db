# Define project directory
$projectDir = "C:\Users\sstte\Desktop\projects\mcp_db_server"

# Navigate to project directory
Set-Location $projectDir

# Activate virtual environment
# Note: This only activates for the current PowerShell session. 
# For background processes, we'll explicitly use the venv's python.
. .\venv\Scripts\Activate.ps1

# --- Start MCP Server in the background ---
Write-Host "Starting MCP Server in the background..."
# Using python -m uvicorn to ensure it uses the venv's uvicorn
# Redirecting output to logs to keep the console clean for the chatbot
Start-Process -FilePath "python.exe" -ArgumentList "-m uvicorn main:app --reload --port 8000" -NoNewWindow -PassThru -RedirectStandardOutput "server_output.log" -RedirectStandardError "server_error.log"

# Give the server a moment to start
Write-Host "Giving server 5 seconds to start..."
Start-Sleep -Seconds 5

# --- Start Chatbot ---
Write-Host "Starting Chatbot..."
python chatbot.py

# --- Cleanup Message ---
Write-Host "Chatbot exited. The MCP Server process may still be running in the background."
Write-Host "To stop it, you might need to manually close the PowerShell window or find 'uvicorn' or 'python' processes in Task Manager and end them."
