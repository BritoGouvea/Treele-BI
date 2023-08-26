from requests.auth import HTTPBasicAuth

company = "treele"
username = "treele-sistema-x"
token = "hinUoLzppvsCqpIRt9blchboNPLGf4V4"
baseURL = f"https://api.sienge.com.br/{company}/public/api/v1"
auth = HTTPBasicAuth(username, token)