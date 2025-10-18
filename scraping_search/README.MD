# scraping_search

This directory contains two implementations for web search and content loading services:

## 1. `external_search_openwebui.py` - FastAPI Implementation
```python
scraping_search/external_search_openwebui.py
```

**Overview**  
A FastAPI service for external search and web content loading with Redis caching. Implements:
- `/search` endpoint for query processing
- `/loader` endpoint for URL content fetching
- Redis caching for URL results
- Request logging middleware

**Key Features**
- Uses Redis for caching (TTL: 1 week)
- Threaded URL processing with ThreadPoolExecutor
- Zombie process cleanup for librewolf
- Detailed request/response logging
- Supports DuckDuckGo search (via `process_search_query`)

**Usage**
```bash
uvicorn scraping_search.external_search_openwebui:app --host 0.0.0.0 --port 8888
```

**Endpoints**
| Route     | Method | Description                  |
|-----------|--------|------------------------------|
| `/search` | POST   | Process search queries       |
| `/loader` | POST   | Load content from URLs       |

**Environment Variables**
```env
redis_host=10.28.33.120
redis_port=30479
```

---

## 2. `external_search_openwebui_mcp.py` - FastMCP Implementation
```python
scraping_search/external_search_openwebui_mcp.py
```

**Overview**  
A FastMCP implementation with Redis integration for web search and content loading. Implements:
- `search_web` tool for DuckDuckGo search
- `url_loader` tool for multi-URL content fetching
- Redis caching for URL results

**Key Features**
- Uses Redis for caching (TTL: 1 week)
- Simple synchronous URL processing
- Context-aware tool execution
- Debug logging enabled

**Usage**
```bash
fastmcp run scraping_search/external_search_openwebui_mcp.py --host 0.0.0.0 --port 8889
```

**Endpoints**
| Route         | Method | Description                  |
|--------------|--------|------------------------------|
| `/search`    | POST   | Web search (via tool)        |
| `/loader`    | POST   | URL content loading (via tool) |

**Environment Variables**
```env
redis_host=localhost
redis_port=6379
```

---

## Differences Between Implementations
| Feature                | FastAPI (`external_search_openwebui.py`)       | FastMCP (`external_search_openwebui_mcp.py`) |
|-----------------------|-----------------------------------------------|-----------------------------------------------|
| Framework             | FastAPI + Uvicorn                            | FastMCP                                      |
| Concurrency           | ThreadPoolExecutor                          | Sequential (simpler flow)                    |
| Caching               | Redis (TTL: 1 week)                         | Redis (TTL: 1 week)                          |
| Logging               | Detailed middleware logging                 | Context-aware logging                        |
| Tool Integration      | No explicit tools                           | @mcp.tool decorators                         |

Both implementations serve the same core functionality but use different frameworks for different use cases.