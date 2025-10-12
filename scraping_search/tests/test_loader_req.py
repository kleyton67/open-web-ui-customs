import requests

loader_host = "http://10.28.33.120:8488"

urls = ["https://docs.openwebui.com/features/plugin/tools/ "]

payload = {"urls": urls}
                
res = requests.post(f"{loader_host}/loader", json=payload)

import pdb
pdb.set_trace()