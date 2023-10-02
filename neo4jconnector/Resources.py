from neo4j import GraphDatabase
from neo4jconnector import URI, AUTH
import json

resources = json.load(open('../data/bases/Resources.json'))

financialCategories = [resource['financialCategory'] for resource in resources.values()]
resourceGroups = [resource['resourceGroup'] for resource in resources.values()]

ids = []
setFinancialCategories = []
for financialCategory in financialCategories:
    if financialCategory['id'] not in ids:
        ids.append(financialCategory['id'])
        setFinancialCategories.append(financialCategory)

ids = []
setResourceGroups = []
for resourceGroup in resourceGroups:
    if resourceGroup['id'] not in ids:
        ids.append(resourceGroup['id'])
        setResourceGroups.append(resourceGroup)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    for resource in resources.values():
        print(resource)
        driver.execute_query(
            """
            MERGE (g:ResourceGroup {id: $resourceGroupId, description: $resourceGroupDescription, referenceId: $resourceGroupReferenceId})
            MERGE (f:FinancialCategory {id: $financialCategoryId, description: $financialCategoryDescription})
            MERGE (r:Resource {id: $id, description: $description, unitOfMeasure: $unitOfMeasure, category: $category, resourceCode: $resourceCode, status: $status})
            MERGE (r)-[:RESOURCE_GROUP]->(g)
            MERGE (r)-[:FINANCIAL_CATEGORY]->(f)
            """,
            parameters_= resource,
            resourceGroupId = resource['resourceGroup']['id'],
            resourceGroupDescription = resource['resourceGroup']['description'],
            resourceGroupReferenceId = resource['resourceGroup']['referenceId'],
            financialCategoryId = resource['financialCategory']['id'],
            financialCategoryDescription = resource['financialCategory']['description'],
            database_="neo4j"
        )