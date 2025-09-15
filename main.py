"""
ZeroEntropy MCP Server
"""
import asyncio
import base64
import os
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from zeroentropy import AsyncZeroEntropy, ConflictError, HTTPStatusError
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
        else:
            content_dict[content_type if content_type == "text" else "base64_data"] = content
            
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
    search_type: str = Field(description="Search type: 'snippets' or 'documents'", default="snippets")
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
                k=k,
                include_metadata=True,
                filter=filter_query
            )
        else:
            response = await client.queries.top_snippets(
                collection_name=collection_name,
                query=query,
                k=k,
                precise_responses=True,
                filter=filter_query
            )
        return str(response.results)
    except Exception as e:
        return f"Error applying advanced filter: {str(e)}"




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

@mcp.prompt("")
async def search_prompt(
    topic: str = Field(description="The topic to search for"),
    focus: str = Field(description="Specific focus area", default="general"),
) -> str:
    """Generate a search prompt for African history"""
    return f"Search for information about {topic} in African history, focusing on {focus} aspects."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")