import os
from concurrent.futures import ThreadPoolExecutor
import uvicorn
import traceback
from fastapi import FastAPI, Header, Body, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List
from loguru import logger
from time import process_time
from web_loader import crawler, CrawlerResponse, process_url
import redis
from task import process_search_query
from datetime import timedelta
from queue import Queue

# from duckduckgo_search import DDGS

EXPECTED_BEARER_TOKEN = "your_secret_token_here"

app = FastAPI()


def reap_children():
    """Function to avoid zumbie process from librewolf browser
    """
    try:
        pid = True
        while pid:
            pid = os.waitpid(-1, os.WNOHANG)

            #Wonka's Solution to avoid infinite loop cause pid value -> (0, 0)
            try:
                if pid[0] == 0:
                    pid = False
            except Exception:
                pass
            #---- ----

    except ChildProcessError:
        pass

# Middleware to log requests and responses with processing time
class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = process_time()  # Start timer to measure processing time

        try:
            response = await call_next(
                request
            )  # Call the next middleware or route handler
        except HTTPException as e:
            logger.error(traceback.print_exc())
            logger.error(f"Request Method: {request.method}")
            logger.error(f"Request Path: {request.url.path}")
            logger.error(f"HTTP Exception Status Code: {e.status_code}")
            logger.error(f"Exception Details: {str(e)}")
            return Response(content=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error(f"Request Method: {request.method}")
            logger.error(f"Request Path: {request.url.path}")
            logger.error("Unhandled Exception Status Code: 500")
            logger.error(f"Exception Details: {str(e)}")
            return Response(content="Internal Server Error", status_code=500)
        else:
            process_time_diff = process_time() - start_time  # Calculate processing time
            logger.info(f"Request Method: {request.method}")
            logger.info(f"Request Path: {request.url.path}")
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Processing Time: {process_time_diff:.4f} seconds")

        reap_children()

        return response


# Import necessary libraries

# Documentation: This file implements a FastAPI service for external search and web content loading. It includes:
# - Search endpoint /search for query processing
# - Loader endpoint /loader for URL content fetching
# - Redis caching for URL results
# - Request logging middleware

# Define the Redis connection parameters
REDIS_HOST = os.getenv("redis_host", "10.28.33.120")
REDIS_PORT = int(os.getenv("redis_port", "30479"))
REDIS_DB = 0

# Create a Redis client
client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Mount the middleware to the FastAPI app
app.add_middleware(LoggingMiddleware)


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


@app.post("/search")
def external_search(
    search_request: SearchRequest = Body(...),
    authorization: str | None = Header(None),
):
    logger.info(f"Searching for {search_request.query}")

    results_list = process_search_query(search_request.query, search_request.count)

    logger.info("Results from Duckduckgo:")
    logger.info(results_list)
    return results_list


@app.post("/loader")
def loader_web_page(
    req_loader: LoaderRequest = Body(...),
    authorization: str | None = Header(None),
):
    req_loader = LoaderRequest.model_validate(req_loader)

    loader_res = []
    results_queue = Queue()
    results: List[CrawlerResponse] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks to the thread pool
        for url in req_loader.urls:
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
                            title=markdown_crawler[:25],
                            source=url,
                            description=markdown_crawler[:100],
                        ),
                    )
                )
            else:
                executor.submit(process_url, url, results_queue)

    # Collect results from the queue
    while not results_queue.empty():
        url, result = results_queue.get()
        if isinstance(result, Exception):
            loader_res.append(crawler(url=url))  # Retry on exception
        else:
            loader_res.append(
                LoaderResult(
                    page_content=result,
                    metadata=MetadataLoader(
                        url=url,
                        title=result[:25],
                        source=url,
                        description=result[:100],
                    ),
                )
            )

    [
        loader_res.append(
            LoaderResult(
                page_content=crawler_rep.content,
                metadata=MetadataLoader(
                    url=crawler_rep.url,
                    title=crawler_rep.content[:25],
                    source=crawler_rep.url,
                    description=crawler_rep.content[:100],
                ),
            )
        )
        for crawler_rep in results
        if not isinstance(crawler_rep, Exception)
    ]
    # Data to be stored in Redis with an expiration of one week (7 days)
    expiration_time = timedelta(weeks=1)
    [
        client.setex(
            crawler_res.metadata.url,
            int(expiration_time.total_seconds()),
            crawler_res.page_content,
        )
        for crawler_res in loader_res
    ]

    return loader_res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
