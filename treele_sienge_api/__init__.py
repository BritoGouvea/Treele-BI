import requests
from requests.auth import HTTPBasicAuth
import json

company = "treele"
username = "treele-sistema-x"
token = "hinUoLzppvsCqpIRt9blchboNPLGf4V4"
baseURL = f"https://api.sienge.com.br/{company}/public/api/v1"

DATA = []

def get_request(api_endpoint, offset = 0, count = 0):  

    b_response = requests.get(
        url=baseURL+api_endpoint,
        auth=HTTPBasicAuth(username, token),
        params={
            "offset": offset,
            "limit": 200
        }
    )

    print(b_response)

    requestJson = json.loads(b_response.content.decode("utf-8"))

    DATA.extend(requestJson["results"])

    if count == 0:
        count = requestJson["resultSetMetadata"]["count"]

    if count > len(DATA):
        get_request(api_endpoint, offset+200, count)

get_request('/cost-databases/2/resources')

DATA

with open('InsumosAtivos.json', 'w') as outfile:
    json.dump(DATA, outfile, ensure_ascii=False, indent=4)

# PurchaseRequestItems = json.load(open("PurchaseRequestsItems.json"))

# PurchaseRequestIds = [item["purchaseRequestId"] for item in PurchaseRequestItems]

# PurchaseRequestIds = set(PurchaseRequestIds)

# def get_PurchaseRequest(id):
#     b_response = requests.get(
#         url=baseURL + f"/purchase-requests/{id}",
#         auth=HTTPBasicAuth(username, token)
#     )
#     return json.loads(b_response.content.decode("utf-8"))

# PurchaseRequests = json.load(open("PurchaseRequests.json"))
# PRids = [PurchaseRequest['id'] for PurchaseRequest in PurchaseRequests]

# for PurchaseRequestId in PurchaseRequestIds:
#     if PurchaseRequestId not in PRids:
#         PurchaseRequests.append(get_PurchaseRequest(PurchaseRequestId))
#         with open("PurchaseRequests.json", "w") as outfile:
#             json.dump(PurchaseRequests, outfile, ensure_ascii=False, indent=4)

# sorted_PurchaseRequests = sorted(PurchaseRequests, key=lambda x: x['id'])

# unique_PurchaseRequest = []
# seen_PurchaseRequest = set()
# for PurchaseRequest in sorted_PurchaseRequests:
#     if PurchaseRequest['id'] not in seen_PurchaseRequest:
#         unique_PurchaseRequest.append(PurchaseRequest)
#         seen_PurchaseRequest.add(PurchaseRequest['id'])

# with open("PurchaseRequests.json", "w") as outfile:
#     json.dump(sorted_PurchaseRequests, outfile, ensure_ascii=False, indent=4)

# def get_request_buildingApropriations(endpoint):
#     b_response = requests.get(
#         url=baseURL + f"/{endpoint}",
#         auth=HTTPBasicAuth(username, token)
#     )
#     return json.loads(b_response.content.decode("utf-8"))

# ba = get_request_buildingApropriations("purchase-requests/1463/items/1/delivery-requirements")

# def purchase_requests_authorize(purchaseRequestId):
#     b_response = requests.patch(
#         url=baseURL + f"/purchase-requests/{purchaseRequestId}/authorize",
#         auth=HTTPBasicAuth(username, token),
#         params={
#             "purchaseRequestId": purchaseRequestId
#         }
#     )
#     response =  json.loads(b_response.content.decode("utf-8"))
#     print(response)

# response = purchase_requests_authorize(1492)