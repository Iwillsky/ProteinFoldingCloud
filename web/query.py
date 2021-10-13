from azure.cosmos import CosmosClient
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'hackjoblist'
database = client.get_database_client(database_name)
container_name = 'joblist'
container = database.get_container_client(container_name)

# Enumerate the returned items
import json
for item in container.query_items(
        query='SELECT * FROM r',
        enable_cross_partition_query=True):
    print(json.dumps(item, indent=True))