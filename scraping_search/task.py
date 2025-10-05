from scraping_ddkg import Searcher


def process_search_query(query, count):
    searcher = Searcher()
    results_list = searcher.ddkg_search(
        f"https://duckduckgo.com/?t=h_&q={query}&ia=web",
        count,
    )
    return results_list