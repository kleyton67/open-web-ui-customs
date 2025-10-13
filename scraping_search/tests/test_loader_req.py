import requests

loader_host = "http://0.0.0.0:8888"

urls = ["https://aider.chat/docs/usage/lint-test.html"]

payload = {"urls": urls}
                
res = requests.post(f"{loader_host}/loader", json=payload, allow_redirects=True)

import pdb
pdb.set_trace()