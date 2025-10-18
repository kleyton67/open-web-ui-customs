from typing import List
import requests
import traceback
from loguru import logger



class Tools:
    def __init__(self):
        self.loader_host = "http://10.28.33.120:8488"

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions

    def open_links(
        self,
        urls: List[str],
    ) -> str:
        """
        Open one or more URLs. 

        Args:
            urls (Union[List[str], str]): A single URL as a string, or a list of URLs.

        Returns:
            str: A message indicating the number of URLs that were successfully opened.

        """

        try:
            if isinstance(urls, list):
                payload = {"urls": urls}
            elif isinstance(urls, str):
                payload = {"urls": [urls]}

            res = requests.post(f"{self.loader_host}/loader", json=payload)

            return "============================".join([f"In the page: {doc['metadata']['url']}\n the content is: {doc['page_content']}" for doc in res.json()])
        except:
            logger.error(traceback.format_exc())
            return None
