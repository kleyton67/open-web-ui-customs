from celery import Celery
import redis

# Configure Celery
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def process_search_query(query, count):
    from scraping_ddkg import Searcher
    searcher = Searcher()
    results_list = searcher.ddkg_search(
        f"https://duckduckgo.com/?t=h_&q={query}&ia=web",
        count,
    )
    return results_list