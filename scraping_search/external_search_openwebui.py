import uvicorn
from fastapi import FastAPI, Header, Body, HTTPException
from pydantic import BaseModel
from scraping_ddkg import ddkg_search
from typing import List
from loguru import logger
# from duckduckgo_search import DDGS

EXPECTED_BEARER_TOKEN = "your_secret_token_here"

app = FastAPI()


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
    
    results_list = ddkg_search(f'https://duckduckgo.com/?t=h_&q={search_request.query}&ia=web', search_request.count)

    logger.info("Results from Duckduckgo:")
    logger.info(results_list)
    return results_list


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)