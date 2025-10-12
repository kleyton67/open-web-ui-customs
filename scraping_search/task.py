from scraping_ddkg import Searcher
from loguru import logger


def process_search_query(query, count):
    searcher = Searcher()
    results_list = searcher.ddkg_search(
        f"https://duckduckgo.com/?t=h_&q={query}&ia=web",
        count,
    )
    logger.info(f"Results from search: {results_list}")
    return results_list