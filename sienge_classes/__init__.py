import json
import requests
from requests.auth import HTTPBasicAuth

company = "treele"
username = "treele-sistema-x"
token = "hinUoLzppvsCqpIRt9blchboNPLGf4V4"
baseURL = f"https://api.sienge.com.br/{company}/public/api/v1"
auth = HTTPBasicAuth(username, token)

def get_lists_from_sienge(items: list, url: str, offset: int = 0) -> list:
    b_response = requests.get(
        url=url,
        auth=auth,
        params={
            "offset": 0,
            "limit": 200
        }
    )
    requestJson = json.loads(b_response.content.decode("utf-8"))
    items.extend(requestJson['results'])

    if len(items) < requestJson['resultSetMetadata']['count']:
        get_lists_from_sienge(items, url, offset + 200)