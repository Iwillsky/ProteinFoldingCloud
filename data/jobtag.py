import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import time
import os
import sys
import configparser
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-cosmosdb-resources-portal#create-an-azure-cosmos-db-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Item resource for Azure Cosmos
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

def job_tag(strjobid):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' opened'.format(DATABASE_ID))

        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' opened'.format(CONTAINER_ID))                          
        
        items = list(container.query_items(        
            query="SELECT * FROM r WHERE r.jobid=@jobid",
            parameters=[
                { "name":"@jobid", "value": strjobid }
            ],               
            enable_cross_partition_query=True,
            max_item_count=1
        ))
        docid = items[0].get("id")

        read_item = container.read_item(item=docid, partition_key=strjobid)
        read_item['state'] = 'RUNNING'
        response = container.replace_item(item=read_item, body=read_item)
        os.environ['PROTEIN_POLL_ARRIVING']='0'

        print("Job updated as RUNNING")
        
    except exceptions.CosmosHttpResponseError as e:
        print('\nJob state update caught an error. {0}'.format(e.message))

    finally:
        print("\nJob update exit")

if __name__ == '__main__':
    job_tag(sys.arg[1])