import os
import uvicorn
import asyncio
import traceback
from fastapi import FastAPI, Header, Body, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from scraping_ddkg import ddkg_search
from typing import List
from loguru import logger
from time import process_time
from web_loader import crawler, CrawlerReponse
import redis
from datetime import timedelta

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
            except:
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
            logger.error(f"Unhandled Exception Status Code: 500")
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

# Define the Redis connection parameters
REDIS_HOST = os.getenv("redis_host")
REDIS_PORT = os.getenv("redis_port")
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
async def external_search(
    search_request: SearchRequest = Body(...),
    authorization: str | None = Header(None),
):
    logger.info(f"Searching for {search_request.query}")
    results_list = ddkg_search(
        f"https://duckduckgo.com/?t=h_&q={search_request.query}&ia=web",
        search_request.count,
    )

    logger.info("Results from Duckduckgo:")
    logger.info(results_list)
    return results_list


@app.post("/loader")
async def loader_web_page(
    req_loader: LoaderRequest = Body(...),
    authorization: str | None = Header(None),
):
    # req_loader = LoaderRequest.model_validate(req_loader)

    loader_res = []
    later_run = []
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
            later_run.append(crawler(url=url))

    results: CrawlerReponse = await asyncio.gather(*later_run)
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
