# ZeroEntropy MCP Server

A comprehensive Model Context Protocol (MCP) server for the ZeroEntropy SDK, enabling AI assistants to perform advanced document retrieval, search, and management operations.

## Features

The ZeroEntropy MCP Server provides a complete set of tools for:

### 📚 Collection Management
- Create, list, and delete document collections
- Organize documents into logical groups

### 📄 Document Operations
- Add text documents, files (PDF, TXT, etc.), and multi-page documents
- Automatic OCR and parsing for PDFs
- Update document metadata
- Delete documents
- Batch import from CSV files

### 🔍 Advanced Search
- **Document Search**: Find relevant documents with metadata filtering
- **Page Search**: Search within specific pages of documents
- **Snippet Search**: Extract precise text snippets matching queries
- **Semantic Search**: Comprehensive multi-level search with context
- **Reranking**: Re-order results using advanced ML models

### 🛠️ Utilities
- Parse documents without indexing
- Monitor system and collection status
- Support for metadata filtering with MongoDB-style queries

## Installation

### Prerequisites

1. Python 3.8 or higher
2. ZeroEntropy API key (set as `ZEROENTROPY_API_KEY` environment variable)

### Install Dependencies

```bash
# Install required packages
pip install fastmcp zeroentropy python-dotenv

# Or use the requirements file (if available)
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project directory:

```env
# Required
ZEROENTROPY_API_KEY=your_api_key_here

# Optional MCP configuration
ZEROENTROPY_MCP_TRANSPORT=stdio  # Options: stdio, http, sse
ZEROENTROPY_MCP_PORT=8000        # Port for http/sse transports
```

## Usage

### Running the Server

#### For Claude Desktop (stdio mode)

```bash
python server.py
```

#### As HTTP Server

```bash
ZEROENTROPY_MCP_TRANSPORT=http python server.py
```

#### As SSE Server

```bash
ZEROENTROPY_MCP_TRANSPORT=sse python server.py
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zeroentropy": {
      "command": "python",
      "args": ["/path/to/mcp-server-zeroentropy/server.py"],
      "env": {
        "ZEROENTROPY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools

### Collection Management

#### `create_collection`
Create a new collection for document storage.
```python
# Parameters:
collection_name: str  # Name of the collection to create
```

#### `list_collections`
Get a list of all available collections.
```python
# Returns list of collection names
```

#### `delete_collection`
Delete a collection and all its documents.
```python
# Parameters:
collection_name: str  # Name of the collection to delete
```

### Document Management

#### `add_text_document`
Add a text document to a collection.
```python
# Parameters:
collection_name: str        # Name of the collection
path: str                  # Unique identifier/path for the document
text: str                  # Text content to add
metadata: Optional[str]    # JSON string of metadata key-value pairs
```

#### `add_file_document`
Add a file (PDF, TXT, etc.) to a collection with automatic parsing.
```python
# Parameters:
collection_name: str        # Name of the collection
file_path: str             # Path to the file to add
metadata: Optional[str]    # JSON string of metadata key-value pairs
```

#### `add_pages_document`
Add a document with multiple pages of text content.
```python
# Parameters:
collection_name: str        # Name of the collection
path: str                  # Unique identifier/path for the document
pages: List[str]           # List of page contents
metadata: Optional[str]    # JSON string of metadata key-value pairs
```

#### `get_document_info`
Get information about a specific document.
```python
# Parameters:
collection_name: str       # Name of the collection
path: str                 # Document path/identifier
include_content: bool     # Whether to include document content
```

#### `list_documents`
List documents in a collection with pagination.
```python
# Parameters:
collection_name: str           # Name of the collection
limit: int = 100              # Maximum number to return (max 1024)
path_gt: Optional[str] = None # Path to start from (for pagination)
```

#### `update_document_metadata`
Update metadata for an existing document.
```python
# Parameters:
collection_name: str  # Name of the collection
path: str            # Document path/identifier
metadata: str        # JSON string of metadata to update
```

#### `delete_document`
Delete a document from a collection.
```python
# Parameters:
collection_name: str  # Name of the collection
path: str            # Document path/identifier to delete
```

### Search Operations

#### `search_documents`
Search for the most relevant documents in a collection.
```python
# Parameters:
collection_name: str           # Collection to search
query: str                    # Search query
k: int = 5                   # Number of results (max 2048)
include_metadata: bool = False # Include document metadata
latency_mode: str = "low"     # "low", "medium", or "high"
filter_json: Optional[str]    # JSON filter for metadata
reranker: Optional[str]       # Reranker model (e.g., "zerank-1-small")
```

#### `search_pages`
Search for the most relevant pages across documents.
```python
# Parameters:
collection_name: str           # Collection to search
query: str                    # Search query
k: int = 5                   # Number of results (max 1024)
include_content: bool = False # Include page content
latency_mode: str = "low"     # "low", "medium", or "high"
filter_json: Optional[str]    # JSON filter for metadata
```

#### `search_snippets`
Search for the most relevant text snippets within documents.
```python
# Parameters:
collection_name: str                    # Collection to search
query: str                             # Search query
k: int = 5                            # Number of results (max 128)
precise_responses: bool = False        # Use precise mode
include_document_metadata: bool = False # Include document metadata
filter_json: Optional[str]             # JSON filter for metadata
reranker: Optional[str]                # Reranker model
```

#### `semantic_search_with_context`
Perform a comprehensive semantic search with context.
```python
# Parameters:
collection_name: str         # Collection to search
query: str                  # Search query
context_size: int = 3       # Results per search type
include_snippets: bool = True # Include snippet results
include_pages: bool = False  # Include page results
```

### Utilities

#### `get_status`
Get the status of the ZeroEntropy system or a specific collection.
```python
# Parameters:
collection_name: Optional[str] = None  # Optional collection name
```

#### `parse_document`
Parse a document (PDF, etc.) without indexing it.
```python
# Parameters:
base64_data: str  # Base64-encoded document data
```

#### `rerank_documents`
Rerank a list of documents based on relevance to a query.
```python
# Parameters:
query: str                   # Query to rank against
documents: List[str]         # List of document texts
model: str = "zerank-1-small" # Reranking model
top_n: Optional[int] = None  # Number of top results
```

#### `batch_add_csv_rows`
Add CSV rows as individual documents to a collection.
```python
# Parameters:
collection_name: str                 # Name of the collection
csv_file_path: str                  # Path to the CSV file
text_column: str                    # Column containing main text
metadata_columns: Optional[List[str]] # Columns to include as metadata
```

## Example Use Cases

### 1. Creating a Knowledge Base

```python
# Create a collection
create_collection("knowledge_base")

# Add documents
add_file_document(
    collection_name="knowledge_base",
    file_path="/path/to/document.pdf",
    metadata='{"category": "research", "year": "2024"}'
)

# Search for relevant information
search_snippets(
    collection_name="knowledge_base",
    query="machine learning techniques",
    k=5,
    precise_responses=True
)
```

### 2. Document Analysis Pipeline

```python
# Parse PDF without indexing
parse_document(base64_data="...")  # Returns extracted text

# Add parsed content with custom processing
add_pages_document(
    collection_name="processed_docs",
    path="analyzed_report.pdf",
    pages=["page 1 content", "page 2 content"],
    metadata='{"status": "processed"}'
)
```

### 3. Advanced Search with Filtering

```python
# Search with metadata filters
search_documents(
    collection_name="research_papers",
    query="quantum computing",
    filter_json='{"year": {"$gte": "2020"}, "category": "physics"}',
    include_metadata=True,
    reranker="zerank-1-small"
)
```

### 4. Batch Import from CSV

```python
# Import customer feedback from CSV
batch_add_csv_rows(
    collection_name="customer_feedback",
    csv_file_path="/path/to/feedback.csv",
    text_column="comment",
    metadata_columns=["customer_id", "rating", "date"]
)
```

## Metadata Filtering

The server supports MongoDB-style query operators for filtering:

- `$eq`: Equal to
- `$ne`: Not equal to
- `$gt`: Greater than
- `$gte`: Greater than or equal to
- `$lt`: Less than
- `$lte`: Less than or equal to

Example filter:
```json
{
  "category": {"$eq": "research"},
  "year": {"$gte": "2020"},
  "status": {"$ne": "archived"}
}
```

## Error Handling

All tools return a consistent response format:

```json
{
  "status": "success" | "error",
  "message": "Description of the result or error",
  "data": {}  // Tool-specific response data
}
```

## Performance Considerations

### Latency Modes
- **low**: Fastest response, good for real-time applications
- **medium**: Balanced speed and accuracy
- **high**: Best accuracy, slower response time

### Rate Limits
- Document operations: Follow ZeroEntropy API limits
- Search operations: 
  - Documents: max 2048 results
  - Pages: max 1024 results
  - Snippets: max 128 results

### Best Practices
1. Use appropriate `k` values for search operations
2. Enable `precise_responses` for critical snippet searches
3. Use metadata filtering to narrow search scope
4. Implement pagination for large result sets
5. Consider using reranking for improved relevance

## Testing with MCP Inspector

You can test your server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

The inspector will be available at http://localhost:5173

Connect to your server:
- Transport Type: stdio (or HTTP/SSE based on your configuration)
- Command: `python /path/to/server.py` (for stdio)
- URL: `http://localhost:8000` (for HTTP/SSE)

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Ensure `ZEROENTROPY_API_KEY` is set correctly
   - Check API key validity

2. **Collection Already Exists**
   - Use `list_collections` to check existing collections
   - Delete old collection if needed

3. **Document Parsing Fails**
   - Verify file format is supported
   - Check file encoding for text files
   - Ensure base64 encoding is correct for binary files

4. **Search Returns No Results**
   - Verify documents are indexed (check status)
   - Try broader search terms
   - Check metadata filters

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check the [ZeroEntropy documentation](https://docs.zeroentropy.com)
- Review the MCP server logs for detailed error messages
- Contact support with your API key and error details

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - The Model Context Protocol framework
- [ZeroEntropy SDK](https://zeroentropy.com) - Document retrieval and search API
- [Claude Desktop](https://claude.ai) - AI assistant with MCP support
