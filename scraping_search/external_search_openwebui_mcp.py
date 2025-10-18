import os
from fastmcp import FastMCP, Context
from fastmcp.utilities.logging import configure_logging
from pydantic import BaseModel
from typing import List
from loguru import logger
from task import process_search_query
import redis

# fastmcp run server.py --host "0.0.0.0" --port=8889

configure_logging()

# Redis setup
REDIS_HOST = os.getenv("redis_host")
REDIS_PORT = int(os.getenv("redis_port", "6379"))
REDIS_DB = 0
client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# FastMCP server setup
mcp = FastMCP(name="SearchServer", debug=True)

# Define models
class SearchRequest(BaseModel):
    query: str
    count: int

class LoaderRequest(BaseModel):
    urls: List[str]

class SearchResult(BaseModel):
    link: str
    title: str | None
    snippet: str | None 

class MetadataLoader(BaseModel):
    url: str
    title: str | None
    source: str
    description: str

class LoaderResult(BaseModel):
    page_content: str
    metadata: MetadataLoader

# Search tool
@mcp.tool(description='Perform web search using duckduckgo')
def search_web(request: SearchRequest, ctx: Context):
    """
    Perform web search using duckduckgo
    
    Args:
        request: SearchRequest object containing query parameters
        ctx: Context object for tool execution
        
    Returns:
        List of search results from duckduckgo
    """
    logger.info(f"Searching for {request.query}")
    results_list = process_search_query(request.query, request.count)
    return results_list

# Loader tool
@mcp.tool(description=" Load content from list of URLs")
def url_loader(request: LoaderRequest, ctx: Context):
    """
    Load content from list of URLs
    
    Args:
        request: LoaderRequest object containing URL list
        ctx: Context object for tool execution
        
    Returns:
        List of loaded content from specified URLs
    """
    loader_res = []
    for url in request.urls:
        logger.info(f"Crawling {url}")
        cache = client.getex(name=url)
        if cache:
            markdown_crawler = cache
            logger.info("Results from cache:")
            logger.info(markdown_crawler)
            loader_res.append(
                LoaderResult(
                    page_content=markdown_crawler,
                    metadata=MetadataLoader(
                        url=url,
                        title=markdown_crawler[:20],
                        source=url,
                        description=markdown_crawler[:100]
                    )
                )
            )
    return loader_res

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8889, log_level="DEBUG")