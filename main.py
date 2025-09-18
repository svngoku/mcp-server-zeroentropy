"""
ZeroEntropy MCP Server
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import mcp.types as types
import asyncio
import base64
import os
from typing import Optional, Dict, Any, List
from zeroentropy import AsyncZeroEntropy, ConflictError
from dotenv import load_dotenv

load_dotenv()

# Initialize async ZeroEntropy client
client = AsyncZeroEntropy(
    api_key=os.getenv("ZEROENTROPY_API_KEY")
)

mcp = FastMCP("ZeroEntropy Server", port=3000, stateless_http=True, debug=True)


@mcp.tool(
    title="Search Collection",
    description="Search a collection using ZeroEntropy",
)
async def search_collection(
    collection_name: str = Field(description="The name of the ZeroEntropy collection"),
    query: str = Field(description="The search query"),
    k: int = Field(description="The number of top results to return", default=21),
    reranker: str = Field(description="The reranker to use", default="zerank-1"),
    filter: Optional[Dict[str, Any]] = Field(description="Metadata filter query", default=None)
) -> str:
    """
    Performs a search on the specified collection.

    Args:
        collection_name (str): The name of the ZeroEntropy collection.
        query (str): The search query.
        k (int, optional): The number of top results to return. Defaults to 21.
        reranker (str, optional): The reranker to use. Defaults to 'zerank-1'.
        filter (dict, optional): Metadata filter query using ZeroEntropy query language.

    Returns:
        str: A string representation of search results.
    """
    try:
        response = await client.queries.top_snippets(
            collection_name=collection_name,
            query=query,
            k=k,
            precise_responses=True,
            reranker=reranker,
            filter=filter
        )
        return str(response.results)
    except Exception as e:
        return f"Error performing search: {str(e)}"


@mcp.tool(
    title="Create Collection",
    description="Create a new collection for document storage",
)
async def create_collection(collection_name: str) -> str:
    """Create a new collection for document storage"""
    try:
        await client.collections.add(collection_name=collection_name)
        return f"Collection '{collection_name}' created successfully"
    except ConflictError:
        return f"Collection '{collection_name}' already exists"
    except Exception as e:
        return f"Error creating collection: {str(e)}"


@mcp.tool(
    title="Add Document",
    description="Add a document to a collection",
)
async def add_document(
    collection_name: str = Field(description="Target collection name"),
    path: str = Field(description="Document path/identifier"),
    content_type: str = Field(description="Type: 'text', 'auto', or 'text-pages'", default="text"),
    content: str = Field(description="Document content or base64 data"),
    metadata: Optional[Dict[str, str]] = Field(description="Optional metadata", default=None)
) -> str:
    """Add a document to a collection"""
    try:
        content_dict = {"type": content_type}
        if content_type == "text-pages":
            content_dict["pages"] = content.split("\n---\n")
        elif content_type == "auto":
            content_dict["base64_data"] = content
        else:
            content_dict["text"] = content
            
        await client.documents.add(
            collection_name=collection_name,
            path=path,
            content=content_dict,
            metadata=metadata or {}
        )
        return f"Document '{path}' added to collection '{collection_name}'"
    except ConflictError:
        return f"Document '{path}' already exists in collection '{collection_name}'"
    except Exception as e:
        return f"Error adding document: {str(e)}"


@mcp.tool(
    title="List Collections",
    description="List all available collections",
)
async def list_collections() -> str:
    """List all available collections"""
    try:
        response = await client.collections.get_list()
        return str(response.collection_names)
    except Exception as e:
        return f"Error listing collections: {str(e)}"


@mcp.tool(
    title="Get Collection Status",
    description="Get status information for a collection",
)
async def get_collection_status(collection_name: str = Field(description="Collection name")) -> str:
    """Get status information for a collection"""
    try:
        response = await client.status.get(collection_name=collection_name)
        return str(response)
    except Exception as e:
        return f"Error getting status: {str(e)}"


@mcp.tool(
    title="Search Documents",
    description="Search for documents in a collection",
)
async def search_documents(
    collection_name: str = Field(description="Collection to search"),
    query: str = Field(description="Search query"),
    k: int = Field(description="Number of results", default=5),
    include_metadata: bool = Field(description="Include metadata", default=True),
    filter: Optional[Dict[str, Any]] = Field(description="Metadata filter query", default=None)
) -> str:
    """
        Search for documents in a collection.
        Parameters:
        collection_name: str = Field(description="Collection to search"),
        query: str = Field(description="Search query"),
        k: int = Field(description="Number of results", default=5),
        include_metadata: bool = Field(description="Include metadata", default=True),
        filter: dict = Field(description="Metadata filter query using ZeroEntropy query language", default=None)
    """
    try:
        response = await client.queries.top_documents(
            collection_name=collection_name,
            query=query,
            k=k,
            include_metadata=include_metadata,
            filter=filter
        )
        return str(response.results)
    except Exception as e:
        return f"Error searching documents: {str(e)}"


@mcp.tool(
    title="Filter Documents by Metadata",
    description="Filter documents based on metadata criteria using ZeroEntropy query language",
)
async def filter_documents_by_metadata(
    collection_name: str = Field(description="Collection to search"),
    query: str = Field(description="Search query"),
    author: Optional[str] = Field(description="Filter by author", default=None),
    language: Optional[str] = Field(description="Filter by language", default=None),
    tags: Optional[list[str]] = Field(description="Filter by tags (list)", default=None),
    timestamp_after: Optional[str] = Field(description="Filter by timestamp after (ISO format)", default=None),
    timestamp_before: Optional[str] = Field(description="Filter by timestamp before (ISO format)", default=None),
    k: int = Field(description="Number of results", default=5)
) -> str:
    """
    Filter documents using common metadata criteria.
    Builds a metadata filter query automatically based on provided parameters.
    """
    try:
        filter_conditions = []
        
        # Add author filter
        if author:
            filter_conditions.append({
                "author": {"$eq": author}
            })
        
        # Add language filter
        if language:
            filter_conditions.append({
                "language": {"$eq": language}
            })
        
        # Add tags filter (list intersection)
        if tags:
            filter_conditions.append({
                "list:tags": {"$in": tags}
            })
        
        # Add timestamp filters
        if timestamp_after:
            filter_conditions.append({
                "timestamp": {"$gt": timestamp_after}
            })
        
        if timestamp_before:
            filter_conditions.append({
                "timestamp": {"$lt": timestamp_before}
            })
        
        # Build final filter
        filter_query = None
        if filter_conditions:
            if len(filter_conditions) == 1:
                filter_query = filter_conditions[0]
            else:
                filter_query = {"$and": filter_conditions}
        
        response = await client.queries.top_snippets(
            collection_name=collection_name,
            query=query,
            k=k,
            precise_responses=True,
            filter=filter_query
        )
        return str(response.results)
    except Exception as e:
        return f"Error filtering documents: {str(e)}"


@mcp.tool(
    title="Advanced Metadata Filter",
    description="Apply advanced metadata filtering using custom ZeroEntropy query language",
)
async def advanced_metadata_filter(
    collection_name: str = Field(description="Collection to search"),
    query: str = Field(description="Search query"),
    filter_query: Dict[str, Any] = Field(description="Custom metadata filter using ZeroEntropy query language"),
    k: int = Field(description="Number of results", default=5),
    search_type: str = Field(description="Search type: 'snippets', 'documents', or 'pages'", default="snippets")
) -> str:
    """
    Apply advanced metadata filtering using custom ZeroEntropy query language.
    
    Example filter queries:
    - {"language": {"$eq": "en"}}
    - {"timestamp": {"$gt": "2024-01-01T00:00:00"}}
    - {"list:tags": {"$in": ["tech", "ai"]}}
    - {"$and": [{"author": {"$eq": "John"}}, {"language": {"$eq": "en"}}]}
    - {"$or": [{"language": {"$eq": "en"}}, {"language": {"$eq": "es"}}]}
    """
    try:
        if search_type == "documents":
            response = await client.queries.top_documents(
                collection_name=collection_name,
                query=query,
                k=min(k, 2048),  # Enforce max limit
                include_metadata=True,
                filter=filter_query
            )
        elif search_type == "pages":
            response = await client.queries.top_pages(
                collection_name=collection_name,
                query=query,
                k=min(k, 1024),  # Enforce max limit
                include_content=True,
                latency_mode="low",
                filter=filter_query
            )
        else:
            response = await client.queries.top_snippets(
                collection_name=collection_name,
                query=query,
                k=min(k, 128),  # Enforce max limit
                precise_responses=True,
                filter=filter_query
            )
        return str(response.results)
    except Exception as e:
        return f"Error applying advanced filter: {str(e)}"


@mcp.tool(
    title="Delete Collection",
    description="Delete a collection and all its documents",
)
async def delete_collection(collection_name: str = Field(description="Collection name to delete")) -> str:
    """Delete a collection and all its documents"""
    try:
        await client.collections.delete(collection_name=collection_name)
        return f"Collection '{collection_name}' deleted successfully"
    except Exception as e:
        return f"Error deleting collection: {str(e)}"


@mcp.tool(
    title="Get Document Info",
    description="Get information about a specific document",
)
async def get_document_info(
    collection_name: str = Field(description="Collection name"),
    path: str = Field(description="Document path/identifier"),
    include_content: bool = Field(description="Include document content", default=False)
) -> str:
    """Get information about a specific document"""
    try:
        doc = await client.documents.get_info(
            collection_name=collection_name,
            path=path,
            include_content=include_content
        )
        return str({
            "id": doc.id,
            "path": doc.path,
            "metadata": doc.metadata,
            "index_status": doc.index_status,
            "num_pages": doc.num_pages,
            "content": doc.content if include_content else None
        })
    except Exception as e:
        return f"Error getting document info: {str(e)}"


@mcp.tool(
    title="List Documents",
    description="List documents in a collection with pagination",
)
async def list_documents(
    collection_name: str = Field(description="Collection name"),
    limit: int = Field(description="Maximum number to return (max 1024)", default=100),
    path_gt: Optional[str] = Field(description="Path to start from (for pagination)", default=None)
) -> str:
    """List documents in a collection with pagination"""
    try:
        response = await client.documents.get_info_list(
            collection_name=collection_name,
            limit=min(limit, 1024),
            path_gt=path_gt
        )
        
        documents = []
        docs_list = response.documents if hasattr(response, 'documents') else []
        for doc in docs_list:
            documents.append({
                "id": doc.id,
                "path": doc.path,
                "metadata": doc.metadata,
                "index_status": doc.index_status,
                "num_pages": doc.num_pages
            })
        
        return str({
            "documents": documents,
            "count": len(documents),
            "next_page": response.path_gt if hasattr(response, 'path_gt') else None
        })
    except Exception as e:
        return f"Error listing documents: {str(e)}"


@mcp.tool(
    title="Update Document Metadata",
    description="Update metadata for an existing document",
)
async def update_document_metadata(
    collection_name: str = Field(description="Collection name"),
    path: str = Field(description="Document path/identifier"),
    metadata: Dict[str, Any] = Field(description="New metadata to set")
) -> str:
    """Update metadata for an existing document"""
    try:
        result = await client.documents.update(
            collection_name=collection_name,
            path=path,
            metadata=metadata
        )
        return str({
            "status": "success",
            "previous_id": result.previous_id,
            "new_id": result.new_id
        })
    except Exception as e:
        return f"Error updating metadata: {str(e)}"


@mcp.tool(
    title="Delete Document",
    description="Delete a document from a collection",
)
async def delete_document(
    collection_name: str = Field(description="Collection name"),
    path: str = Field(description="Document path/identifier to delete")
) -> str:
    """Delete a document from a collection"""
    try:
        await client.documents.delete(
            collection_name=collection_name,
            path=path
        )
        return f"Document '{path}' deleted from collection '{collection_name}'"
    except Exception as e:
        return f"Error deleting document: {str(e)}"


@mcp.tool(
    title="Search Pages",
    description="Search for relevant pages across documents",
)
async def search_pages(
    collection_name: str = Field(description="Collection to search"),
    query: str = Field(description="Search query"),
    k: int = Field(description="Number of results (max 1024)", default=5),
    include_content: bool = Field(description="Include page content", default=True),
    latency_mode: str = Field(description="Latency mode: 'low', 'medium', or 'high'", default="low"),
    filter: Optional[Dict[str, Any]] = Field(description="Metadata filter", default=None)
) -> str:
    """Search for relevant pages across documents"""
    try:
        response = await client.queries.top_pages(
            collection_name=collection_name,
            query=query,
            k=min(k, 1024),
            filter=filter,
            include_content=include_content,
            latency_mode=latency_mode
        )
        
        pages = []
        for page in response.results:
            pages.append({
                "path": page.path,
                "page_index": page.page_index,
                "score": page.score,
                "content": page.content if include_content else None
            })
        
        return str({"pages": pages, "count": len(pages)})
    except Exception as e:
        return f"Error searching pages: {str(e)}"


@mcp.tool(
    title="Parse Document",
    description="Parse a document (PDF, etc.) without indexing it",
)
async def parse_document(
    base64_data: str = Field(description="Base64-encoded document data")
) -> str:
    """Parse a document without indexing it"""
    try:
        result = await client.parsers.parse_document(base64_data=base64_data)
        return str({
            "pages": result.pages,
            "num_pages": len(result.pages)
        })
    except Exception as e:
        return f"Error parsing document: {str(e)}"


@mcp.tool(
    title="Rerank Documents",
    description="Rerank documents based on relevance to a query",
)
async def rerank_documents(
    query: str = Field(description="Query to rank against"),
    documents: List[str] = Field(description="List of document texts"),
    model: str = Field(description="Reranking model", default="zerank-1-small"),
    top_n: Optional[int] = Field(description="Number of top results", default=None)
) -> str:
    """Rerank documents based on relevance"""
    try:
        result = await client.models.rerank(
            query=query,
            documents=documents,
            model=model,
            top_n=top_n if top_n else len(documents)
        )
        
        reranked = []
        for item in result.results:
            reranked.append({
                "index": item.index,
                "relevance_score": item.relevance_score,
                "document": documents[item.index] if item.index < len(documents) else None
            })
        
        return str({"reranked": reranked})
    except Exception as e:
        return f"Error reranking: {str(e)}"


@mcp.resource(
    uri="search://{query}",
    description="Get search results for a query",
    name="Search Results",
)
async def get_search_results(query: str) -> str:
    try:
        response = await client.queries.top_snippets(
            collection_name="african_history_book",
            query=query,
            k=5,
            precise_responses=True,
            reranker="zerank-1"
        )
        return str(response.results)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource(
    uri="collection://{collection_name}/status",
    description="Get status for a specific collection",
    name="Collection Status",
)
async def collection_status_resource(collection_name: str) -> str:
    """Get status information for a specific collection"""
    try:
        status = await client.status.get(collection_name=collection_name)
        return str({
            "collection": collection_name,
            "num_documents": status.num_documents,
            "num_indexed": status.num_indexed_documents,
            "num_indexing": status.num_indexing_documents,
            "num_parsing": status.num_parsing_documents,
            "num_failed": status.num_failed_documents
        })
    except Exception as e:
        return f"Error getting status: {str(e)}"


@mcp.resource(
    uri="collections://list",
    description="List all available collections",
    name="Collections List",
)
async def collections_list_resource() -> str:
    """Get a list of all available collections"""
    try:
        response = await client.collections.get_list()
        collections = response.collection_names if hasattr(response, 'collection_names') else []
        return str({
            "collections": collections,
            "count": len(collections)
        })
    except Exception as e:
        return f"Error listing collections: {str(e)}"


@mcp.prompt("")
async def search_prompt(
    topic: str = Field(description="The topic to search for"),
    focus: str = Field(description="Specific focus area", default="general"),
) -> str:
    """Generate a search prompt for African history"""
    return f"Search for information about {topic} in African history, focusing on {focus} aspects."


@mcp.prompt("")
async def filter_search_prompt(
    query: str = Field(description="The search query"),
    author: Optional[str] = Field(description="Filter by author", default=None),
    language: Optional[str] = Field(description="Filter by language", default=None),
    date_range: Optional[str] = Field(description="Date range for filtering", default=None)
) -> str:
    """Generate a filtered search prompt with metadata constraints"""
    filters = []
    if author:
        filters.append(f"author: {author}")
    if language:
        filters.append(f"language: {language}")
    if date_range:
        filters.append(f"date range: {date_range}")
    
    filter_str = f" with filters: {', '.join(filters)}" if filters else ""
    
    return f"""Search for: {query}{filter_str}

Please perform a filtered search and:
1. Apply the specified metadata filters
2. Rank results by relevance
3. Include document metadata in the response
4. Highlight the matching criteria"""


@mcp.prompt("")
async def analyze_collection_prompt(
    collection_name: str = Field(description="Name of the collection to analyze")
) -> str:
    """Generate a prompt for analyzing a collection's contents"""
    return f"""Please analyze the '{collection_name}' collection:

1. Get the collection status to understand document counts
2. List a sample of documents to understand the content types
3. Identify common metadata patterns
4. Suggest optimal search strategies for this collection
5. Recommend any maintenance or optimization actions

Provide a comprehensive overview of the collection's structure and contents."""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")