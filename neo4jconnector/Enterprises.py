from neo4j import GraphDatabase
from neo4j.spatial import WGS84Point
from neo4jconnector import URI, AUTH
import json

enterprises = json.load(open('../data/bases/Enterprises.json'))

for enterprise in enterprises.values():
    longitude = enterprise['coordinates']['longitude']
    latitude = enterprise['coordinates']['latitude']
    enterprise['coordinates'] = WGS84Point((longitude, latitude))

enterprises = [ enterprise for enterprise in enterprises.values()]

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    for enterprise in enterprises:
        driver.execute_query(
            "MERGE (:Enterprise {id: $id, name: $name, cnpj: $cnpj, address: $address, coordinates: $coordinates, creationDate: $creationDate})",
            parameters_=enterprise,
            database_="neo4j",
        )