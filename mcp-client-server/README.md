# MCP Client with API and Cohere Integration

A Model Context Protocol (MCP) client application that exposes a REST API for document processing. The system uses MCP tools powered by Cohere AI to provide recipient suggestions and document improvements.

## Architecture

```
┌─────────────────┐
│   REST API      │  FastAPI application
│   (api.py)      │  Endpoints: /api/recipients, /api/improve
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Client    │  Connects to MCP server
│ (mcp_client.py) │  Invokes tools
└────────┬────────┘
         │ stdio
         ▼
┌─────────────────┐
│   MCP Server    │  Hosts tools
│ (mcp_server.py) │  - get_recipient_suggestion
└────────┬────────┘  - improve_document
         │
         ▼
┌─────────────────┐
│   Cohere API    │  AI-powered processing
└─────────────────┘
```

## Features

- **REST API**: FastAPI-based HTTP endpoints with automatic OpenAPI documentation
- **MCP Tools**: Two document processing tools using the Model Context Protocol
- **AI-Powered**: Cohere's LLM for intelligent document analysis and improvement
- **Async**: Fully asynchronous implementation for high performance

## Tools

### 1. get_recipient_suggestion
Analyzes document content and suggests appropriate recipients from a predefined list.

**Recipients**: Legal, HR, PR, Finance, Engineering, Executive, All Employees

**Use cases**:
- Routing internal communications
- Document distribution workflow
- Compliance and approval routing

### 2. improve_document
Improves document quality by fixing grammar, enhancing clarity, and improving structure.

**Improvements**:
- Grammar and spelling corrections
- Sentence structure enhancement
- Professional tone adjustment
- Readability improvements

## Installation

### Prerequisites
- Python 3.10 or higher
- Cohere API key ([Get one here](https://dashboard.cohere.com/api-keys))

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd /Users/amiramcto/Documents/mcp-client-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Cohere API key
   ```

   Required variables:
   - `COHERE_API_KEY`: Your Cohere API key

## Usage

### Starting the API Server

```bash
python api.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### 1. Get Recipient Suggestions

```bash
curl -X POST http://localhost:8000/api/recipients \
  -H "Content-Type: application/json" \
  -d '{
    "content": "We need to review the new employee benefits package to ensure compliance with labor laws."
  }'
```

**Response**:
```json
{
  "recipients": ["Legal", "HR"],
  "reasoning": "This document requires legal review for compliance and HR involvement for benefits administration.",
  "error": null
}
```

#### 2. Improve Document

```bash
curl -X POST http://localhost:8000/api/improve \
  -H "Content-Type: application/json" \
  -d '{
    "content": "this document need to be more better and clear for everyone to understand it good"
  }'
```

**Response**:
```json
{
  "improved_content": "This document needs to be clearer and more accessible for everyone to understand effectively.",
  "changes_summary": "Fixed grammar errors, improved sentence structure, and enhanced professional tone.",
  "error": null
}
```

#### 3. Health Check

```bash
curl http://localhost:8000/health
```

#### 4. List Available Tools

```bash
curl http://localhost:8000/tools
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Using the MCP Client Directly

You can also use the MCP client directly in your Python code:

```python
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient()
    
    async with client.connect():
        # Get recipient suggestions
        result = await client.get_recipient_suggestion(
            "Document content here..."
        )
        print(result)
        
        # Improve document
        result = await client.improve_document(
            "Document to improve..."
        )
        print(result)

asyncio.run(main())
```

## Project Structure

```
mcp-client-server/
├── api.py                 # FastAPI REST API
├── mcp_client.py          # MCP client implementation
├── mcp_server.py          # MCP server with tools
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `COHERE_API_KEY` | Cohere API key | Required |
| `COHERE_MODEL` | Cohere model to use | `command-r-plus` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |

## Development

### Running the MCP Server Standalone

```bash
python mcp_server.py
```

### Testing the MCP Client

```bash
python mcp_client.py
```

This will run example tests of both tools.

## Error Handling

All endpoints include comprehensive error handling:

- **400 Bad Request**: Invalid input
- **500 Internal Server Error**: Server or AI processing errors

Errors are returned in JSON format:
```json
{
  "detail": "Error description",
  "error": "Detailed error message"
}
```

## Logging

All components use Python's logging module. Logs include:
- API requests and responses
- MCP client connection status
- Tool invocations
- Errors and exceptions

## Troubleshooting

### "COHERE_API_KEY environment variable is not set"
- Create `.env` file from `.env.example`
- Add your Cohere API key

### "Client not connected"
- Ensure MCP server is accessible
- Check that `mcp_server.py` is in the same directory

### Connection errors
- Verify Cohere API key is valid
- Check network connectivity
- Review logs for detailed error messages

## License

This project is provided as-is for demonstration purposes.

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Cohere API Documentation](https://docs.cohere.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
