import uvicorn
from fastapi import FastAPI, Header, Body, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from scraping_ddkg import ddkg_search
from typing import List
from loguru import logger
from time import process_time
# from duckduckgo_search import DDGS

EXPECTED_BEARER_TOKEN = "your_secret_token_here"

app = FastAPI()


# Middleware to log requests and responses with processing time
class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Response):
        start_time = process_time()  # Start timer to measure processing time

        response = await call_next(request)  # Call the next middleware or route handler

        logger.info(f"Request Method: {request.method}")
        logger.info(f"Request Path: {request.url.path}")
        logger.info(f"Response Status Code: {response.status_code}")
        process_time_diff = process_time() - start_time  # Calculate processing time
        logger.info(f"Processing Time: {process_time_diff:.4f} seconds")
        return response


# Mount the middleware to the FastAPI app
app.add_middleware(LoggingMiddleware)


class SearchRequest(BaseModel):
    query: str
    count: int


class SearchResult(BaseModel):
    link: str
    title: str | None
    snippet: str | None


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
