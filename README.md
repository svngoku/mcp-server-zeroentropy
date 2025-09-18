# ZeroEntropy MCP Server

A comprehensive Model Context Protocol (MCP) server for the ZeroEntropy SDK, enabling AI assistants to perform advanced document retrieval, search, and management operations.

This server provides full access to ZeroEntropy's powerful document search and retrieval capabilities through the MCP protocol, making it easy to integrate with AI assistants like Claude Desktop.

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
- **Parameters:**
  - `collection_name`: str - Name of the collection to create
- **Returns:** Success status message

#### `list_collections`
Get a list of all available collections.
- **Returns:** List of collection names

#### `delete_collection`
Delete a collection and all its documents.
- **Parameters:**
  - `collection_name`: str - Name of the collection to delete
- **Returns:** Success status message

#### `get_collection_status`
Get detailed status information for a collection.
- **Parameters:**
  - `collection_name`: str - Collection name
- **Returns:** Document counts and indexing status

### Document Management

#### `add_document`
Add a document to a collection with flexible content types.
- **Parameters:**
  - `collection_name`: str - Target collection name
  - `path`: str - Document path/identifier
  - `content_type`: str - Type: 'text', 'auto', or 'text-pages' (default: 'text')
  - `content`: str - Document content or base64 data
  - `metadata`: Optional[Dict] - Optional metadata
- **Returns:** Success status message

#### `get_document_info`
Get information about a specific document.
- **Parameters:**
  - `collection_name`: str - Name of the collection
  - `path`: str - Document path/identifier
  - `include_content`: bool - Whether to include document content (default: False)
- **Returns:** Document details including ID, metadata, index status, and content

#### `list_documents`
List documents in a collection with pagination support.
- **Parameters:**
  - `collection_name`: str - Name of the collection
  - `limit`: int - Maximum number to return (max 1024, default: 100)
  - `path_gt`: Optional[str] - Path to start from for pagination
- **Returns:** List of documents with metadata and pagination info

#### `update_document_metadata`
Update metadata for an existing document.
- **Parameters:**
  - `collection_name`: str - Name of the collection
  - `path`: str - Document path/identifier
  - `metadata`: Dict - New metadata to set
- **Returns:** Update status with old and new document IDs

#### `delete_document`
Delete a document from a collection.
- **Parameters:**
  - `collection_name`: str - Name of the collection
  - `path`: str - Document path/identifier to delete
- **Returns:** Success status message

### Search Operations

#### `search_collection`
Search a collection using ZeroEntropy's powerful snippet search.
- **Parameters:**
  - `collection_name`: str - The name of the ZeroEntropy collection
  - `query`: str - The search query
  - `k`: int - Number of results (default: 21, max: 128)
  - `reranker`: str - Reranker model (default: 'zerank-1')
  - `filter`: Optional[Dict] - Metadata filter query
- **Returns:** Top snippets with scores and metadata

#### `search_documents`
Search for the most relevant documents in a collection.
- **Parameters:**
  - `collection_name`: str - Collection to search
  - `query`: str - Search query
  - `k`: int - Number of results (default: 5, max: 2048)
  - `include_metadata`: bool - Include document metadata (default: True)
  - `filter`: Optional[Dict] - Metadata filter query
- **Returns:** Ranked documents with relevance scores

#### `search_pages`
Search for the most relevant pages across documents.
- **Parameters:**
  - `collection_name`: str - Collection to search
  - `query`: str - Search query
  - `k`: int - Number of results (default: 5, max: 1024)
  - `include_content`: bool - Include page content (default: True)
  - `latency_mode`: str - "low", "medium", or "high" (default: "low")
  - `filter`: Optional[Dict] - Metadata filter
- **Returns:** Relevant pages with scores and content

#### `filter_documents_by_metadata`
Filter documents based on metadata criteria using ZeroEntropy query language.
- **Parameters:**
  - `collection_name`: str - Collection to search
  - `query`: str - Search query
  - `author`: Optional[str] - Filter by author
  - `language`: Optional[str] - Filter by language
  - `tags`: Optional[List[str]] - Filter by tags
  - `timestamp_after`: Optional[str] - Filter by timestamp after (ISO format)
  - `timestamp_before`: Optional[str] - Filter by timestamp before (ISO format)
  - `k`: int - Number of results (default: 5)
- **Returns:** Filtered search results with automatic query construction

#### `advanced_metadata_filter`
Apply advanced metadata filtering using custom ZeroEntropy query language.
- **Parameters:**
  - `collection_name`: str - Collection to search
  - `query`: str - Search query
  - `filter_query`: Dict - Custom metadata filter using ZeroEntropy query language
  - `k`: int - Number of results (default: 5)
  - `search_type`: str - "snippets", "documents", or "pages" (default: "snippets")
- **Returns:** Advanced filtered results
- **Example filters:**
  - `{"language": {"$eq": "en"}}`
  - `{"timestamp": {"$gt": "2024-01-01T00:00:00"}}`
  - `{"list:tags": {"$in": ["tech", "ai"]}}`
  - `{"$and": [{"author": {"$eq": "John"}}, {"language": {"$eq": "en"}}]}`

### Utilities

#### `get_status` / `get_collection_status`
Get the status of the ZeroEntropy system or a specific collection.
- **Parameters:**
  - `collection_name`: Optional[str] - Optional collection name for specific status
- **Returns:** Document counts, indexing status, parsing status, and failed documents

#### `parse_document`
Parse a document (PDF, etc.) without indexing it.
- **Parameters:**
  - `base64_data`: str - Base64-encoded document data
- **Returns:** Extracted page contents and page count

#### `rerank_documents`
Rerank a list of documents based on relevance to a query.
- **Parameters:**
  - `query`: str - Query to rank against
  - `documents`: List[str] - List of document texts
  - `model`: str - Reranking model (default: "zerank-1-small")
  - `top_n`: Optional[int] - Number of top results
- **Returns:** Reranked documents with relevance scores

### Resources

#### `search://{query}`
Get search results for a specific query.
- **URI Pattern:** `search://your-search-query`
- **Returns:** Search results from the default collection

#### `collection://{collection_name}/status`
Get status information for a specific collection.
- **URI Pattern:** `collection://my-collection/status`
- **Returns:** Collection status including document counts

#### `collections://list`
List all available collections.
- **URI Pattern:** `collections://list`
- **Returns:** List of all collection names with count

### Prompts

#### `search_prompt`
Generate a search prompt for exploring a topic.
- **Parameters:**
  - `topic`: str - The topic to search for
  - `focus`: str - Specific focus area (default: "general")
- **Returns:** Formatted search prompt

#### `filter_search_prompt`
Generate a filtered search prompt with metadata constraints.
- **Parameters:**
  - `query`: str - The search query
  - `author`: Optional[str] - Filter by author
  - `language`: Optional[str] - Filter by language
  - `date_range`: Optional[str] - Date range for filtering
- **Returns:** Formatted filtered search prompt

#### `analyze_collection_prompt`
Generate a prompt for analyzing a collection's contents.
- **Parameters:**
  - `collection_name`: str - Name of the collection to analyze
- **Returns:** Comprehensive analysis prompt

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
