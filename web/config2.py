import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://hacktest.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', ''),
    'database_id': os.environ.get('COSMOS_DATABASE', 'hackjoblist'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'jobqueue'),
}

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'
container = database.get_container_client(container_name)